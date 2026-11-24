"""O TMDB (themoviedb.org): a busca e os detalhes dos filmes e das séries, em português, com onde assistir no Brasil
(dados da JustWatch, que o TMDB repassa e que pedem o crédito) e as capas. Só biblioteca padrão.

A chave é de cada casa (a conta grátis do TMDB, uso pessoal): a chave da API (v3, 32 letras) vai no endereço; o token de
leitura (v4, começa com eyJ) vai no cabeçalho. Nada aqui grava: o server.py guarda o que vier."""
import json
import re
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p"
PAIS = "BR"
IDIOMA = "pt-BR"
CAPA_RE = re.compile(r"^/[A-Za-z0-9_-]{1,80}\.(?:jpg|jpeg|png)$")
TAMANHOS = ("w92", "w185", "w342", "w500")
MAX_IMG = 3 * 1024 * 1024


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
        """Filmes e séries pelo nome: [{tmdb, tipo, nome, original, ano, capa, sinopse}] (sem pessoas)."""
        texto = " ".join(str(texto or "").split())[:120]
        if len(texto) < 2:
            return []
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
        return out[:20]

    def detalhes(self, tipo, tmdb_id):
        """Os detalhes de um filme ou de uma série, já no formato do app (sem o que é da casa: situação, quem, nota)."""
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
