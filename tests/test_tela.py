"""A tela num Chromium (playwright), com o servidor de verdade e o TMDB de mentira: adicionar, marcar o episódio, o
Voltar do celular, Buscar, Vistos, Configurações, Sobre e o padrão da família (ícones, nada passando da largura)."""
import unittest

from tests import apoio
from tests.apoio import S

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover (o GitHub instala; sem ele, o teste diz que pulou)
    sync_playwright = None


@unittest.skipIf(sync_playwright is None, "sem o playwright")
class TestTela(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = apoio.Servidor.subir()
        cls.pw = sync_playwright().start()
        cls.nav = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.nav.close()
        cls.pw.stop()

    def setUp(self):
        apoio.limpar()
        apoio.fixar_hoje(self)
        S.guardar_chave(apoio.CHAVE)
        self.erros = []

    def abrir(self, largura=390, tema="dark"):
        pg = self.nav.new_page(viewport={"width": largura, "height": 800}, color_scheme=tema)
        pg.on("pageerror", lambda e: self.erros.append(str(e)))
        pg.goto(self.base + "/")
        pg.wait_for_selector("#app .card")
        self.addCleanup(pg.close)
        return pg

    def padrao(self, pg, onde):
        """O padrão da família: nada passa da largura, todo cartão começa com o ícone e todo botão com texto tem ícone."""
        self.assertLessEqual(pg.evaluate("document.documentElement.scrollWidth"), pg.viewport_size["width"], onde)
        sem = pg.evaluate("""[...document.querySelectorAll('.card')].filter(c => !c.querySelector(':scope > .rot .rot-ic svg')).map(c => c.id)""")
        self.assertEqual(sem, [], onde + ": cartão sem ícone")
        sem = pg.evaluate("""[...document.querySelectorAll('button.btn, a.btn, .escolha, .linha')].filter(b => b.textContent.trim() && !b.querySelector('svg')).map(b => b.textContent.trim())""")
        self.assertEqual(sem, [], onde + ": botão sem ícone")

    def test_adicionar_marcar_e_voltar(self):
        pg = self.abrir()
        self.assertIn("A lista está vazia", pg.inner_text("#app"))
        self.padrao(pg, "Agora vazio")
        pg.click("#nav .add")
        pg.fill("#add-q", "estrelas")
        pg.wait_for_selector(".resultados .tit")
        self.padrao(pg, "Adicionar")
        pg.click(".resultados .tit")
        pg.wait_for_selector(".folha .topo-tit")
        self.assertEqual(pg.inner_text(".folha-tt"), "Mar de Estrelas")
        self.assertIn("on", pg.get_attribute(".escolha[data-v=quero]", "class"))
        pg.click(".escolha[data-v=vendo]")
        pg.wait_for_selector(".escolha.on[data-v=vendo]")
        pg.click(".folha [data-a=proximo]")
        pg.wait_for_function("document.querySelector('#f-ep') && document.querySelector('#f-ep').value === '1'")
        self.assertEqual(pg.input_value("#f-temp"), "1")
        pg.click(".estrelas [data-v='4']")
        pg.wait_for_selector(".estrelas button.on >> nth=3")
        self.padrao(pg, "o título")
        t = S.ler()["titulos"][0]
        self.assertEqual((t["situacao"], t["temp"], t["ep"], t["nota"], t["quem"]), ("vendo", 1, 1, 4, ["person.ana"]))
        pg.go_back()
        pg.wait_for_selector(".folha", state="detached")
        self.assertIn("Vendo agora", pg.inner_text("#app"))
        self.assertIn("Novos episódios", pg.inner_text("#app"))
        pg.click("#vendo .mais1")
        pg.wait_for_function("document.querySelector('#vendo').textContent.includes('parou em T1 E2')")
        self.assertEqual(self.erros, [])

    def test_buscar_vistos_mais(self):
        for tipo, n, sit in (("serie", 202, "vendo"), ("filme", 101, "visto"), ("filme", 103, "abandonado")):
            S.adicionar({"tipo": tipo, "tmdb": n, "situacao": sit}, "person.beto")
        pg = self.abrir(320, "light")
        self.padrao(pg, "Agora")
        pg.click("#nav [data-v=buscar]")
        self.assertEqual(pg.locator("#resultado .tit").count(), 2, "os abandonados ficam recolhidos no fim")
        self.assertIn("Abandonados (1)", pg.inner_text("#resultado"))
        pg.click("[data-a=aband]")
        self.assertEqual(pg.locator("#resultado .tit").count(), 3)
        pg.click("[data-a=f-tipo][data-v=serie]")
        self.assertEqual(pg.locator("#resultado .tit").count(), 1)
        pg.fill("#b-texto", "zzz")
        self.assertIn("Nenhum título", pg.inner_text("#resultado"))
        self.padrao(pg, "Buscar")
        pg.click("#nav [data-v=vistos]")
        self.assertIn("A Grande Viagem", pg.inner_text("#app"))
        self.padrao(pg, "Vistos")
        pg.click("#nav [data-v=mais]")
        pg.click("[data-a=ir-config]")
        self.assertIn("••••aaaa", pg.inner_text("#app"))
        self.padrao(pg, "Integrações")
        for aba in ("dados", "aparencia", "opcoes"):
            pg.click(f"[data-a=aba][data-v={aba}]")
            pg.wait_for_timeout(150)
            self.padrao(pg, aba)
        pg.click("[data-a=aba][data-v=aparencia]")
        pg.click(".tsw[data-v=azul]")
        pg.wait_for_function("getComputedStyle(document.documentElement).getPropertyValue('--accent').trim().toUpperCase() === '#62B5FF'")
        self.assertEqual(S.ler()["ajustes"]["cor"], "azul")
        pg.go_back()
        pg.click("[data-a=sobre]")
        self.assertIn("Este app · v" + S.VERSAO, pg.inner_text("#app"))
        self.assertIn("TMDB", pg.inner_text("#creditos"))
        self.padrao(pg, "Sobre")
        pg.go_back()
        pg.go_back()
        pg.wait_for_function("document.querySelector('#app h1').textContent.includes('Vistos')")
        self.assertEqual(pg.get_attribute("#nav [data-v=vistos]", "aria-current"), "page", "o Voltar do celular volta tela por tela")
        self.assertEqual(self.erros, [])

    def test_sem_chave_e_computador(self):
        S.guardar_chave("")
        pg = self.abrir(1280)
        self.assertIn("Comece aqui", pg.inner_text("#app"))
        self.assertTrue(pg.is_visible("#lado"))
        self.assertFalse(pg.is_visible("#nav"))
        pg.click("#lado [data-a=adicionar]")
        self.assertIn("Falta a chave do TMDB", pg.inner_text(".folha"))
        pg.click(".folha [data-a=ir-config]")
        pg.wait_for_selector("#f-chave")
        pg.fill("#f-chave", apoio.CHAVE)
        pg.click("[data-a=chave-salvar]")
        pg.wait_for_selector(".status:not(.erro)")
        self.assertEqual(S.chave_tmdb(), apoio.CHAVE)
        self.assertEqual(self.erros, [])
