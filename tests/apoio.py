"""Apoio dos testes: um TMDB e um IGDB de mentira (com títulos e jogos inventados), o servidor do OdisseIA numa porta
livre e pedidos.

Os títulos, os nomes e as capas são inventados: nada aqui é da casa do dono."""
import base64
import json
import os
import re
import shutil
import socket
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from datetime import datetime, timezone
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
          "poster_path": "/viagem.jpg", "status": "Released", "watch/providers": ONDE, "belongs_to_collection": {"id": 301, "name": "Coleção A Grande Viagem", "poster_path": "/viagem.jpg"}},
    105: {"id": 105, "title": "A Grande Viagem 2", "original_title": "The Long Trip 2", "release_date": "2022-07-01", "runtime": 120, "genres": [],
          "overview": "A família volta para a estrada.", "poster_path": "/viagem.jpg", "watch/providers": {"results": {}},
          "belongs_to_collection": {"id": 301, "name": "Coleção A Grande Viagem", "poster_path": "/viagem.jpg"}},
    106: {"id": 106, "title": "A Grande Viagem 3", "original_title": "The Long Trip 3", "release_date": "2027-06-01", "runtime": None, "genres": [],
          "overview": "", "poster_path": None, "watch/providers": {"results": {}}, "belongs_to_collection": {"id": 301, "name": "Coleção A Grande Viagem", "poster_path": "/viagem.jpg"}},
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


IGDB_ID = "idteste0123456789abcd"
IGDB_SEGREDO = "segredoteste0123456789"


def _quando(iso):
    return int(datetime.fromisoformat(iso + "T12:00:00").replace(tzinfo=timezone.utc).timestamp())


SAGA = [{"id": 501, "name": "Saga da Torre"}]
JOGOS = {
    701: {"id": 701, "name": "Torre do Relógio", "first_release_date": _quando("2021-06-15"), "cover": {"id": 1, "image_id": "co1torre"},
          "game_type": 0, "summary": "A clock tower puzzle adventure.", "genres": [{"id": 1, "name": "Puzzle"}, {"id": 2, "name": "Adventure"}],
          "platforms": [{"id": 6, "name": "PC (Microsoft Windows)"}, {"id": 167, "name": "PlayStation 5"}, {"id": 6, "name": "PC (Microsoft Windows)"}],
          "collections": SAGA, "url": "https://www.igdb.com/games/torre-do-relogio", "total_rating": 88, "total_rating_count": 400},
    702: {"id": 702, "name": "Torre do Relógio 2", "first_release_date": _quando("2024-03-01"), "cover": {"id": 2, "image_id": "co2torre"},
          "category": 0, "summary": "The tower again.", "platforms": [{"id": 130, "name": "Nintendo Switch"}], "collections": SAGA},
    703: {"id": 703, "name": "Torre do Relógio 3", "first_release_date": _quando("2027-03-01"), "game_type": 0, "collections": SAGA},
    704: {"id": 704, "name": "Torre do Relógio Remasterizado", "first_release_date": _quando("2025-01-10"), "game_type": 9, "collections": SAGA,
          "cover": {"id": 4, "image_id": "co4torre"}},
    705: {"id": 705, "name": "Ilha dos Ventos", "first_release_date": _quando("2025-10-01"), "cover": {"id": 5, "image_id": "co5ilha"},
          "game_type": 0, "summary": "Sail between windy islands.", "platforms": [{"id": 130, "name": "Nintendo Switch"}, {"id": 82, "name": "Web browser"}],
          "total_rating": 91, "total_rating_count": 300, "hypes": 50, "url": "https://outro.site/ilha"},
    706: {"id": 706, "name": "Torre do Relógio Pacote", "game_type": 3, "collections": SAGA},
    707: {"id": 707, "name": "Torre do Relógio Trilha Sonora", "game_type": 1},
    708: {"id": 708, "name": "Torre do Relógio Deluxe", "game_type": 0, "version_parent": 701},
}
COLECOES_JOGOS = {501: {"id": 501, "name": "Saga da Torre"}}
POPULARES = {1: [705, 707, 701, 702, 999], 3: [701]}


