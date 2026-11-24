"""O TMDB (themoviedb.org): a busca e os detalhes dos filmes e das séries, em português, com onde assistir no Brasil
(dados da JustWatch, que o TMDB repassa e que pedem o crédito) e as capas. Só biblioteca padrão.

A chave é de cada casa (a conta grátis do TMDB, uso pessoal): a chave da API (v3, 32 letras) vai no endereço; o token de
leitura (v4, começa com eyJ) vai no cabeçalho. Nada aqui grava: o server.py guarda o que vier."""
import json
import re
import urllib.error
from itertools import zip_longest
import urllib.parse
import urllib.request

API = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p"
PAIS = "BR"
IDIOMA = "pt-BR"
CAPA_RE = re.compile(r"^/[A-Za-z0-9_-]{1,80}\.(?:jpg|jpeg|png)$")
TAMANHOS = ("w92", "w185", "w342", "w500")
MAX_IMG = 3 * 1024 * 1024
# as listas prontas do Adicionar (0.2.0, o dono: "os mais vistos, os mais bem avaliados... listas prontas onde eu clico e
# marco como visto"): o nome na tela e, por tipo, a rota do TMDB (Em alta é a mesma para os dois)
LISTAS = {"alta": "Em alta", "populares": "Mais populares", "avaliados": "Mais bem avaliados", "colecoes": "Coleções", "estreias": "Estreias"}
ROTAS = {"populares": ("popular", "popular"), "avaliados": ("top_rated", "top_rated"), "estreias": ("now_playing", "on_the_air")}
MAX_PAGINAS = 20


class ErroTMDB(Exception):
    """Um erro para mostrar na tela, já em português."""


