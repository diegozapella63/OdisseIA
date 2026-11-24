"""As regras dos títulos, as mesmas para a tela e para as ferramentas do CorrerIA: limpar o que chega, achar um título,
criar com os detalhes do TMDB, mudar a situação, quem, a nota e o episódio, e o próximo episódio. Só mexem no dicionário
dos dados; quem grava é o server.py."""
import re
import secrets
import unicodedata
from datetime import date, datetime

SITUACOES = {"quero": "Quero ver", "vendo": "Vendo", "visto": "Visto", "abandonado": "Abandonado"}
TIPOS = {"filme": "Filme", "serie": "Série"}
MAX_TITULOS = 3000
MAX_NOTAS = 2000
ID_RE = re.compile(r"^t[0-9a-f]{8}$")
DATA_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PESSOA_RE = re.compile(r"^person\.[a-z0-9_]{1,60}$")


class ErroRegra(ValueError):
    """Um pedido que não vale, com a frase que diz o que vale."""


def novo_id(usados=()):
    while True:
        i = "t" + secrets.token_hex(4)
        if i not in usados:
            return i


def sem_acento(s):
    s = unicodedata.normalize("NFKD", str(s or "").lower())
    return " ".join("".join(c for c in s if not unicodedata.combining(c)).split())


def _txt(v, n):
    return " ".join(str(v or "").split())[:n]


def _int(v, minimo=0, maximo=10 ** 6, padrao=0):
    try:
        n = int(v)
    except (TypeError, ValueError):
        return padrao
    return max(minimo, min(maximo, n))


def _nomes(v, n=12):
    return [_txt(x, 60) for x in (v if isinstance(v, list) else []) if _txt(x, 60)][:n]


def _ep(v):
    if not isinstance(v, dict):
        return None
    e = {"data": str(v.get("data") or "")[:10], "temp": _int(v.get("temp"), 0, 999), "ep": _int(v.get("ep"), 0, 9999), "nome": _txt(v.get("nome"), 120)}
    return e if e["temp"] >= 1 and e["ep"] >= 1 else None


def limpar_titulo(t):
    """Um título como o app guarda (o que vem de um arquivo importado passa por aqui), ou None."""
    if not isinstance(t, dict) or not ID_RE.match(str(t.get("id") or "")) or t.get("tipo") not in TIPOS:
        return None
    nome = _txt(t.get("nome"), 160)
    if not nome:
        return None
    o = {"id": t["id"], "tipo": t["tipo"], "tmdb": _int(t.get("tmdb"), 0, 10 ** 9) or None, "nome": nome, "original": _txt(t.get("original"), 160),
         "ano": _int(t.get("ano"), 0, 3000) or None, "capa": str(t.get("capa") or "") if re.match(r"^t[0-9a-f]{8}\.(jpg|png)$", str(t.get("capa") or "")) else "",
         "capa_tmdb": str(t.get("capa_tmdb") or "")[:90], "sinopse": _txt(t.get("sinopse"), 1200), "generos": _nomes(t.get("generos"), 6),
         "situacao": t.get("situacao") if t.get("situacao") in SITUACOES else "quero",
         "quem": [p for p in (t.get("quem") if isinstance(t.get("quem"), list) else []) if isinstance(p, str) and PESSOA_RE.match(p)][:12],
         "nota": _int(t.get("nota"), 0, 5), "notas": str(t.get("notas") or "")[:MAX_NOTAS],
         "criado": str(t.get("criado") or "")[:25], "atualizado": str(t.get("atualizado") or "")[:25],
         "visto_em": str(t.get("visto_em") or "") if DATA_RE.match(str(t.get("visto_em") or "")) else None,
         "tmdb_em": str(t.get("tmdb_em") or "")[:25]}
    w = t.get("onde") if isinstance(t.get("onde"), dict) else {}
    o["onde"] = {k: _nomes(w.get(k)) for k in ("assinatura", "gratis", "alugar", "comprar")}
    o["onde"]["link"] = str(w.get("link") or "")[:300] if str(w.get("link") or "").startswith("https://") else ""
    if o["tipo"] == "filme":
        o["duracao"] = _int(t.get("duracao"), 0, 2000) or None
        c = t.get("colecao") if isinstance(t.get("colecao"), dict) else {}
        o["colecao"] = {"id": _int(c.get("id"), 1, 10 ** 9), "nome": _txt(c.get("nome"), 160)} if _int(c.get("id"), 0, 10 ** 9) else None
    else:
        temps = []
        for s in t.get("temporadas") if isinstance(t.get("temporadas"), list) else []:
            if isinstance(s, dict) and _int(s.get("n"), 0, 999) >= 1 and _int(s.get("episodios"), 0, 9999) >= 1:
                temps.append({"n": _int(s.get("n"), 1, 999), "episodios": _int(s.get("episodios"), 1, 9999)})
        o["temporadas"] = sorted({s["n"]: s for s in temps}.values(), key=lambda s: s["n"])[:60]
        o["temp"], o["ep"] = _int(t.get("temp"), 0, 999), _int(t.get("ep"), 0, 9999)
        if not o["temp"] or not o["ep"]:
            o["temp"] = o["ep"] = 0
        o["proximo"], o["ultimo"] = _ep(t.get("proximo")), _ep(t.get("ultimo"))
        o["fim"] = t.get("fim") is True
    return o


