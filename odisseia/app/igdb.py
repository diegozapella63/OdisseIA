"""O IGDB (igdb.com, da Twitch): a busca e os detalhes dos jogos, as listas prontas, as coleções (as séries de jogos) e
as capas. Só biblioteca padrão.

A conta é de cada casa: um app grátis no Twitch Developers dá o Client ID e o Client Secret; com eles, o acesso (vale uns
60 dias) sai do id.twitch.tv e fica só na memória. Os pedidos ao IGDB são POST com o texto da consulta (Apicalypse). Os
nomes e as sinopses vêm em inglês: o IGDB não tem português. Nada aqui grava: o server.py guarda o que vier."""
import json
import re
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API = "https://api.igdb.com/v4"
TOKEN = "https://id.twitch.tv/oauth2/token"
IMG = "https://images.igdb.com/igdb/image/upload"
CAPA_RE = re.compile(r"^[a-z0-9]{2,40}$")
TAMANHOS = ("t_cover_small", "t_cover_big")
MAX_IMG = 3 * 1024 * 1024
UA = "OdisseIA (Home Assistant)"
# as listas prontas do Adicionar, com os mesmos ids das do TMDB (a tela troca só o nome)
LISTAS = {"alta": "Em alta", "populares": "Mais jogados", "avaliados": "Mais bem avaliados", "colecoes": "Coleções", "estreias": "Lançamentos"}
POPULARIDADE = {"alta": 1, "populares": 3}  # 1: as visitas no IGDB; 3: quem pôs o jogo em Jogando
POR_PAGINA = 20
MAX_PAGINAS = 10
CAMPOS = ("fields name,first_release_date,cover.image_id,game_type,category,version_parent,summary,genres.name,"
          "platforms.name,collections.name,url;")
# o tipo de cada jogo (game_type, o category de antes): 0 principal, 1 DLC, 2 expansão, 3 pacote, 4 expansão
# independente, 5 mod, 6 episódio, 7 temporada, 8 remake, 9 remaster, 10 jogo expandido, 11 port, 12 fork, 13 pack, 14
# atualização. A busca mostra também as expansões; uma coleção, só os jogos de verdade (sem as remasterizações).
NA_BUSCA = {0, 2, 4, 6, 8, 9, 10}
NAS_LISTAS = {0, 4, 8, 9, 10}
NA_COLECAO = {0, 4, 8}
PLATAFORMAS = {"PC (Microsoft Windows)": "PC", "Web browser": "Navegador", "Mac": "Mac", "Linux": "Linux"}
_TOKENS = {}  # (Client ID, Client Secret, endereço) → (acesso, até quando): um para o app todo
_TRAVA = threading.Lock()


class ErroIGDB(Exception):
    """Um erro para mostrar na tela, já em português."""


