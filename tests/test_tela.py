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
        pg.wait_for_selector(".cartazes .cz")
        self.assertEqual(pg.inner_text(".chip.on"), "Em alta", "abre nas listas prontas")
        self.assertFalse(pg.evaluate("document.activeElement.id === 'add-q'"), "sem o foco no campo: o teclado não sobe")
        self.padrao(pg, "Adicionar")
        pg.fill("#add-q", "estrelas")
        pg.wait_for_function("document.querySelectorAll('.cartazes .cz').length === 1")
        pg.click(".cz:has-text('Mar de Estrelas') .cz-capa")
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
        pg.wait_for_selector(".folha #add-q")
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
        pg.click("#nav [data-v=historico]")
        self.assertIn("Nenhuma série vista", pg.inner_text("#app"), "abre em Séries")
        pg.click("[data-a=hist][data-v=filme]")
        self.assertIn("A Grande Viagem", pg.inner_text("#app"))
        self.padrao(pg, "Histórico")
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
        pg.wait_for_function("document.querySelector('#app h1').textContent.includes('Histórico')")
        self.assertEqual(pg.get_attribute("#nav [data-v=historico]", "aria-current"), "page", "o Voltar do celular volta tela por tela")
        self.assertIn("A Grande Viagem", pg.inner_text("#app"), "a aba do Histórico fica guardada")
        self.assertEqual(self.erros, [])

    def test_ja_vi_e_colecao(self):
        pg = self.abrir()
        pg.click("#nav .add")
        pg.click("[data-a=add-lista][data-v=avaliados]")
        pg.click("[data-a=add-tipo][data-v=serie]")
        pg.wait_for_selector(".cartazes .cz-nome >> text=Mar de Estrelas")
        pg.click(".cz:has-text('Mar de Estrelas') [data-a=cz-visto]")
        pg.wait_for_selector(".cz.feito .cz-sit >> text=Visto")
        t = S.ler()["titulos"][0]
        self.assertEqual((t["situacao"], t["temp"], t["ep"]), ("visto", 2, 2), "a série inteira, até o último episódio que saiu")
        self.assertEqual(pg.locator(".cz.feito [data-a=cz-visto]").count(), 0, "vista: sem o Já vi")
        pg.click(".cz:has-text('Casa no Morro') [data-a=cz-quero]")
        pg.wait_for_selector(".cz:has-text('Casa no Morro') .cz-sit >> text=Quero ver")
        pg.click("[data-a=add-mais]")
        pg.wait_for_function("document.querySelectorAll('.cartazes .cz').length === 2 && !document.querySelector('[data-a=add-mais]')")  # a página 2 só tem um item estragado
        pg.click("[data-a=add-tipo][data-v='']")
        pg.fill("#add-q", "grande viagem")
        pg.wait_for_selector(".cz-nome >> text=Coleção A Grande Viagem")
        self.assertEqual(pg.locator(".cz:has-text('A Grande Viagem 3') [data-a=cz-visto]").count(), 0, "o que ainda não saiu não tem o Já vi")
        pg.click(".cz:has-text('Coleção A Grande Viagem') .cz-capa")
        pg.wait_for_selector(".folha [data-a=col-todos][data-v=visto]")
        self.assertIn("sai em 01/06/2027", pg.inner_text(".folha"))
        self.padrao(pg, "a coleção")
        pg.click(".folha [data-a=col-todos][data-v=visto]")
        pg.wait_for_function("document.querySelectorAll('.folha .cz.feito').length === 2")
        nomes = sorted((x["nome"], x["situacao"]) for x in S.ler()["titulos"] if x["tipo"] == "filme")
        self.assertEqual(nomes, [("A Grande Viagem", "visto"), ("A Grande Viagem 2", "visto")], "o que ainda não saiu fica de fora")
        pg.click(".folha .cz-capa >> nth=0")
        pg.wait_for_selector(".folha [data-a=abrir-colecao]")
        pg.go_back()
        pg.wait_for_selector(".folha [data-a=col-todos]")
        pg.go_back()
        pg.wait_for_selector(".folha #add-q")
        self.assertEqual(pg.input_value("#add-q"), "grande viagem", "o Voltar volta janela por janela")
        pg.go_back()
        pg.wait_for_selector(".folha", state="detached")
        self.assertEqual(self.erros, [])

    def test_o_que_controlar(self):
        S.adicionar({"tipo": "filme", "tmdb": 101, "situacao": "quero"})
        S.adicionar({"tipo": "serie", "tmdb": 202, "situacao": "vendo"})
        pg = self.abrir()
        pg.click("#nav [data-v=mais]")
        pg.click("[data-a=ir-config]")
        pg.click("[data-a=aba][data-v=opcoes]")
        pg.click("[data-a=aj-tipo][data-k=filme]")
        pg.wait_for_selector("[data-a=aj-tipo][data-k=serie][disabled]")
        self.assertIn("Pelo menos um fica ligado.", pg.inner_text("#controlar"))
        self.assertFalse(S.ler()["ajustes"]["tipos"]["filme"])
        self.padrao(pg, "Opções")
        pg.click("#nav [data-v=buscar]")
        self.assertEqual(pg.locator("[data-a=f-tipo]").count(), 0, "com um tipo só, sem a escolha do tipo")
        self.assertNotIn("A Grande Viagem", pg.inner_text("#resultado"))
        pg.click("#nav [data-v=historico]")
        self.assertEqual(pg.locator("[data-a=hist]").count(), 0)
        pg.click("#nav .add")
        pg.wait_for_selector(".cartazes .cz")
        self.assertEqual(pg.locator("[data-a=add-tipo]").count(), 0)
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
