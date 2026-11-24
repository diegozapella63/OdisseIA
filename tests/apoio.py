"""Apoio dos testes: um TMDB de mentira (com títulos inventados), o servidor do OdisseIA numa porta livre e pedidos.

Os títulos, os nomes e as capas são inventados: nada aqui é da casa do dono."""
import base64
import json
import os
import shutil
import socket
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(RAIZ, "odisseia", "app")
sys.path.insert(0, APP)

CHAVE = "a" * 32
TOKEN = "eyJteste.token.leitura"
CHAVE_RECUSADA = "c" * 32  # passa na porta, mas o /authentication diz que não
CAPAS = {
    "/viagem.jpg": base64.b64decode("/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAA0JCgsKCA0LCgsODg0PEyAVExISEyccHhcgLikxMC4pLSwzOko+MzZGNywtQFdBRkxOUlNSMj5aYVpQYEpRUk//2wBDAQ4ODhMREyYVFSZPNS01T09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0//wAARCABaADwDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwCjRRRXvGwUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRXVf8Id/1EP8AyD/9lUTqwp/ExN2OVorqv+EO/wCoh/5B/wDsqP8AhDv+oh/5B/8Asqz+tUu/5i5kcrRXVf8ACHf9RD/yD/8AZUf8Id/1EP8AyD/9lR9apd/zDmRytFbWs6D/AGXaJP8AavN3SBNvl7exOep9Kxa1hOM1eI07hXqdeWV6nXFjvs/MmYUUUVwEBRRRQBgeMv8AkExf9dx/6C1cXXaeMv8AkExf9dx/6C1cXXq4T+GaR2Crf9p6h/z/AF1/3+b/ABqpRXQ0nuUW/wC09Q/5/rr/AL/N/jR/aeof8/11/wB/m/xqpRS5I9hFv+09Q/5/rr/v83+NH9p6h/z/AF1/3+b/ABqpRRyR7ATzXl1cIEnuZpVByA7lhn8agooqkkthn//Z"),
    "/estrelas.jpg": base64.b64decode("/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAA0JCgsKCA0LCgsODg0PEyAVExISEyccHhcgLikxMC4pLSwzOko+MzZGNywtQFdBRkxOUlNSMj5aYVpQYEpRUk//2wBDAQ4ODhMREyYVFSZPNS01T09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0//wAARCABaADwDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDNooor3jxwooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiur/AOEM/wCoh/5B/wDsqznVhT+Jlwpyn8JylFdX/wAIZ/1EP/IP/wBlR/whn/UQ/wDIP/2VZ/WqXf8AMv6vU7HKUV1f/CGf9RD/AMg//ZUf8IZ/1EP/ACD/APZUfWqXf8w+r1OxylFbeteH/wCybNLj7V5u6QJt8vb2Jz1PpWJWsJxmrxM5RcXZhXq9eUV6vXHjfs/M6sJ1CiiiuA7AooooA57xr/yCIv8AruP/AEFq4mu28a/8giL/AK7j/wBBauJr1MJ/DPOxPxhVr+1NR/5/7r/v83+NVaK6Wk9zFNrYtf2pqP8Az/3X/f5v8aP7U1H/AJ/7r/v83+NVaKXJHsHM+5a/tTUf+f8Auv8Av83+NH9qaj/z/wB1/wB/m/xqrRRyR7BzPuTT3l3cIEuLmaVQchXkLDPrzUNFFNJLYTdz/9k="),
    "/texto.jpg": b"isto nao e uma imagem",
    "/farol.jpg": base64.b64decode("/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAA0JCgsKCA0LCgsODg0PEyAVExISEyccHhcgLikxMC4pLSwzOko+MzZGNywtQFdBRkxOUlNSMj5aYVpQYEpRUk//2wBDAQ4ODhMREyYVFSZPNS01T09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0//wAARCABaADwDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwCtRRRSPBCiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKK6f8A4RH/AKf/APyD/wDZUGkKU6nwo5iiun/4RH/p/wD/ACD/APZUf8Ij/wBP/wD5B/8AsqZp9Vq9vyOYorp/+ER/6f8A/wAg/wD2VH/CI/8AT/8A+Qf/ALKgPqtXt+RzFFbGsaF/Zlqs/wBp83c4THl7exPqfSsekZThKDtIK9OrzGvTqZ2YL7XyCiiig7wooooAwvF//IKi/wCu4/8AQWrjq7Hxf/yCov8AruP/AEFq46g8vF/xAq1/aV//AM/1z/39b/GqtFI5k2ti1/aV/wD8/wBc/wDf1v8AGj+0r/8A5/rn/v63+NVaKB88u5a/tK//AOf65/7+t/jR/aV//wA/1z/39b/GqtFAc8u5NNd3M6BJ7iaRQcgO5Iz+NQ0UUCbb3P/Z"),
}
ONDE = {"results": {"BR": {"link": "https://www.themoviedb.org/movie/101/watch?locale=BR",
                           "flatrate": [{"provider_name": "Cine Lumen"}], "rent": [{"provider_name": "Loja Pipoca"}]},
                    "US": {"flatrate": [{"provider_name": "Outro"}]}}}
