"""Refaz as capturas do README (docs/*.png) com o servidor de verdade e o TMDB e o IGDB de mentira dos testes (títulos e
jogos inventados; Ana e Beto). Uso: python3 tools/prints_readme.py (precisa do playwright). Nada sai para a internet."""
import os
import sys
import threading
from http.server import ThreadingHTTPServer

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "tests"))
import apoio  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

S = apoio.S
SAIDA = os.path.join(RAIZ, "docs")


def casa():
    """A mesma casa do dev/rodar.py."""
    apoio.limpar()
    S.guardar_chave(apoio.CHAVE)
    S.guardar_igdb(apoio.IGDB_ID, apoio.IGDB_SEGREDO)
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
    return serie["id"]


def main():
    os.makedirs(SAIDA, exist_ok=True)
    serie = casa()
    srv = ThreadingHTTPServer(("127.0.0.1", 0), S.Handler)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/"
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        pg = nav.new_page(viewport={"width": 390, "height": 844}, color_scheme="dark", device_scale_factor=2,
                          extra_http_headers={"X-Remote-User-Id": "u-ana", "X-Remote-User-Display-Name": "Ana Exemplo"})
        pg.goto(url)
        pg.wait_for_selector("#nav [data-v=agora]")
        pg.wait_for_timeout(800)
        pg.screenshot(path=f"{SAIDA}/agora.png")
        pg.click('#nav [data-a="adicionar"]')
        pg.wait_for_selector(".cartazes .cz")
        pg.wait_for_timeout(800)
        pg.screenshot(path=f"{SAIDA}/adicionar.png")
        pg.keyboard.press("Escape")
        pg.wait_for_selector(".folha", state="detached")
        pg.click(f'[data-a="abrir"][data-id="{serie}"]')
        pg.wait_for_selector(".folha")
        pg.wait_for_timeout(600)
        pg.screenshot(path=f"{SAIDA}/titulo.png")
        pg.keyboard.press("Escape")
        pg.wait_for_selector(".folha", state="detached")
        pg.click("#nav [data-v=vistos]")
        pg.wait_for_timeout(800)
        pg.screenshot(path=f"{SAIDA}/concluidos.png")
        nav.close()
    srv.shutdown()
    print("ok")


if __name__ == "__main__":
    main()