# a Open Library de mentira: livros, autores e ISBN inventados
LIVROS = {
    901: {"key": "/works/OL901W", "title": "O Farol das Marés", "author_name": ["Ana Autora"], "first_publish_year": 2001, "cover_i": 5001,
          "number_of_pages_median": 320, "isbn": ["9786500000017", "6500000013"], "subject": ["Aventura", "Mar"]},
    902: {"key": "/works/OL902W", "title": "A Torre de Vidro", "author_name": ["Beto Escritor", "Ana Autora"], "first_publish_year": 1998,
          "isbn": ["9786500000024"], "subject": ["Mistério"]},
    903: {"key": "/works/OL903W", "title": "The Glass Lighthouse", "author_name": ["Carla Writer"], "first_publish_year": 2015, "cover_i": 5003,
          "number_of_pages_median": 210, "isbn": ["9786500000031"], "editions": {"docs": [{"title": "O Farol de Vidro", "language": ["por"]}]}},
}
SINOPSES_LIVROS = {901: {"description": {"type": "/type/text", "value": "Uma faroleira e o mar que não devolve nada."}}, 902: {"description": "Um mistério numa torre."}, 903: {}}
CAPAS_LIVROS = {"5001": "/viagem.jpg", "5003": "/estrelas.jpg"}