FILMES = {
    101: {"id": 101, "title": "A Grande Viagem", "original_title": "The Long Trip", "release_date": "2019-05-10", "runtime": 132,
          "genres": [{"name": "Aventura"}, {"name": "Drama"}], "overview": "Uma família cruza o país num ônibus velho.",
          "poster_path": "/viagem.jpg", "status": "Released", "watch/providers": ONDE, "belongs_to_collection": {"id": 301, "name": "Coleção A Grande Viagem"}},
    105: {"id": 105, "title": "A Grande Viagem 2", "original_title": "The Long Trip 2", "release_date": "2022-07-01", "runtime": 120, "genres": [],
          "overview": "A família volta para a estrada.", "poster_path": "/viagem.jpg", "watch/providers": {"results": {}},
          "belongs_to_collection": {"id": 301, "name": "Coleção A Grande Viagem"}},
    106: {"id": 106, "title": "A Grande Viagem 3", "original_title": "The Long Trip 3", "release_date": "2027-06-01", "runtime": None, "genres": [],
          "overview": "", "poster_path": None, "watch/providers": {"results": {}}, "belongs_to_collection": {"id": 301, "name": "Coleção A Grande Viagem"}},
    103: {"id": 103, "title": "Farol Distante", "original_title": "Farol Distante", "release_date": "2021-08-01", "runtime": 95,
          "genres": [{"name": "Suspense"}], "overview": "", "poster_path": "/farol.jpg", "status": "Released", "watch/providers": {"results": {}}},
}
SERIES = {
    202: {"id": 202, "name": "Mar de Estrelas", "original_name": "Sea of Stars", "first_air_date": "2023-02-01", "status": "Returning Series",
          "genres": [{"name": "Ficção científica"}], "overview": "Uma tripulação perdida tenta voltar para casa.", "poster_path": "/estrelas.jpg",
          "seasons": [{"season_number": 0, "episode_count": 2}, {"season_number": 1, "episode_count": 3}, {"season_number": 2, "episode_count": 4}],
          "last_episode_to_air": {"air_date": "2026-11-20", "season_number": 2, "episode_number": 2, "name": "A Volta"},
          "next_episode_to_air": {"air_date": "2026-11-27", "season_number": 2, "episode_number": 3, "name": "O Farol"},
          "watch/providers": {"results": {"BR": {"flatrate": [{"provider_name": "Cine Lumen"}]}}}},
    204: {"id": 204, "name": "Casa no Morro", "original_name": "Casa no Morro", "first_air_date": "2018-03-01", "status": "Ended",
          "genres": [{"name": "Comédia"}], "overview": "Três irmãos dividem uma casa.", "poster_path": None,
          "seasons": [{"season_number": 1, "episode_count": 2}],
          "last_episode_to_air": {"air_date": "2018-04-01", "season_number": 1, "episode_number": 2, "name": "Fim"},
          "next_episode_to_air": None, "watch/providers": {"results": {}}},
}


