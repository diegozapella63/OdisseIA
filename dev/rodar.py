"""O OdisseIA no computador, com o TMDB e o IGDB de mentira dos testes (títulos e jogos inventados) e Ana e Beto de exemplo.

    python3 dev/rodar.py            abre em http://127.0.0.1:8099 (a chave do TMDB de mentira já vem posta)
    python3 dev/rodar.py --vazio    sem nenhum título
"""
import os
import sys
import time
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
import apoio  # noqa: E402

S = apoio.S
porta = int(os.environ.get("PORTA", "8099"))
apoio.limpar()
S.guardar_chave(apoio.CHAVE)
S.guardar_igdb(apoio.IGDB_ID, apoio.IGDB_SEGREDO)
if "--vazio" not in sys.argv:
    S.adicionar({"tipo": "serie", "tmdb": 202, "situacao": "quero"}, "person.ana")
    S.adicionar({"tipo": "filme", "tmdb": 101, "situacao": "quero"}, "person.beto")
    S.adicionar({"tipo": "serie", "tmdb": 204, "situacao": "visto"}, "person.ana")
    S.adicionar({"tipo": "filme", "tmdb": 103, "situacao": "visto"}, "")
    S.adicionar({"tipo": "jogo", "igdb": 701, "situacao": "visto"}, "person.beto")
    S.adicionar({"tipo": "jogo", "igdb": 703, "situacao": "quero"}, "person.ana")
    d = S.ler()
    for tipo, nome in (("filme", "Para ver em família"), ("filme", "Clássicos"), ("serie", "Para ver a dois"), ("jogo", "Para jogar junto")):
        S.R.mudar_categorias(d, {"acao": "nova", "tipo": tipo, "nome": nome})
    S.salvar(d)
    serie = next(t for t in d["titulos"] if t["tmdb"] == 202)
    S.mudar_titulo({"acao": "mudar", "id": serie["id"], "campos": {"temp": 1, "ep": 3, "categoria": d["categorias"]["serie"][0]["id"]}})
srv = ThreadingHTTPServer(("127.0.0.1", porta), S.Handler)
print(f"OdisseIA em http://127.0.0.1:{porta} (dados em {S.DATA_DIR})", flush=True)
try:
    srv.serve_forever()
except KeyboardInterrupt:
    time.sleep(0)
