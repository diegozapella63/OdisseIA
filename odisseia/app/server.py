"""OdisseIA: os filmes, as séries e os jogos da casa, um app do Home Assistant (ingress). Só biblioteca padrão do Python.

Os dados ficam em /data/odisseia.json (com rev: cada gravação soma 1 e a tela vê pelo /api/rev), as capas em /data/capas,
a chave do TMDB e a conta do IGDB em /data/segredos.json (600; nunca voltam para a tela, só o fim) e as versões
automáticas em /data/versoes. Os filmes e as séries vêm do TMDB (tmdb.py), os jogos do IGDB (igdb.py), as regras dos
títulos são as do regras.py e as ferramentas do CorrerIA, as do ferramentas.py."""
import base64
import hmac
import io
import json
import os
import re
import secrets
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from itertools import zip_longest
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import ferramentas  # noqa: E402
import igdb as G  # noqa: E402
import regras as R  # noqa: E402
import tmdb as T  # noqa: E402


def ler_versao():
    """A versão fica num lugar só, o config.yaml do app: no contêiner, ao lado do server.py (o Dockerfile copia); no
    computador, na pasta de cima."""
    for arq in (os.path.join(AQUI, "config.yaml"), os.path.join(AQUI, "..", "config.yaml")):
        try:
            with open(arq, encoding="utf-8") as f:
                m = re.search(r'^version:\s*"?([\d.]+)', f.read(), re.M)
            if m:
                return m.group(1)
        except OSError:
            continue
    return "0.0.0"


VERSAO = ler_versao()
DEV = os.environ.get("ODISSEIA_DEV") == "1"
DATA_DIR = os.environ.get("ODISSEIA_DATA", "/data")
SHARE_DIR = os.environ.get("ODISSEIA_SHARE", "/share/odisseia")
WWW = os.environ.get("ODISSEIA_WWW", os.path.join(AQUI, "www"))
PORTA = int(os.environ.get("ODISSEIA_PORTA", "8099"))
TOKEN = os.environ.get("SUPERVISOR_TOKEN")
HA_API = os.environ.get("ODISSEIA_HA_API", "http://supervisor/core/api")
TMDB_API = os.environ.get("ODISSEIA_TMDB", T.API)
TMDB_IMG = os.environ.get("ODISSEIA_TMDB_IMG", T.IMG)
IGDB_API = os.environ.get("ODISSEIA_IGDB", G.API)
IGDB_TOKEN = os.environ.get("ODISSEIA_TWITCH", G.TOKEN)
IGDB_IMG = os.environ.get("ODISSEIA_IGDB_IMG", G.IMG)
DADOS_ARQ = os.path.join(DATA_DIR, "odisseia.json")
SEGREDOS_ARQ = os.path.join(DATA_DIR, "segredos.json")
CAPAS = os.path.join(DATA_DIR, "capas")
VERSOES = os.path.join(DATA_DIR, "versoes")
BACKUPS = os.path.join(SHARE_DIR, "backups")
PERMITIDOS = {"172.30.32.2", "127.0.0.1", "::1"}  # o ingress do Home Assistant chega sempre por este endereço
MAX_CORPO = 1024 * 1024
MAX_IMPORTAR = 120 * 1024 * 1024
TRAVA = threading.RLock()
MIME = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
        ".svg": "image/svg+xml", ".png": "image/png", ".woff2": "font/woff2", ".woff": "font/woff", ".txt": "text/plain; charset=utf-8"}


def log(*partes):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), *partes, flush=True)


def agora_iso():
    return datetime.now().isoformat(timespec="seconds")