class IGDB:
    def __init__(self, cliente, segredo, api=API, token=TOKEN, img=IMG, timeout=12):
        self.cliente = str(cliente or "").strip()
        self.segredo = str(segredo or "").strip()
        self.api = api.rstrip("/")
        self.token_url = token
        self.img = img.rstrip("/")
        self.timeout = timeout

    def _token(self, novo=False):
        k = (self.cliente, self.segredo, self.token_url)
        with _TRAVA:
            v = _TOKENS.get(k)
        if v and not novo and v[1] > time.time() + 60:
            return v[0]
        corpo = urllib.parse.urlencode({"client_id": self.cliente, "client_secret": self.segredo, "grant_type": "client_credentials"}).encode()
        req = urllib.request.Request(self.token_url, data=corpo, method="POST", headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                j = json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            if e.code in (400, 401, 403):
                raise ErroIGDB("A Twitch não aceitou o Client ID e o Client Secret. Confira em Mais › Configurações › Integrações.")
            raise ErroIGDB(f"A Twitch respondeu com erro ({e.code}).")
        except (urllib.error.URLError, OSError, ValueError):
            raise ErroIGDB("Não consegui falar com a Twitch agora. Confira a internet do Home Assistant.")
        tok = j.get("access_token") if isinstance(j, dict) else None
        if not isinstance(tok, str) or not tok:
            raise ErroIGDB("A Twitch não mandou o acesso ao IGDB.")
        try:
            dura = int(j.get("expires_in") or 3600)
        except (TypeError, ValueError):
            dura = 3600
        with _TRAVA:
            _TOKENS[k] = (tok, time.time() + dura)
        return tok

    def _pedir(self, rota, consulta, de_novo=True):
        if not self.cliente or not self.segredo:
            raise ErroIGDB("Falta a conta do IGDB (Mais › Configurações › Integrações).")
        cab = {"Client-ID": self.cliente, "Authorization": "Bearer " + self._token(), "Accept": "application/json",
               "Content-Type": "text/plain", "User-Agent": UA}
        req = urllib.request.Request(f"{self.api}/{rota}", data=consulta.encode("utf-8"), method="POST", headers=cab)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                j = json.loads(r.read() or b"[]")
        except urllib.error.HTTPError as e:
            if e.code in (401, 403) and de_novo:  # o acesso venceu: um novo, uma vez
                self._token(novo=True)
                return self._pedir(rota, consulta, False)
            if e.code in (401, 403):
                raise ErroIGDB("O IGDB não aceitou o acesso. Confira o Client ID e o Client Secret em Mais › Configurações › Integrações.")
            if e.code == 429:
                raise ErroIGDB("O IGDB pediu um tempo (muitos pedidos). Tente de novo daqui a pouco.")
            raise ErroIGDB(f"O IGDB respondeu com erro ({e.code}).")
        except (urllib.error.URLError, OSError, ValueError):
            raise ErroIGDB("Não consegui falar com o IGDB agora. Confira a internet do Home Assistant.")
        return [x for x in j if isinstance(x, dict)] if isinstance(j, list) else []

    def testar(self):
        """O Client ID e o Client Secret valem? (um acesso novo e uma consulta pequena)"""
        self._token(novo=True)
        self._pedir("games", "fields name; limit 1;")
        return True

    def buscar(self, texto):
        """Jogos pelo nome: as coleções (as séries de jogos) que combinam vêm na frente (até 2), depois os jogos (até 20)."""
        texto = " ".join(str(texto or "").split())[:120]
        if len(texto) < 2:
            return []
        q = texto.replace('"', " ").replace("\\", " ")
        rs = self._pedir("games", f'search "{q}"; {CAMPOS} where version_parent = null; limit 40;')
        jogos = [resumo(x) for x in rs if valido(x, NA_BUSCA)]
        alvo, cols, vistas = _sa(texto), [], set()
        if len(texto) >= 3:  # as coleções pelo nome delas (uma série pode ter outro nome que os jogos)
            try:
                for c in self.colecoes(q):
                    vistas.add(c["igdb"])
                    cols.append(c)
            except ErroIGDB:  # a busca das coleções é a mais: sem ela, os jogos
                pass
        for j in jogos:
            c = j.get("colecao")
            if c and c["id"] not in vistas and alvo in _sa(c["nome"]):
                vistas.add(c["id"])
                cols.append(como_colecao(c))
        return cols[:2] + jogos[:20]

    def colecoes(self, texto):
        """As coleções (as séries de jogos) cujo nome contém o texto, com a capa de um jogo delas (até 5)."""
        q = " ".join(str(texto or "").replace('"', " ").replace("\\", " ").split())[:120]
        cs = [c for c in self._pedir("collections", f'fields name; where name ~ *"{q}"*; limit 5;') if isinstance(c.get("id"), int) and _txt(c.get("name"), 160)]
        if not cs:
            return []
        capas = {}
        ids = ",".join(str(c["id"]) for c in cs)
        for x in self._pedir("games", f"fields cover.image_id,collections,game_type,category; where collections = ({ids}) & version_parent = null; sort total_rating_count desc; limit 50;"):
            capa = _capa(x.get("cover"))
            for c in x.get("collections") or []:
                n = c.get("id") if isinstance(c, dict) else c
                if capa and isinstance(n, int) and n not in capas:
                    capas[n] = capa
        return [como_colecao({"id": c["id"], "nome": _txt(c["name"], 160), "capa": capas.get(c["id"], "")}) for c in cs]

    def por_ids(self, ids):
        """Os jogos destes números, na mesma ordem (os que o IGDB não tem ficam de fora)."""
        ids = [int(i) for i in ids if isinstance(i, int) and not isinstance(i, bool)][:500]
        if not ids:
            return []
        rs = {x["id"]: x for x in self._pedir("games", f"{CAMPOS} where id = ({','.join(map(str, ids))}); limit {len(ids)};") if isinstance(x.get("id"), int)}
        return [rs[i] for i in ids if i in rs]

    def lista(self, nome, pagina=1):
        """Uma lista pronta: (jogos, tem_mais). Em alta e Mais jogados pela popularidade do IGDB; Mais bem avaliados pela
        nota (com muitas notas); Lançamentos: os dos últimos 90 dias que a turma mais esperava."""
        if nome not in LISTAS or nome == "colecoes":  # as coleções saem dos jogos (server.lista_colecoes)
            raise ErroIGDB("Lista desconhecida.")
        try:
            pagina = max(1, min(MAX_PAGINAS, int(pagina)))
        except (TypeError, ValueError):
            pagina = 1
        if nome in POPULARIDADE:
            n = POR_PAGINA + 10  # alguns saem (DLC, edições): pede um pouco mais
            pp = self._pedir("popularity_primitives", f"fields game_id,value; sort value desc; limit {n}; offset {(pagina - 1) * n}; where popularity_type = {POPULARIDADE[nome]};")
            ids = list(dict.fromkeys(p["game_id"] for p in pp if isinstance(p.get("game_id"), int)))
            jogos = [resumo(x) for x in self.por_ids(ids) if valido(x, NAS_LISTAS)]
            return jogos[:POR_PAGINA], len(pp) >= n and pagina < MAX_PAGINAS
        off = (pagina - 1) * POR_PAGINA
        if nome == "avaliados":
            rs = self._pedir("games", f"{CAMPOS} where total_rating_count > 150 & version_parent = null; sort total_rating desc; limit {POR_PAGINA}; offset {off};")
        else:
            agora = int(time.time())
            rs = self._pedir("games", f"{CAMPOS} where first_release_date >= {agora - 90 * 86400} & first_release_date <= {agora} & version_parent = null & hypes > 0; "
                                      f"sort hypes desc; limit {POR_PAGINA}; offset {off};")
        return [resumo(x) for x in rs if valido(x, NAS_LISTAS)], len(rs) >= POR_PAGINA and pagina < MAX_PAGINAS

    def colecao(self, n):
        """Uma coleção (uma série de jogos) com os jogos dela, na ordem em que saíram (sem data, no fim)."""
        try:
            n = int(n)
        except (TypeError, ValueError):
            raise ErroIGDB("Essa coleção não tem o número do IGDB.")
        c = self._pedir("collections", f"fields name; where id = {n};")
        if not c:
            raise ErroIGDB("O IGDB não achou essa coleção.")
        rs = self._pedir("games", f"{CAMPOS} where collections = ({n}) & version_parent = null; limit 200;")
        jogos = sorted((resumo(x) for x in rs if valido(x, NA_COLECAO)), key=lambda j: (not j["data"], j["data"]))[:100]
        return {"igdb": n, "nome": _txt(c[0].get("name"), 160) or "Sem nome", "capa": next((j["capa"] for j in jogos if j["capa"]), ""),
                "sinopse": "", "itens": jogos}

    def detalhes(self, n):
        """Os detalhes de um jogo, já no formato do app (sem o que é da casa)."""
        try:
            n = int(n)
        except (TypeError, ValueError):
            raise ErroIGDB("Esse jogo não tem o número do IGDB.")
        rs = self.por_ids([n])
        if not rs:
            raise ErroIGDB("O IGDB não achou esse jogo.")
        return detalhes(rs[0])

    def varios(self, ids):
        """Os detalhes de vários jogos num pedido só (uma coleção inteira): {número: detalhes}."""
        out = {}
        for i in range(0, len(ids), 200):
            for x in self.por_ids(ids[i:i + 200]):
                out[x["id"]] = detalhes(x)
        return out

    def imagem(self, capa, tamanho="t_cover_big"):
        """Os bytes de uma capa (JPG), ou None."""
        if not capa or not CAPA_RE.match(capa) or tamanho not in TAMANHOS:
            return None
        try:
            req = urllib.request.Request(f"{self.img}/{tamanho}/{capa}.jpg", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                dado = r.read(MAX_IMG + 1)
        except (urllib.error.URLError, OSError, ValueError):
            return None
        if len(dado) > MAX_IMG or dado[:3] != b"\xff\xd8\xff":
            return None
        return dado


def _sa(s):
    s = unicodedata.normalize("NFKD", str(s or "").lower())
    return " ".join("".join(c for c in s if not unicodedata.combining(c)).split())


def _txt(v, n):
    return " ".join(str(v or "").split())[:n]


def _tipo(x):
    for k in ("game_type", "category"):
        v = x.get(k)
        if isinstance(v, dict):
            v = v.get("id")
        if isinstance(v, int) and not isinstance(v, bool):
            return v
    return 0


def valido(x, tipos):
    return isinstance(x.get("id"), int) and bool(_txt(x.get("name"), 160)) and not x.get("version_parent") and _tipo(x) in tipos


def _data(x):
    try:
        return datetime.fromtimestamp(int(x.get("first_release_date")), timezone.utc).strftime("%Y-%m-%d")
    except (TypeError, ValueError, OverflowError, OSError):
        return ""


def _capa(c):
    v = c.get("image_id") if isinstance(c, dict) else None
    return v if isinstance(v, str) and CAPA_RE.match(v) else ""


def resumo(x):
    data = _data(x)
    cols = [c for c in x.get("collections") or [] if isinstance(c, dict) and isinstance(c.get("id"), int) and _txt(c.get("name"), 160)]
    capa = _capa(x.get("cover"))
    return {"igdb": x["id"], "tipo": "jogo", "nome": _txt(x.get("name"), 160), "original": "", "ano": int(data[:4]) if data else None,
            "data": data, "capa": capa, "sinopse": _txt(x.get("summary"), 1200),
            "colecao": {"id": cols[0]["id"], "nome": _txt(cols[0]["name"], 160), "capa": capa} if cols else None}


def como_colecao(c):
    """Uma coleção como um resultado da busca (a capa é a do jogo em que ela apareceu)."""
    return {"igdb": c["id"], "tipo": "colecao_jogos", "nome": c["nome"], "original": "", "ano": None, "data": "", "capa": c.get("capa") or "", "sinopse": ""}


def plataformas(x):
    out = []
    for p in x.get("platforms") or []:
        n = _txt(p.get("name"), 60) if isinstance(p, dict) else ""
        n = PLATAFORMAS.get(n, n)
        if n and n not in out:
            out.append(n)
    return out[:12]


def detalhes(x):
    d = resumo(x)
    d["generos"] = [_txt(g.get("name"), 40) for g in x.get("genres") or [] if isinstance(g, dict) and g.get("name")][:6]
    d["plataformas"] = plataformas(x)
    url = x.get("url") if isinstance(x.get("url"), str) and x["url"].startswith("https://www.igdb.com/") else ""
    d["link"] = url[:300]
    return d