class TMDB:
    def __init__(self, chave, api=API, img=IMG, timeout=12):
        self.chave = str(chave or "").strip()
        self.api = api.rstrip("/")
        self.img = img.rstrip("/")
        self.timeout = timeout

    def _pedir(self, caminho, params=None):
        if not self.chave:
            raise ErroTMDB("Falta a chave do TMDB (Mais › Configurações › Integrações).")
        q = dict(params or {})
        cab = {"Accept": "application/json", "User-Agent": "OdisseIA (Home Assistant)"}
        if self.chave.startswith("eyJ"):
            cab["Authorization"] = "Bearer " + self.chave
        else:
            q["api_key"] = self.chave
        url = self.api + caminho + ("?" + urllib.parse.urlencode(q) if q else "")
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=cab), timeout=self.timeout) as r:
                return json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise ErroTMDB("O TMDB não aceitou a chave. Confira a chave em Mais › Configurações › Integrações.")
            if e.code == 404:
                raise ErroTMDB("O TMDB não achou esse título.")
            if e.code == 429:
                raise ErroTMDB("O TMDB pediu um tempo (muitos pedidos). Tente de novo daqui a pouco.")
            raise ErroTMDB(f"O TMDB respondeu com erro ({e.code}).")
        except (urllib.error.URLError, OSError, ValueError):
            raise ErroTMDB("Não consegui falar com o TMDB agora. Confira a internet do Home Assistant.")

    def testar(self):
        """A chave vale? (o /authentication responde com sucesso para as duas formas de chave)"""
        r = self._pedir("/authentication")
        if r.get("success") is False:
            raise ErroTMDB("O TMDB não aceitou a chave.")
        return True

    def buscar(self, texto, tipo=""):
        """Filmes e séries pelo nome: [{tmdb, tipo, nome, original, ano, capa, sinopse}] (sem pessoas). Com Tudo ou Filme,
        as coleções de filmes (as sagas) que combinam vêm na frente (até 2), com tipo colecao."""
        texto = " ".join(str(texto or "").split())[:120]
        if len(texto) < 2:
            return []
        if tipo == "colecao":
            return self.colecoes(texto)
        rota = {"filme": "/search/movie", "serie": "/search/tv"}.get(tipo, "/search/multi")
        r = self._pedir(rota, {"query": texto, "language": IDIOMA, "include_adult": "false", "page": 1})
        out = []
        for x in r.get("results") or []:
            if not isinstance(x, dict):
                continue
            mt = x.get("media_type") or {"filme": "movie", "serie": "tv"}.get(tipo)
            if mt not in ("movie", "tv"):
                continue
            out.append(resumo(x, "filme" if mt == "movie" else "serie"))
        cols = []
        if tipo in ("", "filme") and len(texto) >= 3:
            try:
                cols = self.colecoes(texto)[:2]
            except ErroTMDB:  # a busca das coleções é a mais: sem ela, os filmes e as séries
                cols = []
        return cols + out[:20]

    def lista(self, nome, tipo="", pagina=1):
        """Uma lista pronta do TMDB: (resultados, tem_mais). Sem tipo, Em alta mistura os dois; Mais populares e Mais bem
        avaliados intercalam filmes e séries; Estreias são os filmes nos cinemas do Brasil (numa série, as que estão no ar)."""
        if nome not in LISTAS or nome == "colecoes":  # as coleções saem dos filmes populares (server.lista_colecoes)
            raise ErroTMDB("Lista desconhecida.")
        try:
            pagina = max(1, min(MAX_PAGINAS, int(pagina)))
        except (TypeError, ValueError):
            pagina = 1
        q = {"language": IDIOMA, "page": pagina}
        if nome == "alta":
            r = self._pedir(f"/trending/{ {'filme': 'movie', 'serie': 'tv'}.get(tipo, 'all') }/week", q)
            fontes = [(None, r)]
        else:
            tipos = [tipo] if tipo in ("filme", "serie") else (["filme"] if nome == "estreias" else ["filme", "serie"])
            fontes = []
            for tp in tipos:
                rota = ROTAS[nome][0 if tp == "filme" else 1]
                fontes.append((tp, self._pedir(f"/{'movie' if tp == 'filme' else 'tv'}/{rota}", dict(q, region=PAIS) if tp == "filme" else q)))
        listas = []
        for tp, r in fontes:
            itens = []
            for x in r.get("results") or []:
                if not isinstance(x, dict) or not isinstance(x.get("id"), int):
                    continue
                mt = tp or {"movie": "filme", "tv": "serie"}.get(x.get("media_type"))
                if mt:
                    itens.append(resumo(x, mt))
            listas.append(itens)
        out = [x for grupo in zip_longest(*listas) for x in grupo if x]
        try:
            total = min(int(r.get("total_pages") or 1) for _, r in fontes)
        except (TypeError, ValueError):
            total = 1
        return out, pagina < min(total, MAX_PAGINAS)

    def colecoes(self, texto):
        """As coleções de filmes (as sagas) pelo nome."""
        r = self._pedir("/search/collection", {"query": " ".join(str(texto or "").split())[:120], "language": IDIOMA, "page": 1})
        out = []
        for x in r.get("results") or []:
            if isinstance(x, dict) and isinstance(x.get("id"), int):
                out.append(dict(resumo(dict(x, title=x.get("name"), original_title=x.get("original_name")), "filme"), tipo="colecao", ano=None))
        return out[:10]

    def colecao(self, n):
        """Uma coleção de filmes com os filmes dela, na ordem em que saíram (sem data, no fim)."""
        try:
            n = int(n)
        except (TypeError, ValueError):
            raise ErroTMDB("Essa coleção não tem o número do TMDB.")
        x = self._pedir(f"/collection/{n}", {"language": IDIOMA})
        filmes = [dict(resumo(p, "filme"), data=str(p.get("release_date") or "")[:10]) for p in x.get("parts") or [] if isinstance(p, dict) and isinstance(p.get("id"), int)]
        filmes.sort(key=lambda f: (not f["data"], f["data"]))
        c = resumo(dict(x, title=x.get("name"), original_title=x.get("original_name")), "filme")
        return {"tmdb": x.get("id"), "nome": c["nome"], "capa": c["capa"], "sinopse": c["sinopse"], "filmes": filmes[:60]}

    def detalhes(self, tipo, tmdb_id):
        """Os detalhes de um filme ou de uma série, já no formato do app (sem o que é da casa: situação, quem, categoria)."""
        try:
            n = int(tmdb_id)
        except (TypeError, ValueError):
            raise ErroTMDB("Esse título não tem o número do TMDB.")
        rota = f"/movie/{n}" if tipo == "filme" else f"/tv/{n}"
        x = self._pedir(rota, {"language": IDIOMA, "append_to_response": "watch/providers"})
        return detalhes(x, tipo)

    def imagem(self, caminho, tamanho="w342"):
        """Os bytes de uma capa (JPG ou PNG), ou None."""
        if not caminho or not CAPA_RE.match(caminho) or tamanho not in TAMANHOS:
            return None
        try:
            req = urllib.request.Request(f"{self.img}/{tamanho}{caminho}", headers={"User-Agent": "OdisseIA (Home Assistant)"})
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                dado = r.read(MAX_IMG + 1)
        except (urllib.error.URLError, OSError, ValueError):
            return None
        if len(dado) > MAX_IMG or not (dado[:3] == b"\xff\xd8\xff" or dado[:8] == b"\x89PNG\r\n\x1a\n"):
            return None
        return dado