COLECOES = {
    301: {"id": 301, "name": "Coleção A Grande Viagem", "original_name": "The Long Trip Collection", "overview": "Os três filmes da família na estrada.",
          "poster_path": "/viagem.jpg", "parts": [{"id": 106, "title": "A Grande Viagem 3", "release_date": "2027-06-01"},
                                                  {"id": 101, "title": "A Grande Viagem", "original_title": "The Long Trip", "release_date": "2019-05-10", "poster_path": "/viagem.jpg"},
                                                  {"id": 105, "title": "A Grande Viagem 2", "release_date": "2022-07-01"}, {"id": "x"}]},
}


class TMDBFalso:
    """O TMDB de mentira: a mesma forma das respostas de verdade, só com os títulos daqui. pedidos: o que chegou."""

    def __init__(self):
        self.pedidos = []
        dono = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                u = urlparse(self.path)
                q = {k: v[0] for k, v in parse_qs(u.query).items()}
                dono.pedidos.append((u.path, q, self.headers.get("Authorization")))
                if u.path.startswith("/t/p/"):
                    dado = CAPAS.get("/" + u.path.rsplit("/", 1)[-1])
                    return self.resp(200, dado, "image/jpeg") if dado else self.resp(404, b"{}")
                if q.get("api_key") not in (CHAVE, CHAVE_RECUSADA) and self.headers.get("Authorization") != "Bearer " + TOKEN:
                    return self.resp(401, {"success": False, "status_message": "Invalid API key"})
                if u.path == "/3/authentication":
                    return self.resp(200, {"success": q.get("api_key") != CHAVE_RECUSADA})
                if u.path in ("/3/movie/429", "/3/movie/500"):
                    return self.resp(int(u.path[-3:]), {})
                m = u.path.split("/")
                if u.path == "/3/search/collection":
                    alvo = q.get("query", "").lower()
                    return self.resp(200, {"results": [c for c in COLECOES.values() if alvo in c["name"].lower()] + ["x"]})
                if u.path.startswith("/3/collection/"):
                    n = int(u.path.rsplit("/", 1)[-1])
                    return self.resp(200, COLECOES[n]) if n in COLECOES else self.resp(404, {})
                lista = re_lista(u.path)
                if lista:
                    pag = int(q.get("page", 1))
                    return self.resp(200, {"page": pag, "total_pages": 2, "results": lista[(pag - 1) * 2:pag * 2]})
                if u.path.startswith("/3/search/"):
                    alvo = q.get("query", "").lower()
                    rs = []
                    if m[3] in ("multi", "movie"):
                        rs += [dict(f, media_type="movie") for f in FILMES.values() if alvo in f["title"].lower() or alvo in f["original_title"].lower()]
                    if m[3] in ("multi", "tv"):
                        rs += [dict(s, media_type="tv") for s in SERIES.values() if alvo in s["name"].lower() or alvo in s["original_name"].lower()]
                    if alvo == "estranho":
                        rs += ["isto não é um título", {"id": 1, "media_type": "movie", "title": "Estranho", "poster_path": "/../x.jpg"}]
                    if m[3] == "multi" and "ana" in alvo:
                        rs.append({"id": 9, "media_type": "person", "name": "Ana Atriz"})
                    if m[3] != "multi":
                        for r in rs:
                            r.pop("media_type")
                    return self.resp(200, {"page": 1, "results": rs})
                if len(m) == 4 and m[2] == "movie" and int(m[3]) in FILMES:
                    return self.resp(200, FILMES[int(m[3])])
                if len(m) == 4 and m[2] == "tv" and int(m[3]) in SERIES:
                    return self.resp(200, SERIES[int(m[3])])
                return self.resp(404, {"success": False})

            def resp(self, st, corpo, tipo="application/json"):
                b = corpo if isinstance(corpo, bytes) else json.dumps(corpo).encode()
                self.send_response(st)
                self.send_header("Content-Type", tipo)
                self.send_header("Content-Length", str(len(b)))
                self.end_headers()
                self.wfile.write(b)

        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.porta = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def fechar(self):
        self.srv.shutdown()
        self.srv.server_close()