def limpar_dados(d):
    """O arquivo inteiro como o app guarda: o que não vale sai (um título repetido pelo id também)."""
    d = d if isinstance(d, dict) else {}
    vistos, titulos = set(), []
    for t in d.get("titulos") if isinstance(d.get("titulos"), list) else []:
        o = limpar_titulo(t)
        if o and o["id"] not in vistos:
            vistos.add(o["id"])
            titulos.append(o)
    aj = d.get("ajustes") if isinstance(d.get("ajustes"), dict) else {}
    tipos = aj.get("tipos") if isinstance(aj.get("tipos"), dict) else {}
    tipos = {k: tipos.get(k) is not False for k in TIPOS}
    if not any(tipos.values()):
        tipos = {k: True for k in TIPOS}
    ajustes = {"cor": aj.get("cor") if isinstance(aj.get("cor"), str) and re.match(r"^[a-z]{2,12}$", aj["cor"]) else "lilas",
               "cor_dia": aj.get("cor_dia") is not False, "quem": aj.get("quem") is not False, "correria": aj.get("correria") is True,
               "tipos": tipos}
    return {"versao": 1, "rev": _int(d.get("rev"), 0, 10 ** 12), "titulos": titulos[:MAX_TITULOS], "ajustes": ajustes}


def ep_txt(temp, ep):
    return f"T{temp} E{ep}"


def achar(d, ref):
    """Um título pelo id ou pelo nome (sem acento nem maiúsculas: o igual, senão o único que contém o texto)."""
    ref = str(ref or "").strip()
    if not ref:
        raise ErroRegra("Diga qual título (o id ou o nome).")
    for t in d["titulos"]:
        if t["id"] == ref:
            return t
    alvo = sem_acento(ref)
    iguais = [t for t in d["titulos"] if alvo in (sem_acento(t["nome"]), sem_acento(t["original"]))]
    if len(iguais) == 1:
        return iguais[0]
    parecidos = iguais or [t for t in d["titulos"] if alvo in sem_acento(t["nome"]) or alvo in sem_acento(t["original"])]
    if len(parecidos) == 1:
        return parecidos[0]
    if not parecidos:
        raise ErroRegra(f"Nenhum título com «{ref}» na lista da casa.")
    raise ErroRegra("Mais de um título com «" + ref + "»: " + "; ".join(f"{t['nome']}" + (f" ({t['ano']})" if t["ano"] else "") + f" [{t['id']}]" for t in parecidos[:8]) + ". Use o id.")


def de_tmdb(d, tipo, tmdb_id):
    return next((t for t in d["titulos"] if t["tipo"] == tipo and t["tmdb"] == tmdb_id), None)


def aplicar_detalhes(t, det, agora):
    """O que vem do TMDB por cima do título (o que é da casa, como a situação, quem, a nota e o episódio, fica)."""
    for k in ("nome", "original", "ano", "sinopse", "generos", "onde"):
        if det.get(k) not in (None, "") or k in ("generos", "onde"):
            t[k] = det.get(k) if det.get(k) is not None else t.get(k)
    t["capa_tmdb"] = det.get("capa") or t.get("capa_tmdb", "")
    if t["tipo"] == "filme":
        t["duracao"] = det.get("duracao") or t.get("duracao")
        t["colecao"] = det.get("colecao") if "colecao" in det else t.get("colecao")
    else:
        t["temporadas"] = det.get("temporadas") or t.get("temporadas") or []
        t["proximo"], t["ultimo"], t["fim"] = det.get("proximo"), det.get("ultimo"), det.get("fim") is True
    t["tmdb_em"] = agora
    return t