def _ano(data):
    m = re.match(r"^(\d{4})", str(data or ""))
    return int(m.group(1)) if m else None


def _txt(v, n):
    return " ".join(str(v or "").split())[:n]


def resumo(x, tipo):
    filme = tipo == "filme"
    capa = x.get("poster_path") if isinstance(x.get("poster_path"), str) and CAPA_RE.match(x.get("poster_path") or "") else ""
    return {"tmdb": x.get("id"), "tipo": tipo,
            "nome": _txt(x.get("title") if filme else x.get("name"), 160) or _txt(x.get("original_title") if filme else x.get("original_name"), 160),
            "original": _txt(x.get("original_title") if filme else x.get("original_name"), 160),
            "ano": _ano(x.get("release_date") if filme else x.get("first_air_date")),
            "data": str((x.get("release_date") if filme else x.get("first_air_date")) or "")[:10],
            "capa": capa, "sinopse": _txt(x.get("overview"), 1200)}


def _nomes(lista):
    out = []
    for p in lista or []:
        n = _txt((p or {}).get("provider_name"), 60) if isinstance(p, dict) else ""
        if n and n not in out:
            out.append(n)
    return out[:12]


def onde(x):
    """Onde assistir no Brasil (JustWatch, pelo TMDB): {assinatura, gratis, alugar, comprar, link}."""
    br = (((x.get("watch/providers") or {}).get("results") or {}).get(PAIS)) or {}
    if not isinstance(br, dict):
        br = {}
    link = br.get("link") if isinstance(br.get("link"), str) and br.get("link", "").startswith("https://") else ""
    return {"assinatura": _nomes(br.get("flatrate")), "gratis": _nomes((br.get("free") or []) + (br.get("ads") or [])),
            "alugar": _nomes(br.get("rent")), "comprar": _nomes(br.get("buy")), "link": link[:300]}


def _ep(e):
    if not isinstance(e, dict):
        return None
    try:
        return {"data": str(e.get("air_date") or "")[:10], "temp": int(e.get("season_number") or 0), "ep": int(e.get("episode_number") or 0),
                "nome": _txt(e.get("name"), 120)}
    except (TypeError, ValueError):
        return None


def detalhes(x, tipo):
    d = resumo(x, tipo)
    d["generos"] = [_txt(g.get("name"), 40) for g in x.get("genres") or [] if isinstance(g, dict) and g.get("name")][:6]
    d["onde"] = onde(x)
    if tipo == "filme":
        try:
            d["duracao"] = int(x.get("runtime") or 0) or None
        except (TypeError, ValueError):
            d["duracao"] = None
        c = x.get("belongs_to_collection")
        capa = c.get("poster_path") if isinstance(c, dict) and isinstance(c.get("poster_path"), str) and CAPA_RE.match(c.get("poster_path")) else ""
        d["colecao"] = {"id": c["id"], "nome": _txt(c.get("name"), 160), "capa": capa} if isinstance(c, dict) and isinstance(c.get("id"), int) else None
        return d
    temps = []
    for s in x.get("seasons") or []:
        try:
            n, eps = int(s.get("season_number")), int(s.get("episode_count") or 0)
        except (TypeError, ValueError, AttributeError):
            continue
        if n >= 1 and eps >= 1:  # a temporada 0 são os especiais: fora da conta
            temps.append({"n": n, "episodios": eps})
    d["temporadas"] = sorted(temps, key=lambda t: t["n"])[:60]
    d["fim"] = str(x.get("status") or "") in ("Ended", "Canceled")
    prox = _ep(x.get("next_episode_to_air"))
    d["proximo"] = prox if prox and prox["temp"] >= 1 and prox["ep"] >= 1 and re.match(r"^\d{4}-\d{2}-\d{2}$", prox["data"]) else None
    ult = _ep(x.get("last_episode_to_air"))
    d["ultimo"] = ult if ult and ult["temp"] >= 1 and ult["ep"] >= 1 else None
    return d
