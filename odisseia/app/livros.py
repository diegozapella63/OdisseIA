"""Os livros, pela Open Library (openlibrary.org, do Internet Archive): a busca pelo nome ou pelo ISBN (o número do código
de barras), os detalhes de uma obra e as capas. Só biblioteca padrão, sem conta nem chave.

A Open Library pede que os apps se identifiquem no User-Agent e não passem de um pedido por segundo (a página dos
desenvolvedores dela): o app se identifica pelo nome e pelo repositório, e os pedidos saem um de cada vez, com um
intervalo. Uma obra é a OL<número>W: o número é o que o app guarda (ol). Nada aqui grava: o server.py guarda o que vier."""
import json
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://openlibrary.org"
IMG = "https://covers.openlibrary.org"
UA = "OdisseIA (app do Home Assistant; https://github.com/diegozapella63/OdisseIA)"
CAMPOS = "key,title,author_name,first_publish_year,cover_i,number_of_pages_median,isbn,subject,editions,editions.title,editions.language"
TAMANHOS = ("ol_S", "ol_M", "ol_L")
MAX_IMG = 3 * 1024 * 1024
INTERVALO = 1.0  # segundos entre dois pedidos (o limite de quem não tem cadastro)
ISBN_RE = re.compile(r"^(?:\d{9}[\dXx]|\d{13})$")
_TRAVA = threading.Lock()
_ULTIMO = [0.0]


class ErroLivros(Exception):
    """Um erro para mostrar na tela, já em português."""


def isbn_de(texto):
    """O ISBN (10 ou 13 dígitos) de um texto que é só ele, com ou sem traços e espaços; "" se não é um."""
    t = re.sub(r"[\s-]", "", str(texto or ""))
    return t.upper() if ISBN_RE.match(t) else ""


def numero(chave):
    """O número de uma obra: «/works/OL45804W» → 45804 (0 se não é uma obra)."""
    m = re.search(r"OL(\d{1,12})W$", str(chave or ""))
    return int(m.group(1)) if m else 0


def _texto(v, n):
    if isinstance(v, dict):
        v = v.get("value")
    return " ".join(str(v or "").split())[:n]


def _nomes(v, n=6):
    out = []
    for x in v if isinstance(v, list) else []:
        t = " ".join(str(x or "").split())[:60]
        if t and t.lower() not in (y.lower() for y in out):
            out.append(t)
    return out[:n]


def do_doc(d):
    """Um resultado da busca como o app usa (ou None): o nome da edição em português quando a busca trouxe uma."""
    n = numero(d.get("key")) if isinstance(d, dict) else 0
    nome = _texto(d.get("title"), 160) if n else ""
    if not nome:
        return None
    eds = (d.get("editions") or {}).get("docs") if isinstance(d.get("editions"), dict) else None
    ed = next((e for e in eds if isinstance(e, dict) and "por" in (e.get("language") or []) and _texto(e.get("title"), 160)), None) if isinstance(eds, list) else None
    ano = d.get("first_publish_year")
    pag = d.get("number_of_pages_median")
    capa = d.get("cover_i")
    isbns = [str(x) for x in d.get("isbn") or [] if isbn_de(x)] if isinstance(d.get("isbn"), list) else []
    return {"tipo": "livro", "ol": n, "nome": _texto(ed["title"], 160) if ed else nome, "original": nome if ed and _texto(ed["title"], 160) != nome else "",
            "ano": ano if isinstance(ano, int) and not isinstance(ano, bool) and 0 < ano < 3000 else None,
            "capa": str(capa) if isinstance(capa, int) and not isinstance(capa, bool) and capa > 0 else "",
            "autores": _nomes(d.get("author_name"), 4), "paginas": pag if isinstance(pag, int) and not isinstance(pag, bool) and 0 < pag < 20000 else None,
            "generos": _nomes(d.get("subject"), 6), "isbn": next((x for x in isbns if len(x) == 13), isbns[0] if isbns else ""), "sinopse": "", "saiu": True}


class Livros:
    def __init__(self, api=API, img=IMG, timeout=12, intervalo=INTERVALO):
        self.api, self.img, self.timeout, self.intervalo = api.rstrip("/"), img.rstrip("/"), timeout, intervalo

    def _pedir(self, caminho, params=None):
        url = self.api + caminho + ("?" + urllib.parse.urlencode(params) if params else "")
        with _TRAVA:  # um pedido de cada vez, com o intervalo que a Open Library pede
            espera = _ULTIMO[0] + self.intervalo - time.time()
            if espera > 0:
                time.sleep(min(espera, self.intervalo))
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    return json.loads(r.read(4 * 1024 * 1024).decode("utf-8", "replace"))
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    raise ErroLivros("A Open Library não tem esse livro.") from None
                if e.code in (403, 429):
                    raise ErroLivros("A Open Library pediu para esperar um pouco: tente de novo daqui a um minuto.") from None
                raise ErroLivros(f"A Open Library respondeu com erro ({e.code}).") from None
            except (urllib.error.URLError, OSError, ValueError):
                raise ErroLivros("Sem resposta da Open Library: confira a internet.") from None
            finally:
                _ULTIMO[0] = time.time()

    def buscar(self, q, limite=20):
        """Os livros com esse nome (ou autor), ou o livro desse ISBN."""
        q = " ".join(str(q or "").split())[:120]
        if not q:
            return []
        isbn = isbn_de(q)
        d = self._pedir("/search.json", {"q": "isbn:" + isbn if isbn else q, "fields": CAMPOS, "limit": limite, "lang": "pt"})
        out, vistos = [], set()
        for x in d.get("docs") if isinstance(d, dict) and isinstance(d.get("docs"), list) else []:
            r = do_doc(x)
            if r and r["ol"] not in vistos:
                vistos.add(r["ol"])
                out.append(r)
        return out

    def detalhes(self, n):
        """Os detalhes de uma obra pelo número: o que a busca diz dela e a sinopse da página da obra."""
        if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
            raise ErroLivros("Esse livro não veio da Open Library.")
        d = self._pedir("/search.json", {"q": f"key:/works/OL{n}W", "fields": CAMPOS, "limit": 1, "lang": "pt"})
        docs = d.get("docs") if isinstance(d, dict) and isinstance(d.get("docs"), list) else []
        r = next((x for x in (do_doc(y) for y in docs) if x and x["ol"] == n), None)
        if not r:
            raise ErroLivros("A Open Library não tem esse livro.")
        try:
            obra = self._pedir(f"/works/OL{n}W.json")
            r["sinopse"] = _texto(obra.get("description"), 1200) if isinstance(obra, dict) else ""
        except ErroLivros:
            pass  # sem a sinopse, o resto vale
        r["link"] = f"https://openlibrary.org/works/OL{n}W"
        return r

    def imagem(self, capa, tamanho="ol_M"):
        """Os bytes da capa (JPEG), ou None."""
        if tamanho not in TAMANHOS or not re.match(r"^\d{1,12}$", str(capa or "")):
            return None
        try:
            req = urllib.request.Request(f"{self.img}/b/id/{capa}-{tamanho[3:]}.jpg?default=false", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                dado = r.read(MAX_IMG + 1)
        except (urllib.error.URLError, OSError, ValueError):
            return None
        return dado if 100 < len(dado) <= MAX_IMG and dado[:2] == b"\xff\xd8" else None