def criar(d, det, situacao="quero", quem=(), agora=None):
    """Um título novo com os detalhes do TMDB. Já na lista (o mesmo número do TMDB e o mesmo tipo): devolve o que já
    existe e False."""
    agora = agora or datetime.now().isoformat(timespec="seconds")
    if det.get("tipo") not in TIPOS:
        raise ErroRegra("O tipo precisa ser filme ou serie.")
    ja = de_tmdb(d, det["tipo"], det.get("tmdb"))
    if ja:
        return ja, False
    if len(d["titulos"]) >= MAX_TITULOS:
        raise ErroRegra(f"A lista chegou a {MAX_TITULOS} títulos.")
    if situacao not in SITUACOES:
        raise ErroRegra("A situação vale quero, vendo, visto ou abandonado.")
    t = {"id": novo_id({x["id"] for x in d["titulos"]}), "tipo": det["tipo"], "tmdb": det.get("tmdb"), "nome": det.get("nome") or "Sem nome",
         "original": det.get("original") or "", "ano": det.get("ano"), "capa": "", "capa_tmdb": "", "sinopse": "", "generos": [],
         "situacao": "quero", "quem": [], "nota": 0, "notas": "", "criado": agora, "atualizado": agora, "visto_em": None, "tmdb_em": "",
         "onde": {"assinatura": [], "gratis": [], "alugar": [], "comprar": [], "link": ""}}
    if t["tipo"] == "filme":
        t.update(duracao=None, colecao=None)
    else:
        t.update(temporadas=[], temp=0, ep=0, proximo=None, ultimo=None, fim=False)
    aplicar_detalhes(t, det, agora)
    mudar(t, {"situacao": situacao, "quem": list(quem)}, None, agora)
    d["titulos"].insert(0, t)
    return t, True


def episodios_ate(t, temp, ep):
    """Quantos episódios há do começo até temp/ep (inclusive), pelas temporadas que o TMDB conhece."""
    n = 0
    for s in t.get("temporadas") or []:
        if s["n"] < temp:
            n += s["episodios"]
        elif s["n"] == temp:
            n += min(ep, s["episodios"])
    return n


def faltam(t):
    """Quantos episódios já saíram e ainda não foram vistos (None num filme ou sem o último episódio)."""
    if t["tipo"] != "serie" or not t.get("ultimo"):
        return None
    u = t["ultimo"]
    return max(0, episodios_ate(t, u["temp"], u["ep"]) - (episodios_ate(t, t["temp"], t["ep"]) if t["temp"] else 0))


def seguinte(t):
    """O episódio depois do último visto: (temp, ep), ou None se não há."""
    temps = t.get("temporadas") or []
    if not temps:
        return None
    if not t["temp"]:
        return (temps[0]["n"], 1)
    for i, s in enumerate(temps):
        if s["n"] == t["temp"]:
            if t["ep"] < s["episodios"]:
                return (s["n"], t["ep"] + 1)
            return (temps[i + 1]["n"], 1) if i + 1 < len(temps) else None
    depois = [s for s in temps if s["n"] > t["temp"]]
    return (depois[0]["n"], 1) if depois else None


def ja_saiu(t, temp, ep):
    """O episódio já saiu? (pelo último que saiu; sem essa informação, vale)"""
    u = t.get("ultimo")
    return not u or (temp, ep) <= (u["temp"], u["ep"])


