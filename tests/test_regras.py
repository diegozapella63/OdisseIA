"""regras.py: limpar o que chega, achar um título, criar, mudar, o próximo episódio e as categorias (as mesmas regras da
tela e do CorrerIA)."""
import unittest

from tests import apoio  # noqa: F401 (põe o app no caminho)
import regras as R
import tmdb as T

AGORA = "2026-11-24T10:00:00"


def serie(**extra):
    det = T.detalhes(dict(apoio.SERIES[202]), "serie")
    det.update(extra)
    return det


def filme(n=101):
    return T.detalhes(dict(apoio.FILMES[n]), "filme")


class TestRegras(unittest.TestCase):
    def dados(self):
        return R.limpar_dados({})

    def test_limpar_dados_tira_o_que_nao_vale(self):
        d = R.limpar_dados({"rev": "x", "titulos": [{"id": "t00000001", "tipo": "filme", "nome": "  Um  ", "quem": ["person.ana", "x"], "nota": 9,
                                                     "situacao": "vendo", "capa": "../x.jpg", "visto_em": "ontem", "onde": {"link": "http://x", "assinatura": ["A", "", 3]},
                                                     "categoria": "c000001"},
                                                    {"id": "t00000001", "tipo": "filme", "nome": "Repetido"}, {"id": "zz", "tipo": "filme", "nome": "x"},
                                                    {"id": "t00000002", "tipo": "disco", "nome": "x"}, {"id": "t00000003", "tipo": "serie", "nome": ""},
                                                    {"id": "t00000004", "tipo": "serie", "nome": "S", "temp": 3, "ep": 0, "situacao": "abandonado", "categoria": "c000001",
                                                     "temporadas": [{"n": 2, "episodios": 5}, {"n": 1, "episodios": 4}, {"n": 0, "episodios": 9}, "x"]}, 5],
                              "categorias": {"filme": [{"id": "c000001", "nome": " Família "}, {"id": "c000001", "nome": "Repetida"}, {"id": "x", "nome": "y"}, {"id": "c000002", "nome": ""}],
                                             "serie": "x"},
                              "ajustes": {"cor": "Azul!", "cor_dia": False, "correria": "sim"}})
        self.assertEqual([t["id"] for t in d["titulos"]], ["t00000001", "t00000004"])
        t = d["titulos"][0]
        self.assertEqual((t["nome"], t["quem"], t["situacao"], t["capa"], t["visto_em"], t["categoria"]), ("Um", ["person.ana"], "quero", "", None, "c000001"))
        self.assertNotIn("nota", t, "0.3.0: a nota saiu")
        self.assertEqual(t["onde"], {"assinatura": ["A", "3"], "gratis": [], "alugar": [], "comprar": [], "link": ""})
        s = d["titulos"][1]
        self.assertEqual(([x["n"] for x in s["temporadas"]], s["temp"], s["ep"], s["situacao"], s["categoria"]), ([1, 2], 0, 0, "quero", ""),
                         "o Vendo e o Abandonado viram Quero ver; a categoria de filme numa série sai")
        self.assertEqual(d["categorias"], {"filme": [{"id": "c000001", "nome": "Família", "cor": "vermelho"}], "serie": [], "jogo": [], "livro": []}, "sem cor, a primeira livre")
        self.assertEqual(d["ajustes"], {"cor": "lilas", "cor_dia": False, "quem": True, "correria": False, "tipos": {"filme": True, "serie": True, "jogo": True, "livro": False},
                                        "ia": True, "ia_conversa": "", "ia_fotos": "", "ia_pesquisa": "", "fala": "", "sensores": False})
        # 0.7.0: a IA de cada uso só aceita uma tarefa de IA; Usar IA começa ligado
        aj = R.limpar_dados({"ajustes": {"ia": False, "ia_conversa": "ai_task.gemini", "ia_fotos": "camera.x", "ia_pesquisa": 3}})["ajustes"]
        self.assertEqual((aj["ia"], aj["ia_conversa"], aj["ia_fotos"], aj["ia_pesquisa"]), (False, "ai_task.gemini", "", ""))
        self.assertEqual(R.limpar_dados({"ajustes": {"tipos": {"filme": False, "serie": False, "jogo": False}}})["ajustes"]["tipos"], {"filme": True, "serie": True, "jogo": True, "livro": False}, "nunca todos desligados")
        self.assertEqual(R.limpar_dados({"ajustes": {"tipos": {"filme": False, "serie": False}}})["ajustes"]["tipos"], {"filme": False, "serie": False, "jogo": True, "livro": False}, "os jogos de uma casa de antes começam ligados")
        self.assertEqual(R.limpar_dados({"ajustes": {"tipos": {"filme": False}}})["ajustes"]["tipos"], {"filme": False, "serie": True, "jogo": True, "livro": False})
        f = R.limpar_titulo({"id": "t00000009", "tipo": "filme", "nome": "F", "colecao": {"id": 7, "nome": " Saga ", "capa": "/s.jpg"}})
        self.assertEqual(f["colecao"], {"id": 7, "nome": "Saga", "capa": "/s.jpg"})
        self.assertIsNone(R.limpar_titulo({"id": "t00000009", "tipo": "filme", "nome": "F", "colecao": {"id": "x"}})["colecao"])
        self.assertEqual(d["rev"], 0)
        self.assertEqual(R.limpar_dados(None)["titulos"], [])

    def test_criar_e_achar(self):
        d = self.dados()
        t, novo = R.criar(d, serie(), "quero", ["person.ana"], AGORA)
        self.assertTrue(novo)
        self.assertRegex(t["id"], r"^t[0-9a-f]{8}$")
        self.assertEqual((t["situacao"], t["quem"], t["temp"], t["fim"], t["categoria"]), ("quero", ["person.ana"], 0, False, ""))
        self.assertEqual([s["n"] for s in t["temporadas"]], [1, 2], "a temporada 0 (especiais) fica de fora")
        self.assertEqual(t["onde"]["assinatura"], ["Cine Lumen"])
        self.assertEqual(R.limpar_titulo(t), t, "o que o app cria é o que ele guarda")
        de_novo, novo = R.criar(d, serie(), "quero", [], AGORA)
        self.assertFalse(novo)
        self.assertIs(de_novo, t)
        f, _ = R.criar(d, filme(), "quero", [], AGORA)
        self.assertEqual((f["duracao"], f["colecao"]["id"]), (132, 301))
        self.assertIs(R.achar(d, t["id"]), t)
        self.assertIs(R.achar(d, "mar de estrelas"), t)
        self.assertIs(R.achar(d, "SEA OF STARS"), t)
        self.assertIs(R.achar(d, "grande"), f)
        with self.assertRaisesRegex(R.ErroRegra, "Nenhum título"):
            R.achar(d, "nada disso")
        with self.assertRaisesRegex(R.ErroRegra, "Diga qual"):
            R.achar(d, "")
        R.criar(d, dict(filme(103), nome="Mar Aberto", original=""), "quero", [], AGORA)
        with self.assertRaisesRegex(R.ErroRegra, "Mais de um título"):
            R.achar(d, "mar")
        with self.assertRaisesRegex(R.ErroRegra, "tipo"):
            R.criar(d, {"tipo": "disco"}, "quero", [], AGORA)
        with self.assertRaisesRegex(R.ErroRegra, "situação"):
            R.criar(d, dict(serie(), tmdb=999), "vendo", [], AGORA)

    def test_mudar(self):
        d = self.dados()
        c = R.mudar_categorias(d, {"acao": "nova", "tipo": "serie", "nome": "Para ver a dois"})
        t, _ = R.criar(d, serie(), "quero", [], AGORA)
        R.mudar(t, {"temp": 1, "ep": 2}, None, AGORA)
        self.assertEqual((t["temp"], t["ep"], t["situacao"]), (1, 2, "quero"), "0.3.0: continua Quero ver")
        self.assertTrue(R.em_andamento(t))
        self.assertEqual(R.faltam(t), 3, "T1 E3, T2 E1 e T2 E2 já saíram")
        for campos, erro in (({"temp": 3, "ep": 1}, "não tem a temporada 3"), ({"temp": 1, "ep": 9}, "tem 3 episódios"), ({"temp": "1", "ep": 1}, "números"),
                             ({"categoria": "c999999"}, "Categoria desconhecida: valem Para ver a dois"), ({"situacao": "vendo"}, "situação"),
                             ({"quem": ["ana"]}, "person"), ({"quem": ["person.zeca"]}, "não está na casa"), ("x", "objeto")):
            with self.assertRaisesRegex(R.ErroRegra, erro):
                R.mudar(t, campos, {"person.ana"}, AGORA, d["categorias"]["serie"])
        R.mudar(t, {"categoria": c["id"], "notas": "boa", "quem": ["person.ana", "person.ana"]}, {"person.ana"}, AGORA, d["categorias"]["serie"])
        self.assertEqual((t["categoria"], t["notas"], t["quem"]), (c["id"], "boa", ["person.ana"]))
        self.assertEqual(R.nome_categoria(d, t), "Para ver a dois")
        R.mudar(t, {"categoria": ""}, None, AGORA)
        self.assertEqual(t["categoria"], "")
        R.mudar(t, {"situacao": "visto"}, None, AGORA)
        self.assertEqual((t["situacao"], t["visto_em"], t["temp"], t["ep"]), ("visto", "2026-11-24", 2, 2), "Visto vai até o último que saiu")
        self.assertFalse(R.em_andamento(t))
        R.mudar(t, {"situacao": "quero"}, None, AGORA)
        self.assertIsNone(t["visto_em"])
        R.mudar(t, {"temp": 0, "ep": 5}, None, AGORA)
        self.assertEqual((t["temp"], t["ep"]), (0, 0))
        f, _ = R.criar(d, filme(), "quero", [], AGORA)
        with self.assertRaisesRegex(R.ErroRegra, "só numa série"):
            R.mudar(f, {"temp": 1, "ep": 1}, None, AGORA)
        R.mudar(f, {"situacao": "visto"}, None, AGORA)
        self.assertEqual(f["visto_em"], "2026-11-24")

    def test_proximo_episodio(self):
        d = self.dados()
        t, _ = R.criar(d, serie(), "quero", [], AGORA)
        self.assertEqual(R.seguinte(t), (1, 1))
        R.proximo_ep(t, AGORA)
        self.assertEqual((t["temp"], t["ep"], t["situacao"]), (1, 1, "quero"))
        R.proximo_ep(t, AGORA)
        R.proximo_ep(t, AGORA)
        R.proximo_ep(t, AGORA)
        self.assertEqual((t["temp"], t["ep"]), (2, 1), "do fim da temporada para a seguinte")
        R.proximo_ep(t, AGORA)
        with self.assertRaisesRegex(R.ErroRegra, "todos os episódios que saíram.*27/11/2026"):
            R.proximo_ep(t, AGORA)
        self.assertEqual(R.faltam(t), 0)
        c, _ = R.criar(d, T.detalhes(dict(apoio.SERIES[204]), "serie"), "quero", [], AGORA)
        R.proximo_ep(c, AGORA)
        self.assertEqual(c["situacao"], "quero")
        R.proximo_ep(c, AGORA)
        self.assertEqual((c["situacao"], c["visto_em"]), ("visto", "2026-11-24"), "o último episódio de uma série que acabou: Visto")
        f, _ = R.criar(d, filme(), "quero", [], AGORA)
        with self.assertRaisesRegex(R.ErroRegra, "só numa série"):
            R.proximo_ep(f, AGORA)
        self.assertIsNone(R.faltam(f))
        sem = dict(c, temporadas=[], temp=0, ep=0)
        self.assertIsNone(R.seguinte(sem))
        fora = dict(c, temp=5, ep=1, temporadas=[{"n": 1, "episodios": 2}, {"n": 7, "episodios": 2}])
        self.assertEqual(R.seguinte(fora), (7, 1))
        self.assertIsNone(R.seguinte(dict(fora, temp=9)))
        self.assertTrue(R.ja_saiu(dict(c, ultimo=None), 9, 9))

    def test_categorias(self):
        d = self.dados()
        a = R.mudar_categorias(d, {"acao": "nova", "tipo": "filme", "nome": " Família "})
        self.assertRegex(a["id"], r"^c[0-9a-f]{6}$")
        b = R.mudar_categorias(d, {"acao": "nova", "tipo": "filme", "nome": "Clássicos"})
        f, _ = R.criar(d, filme(), "quero", [], AGORA)
        f["categoria"] = a["id"]
        for corpo, erro in (({"acao": "nova", "tipo": "disco", "nome": "x"}, "tipo"), ({"acao": "nova", "tipo": "filme", "nome": " "}, "Escreva"),
                            ({"acao": "nova", "tipo": "filme", "nome": "FAMÍLIA"}, "já existe"), ({"acao": "renomear", "id": b["id"], "nome": "familia"}, "já existe"),
                            ({"acao": "renomear", "id": b["id"], "nome": ""}, "Escreva"), ({"acao": "apagar", "id": "c000000"}, "não existe"),
                            ({"acao": "voar", "id": a["id"]}, "desconhecida")):
            with self.assertRaisesRegex(R.ErroRegra, erro):
                R.mudar_categorias(d, corpo)
        R.mudar_categorias(d, {"acao": "renomear", "id": a["id"], "nome": "Em família"})
        self.assertEqual(R.nome_categoria(d, f), "Em família")
        self.assertEqual(R.achar_categoria(d, "filme", "em familia"), a["id"])
        self.assertEqual(R.achar_categoria(d, "filme", ""), "")
        with self.assertRaisesRegex(R.ErroRegra, "Valem: Em família, Clássicos"):
            R.achar_categoria(d, "filme", "Terror")
        with self.assertRaisesRegex(R.ErroRegra, "Crie em Mais › Categorias"):
            R.achar_categoria(d, "serie", "Terror")
        R.mudar_categorias(d, {"acao": "apagar", "id": a["id"]})
        self.assertEqual((f["categoria"], [c["nome"] for c in d["categorias"]["filme"]]), ("", ["Clássicos"]), "apagar tira dos títulos")
        for i in range(R.MAX_CATEGORIAS - 1):
            R.mudar_categorias(d, {"acao": "nova", "tipo": "filme", "nome": f"C{i}"})
        with self.assertRaisesRegex(R.ErroRegra, "Até 40"):
            R.mudar_categorias(d, {"acao": "nova", "tipo": "filme", "nome": "Mais uma"})

    def test_data_br(self):
        self.assertEqual(R.data_br("2026-11-27"), "27/11/2026")
        self.assertEqual(R.data_br("logo"), "logo")