class TMDBFalso:
    """O TMDB de mentira: a mesma forma das respostas de verdade, só com os títulos daqui. pedidos: o que chegou."""

    def __init__(self):
        self.pedidos = []
        self.tokens = set()
        self.n_token = 0
        self.falha_igdb = 0
        self.falha_ol = 0  # o código que a Open Library de mentira responde (0: funciona)
        dono = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                u = urlparse(self.path)
                q = {k: v[0] for k, v in parse_qs(u.query).items()}
                dono.pedidos.append((u.path, q, self.headers.get("Authorization")))
                if u.path.startswith("/igdb/image/upload/"):
                    dado = CAPAS.get({"co1torre": "/viagem.jpg", "co2torre": "/estrelas.jpg", "co5ilha": "/farol.jpg", "co4torre": "/texto.jpg"}.get(u.path.rsplit("/", 1)[-1][:-4], ""))
                    return self.resp(200, dado, "image/jpeg") if dado else self.resp(404, b"{}")
                if u.path.startswith("/olimg/b/id/"):
                    dado = CAPAS.get(CAPAS_LIVROS.get(u.path.rsplit("/", 1)[-1].split("-")[0], ""))
                    return self.resp(200, dado, "image/jpeg") if dado else self.resp(404, b"{}")
                if u.path.startswith("/ol/"):
                    dono.ua_ol = self.headers.get("User-Agent")
                    if dono.falha_ol:
                        return self.resp(dono.falha_ol, {})
                    if u.path == "/ol/search.json":
                        alvo = q.get("q", "").lower()
                        if alvo.startswith("isbn:"):
                            docs = [v for v in LIVROS.values() if alvo[5:] in [i.lower() for i in v["isbn"]]]
                        elif alvo.startswith("key:"):
                            docs = [v for v in LIVROS.values() if v["key"].lower() == alvo[4:]]
                        else:
                            docs = [v for v in LIVROS.values() if alvo in v["title"].lower() or any(alvo in a.lower() for a in v["author_name"])
                                    or any(alvo in e["title"].lower() for e in (v.get("editions") or {}).get("docs", []))]
                        return self.resp(200, {"numFound": len(docs), "docs": docs + (["x", {"key": "/authors/OL1A", "title": "Não é obra"}] if alvo == "estranho" else [])})
                    m = re.match(r"^/ol/works/OL(\d+)W\.json$", u.path)
                    if m and int(m.group(1)) in SINOPSES_LIVROS:
                        return self.resp(200, SINOPSES_LIVROS[int(m.group(1))])
                    return self.resp(404, {})
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

            def do_POST(self):
                u = urlparse(self.path)
                corpo = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode()
                dono.pedidos.append((u.path, corpo, self.headers.get("Authorization")))
                if u.path == "/oauth2/token":
                    f = {k: v[0] for k, v in parse_qs(corpo).items()}
                    if f.get("client_id") == IGDB_ID and f.get("client_secret") == IGDB_SEGREDO and f.get("grant_type") == "client_credentials":
                        dono.n_token += 1
                        dono.tokens.add(f"tok{dono.n_token}")
                        return self.resp(200, {"access_token": f"tok{dono.n_token}", "expires_in": 5000000, "token_type": "bearer"})
                    return self.resp(403, {"status": 403, "message": "invalid client secret"})
                if self.headers.get("Client-ID") != IGDB_ID or (self.headers.get("Authorization") or "")[7:] not in dono.tokens:
                    return self.resp(401, {"message": "Authorization Failure"})
                if dono.falha_igdb:
                    return self.resp(dono.falha_igdb, [])
                rota = u.path.rsplit("/", 1)[-1]
                limite = int((re.search(r"limit (\d+);", corpo) or [0, 10])[1])
                desde = int((re.search(r"offset (\d+);", corpo) or [0, 0])[1])
                if rota == "popularity_primitives":
                    tp = int(re.search(r"popularity_type = (\d+)", corpo)[1])
                    return self.resp(200, [{"game_id": g, "value": 1.0 / (i + 1)} for i, g in enumerate(POPULARES.get(tp, []))][desde:desde + limite])
                if rota == "collections":
                    if m := re.search(r'name ~ \*"([^"]*)"\*', corpo):
                        return self.resp(200, [c for c in COLECOES_JOGOS.values() if m[1].lower() in c["name"].lower()])
                    n = int(re.search(r"where id = (\d+)", corpo)[1])
                    return self.resp(200, [COLECOES_JOGOS[n]] if n in COLECOES_JOGOS else [])
                rs = list(JOGOS.values())
                if m := re.search(r'search "([^"]*)"', corpo):
                    rs = [j for j in rs if m[1].lower() in j["name"].lower()]
                if m := re.search(r"where id = \(([\d,]+)\)", corpo):
                    ids = {int(x) for x in m[1].split(",")}
                    rs = [j for j in rs if j["id"] in ids]
                if m := re.search(r"collections = \(([\d,]+)\)", corpo):
                    ns = {int(x) for x in m[1].split(",")}
                    rs = [j for j in rs if any(c["id"] in ns for c in j.get("collections") or [])]
                if "total_rating_count >" in corpo:
                    rs = sorted((j for j in rs if j.get("total_rating_count")), key=lambda j: -j["total_rating"])
                if "hypes > 0" in corpo:
                    rs = [j for j in rs if j.get("hypes")]
                if "version_parent = null" in corpo:
                    rs = [j for j in rs if not j.get("version_parent")]
                return self.resp(200, rs[desde:desde + limite] + (["x"] if "search" in corpo else []))

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
                  ODISSEIA_URL_INTERNA="http://odisseia-teste:8099", ODISSEIA_IGDB=f"http://127.0.0.1:{TMDB.porta}/v4",
                  ODISSEIA_TWITCH=f"http://127.0.0.1:{TMDB.porta}/oauth2/token", ODISSEIA_IGDB_IMG=f"http://127.0.0.1:{TMDB.porta}/igdb/image/upload",
                  ODISSEIA_OL=f"http://127.0.0.1:{TMDB.porta}/ol", ODISSEIA_OL_IMG=f"http://127.0.0.1:{TMDB.porta}/olimg", ODISSEIA_OL_INTERVALO="0")
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
    S.ESTADO_IGDB.update(erro="", em="")
    S.G._TOKENS.clear()
    TMDB.falha_igdb = 0
    TMDB.falha_ol = 0
    S.IMGS.clear()
    S.DETALHES.clear()
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