def re_lista(caminho):
    """As listas prontas do TMDB de mentira: duas por página, duas páginas."""
    m = caminho.split("/")
    filmes = [dict(f, media_type="movie") for f in FILMES.values()]
    series = [dict(s, media_type="tv") for s in SERIES.values()]
    if len(m) == 5 and m[2] == "trending":
        return {"all": filmes[:1] + series + filmes[1:], "movie": filmes, "tv": series}.get(m[3])
    if len(m) == 4 and m[2] == "movie" and m[3] in ("popular", "top_rated", "now_playing"):
        return filmes
    if len(m) == 4 and m[2] == "tv" and m[3] in ("popular", "top_rated", "on_the_air"):
        return series + [{"id": "x"}]
    return None


def porta_livre():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


TMDB = TMDBFalso()
PASTA = tempfile.mkdtemp(prefix="odisseia-teste-")
os.environ.update(ODISSEIA_DEV="1", ODISSEIA_DATA=os.path.join(PASTA, "data"), ODISSEIA_SHARE=os.path.join(PASTA, "share", "odisseia"),
                  ODISSEIA_TMDB=f"http://127.0.0.1:{TMDB.porta}/3", ODISSEIA_TMDB_IMG=f"http://127.0.0.1:{TMDB.porta}/t/p",
                  ODISSEIA_URL_INTERNA="http://odisseia-teste:8099")
os.environ.pop("SUPERVISOR_TOKEN", None)
import server as S  # noqa: E402


class Servidor:
    """O servidor do OdisseIA de verdade numa porta livre (uma vez para todos os testes)."""
    _srv = None

    @classmethod
    def subir(cls):
        if not cls._srv:
            cls._srv = ThreadingHTTPServer(("127.0.0.1", 0), S.Handler)
            threading.Thread(target=cls._srv.serve_forever, daemon=True).start()
        return f"http://127.0.0.1:{cls._srv.server_address[1]}"


HOJE = "2026-11-24T10:00:00"  # o "agora" dos testes: o próximo episódio do TMDB de mentira sai em 27/11/2026


def fixar_hoje(teste):
    """O servidor acha que hoje é 24/11/2026 (nada depende do relógio de verdade)."""
    from unittest import mock
    p = mock.patch.object(S, "agora_iso", return_value=HOJE)
    p.start()
    teste.addCleanup(p.stop)


def limpar():
    """Começa sem dados (a pasta do app e a share vazias, nenhuma chave)."""
    for p in (S.DATA_DIR, os.path.dirname(S.SHARE_DIR)):
        shutil.rmtree(p, ignore_errors=True)
    os.makedirs(S.DATA_DIR, exist_ok=True)
    S.ESTADO_TMDB.update(erro="", em="")
    S.IMGS.clear()
    S.CORRERIA._chave = None
    S.CORRERIA.ultimo = None


def pedir(base, metodo, rota, corpo=None, cab=None):
    """(status, json ou bytes)."""
    dado = json.dumps(corpo).encode() if isinstance(corpo, (dict, list)) else corpo
    req = urllib.request.Request(base + rota, data=dado, method=metodo, headers=dict({"Content-Type": "application/json"}, **(cab or {})))
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            b, st, tipo = r.read(), r.status, r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        b, st, tipo = e.read(), e.code, e.headers.get("Content-Type", "")
    return st, (json.loads(b) if "json" in tipo and b else b)
