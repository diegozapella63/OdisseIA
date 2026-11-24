"""O OdisseIA no computador, com o TMDB de mentira dos testes (títulos inventados) e Ana e Beto de exemplo.

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
if "--vazio" not in sys.argv:
    S.adicionar({"tipo": "serie", "tmdb": 202, "situacao": "vendo"}, "person.ana")
    S.adicionar({"tipo": "filme", "tmdb": 101, "situacao": "quero"}, "person.beto")
    S.adicionar({"tipo": "serie", "tmdb": 204, "situacao": "visto"}, "person.ana")
    S.adicionar({"tipo": "filme", "tmdb": 103, "situacao": "abandonado"}, "")
    d = S.ler()
    serie = next(t for t in d["titulos"] if t["tmdb"] == 202)
    S.mudar_titulo({"acao": "mudar", "id": serie["id"], "campos": {"temp": 1, "ep": 3, "nota": 4}})
srv = ThreadingHTTPServer(("127.0.0.1", porta), S.Handler)
print(f"OdisseIA em http://127.0.0.1:{porta} (dados em {S.DATA_DIR})", flush=True)
try:
    srv.serve_forever()
except KeyboardInterrupt:
    time.sleep(0)