def mudar(t, campos, pessoas, agora=None):
    """Muda a situação, quem, a nota, o episódio e as notas. pessoas: os ids que valem (None: não confere)."""
    agora = agora or datetime.now().isoformat(timespec="seconds")
    hoje = agora[:10]
    if not isinstance(campos, dict):
        raise ErroRegra("Mande os campos num objeto.")
    if "quem" in campos:
        q = campos["quem"] if isinstance(campos["quem"], list) else []
        if any(not isinstance(p, str) or not PESSOA_RE.match(p) for p in q):
            raise ErroRegra("Quem: os ids das pessoas (person.…).")
        if pessoas is not None:
            fora = [p for p in q if p not in pessoas]
            if fora:
                raise ErroRegra("Pessoa que não está na casa: " + ", ".join(fora) + ".")
        t["quem"] = list(dict.fromkeys(q))[:12]
    if "nota" in campos:
        n = campos["nota"]
        if not isinstance(n, int) or isinstance(n, bool) or not 0 <= n <= 5:
            raise ErroRegra("A nota vai de 1 a 5 (0 tira a nota).")
        t["nota"] = n
    if "notas" in campos:
        t["notas"] = str(campos["notas"] or "")[:MAX_NOTAS]
    if "temp" in campos or "ep" in campos:
        if t["tipo"] != "serie":
            raise ErroRegra("Episódio só numa série.")
        temp, ep = campos.get("temp", t["temp"]), campos.get("ep", t["ep"])
        if not isinstance(temp, int) or not isinstance(ep, int) or isinstance(temp, bool) or isinstance(ep, bool):
            raise ErroRegra("A temporada e o episódio são números.")
        if temp == 0 or ep == 0:
            t["temp"] = t["ep"] = 0
        else:
            s = next((s for s in t.get("temporadas") or [] if s["n"] == temp), None)
            if t.get("temporadas") and not s:
                raise ErroRegra(f"Essa série não tem a temporada {temp}.")
            if s and not 1 <= ep <= s["episodios"]:
                raise ErroRegra(f"A temporada {temp} tem {s['episodios']} episódios.")
            t["temp"], t["ep"] = temp, ep
        if t["temp"] and t["situacao"] == "quero" and "situacao" not in campos:
            t["situacao"] = "vendo"
    if "situacao" in campos:
        s = campos["situacao"]
        if s not in SITUACOES:
            raise ErroRegra("A situação vale quero, vendo, visto ou abandonado.")
        antes = t["situacao"]
        t["situacao"] = s
        if s == "visto" and antes != "visto":
            t["visto_em"] = hoje
            if t["tipo"] == "serie" and "temp" not in campos and "ep" not in campos:
                u = t.get("ultimo") or ({"temp": t["temporadas"][-1]["n"], "ep": t["temporadas"][-1]["episodios"]} if t.get("temporadas") else None)
                if u:
                    t["temp"], t["ep"] = u["temp"], u["ep"]
        elif s != "visto":
            t["visto_em"] = None
    t["atualizado"] = agora
    return t


def proximo_ep(t, agora=None):
    """Marca o episódio seguinte como visto. No último que saiu de uma série que acabou, vira Visto."""
    if t["tipo"] != "serie":
        raise ErroRegra("Episódio só numa série.")
    s = seguinte(t)
    if not s or not ja_saiu(t, *s):
        raise ErroRegra("Você já viu todos os episódios que saíram" + (f" (o próximo sai em {data_br(t['proximo']['data'])})." if t.get("proximo") else "."))
    campos = {"temp": s[0], "ep": s[1]}
    if t["situacao"] in ("quero", "abandonado"):
        campos["situacao"] = "vendo"
    mudar(t, campos, None, agora)
    if t.get("fim") and not seguinte(t) or t.get("fim") and t.get("ultimo") and (t["temp"], t["ep"]) >= (t["ultimo"]["temp"], t["ultimo"]["ep"]):
        mudar(t, {"situacao": "visto"}, None, agora)
    return t


def data_br(iso):
    try:
        d = date.fromisoformat(str(iso)[:10])
    except ValueError:
        return str(iso or "")
    return d.strftime("%d/%m/%Y")


def tipos_ligados(d):
    """Os tipos que a casa controla (Opções › O que controlar): os outros somem da tela e do CorrerIA, sem apagar nada."""
    return [k for k in TIPOS if d["ajustes"]["tipos"].get(k)]


def conferir_tipo(d, tipo):
    if tipo in TIPOS and tipo not in tipos_ligados(d):
        raise ErroRegra(f"{'Filmes' if tipo == 'filme' else 'Séries'} estão desligados em Opções › O que controlar.")
