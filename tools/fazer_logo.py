"""Desenha odisseia/icon.png (128 × 128) e odisseia/logo.png (679 × 250), no jeito dos outros apps da família: o quadrado
inclinado na cor do app (Lilás) com o play, e o nome com o IA na cor. Precisa do playwright (python -m playwright install chromium).

    python3 tools/fazer_logo.py
"""
import os
import tempfile

from playwright.sync_api import sync_playwright

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTE = os.path.join(RAIZ, "odisseia", "app", "www", "fonts", "barlow-condensed-700.woff")
LILAS, TINTA, NOME = "#B99BFF", "#1a1206", "#1F2430"
ICONE = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{{w}}" height="{{w}}"><rect x="8" y="8" width="48" height="48" rx="13"
  transform="rotate(-8 32 32)" fill="{LILAS}"/><path d="M26 21.5v21a2 2 0 0 0 3 1.7l17-10.5a2 2 0 0 0 0-3.4L29 19.8a2 2 0 0 0-3 1.7z" fill="{TINTA}"/></svg>"""
PAGINA = f"""<!doctype html><html><head><style>
@font-face {{ font-family: BC; src: url("{FONTE}") format("woff"); font-weight: 700; }}
html, body {{ margin: 0; background: transparent; }}
#icone {{ width: 128px; height: 128px; }}
#logo {{ width: 679px; height: 250px; display: flex; align-items: center; gap: 14px; padding-left: 14px; box-sizing: border-box; }}
.wm {{ font: 700 132px/1 BC; color: {NOME}; letter-spacing: -1px; }}
.wm span {{ color: #8A63F0; }}
</style></head><body><div id="icone">{ICONE.format(w=128)}</div><div id="logo">{ICONE.format(w=236)}<div class="wm">Odisse<span>IA</span></div></div></body></html>"""

with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_page()
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(PAGINA.replace(FONTE, "file://" + FONTE))
    pg.goto("file://" + f.name)
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(300)
    pg.locator("#icone").screenshot(path=os.path.join(RAIZ, "odisseia", "icon.png"), omit_background=True)
    pg.locator("#logo").screenshot(path=os.path.join(RAIZ, "odisseia", "logo.png"), omit_background=True)
    nav.close()
    os.remove(f.name)
print("icon.png e logo.png prontos")