def _gravar(caminho, dado, modo=None):
    """Grava num arquivo temporário e troca de uma vez (nunca fica um arquivo pela metade)."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    tmp = f"{caminho}.{secrets.token_hex(4)}.tmp"
    with open(tmp, "wb") as f:
        f.write(dado if isinstance(dado, bytes) else dado.encode("utf-8"))
    if modo:
        os.chmod(tmp, modo)
    os.replace(tmp, caminho)


# ---------------------------------------------------------------- os dados

def ler():
    try:
        with open(DADOS_ARQ, encoding="utf-8") as f:
            return R.limpar_dados(json.load(f))
    except (OSError, ValueError):
        return R.limpar_dados({})


def salvar(d, motivo=""):
    """Grava com a revisão nova. Uma vez por dia, a versão de antes vai para as Versões anteriores."""
    d["rev"] = d.get("rev", 0) + 1
    if os.path.exists(DADOS_ARQ) and not any(v["motivo"] == "do dia" and v["em"][:10] == agora_iso()[:10] for v in versoes()):
        guardar_versao("do dia")
    _gravar(DADOS_ARQ, json.dumps(d, ensure_ascii=False, indent=1))
    return d


def versoes():
    """As versões anteriores: [{nome, em, tamanho, motivo}], a mais nova primeiro."""
    out = []
    try:
        nomes = os.listdir(VERSOES)
    except OSError:
        return out
    for n in nomes:
        m = re.match(r"^odisseia-(\d{8})-(\d{6})-([a-z-]+)\.json$", n)
        if not m:
            continue
        em = f"{m.group(1)[:4]}-{m.group(1)[4:6]}-{m.group(1)[6:]}T{m.group(2)[:2]}:{m.group(2)[2:4]}:{m.group(2)[4:]}"
        out.append({"nome": n, "em": em, "tamanho": os.path.getsize(os.path.join(VERSOES, n)), "motivo": m.group(3).replace("-", " ")})
    return sorted(out, key=lambda v: v["nome"], reverse=True)


def guardar_versao(motivo):
    """Uma cópia do arquivo de agora (as 5 últimas ficam)."""
    try:
        with open(DADOS_ARQ, "rb") as f:
            dado = f.read()
    except OSError:
        return
    nome = f"odisseia-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{re.sub(r'[^a-z]+', '-', motivo)}.json"
    _gravar(os.path.join(VERSOES, nome), dado, 0o600)
    for v in versoes()[5:]:
        try:
            os.remove(os.path.join(VERSOES, v["nome"]))
        except OSError:
            pass


# ---------------------------------------------------------------- a chave do TMDB e a conta do IGDB (só em /data, nunca na tela)

def segredos():
    try:
        with open(SEGREDOS_ARQ, encoding="utf-8") as f:
            s = json.load(f)
        return s if isinstance(s, dict) else {}
    except (OSError, ValueError):
        return {}


def chave_tmdb():
    return str(segredos().get("tmdb") or "")


def guardar_chave(chave):
    s = segredos()
    if chave:
        s["tmdb"] = chave
    else:
        s.pop("tmdb", None)
    _gravar(SEGREDOS_ARQ, json.dumps(s), 0o600)


def cliente():
    return T.TMDB(chave_tmdb(), TMDB_API, TMDB_IMG)


ESTADO_TMDB = {"erro": "", "em": ""}  # o último erro do TMDB (some no próximo pedido que dá certo)


def tmdb_fez(fn, *args):
    """Chama o TMDB e lembra o último erro, para a tela mostrar no cartão."""
    try:
        r = fn(*args)
        ESTADO_TMDB.update(erro="", em=agora_iso())
        return r
    except T.ErroTMDB as e:
        ESTADO_TMDB.update(erro=str(e), em=agora_iso())
        raise


def estado_tmdb():
    c = chave_tmdb()
    return {"chave": bool(c), "fim": ("••••" + c[-4:]) if c else "", "erro": ESTADO_TMDB["erro"] if c else ""}


def conta_igdb():
    """(Client ID, Client Secret) do app da casa no Twitch Developers, ou ("", "")."""
    s = segredos()
    return str(s.get("igdb_id") or ""), str(s.get("igdb_segredo") or "")


def guardar_igdb(cid, segredo):
    s = segredos()
    if cid and segredo:
        s.update(igdb_id=cid, igdb_segredo=segredo)
    else:
        s.pop("igdb_id", None)
        s.pop("igdb_segredo", None)
    _gravar(SEGREDOS_ARQ, json.dumps(s), 0o600)


def cliente_igdb():
    return G.IGDB(*conta_igdb(), IGDB_API, IGDB_TOKEN, IGDB_IMG)


ESTADO_IGDB = {"erro": "", "em": ""}


def igdb_fez(fn, *args):
    try:
        r = fn(*args)
        ESTADO_IGDB.update(erro="", em=agora_iso())
        return r
    except G.ErroIGDB as e:
        ESTADO_IGDB.update(erro=str(e), em=agora_iso())
        raise


def estado_igdb():
    c = conta_igdb()[0]
    return {"chave": bool(c), "fim": ("••••" + c[-4:]) if c else "", "erro": ESTADO_IGDB["erro"] if c else ""}


ERROS = (T.ErroTMDB, G.ErroIGDB)


# ---------------------------------------------------------------- as pessoas da casa

_pessoas = {"v": None, "t": 0}


def ha_get(caminho, timeout=10):
    req = urllib.request.Request(HA_API + caminho, headers={"Authorization": f"Bearer {TOKEN}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def pessoas():
    """As pessoas do Home Assistant: [{id, nome, usuario}]. Fora dele, Ana e Beto de exemplo (no computador)."""
    if not TOKEN:
        return [{"id": "person.ana", "nome": "Ana", "usuario": "u-ana"}, {"id": "person.beto", "nome": "Beto", "usuario": "u-beto"}] if DEV else []
    if _pessoas["v"] is not None and time.time() - _pessoas["t"] < 60:
        return _pessoas["v"]
    try:
        v = sorted(({"id": s["entity_id"], "nome": (s.get("attributes") or {}).get("friendly_name") or s["entity_id"][7:],
                     "usuario": str((s.get("attributes") or {}).get("user_id") or "")}
                    for s in ha_get("/states") if str(s.get("entity_id", "")).startswith("person.")), key=lambda p: R.sem_acento(p["nome"]))
    except (urllib.error.URLError, OSError, ValueError, TypeError, KeyError) as e:
        log("Pessoas do Home Assistant:", e)
        return _pessoas["v"] or []
    _pessoas.update(v=v, t=time.time())
    return v


def eu(usuario):
    return next((p["id"] for p in pessoas() if usuario and p["usuario"] == usuario), "")


# ---------------------------------------------------------------- as capas

def caminho_capa(nome):
    return os.path.join(CAPAS, nome)


def gravar_capa(t, dado):
    if not dado:
        return
    nome = t["id"] + (".png" if dado[:4] == b"\x89PNG" else ".jpg")
    _gravar(caminho_capa(nome), dado)
    if t.get("capa") and t["capa"] != nome:
        apagar_capa(t["capa"])
    t["capa"] = nome


def apagar_capa(nome):
    if nome and re.match(r"^t[0-9a-f]{8}\.(jpg|png)$", nome):
        try:
            os.remove(caminho_capa(nome))
        except OSError:
            pass


IMGS = {}  # as capas da busca (o Adicionar), na memória: {tamanho+caminho: bytes}, até 300


def baixar_capa(tipo, capa):
    """Os bytes da capa de um título (a do TMDB num filme ou numa série, a do IGDB num jogo), ou None."""
    if not capa:
        return None
    return cliente_igdb().imagem(capa, "t_cover_big") if tipo == "jogo" else cliente().imagem(capa, "w342")


def capa_da_busca(tamanho, caminho):
    k = tamanho + caminho
    if k not in IMGS:
        dado = cliente_igdb().imagem(caminho, tamanho) if tamanho.startswith("t_") else cliente().imagem(caminho, tamanho)
        if not dado:
            return None
        if len(IMGS) >= 300:
            IMGS.pop(next(iter(IMGS)))
        IMGS[k] = dado
    return IMGS[k]


# ---------------------------------------------------------------- os títulos

def adicionar(corpo, quem_usa=""):
    tipo = corpo.get("tipo")
    n = corpo.get(R.fonte(tipo))
    if tipo not in R.TIPOS or not isinstance(n, int) or isinstance(n, bool):
        raise ValueError("Escolha um filme, uma série ou um jogo da busca.")
    situacao = corpo.get("situacao") or "quero"
    if situacao not in R.SITUACOES:
        raise ValueError("A situação vale quero ou visto.")
    R.conferir_tipo(ler(), tipo)
    with TRAVA:
        ja = R.de_fonte(ler(), tipo, n)
    if ja:
        return {"titulo": ja, "novo": False}
    det = detalhes(tipo, n)
    capa = baixar_capa(tipo, det.get("capa"))
    quem = [quem_usa] if quem_usa and ler()["ajustes"]["quem"] else []
    with TRAVA:
        d = ler()
        t, novo = R.criar(d, det, situacao, quem, agora_iso())
        if novo:
            gravar_capa(t, capa)
            salvar(d)
    return {"titulo": t, "novo": novo}


def marcar_ja(rs, d=None):
    """Cada resultado do TMDB ou do IGDB com ja (o id na lista) e a situação dele (None fora da lista)."""
    d = d or ler()
    for r in rs:
        ja = R.de_fonte(d, r["tipo"], r.get(R.fonte(r["tipo"]))) if r["tipo"] in R.TIPOS else None
        r.update(ja=ja["id"] if ja else None, situacao=ja["situacao"] if ja else None)
    return rs


def tipo_de_busca(tipo):
    """O tipo de uma busca: o pedido, ou o único ligado em Opções › O que controlar."""
    ligados = R.tipos_ligados(ler())
    return tipo if tipo in ligados else (ligados[0] if len(ligados) == 1 else "")


def so_ligados(rs):
    ligados = R.tipos_ligados(ler())
    return [r for r in rs if r["tipo"] in ligados or (r["tipo"] == "colecao" and "filme" in ligados) or (r["tipo"] == "colecao_jogos" and "jogo" in ligados)]


def fontes(tipo):
    """De onde vêm uma busca e uma lista: (TMDB, IGDB). Com um tipo, a dele; sem tipo, as dos tipos ligados que têm a
    conta posta (sem nenhuma, a dos filmes e das séries, que diz o que falta)."""
    if tipo == "jogo":
        return False, True
    if tipo in ("filme", "serie"):
        return True, False
    lig = set(R.tipos_ligados(ler()))
    tv = bool(lig & {"filme", "serie"})
    tm, ig = tv and bool(chave_tmdb()), "jogo" in lig and bool(conta_igdb()[0])
    return (tm, ig) if tm or ig else (tv, not tv)


def juntar(chamadas):
    """Chama cada fonte e junta: as coleções na frente, depois um resultado de cada fonte por vez. Uma que falha fica de
    fora se outra deu certo. (resultados, tem_mais)"""
    partes, erro = [], None
    for fn in chamadas:
        try:
            partes.append(fn())
        except ERROS as e:
            erro = erro or e
    if not partes:
        raise erro
    cols = [[r for r in p[0] if r["tipo"].startswith("colecao")] for p in partes]
    outros = [[r for r in p[0] if not r["tipo"].startswith("colecao")] for p in partes]
    um_de_cada = lambda ls: [x for grupo in zip_longest(*ls) for x in grupo if x]  # noqa: E731
    return um_de_cada(cols) + um_de_cada(outros), any(p[1] for p in partes)


def buscar(q, tipo):
    tipo = tipo_de_busca(tipo)
    tm, ig = fontes(tipo)
    chamadas = []
    if tm:
        chamadas.append(lambda: (com_colecao(so_ligados(tmdb_fez(cliente().buscar, q, tipo))), False))
    if ig:
        chamadas.append(lambda: (so_ligados(igdb_fez(cliente_igdb().buscar, q)), False))
    return marcar_ja(juntar(chamadas)[0])


DETALHES = {}  # (tipo, número) → (quando, detalhes): os detalhes lidos valem 12 horas (a coleção de cada filme da lista)


def detalhes(tipo, n):
    v = DETALHES.get((tipo, n))
    if v and time.time() - v[0] < 12 * 3600:
        return v[1]
    det = igdb_fez(cliente_igdb().detalhes, n) if tipo == "jogo" else tmdb_fez(cliente().detalhes, tipo, n)
    if len(DETALHES) > 3000:
        DETALHES.clear()
    DETALHES[(tipo, n)] = (time.time(), det)
    return det


def com_colecao(rs):
    """0.3.0 (o dono: "uma opção direta nessa tela para eu clicar e abrir a coleção"): cada filme da lista com a coleção
    dele, pelos detalhes (8 de cada vez, guardados por 12 horas). Um filme que não deu fica sem."""
    def um(r):
        try:
            r["colecao"] = detalhes("filme", r["tmdb"]).get("colecao")
        except T.ErroTMDB:
            r["colecao"] = None
    filmes = [r for r in rs if r["tipo"] == "filme"]
    if filmes:
        with ThreadPoolExecutor(max_workers=8) as ex:
            list(ex.map(um, filmes))
    return rs


def _pagina(pagina, maximo=5):
    try:
        return max(1, min(maximo, int(pagina)))
    except (TypeError, ValueError):
        return 1


def lista_colecoes(pagina):
    """As coleções dos filmes mais populares e mais bem avaliados (o TMDB não tem uma lista de coleções), sem repetir."""
    pagina = _pagina(pagina)
    filmes = []
    for nome in ("populares", "avaliados"):
        filmes += tmdb_fez(cliente().lista, nome, "filme", pagina)[0]
    out, vistos = [], set()
    for r in com_colecao(filmes):
        c = r.get("colecao")
        if c and c["id"] not in vistos:
            vistos.add(c["id"])
            out.append({"tmdb": c["id"], "tipo": "colecao", "nome": c["nome"], "original": "", "ano": None, "data": "", "capa": c.get("capa") or "", "sinopse": ""})
    return out, pagina < 5


def lista_colecoes_jogos(pagina):
    """As coleções (as séries de jogos) dos jogos em alta e dos mais bem avaliados, sem repetir."""
    pagina = _pagina(pagina)
    jogos = []
    for nome in ("alta", "avaliados"):
        jogos += igdb_fez(cliente_igdb().lista, nome, pagina)[0]
    out, vistos = [], set()
    for j in jogos:
        c = j.get("colecao")
        if c and c["id"] not in vistos:
            vistos.add(c["id"])
            out.append(G.como_colecao(c))
    return out, pagina < 5


def lista_pronta(nome, tipo="", pagina=1):
    """Uma lista pronta: a do TMDB (filmes e séries), a do IGDB (jogos) ou as duas juntas (Tudo)."""
    if nome not in T.LISTAS:
        raise ValueError("Lista desconhecida.")
    tipo = tipo_de_busca(tipo)
    lig = R.tipos_ligados(ler())
    tm, ig = fontes(tipo)
    chamadas = []
    if nome == "colecoes":
        if tm and "filme" in lig and tipo != "serie":
            chamadas.append(lambda: lista_colecoes(pagina))
        if ig:
            chamadas.append(lambda: lista_colecoes_jogos(pagina))
        if not chamadas:
            return {"resultados": [], "mais": False}
    else:
        if tm:
            def do_tmdb():
                rs, mais = tmdb_fez(cliente().lista, nome, tipo, pagina)
                return com_colecao(so_ligados(rs)), mais
            chamadas.append(do_tmdb)
        if ig:
            chamadas.append(lambda: igdb_fez(cliente_igdb().lista, nome, pagina))
    rs, mais = juntar(chamadas)
    return {"resultados": marcar_ja(rs), "mais": mais}


def colecao_de(tipo, n):
    return igdb_fez(cliente_igdb().colecao, n) if tipo == "jogo" else tmdb_fez(cliente().colecao, n)


def colecao(n, tipo="filme"):
    """Uma coleção (uma saga de filmes ou uma série de jogos) com o que já está na lista: cada item com ja (o id),
    situacao e saiu."""
    col = colecao_de(tipo, n)
    d, hoje, k = ler(), agora_iso()[:10], R.fonte(tipo)
    for f in col["itens"]:
        ja = R.de_fonte(d, tipo, f[k])
        f.update(ja=ja["id"] if ja else None, situacao=ja["situacao"] if ja else None, saiu=bool(f["data"]) and f["data"] <= hoje)
    return col


def adicionar_colecao(corpo, quem_usa=""):
    """Põe tudo de uma coleção na lista (os filmes de uma saga, os jogos de uma série), como Quero ver (jogar) ou como
    Visto (Jogado). Visto: só os que já saíram, e os que já estavam na lista viram Visto; Quero ver não mexe nos que já
    estavam. {nome, tipo, novos, marcados, ja, fora}"""
    n, situacao, tipo = corpo.get("colecao"), corpo.get("situacao") or "quero", corpo.get("tipo") or "filme"
    if not isinstance(n, int) or isinstance(n, bool):
        raise ValueError("Escolha uma coleção da busca.")
    if tipo not in ("filme", "jogo"):
        raise ValueError("Uma coleção é de filmes ou de jogos.")
    if situacao not in ("quero", "visto"):
        raise ValueError("Numa coleção, a situação vale quero ou visto.")
    R.conferir_tipo(ler(), tipo)
    # 0.5.0 (o dono: "antes do já vi todos, as opções de categorias para selecionar a categoria de todos"): a categoria vale
    # para tudo o que entra (os novos e os que já estavam)
    cat = corpo.get("categoria")
    cats = {c["id"]: c["nome"] for c in ler()["categorias"][tipo]}
    if cat is not None and (not isinstance(cat, str) or (cat and cat not in cats)):
        raise ValueError("Categoria desconhecida.")
    col = colecao_de(tipo, n)
    hoje, k = agora_iso()[:10], R.fonte(tipo)
    with TRAVA:
        d = ler()
    entram = [f for f in col["itens"] if situacao == "quero" or (f["data"] and f["data"] <= hoje)]
    faltam = [f[k] for f in entram if not R.de_fonte(d, tipo, f[k])]
    if tipo == "jogo":
        dets = igdb_fez(cliente_igdb().varios, faltam) if faltam else {}
        dets = [dets[i] for i in faltam if i in dets]
    else:
        dets = [detalhes("filme", i) for i in faltam]
    with ThreadPoolExecutor(max_workers=6) as ex:
        capas = list(ex.map(lambda det: baixar_capa(tipo, det.get("capa")), dets))
    res = {"nome": col["nome"], "tipo": tipo, "novos": 0, "marcados": 0, "ja": 0, "fora": len(col["itens"]) - len(entram)}
    with TRAVA:
        d = ler()
        quem = [quem_usa] if quem_usa and d["ajustes"]["quem"] else []
        criados = set()
        for det, capa in reversed(list(zip(dets, capas))):  # o primeiro da coleção fica em cima
            t, criou = R.criar(d, det, situacao, quem, agora_iso())
            if criou:
                gravar_capa(t, capa)
                criados.add(t["id"])
                res["novos"] += 1
        for f in entram:
            t = R.de_fonte(d, tipo, f[k])
            if not t or t["id"] in criados:
                continue
            if situacao == "visto" and t["situacao"] != "visto":
                R.mudar(t, {"situacao": "visto"}, None, agora_iso())
                res["marcados"] += 1
            else:
                res["ja"] += 1
        mudou = False
        if cat is not None:
            res["categoria"] = cats.get(cat, "")
            for f in entram:
                t = R.de_fonte(d, tipo, f[k])
                if t and t["categoria"] != cat:
                    t["categoria"], mudou = cat, True
        if res["novos"] or res["marcados"] or mudou:
            salvar(d)
    res["rev"] = d["rev"]
    return res


def atualizar(tid):
    """Os detalhes de novo pelo TMDB ou pelo IGDB (o próximo episódio, onde assistir, as plataformas, a capa)."""
    with TRAVA:
        t = R.achar(ler(), tid)
    tipo, n = t["tipo"], t.get(R.fonte(t["tipo"]))
    if not n:
        raise ValueError("Esse título não veio do " + ("IGDB." if tipo == "jogo" else "TMDB."))
    det = igdb_fez(cliente_igdb().detalhes, n) if tipo == "jogo" else tmdb_fez(cliente().detalhes, tipo, n)
    antes = t.get("capa_igdb" if tipo == "jogo" else "capa_tmdb")
    capa = None
    if det.get("capa") and (det["capa"] != antes or not t.get("capa") or not os.path.exists(caminho_capa(t["capa"]))):
        capa = baixar_capa(tipo, det["capa"])
    with TRAVA:
        d = ler()
        t = next((x for x in d["titulos"] if x["id"] == tid), None)
        if not t:
            raise ValueError("Esse título não está mais na lista.")
        R.aplicar_detalhes(t, det, agora_iso())
        if capa:
            gravar_capa(t, capa)
        salvar(d)
    return t


def mudar_varios(corpo):
    """O Alterar do Selecionar: {itens: [{id, campos: {categoria?, quem?}}]} → {titulos, rev}."""
    with TRAVA:
        d = ler()
        ts = R.lote(d, corpo.get("itens"), {p["id"] for p in pessoas()}, agora_iso())
        salvar(d)
    return {"titulos": ts, "rev": d["rev"]}


def mudar_titulo(corpo):
    acao, tid = corpo.get("acao"), str(corpo.get("id") or "")
    if acao == "lote":
        return mudar_varios(corpo)
    with TRAVA:
        d = ler()
        t = next((x for x in d["titulos"] if x["id"] == tid), None)
        if not t:
            raise ValueError("Esse título não está mais na lista.")
        if acao == "mudar":
            R.mudar(t, corpo.get("campos"), {p["id"] for p in pessoas()} | set(t["quem"]), agora_iso(), d["categorias"][t["tipo"]])
        elif acao == "proximo":
            R.proximo_ep(t, agora_iso())
        elif acao == "apagar":
            d["titulos"] = [x for x in d["titulos"] if x["id"] != tid]
            apagar_capa(t.get("capa"))
        else:
            raise ValueError("Ação desconhecida.")
        salvar(d)
    return {"titulo": None if acao == "apagar" else t, "rev": d["rev"]}


def precisa_atualizar(t, agora):
    """No laço: as séries que a casa vê ou quer ver e os jogos que ainda vão sair, de dia em dia (o próximo episódio, a
    data); o resto, de semana em semana."""
    if not t.get(R.fonte(t["tipo"])):
        return False
    try:
        idade = agora - datetime.fromisoformat(t.get("igdb_em" if t["tipo"] == "jogo" else "tmdb_em") or "2000-01-01T00:00:00")
    except ValueError:
        return True
    if t["tipo"] == "serie" and t["situacao"] == "quero" or t["tipo"] == "jogo" and t["situacao"] == "quero" and (t.get("data") or "9") > agora.date().isoformat():
        return idade > timedelta(hours=20)
    return idade > timedelta(days=7)


def uma_volta(agora=None):
    """Uma passada do laço: até 30 títulos com os detalhes velhos. Uma fonte sem a conta (ou sem internet) para ali."""
    agora = agora or datetime.now()
    tem = {"tmdb": bool(chave_tmdb()), "igdb": bool(conta_igdb()[0])}
    parou = set()
    fila = [(t["id"], R.fonte(t["tipo"])) for t in ler()["titulos"] if tem[R.fonte(t["tipo"])] and precisa_atualizar(t, agora)][:30]
    for tid, f in fila:
        if f in parou:
            continue
        try:
            atualizar(tid)
        except (ValueError, *ERROS) as e:
            log("Atualizar", tid, e)
            if any(p in str(e) for p in ("chave", "internet", "Client", "acesso")):
                parou.add(f)
        time.sleep(0.5)


def laco():
    time.sleep(60)
    while True:
        try:
            uma_volta()
        except Exception as e:  # noqa: BLE001 (o laço nunca para)
            log("Laço:", e)
        time.sleep(30 * 60)


# ---------------------------------------------------------------- Dados: exportar, backup, importar, versões, começar do zero

def montar_zip():
    with TRAVA:
        d = ler()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("odisseia.json", json.dumps(d, ensure_ascii=False, indent=1))
        z.writestr("manifesto.json", json.dumps({"app": "odisseia", "nome": "OdisseIA", "versao": VERSAO, "gravado_em": datetime.now().astimezone().isoformat(timespec="seconds")}))
        for t in d["titulos"]:
            if t.get("capa") and os.path.exists(caminho_capa(t["capa"])):
                z.write(caminho_capa(t["capa"]), "capas/" + t["capa"], compress_type=zipfile.ZIP_STORED)
    return buf.getvalue()


def nome_zip():
    return f"odisseia-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}.zip"


def backups():
    try:
        nomes = sorted((n for n in os.listdir(BACKUPS) if re.match(r"^odisseia-[\d-]+\.zip$", n)), reverse=True)
    except OSError:
        return []
    out = []
    for n in nomes:
        p = os.path.join(BACKUPS, n)
        out.append({"nome": n, "em": datetime.fromtimestamp(os.path.getmtime(p)).isoformat(timespec="seconds"), "tamanho": os.path.getsize(p), "motivo": ""})
    return out


def fazer_backup():
    dado = montar_zip()
    nome = nome_zip()
    _gravar(os.path.join(BACKUPS, nome), dado, 0o600)
    for b in backups()[10:]:
        try:
            os.remove(os.path.join(BACKUPS, b["nome"]))
        except OSError:
            pass
    return nome


def ler_pacote(dado):
    """O que vem num arquivo do Exportar (um .zip com o odisseia.json e as capas) ou só o odisseia.json: (dados, capas)."""
    capas = {}
    if dado[:2] == b"PK":
        try:
            with zipfile.ZipFile(io.BytesIO(dado)) as z:
                nomes = set(z.namelist())
                if "odisseia.json" not in nomes:
                    raise ValueError("Esse arquivo não é um backup do OdisseIA.")
                bruto = json.loads(z.read("odisseia.json").decode("utf-8"))
                for n in nomes:
                    m = re.match(r"^capas/(t[0-9a-f]{8}\.(?:jpg|png))$", n)
                    if m and z.getinfo(n).file_size <= T.MAX_IMG:
                        capas[m.group(1)] = z.read(n)
        except (zipfile.BadZipFile, KeyError, UnicodeDecodeError) as e:
            raise ValueError("Não consegui abrir esse arquivo.") from e
    else:
        try:
            bruto = json.loads(dado.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as e:
            raise ValueError("Esse arquivo não é um backup do OdisseIA.") from e
    if not isinstance(bruto, dict) or not isinstance(bruto.get("titulos"), list):
        raise ValueError("Esse arquivo não é um backup do OdisseIA.")
    return R.limpar_dados(bruto), capas


def trocar_tudo(novos, capas, motivo):
    """Troca os dados (e as capas) pelos de um arquivo: antes, a versão de agora vai para as Versões anteriores."""
    with TRAVA:
        guardar_versao(motivo)
        atual = ler()
        novos["rev"] = atual["rev"]
        novos["ajustes"]["correria"] = atual["ajustes"]["correria"]  # a ligação com o CorrerIA é desta casa
        usados = set()
        for t in novos["titulos"]:
            if t.get("capa") in capas:
                _gravar(caminho_capa(t["capa"]), capas[t["capa"]])
            if t.get("capa"):
                usados.add(t["capa"])
        try:
            for n in os.listdir(CAPAS):
                if n not in usados:
                    apagar_capa(n)
        except OSError:
            pass
        salvar(novos)
    publicar_correria()
    return novos


def restaurar(origem, nome):
    if origem == "backup" and re.match(r"^odisseia-[\d-]+\.zip$", str(nome)):
        arq = os.path.join(BACKUPS, nome)
    elif origem == "versao" and re.match(r"^odisseia-\d{8}-\d{6}-[a-z-]+\.json$", str(nome)):
        arq = os.path.join(VERSOES, nome)
    else:
        raise ValueError("Escolha um backup ou uma versão da lista.")
    try:
        with open(arq, "rb") as f:
            dado = f.read()
    except OSError as e:
        raise ValueError("Esse arquivo não existe mais.") from e
    novos, capas = ler_pacote(dado)
    return trocar_tudo(novos, capas, "antes de restaurar")


def zerar():
    with TRAVA:
        guardar_versao("antes de apagar tudo")
        d = ler()
        for t in d["titulos"]:
            apagar_capa(t.get("capa"))
        d["titulos"] = []
        salvar(d)
    return d


# ---------------------------------------------------------------- CorrerIA (o WhatsApp, o Claude e o Gemini)

class Conexao:
    """A chave (em /data) e o arquivo na pasta share que o CorrerIA lê (url, ip_url, chave, as ferramentas)."""

    def __init__(self):
        self.arq_chave = os.path.join(DATA_DIR, "correria.key")
        self.arq_share = os.path.join(SHARE_DIR, "correria.json")
        self._chave = None
        self.ultimo = None

    def chave(self):
        if not self._chave:
            try:
                with open(self.arq_chave, encoding="utf-8") as f:
                    self._chave = f.read().strip()
            except OSError:
                self._chave = ""
            if len(self._chave) < 32:
                self._chave = secrets.token_urlsafe(32)
                _gravar(self.arq_chave, self._chave, 0o600)
        return self._chave

    def endereco(self):
        url = os.environ.get("ODISSEIA_URL_INTERNA")
        if url:
            return url.rstrip("/"), None
        host = socket.gethostname()
        try:
            ip = socket.gethostbyname(host)
        except OSError:
            ip = None
        return f"http://{host}:{PORTA}", ip

    def publicar(self, ligado):
        try:
            if not ligado:
                if os.path.exists(self.arq_share):
                    os.remove(self.arq_share)
                return
            url, ip = self.endereco()
            corpo = {"app": "odisseia", "nome": "OdisseIA",
                     "assunto": "filmes, séries e jogos da casa: o que cada um quer ver (ou jogar) ou já viu (ou jogou), episódios, categorias e onde assistir",
                     "versao": VERSAO, "url": url, "ip_url": f"http://{ip}:{PORTA}" if ip else None, "chave": self.chave(),
                     "ferramentas": "/api/integracao/ferramentas", "gravado_em": datetime.now().isoformat(timespec="seconds")}
            _gravar(self.arq_share, json.dumps(corpo, ensure_ascii=False, indent=1), 0o600)
        except OSError as e:
            log("CorrerIA: não consegui gravar", self.arq_share, e)

    def autorizado(self, headers):
        h = headers.get("Authorization") or ""
        return h.startswith("Bearer ") and hmac.compare_digest(h[7:].strip().encode(), self.chave().encode())


CORRERIA = Conexao()


def correria_ligada():
    return ler()["ajustes"]["correria"]


def publicar_correria():
    CORRERIA.publicar(correria_ligada())


def usar_ferramenta(corpo):
    nome = str(corpo.get("nome") or "")
    if nome not in ferramentas.POR_NOME:
        raise KeyError(nome)
    args = corpo.get("argumentos") if isinstance(corpo.get("argumentos"), dict) else {}
    p = corpo.get("pessoa") if isinstance(corpo.get("pessoa"), dict) else {}
    ps = [{"id": x["id"], "nome": x["nome"]} for x in pessoas()]
    pid = str(p.get("id") or "") if str(p.get("id") or "").startswith("person.") else next(
        (x["id"] for x in ps if R.sem_acento(x["nome"]) == R.sem_acento(p.get("nome"))), "")
    det, capa = None, None
    if nome == "lista_pronta":
        a = ferramentas.conferir(nome, args)
        try:
            r = lista_pronta(a["lista"], a.get("tipo") or "")
        except (*ERROS, R.ErroRegra) as e:
            raise ferramentas.ErroFerramenta(str(e)) from e
        CORRERIA.ultimo = {"app": str(corpo.get("cliente") or "CorrerIA")[:40], "em": agora_iso(), "nome": nome}
        return {"texto": ferramentas.texto_lista(a["lista"], r["resultados"], tipo_de_busca(a.get("tipo") or ""))}
    if nome == "adicionar_colecao":
        a = ferramentas.conferir(nome, args)
        tipo = a.get("tipo") or "filme"
        try:
            R.conferir_tipo(ler(), tipo)
            if tipo == "jogo":
                col = ferramentas.melhor([r for r in igdb_fez(cliente_igdb().buscar, a["nome"]) if r["tipo"] == "colecao_jogos"], a["nome"])
            else:
                col = ferramentas.melhor(tmdb_fez(cliente().colecoes, a["nome"]), a["nome"])
            if not col:
                raise ferramentas.ErroFerramenta(f"Não achei a coleção «{a['nome']}» no {'IGDB' if tipo == 'jogo' else 'TMDB'}.")
            extra = {"categoria": R.achar_categoria(ler(), tipo, a["categoria"])} if "categoria" in a else {}
            res = adicionar_colecao(dict({"colecao": col[R.fonte(tipo)], "tipo": tipo, "situacao": a.get("situacao") or "quero"}, **extra), pid)
        except (*ERROS, ValueError) as e:  # R.ErroRegra também é um ValueError
            raise ferramentas.ErroFerramenta(str(e)) from e
        texto = ferramentas.texto_colecao(res, a.get("situacao") or "quero")
        CORRERIA.ultimo = {"app": str(corpo.get("cliente") or "CorrerIA")[:40], "em": agora_iso(), "nome": nome}
        log("CorrerIA:", CORRERIA.ultimo["app"], nome, "→", texto)
        return {"texto": texto}
    ligados = R.tipos_ligados(ler())
    if nome == "adicionar":
        ferramentas.conferir(nome, args)
        tipo = args.get("tipo") or (ligados[0] if len(ligados) == 1 else None)
        try:
            R.conferir_tipo(ler(), tipo)
        except R.ErroRegra as e:
            raise ferramentas.ErroFerramenta(str(e)) from e
        try:
            # sem tipo, procura nos dois (os filmes e as séries no TMDB, os jogos no IGDB): o nome igual decide
            achou = ferramentas.melhor([r for r in buscar(args["nome"], tipo or "") if r["tipo"] in R.TIPOS], args["nome"], tipo, args.get("ano"))
            if achou:
                k = R.fonte(achou["tipo"])
                with TRAVA:
                    ja = R.de_fonte(ler(), achou["tipo"], achou[k])
                if not ja:
                    det = detalhes(achou["tipo"], achou[k])
                    capa = baixar_capa(achou["tipo"], det.get("capa"))
                else:
                    det = {"tipo": ja["tipo"], k: ja[k]}
        except ERROS as e:
            raise ferramentas.ErroFerramenta(str(e)) from e
    with TRAVA:
        d = ler()
        # o que está desligado em Opções › O que controlar fica fora do que o CorrerIA vê, e volta inteiro ao gravar
        fora = [t for t in d["titulos"] if t["tipo"] not in ligados]
        d["titulos"] = [t for t in d["titulos"] if t["tipo"] in ligados]
        texto, mudou = ferramentas.chamar(nome, args, d, ps, pid, det, agora_iso())
        d["titulos"] += fora
        if mudou:
            if nome == "adicionar" and capa:
                gravar_capa(d["titulos"][0], capa)
            if nome == "apagar":
                vivos = {t["capa"] for t in d["titulos"] if t.get("capa")}
                for t in ler()["titulos"]:
                    if t.get("capa") and t["capa"] not in vivos:
                        apagar_capa(t["capa"])
            salvar(d)
    CORRERIA.ultimo = {"app": str(corpo.get("cliente") or "CorrerIA")[:40], "em": agora_iso(), "nome": nome}
    if mudou:
        log("CorrerIA:", CORRERIA.ultimo["app"], nome, "→", texto.split("\n")[0][:160])
    return {"texto": texto}


# ---------------------------------------------------------------- a tela

def estado(usuario=""):
    d = ler()
    ligados = R.tipos_ligados(d)
    return {"versao": VERSAO, "rev": d["rev"], "titulos": [t for t in d["titulos"] if t["tipo"] in ligados], "categorias": d["categorias"], "ajustes": d["ajustes"], "hoje": agora_iso()[:10],
            "pessoas": [{"id": p["id"], "nome": p["nome"]} for p in pessoas()], "eu": eu(usuario), "tmdb": estado_tmdb(), "igdb": estado_igdb(),
            "correria": {"ligado": d["ajustes"]["correria"], "ultimo": CORRERIA.ultimo}}


def mudar_ajustes(corpo):
    with TRAVA:
        d = ler()
        a = d["ajustes"]
        if "cor" in corpo:
            if not isinstance(corpo["cor"], str) or not re.match(r"^[a-z]{2,12}$", corpo["cor"]):
                raise ValueError("Cor desconhecida.")
            a["cor"], a["cor_dia"] = corpo["cor"], False
        for k in ("cor_dia", "quem", "correria"):
            if k in corpo:
                if not isinstance(corpo[k], bool):
                    raise ValueError(f"{k}: ligado ou desligado.")
                a[k] = corpo[k]
        if "tipos" in corpo:
            t = corpo["tipos"]
            if not isinstance(t, dict) or any(k not in R.TIPOS or not isinstance(v, bool) for k, v in t.items()):
                raise ValueError("tipos: filme, serie e jogo, ligado ou desligado.")
            novos = dict(a["tipos"], **t)
            if not any(novos.values()):
                raise ValueError("Deixe pelo menos um ligado.")
            a["tipos"] = novos
        salvar(d)
    if "correria" in corpo:
        publicar_correria()
    return a


def salvar_chave(corpo):
    chave = " ".join(str(corpo.get("chave") or "").split())
    if not chave:
        guardar_chave("")
        ESTADO_TMDB.update(erro="", em="")
        return estado_tmdb()
    if len(chave) > 600 or not re.match(r"^[A-Za-z0-9._-]+$", chave):
        raise ValueError("Essa chave não parece do TMDB: copie a «Chave da API» ou o «Token de leitura da API».")
    T.TMDB(chave, TMDB_API, TMDB_IMG).testar()
    guardar_chave(chave)
    ESTADO_TMDB.update(erro="", em=agora_iso())
    return estado_tmdb()


def salvar_igdb(corpo):
    """A conta do IGDB: o Client ID e o Client Secret do app da casa no Twitch Developers (testados antes de guardar)."""
    cid, seg = (" ".join(str(corpo.get(k) or "").split()) for k in ("cliente", "segredo"))
    if not cid and not seg:
        guardar_igdb("", "")
        ESTADO_IGDB.update(erro="", em="")
        return estado_igdb()
    if not re.match(r"^[A-Za-z0-9]{10,60}$", cid) or not re.match(r"^[A-Za-z0-9]{10,60}$", seg):
        raise ValueError("Copie o Client ID e o Client Secret do app no Twitch Developers.")
    G.IGDB(cid, seg, IGDB_API, IGDB_TOKEN, IGDB_IMG).testar()
    guardar_igdb(cid, seg)
    ESTADO_IGDB.update(erro="", em=agora_iso())
    return estado_igdb()


class Handler(BaseHTTPRequestHandler):
    server_version = "OdisseIA/" + VERSAO

    def log_message(self, fmt, *args):
        if DEV:
            log(self.address_string(), fmt % args)

    def caminho(self):
        return urlparse(self.path).path.rstrip("/") or "/"

    def permitido(self):
        if self.caminho() == "/api/integracao/ferramentas":
            if correria_ligada() and CORRERIA.autorizado(self.headers):
                return True
            self.enviar(401, {"erro": "Chave inválida ou CorrerIA desligado no OdisseIA."})
            return False
        if DEV or self.client_address[0].replace("::ffff:", "") in PERMITIDOS:
            return True
        self.send_error(403, "Use o OdisseIA pelo painel do Home Assistant.")
        return False

    def enviar(self, status, corpo, tipo="application/json", extra=None):
        if isinstance(corpo, (dict, list)):
            corpo = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
            tipo = "application/json; charset=utf-8"
        elif isinstance(corpo, str):
            corpo = corpo.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("X-Content-Type-Options", "nosniff")
        if not (extra or {}).get("Cache-Control"):
            self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(corpo)

    def corpo(self, limite=MAX_CORPO):
        n = int(self.headers.get("Content-Length") or 0)
        if n > limite:
            raise ValueError("Arquivo grande demais.")
        return self.rfile.read(n) if n else b""

    def corpo_json(self, limite=MAX_CORPO):
        b = self.corpo(limite)
        dado = json.loads(b.decode("utf-8")) if b else {}
        if not isinstance(dado, dict):
            raise ValueError("O pedido precisa ser um objeto JSON.")
        return dado

    def usuario(self):
        return self.headers.get("X-Remote-User-Id") or ("u-ana" if DEV and not TOKEN else "")

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if not self.permitido():
            return
        c = self.caminho()
        q = parse_qs(urlparse(self.path).query)
        try:
            if c == "/api/estado":
                return self.enviar(200, estado(self.usuario()))
            if c == "/api/rev":
                return self.enviar(200, {"rev": ler()["rev"]})
            if c == "/api/busca":
                return self.enviar(200, {"resultados": buscar((q.get("q") or [""])[0], (q.get("tipo") or [""])[0])})
            if c == "/api/lista":
                return self.enviar(200, lista_pronta((q.get("nome") or [""])[0], (q.get("tipo") or [""])[0], (q.get("pagina") or ["1"])[0]))
            m = re.match(r"^/api/capa/(t[0-9a-f]{8}\.(?:jpg|png))$", c)
            if m:
                try:
                    with open(caminho_capa(m.group(1)), "rb") as f:
                        dado = f.read()
                except OSError:
                    return self.enviar(404, {"erro": "Sem capa."})
                return self.enviar(200, dado, MIME[os.path.splitext(m.group(1))[1]] if m.group(1).endswith(".png") else "image/jpeg",
                                   {"Cache-Control": "private, max-age=604800"})
            m = re.match(r"^/api/img/(w92|w185|w342)(/[A-Za-z0-9_-]{1,80}\.(?:jpg|png))$", c) or re.match(r"^/api/img/(t_cover_big)/([a-z0-9]{2,40})\.jpg$", c)
            if m:
                dado = capa_da_busca(m.group(1), m.group(2))
                if not dado:
                    return self.enviar(404, {"erro": "Sem capa."})
                return self.enviar(200, dado, "image/png" if dado[:4] == b"\x89PNG" else "image/jpeg", {"Cache-Control": "private, max-age=86400"})
            if c == "/api/colecao":
                try:
                    n = int((q.get("id") or [""])[0])
                except ValueError:
                    raise ValueError("Escolha uma coleção da busca.")
                return self.enviar(200, {"colecao": colecao(n, "jogo" if (q.get("tipo") or [""])[0] == "jogo" else "filme")})
            if c == "/api/dados":
                return self.enviar(200, {"backups": backups(), "versoes": versoes()})
            if c == "/api/dados/exportar":
                return self.enviar(200, montar_zip(), "application/zip", {"Content-Disposition": f'attachment; filename="{nome_zip()}"'})
            if c == "/api/integracao/ferramentas":
                return self.enviar(200, {"versao": VERSAO, "instrucoes": ferramentas.INSTRUCOES, "ferramentas": ferramentas.lista()})
            if c.startswith("/api/"):
                return self.enviar(404, {"erro": "Rota desconhecida."})
            return self.arquivo(c)
        except ERROS as e:
            return self.enviar(502, {"erro": str(e)})
        except (ValueError, R.ErroRegra) as e:
            return self.enviar(400, {"erro": str(e)})

    def arquivo(self, c):
        nome = "index.html" if c in ("/", "/index.html") or "." not in c.rsplit("/", 1)[-1] else c.lstrip("/")
        caminho = os.path.realpath(os.path.join(WWW, nome))
        if not caminho.startswith(os.path.realpath(WWW) + os.sep) or not os.path.isfile(caminho):
            return self.enviar(404, "Não achei.", "text/plain; charset=utf-8")
        with open(caminho, "rb") as f:
            dado = f.read()
        ext = os.path.splitext(caminho)[1]
        cache = {"Cache-Control": "public, max-age=604800"} if ext in (".woff", ".woff2") else None
        return self.enviar(200, dado, MIME.get(ext, "application/octet-stream"), cache)

    def do_POST(self):
        if not self.permitido():
            return
        c = self.caminho()
        try:
            if c == "/api/integracao/ferramentas":
                corpo = self.corpo_json(MAX_CORPO)
                try:
                    return self.enviar(200, usar_ferramenta(corpo))
                except KeyError:
                    return self.enviar(404, {"erro": "Ferramenta desconhecida."})
                except ferramentas.ErroFerramenta as e:
                    return self.enviar(400, {"erro": str(e)})
            if c == "/api/dados/importar":
                corpo = self.corpo_json(MAX_IMPORTAR)
                try:
                    dado = base64.b64decode(str(corpo.get("arquivo") or ""), validate=True)
                except ValueError as e:
                    raise ValueError("Não consegui ler o arquivo.") from e
                novos, capas = ler_pacote(dado)
                return self.enviar(200, {"rev": trocar_tudo(novos, capas, "antes de importar")["rev"]})
            corpo = self.corpo_json()
            if c == "/api/titulo":
                if corpo.get("acao") == "adicionar":
                    return self.enviar(200, adicionar(corpo, eu(self.usuario())))
                if corpo.get("acao") == "adicionar_colecao":
                    return self.enviar(200, adicionar_colecao(corpo, eu(self.usuario())))
                if corpo.get("acao") == "atualizar":
                    return self.enviar(200, {"titulo": atualizar(str(corpo.get("id") or ""))})
                return self.enviar(200, mudar_titulo(corpo))
            if c == "/api/categorias":
                with TRAVA:
                    d = ler()
                    R.mudar_categorias(d, corpo)
                    salvar(d)
                return self.enviar(200, {"categorias": d["categorias"], "rev": d["rev"]})
            if c == "/api/ajustes":
                return self.enviar(200, {"ajustes": mudar_ajustes(corpo)})
            if c == "/api/tmdb":
                return self.enviar(200, {"tmdb": salvar_chave(corpo)})
            if c == "/api/igdb":
                return self.enviar(200, {"igdb": salvar_igdb(corpo)})
            if c == "/api/dados/backup":
                return self.enviar(200, {"nome": fazer_backup(), "backups": backups()})
            if c == "/api/dados/restaurar":
                return self.enviar(200, {"rev": restaurar(corpo.get("origem"), corpo.get("nome"))["rev"]})
            if c == "/api/dados/zerar":
                if corpo.get("confirmar") is not True:
                    raise ValueError("Confirme para apagar.")
                return self.enviar(200, {"rev": zerar()["rev"]})
            return self.enviar(404, {"erro": "Rota desconhecida."})
        except ERROS as e:
            return self.enviar(502, {"erro": str(e)})
        except (ValueError, R.ErroRegra) as e:
            return self.enviar(400, {"erro": str(e)})


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    publicar_correria()
    threading.Thread(target=laco, daemon=True).start()
    srv = ThreadingHTTPServer(("0.0.0.0", PORTA), Handler)
    log(f"OdisseIA {VERSAO} na porta {PORTA}")
    srv.serve_forever()


if __name__ == "__main__":
    main()
