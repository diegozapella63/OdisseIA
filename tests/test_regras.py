"""regras.py: limpar o que chega, achar um título, criar, mudar e o próximo episódio (as mesmas regras da tela e do CorrerIA)."""
import unittest

from tests import apoio  # noqa: F401 (põe o app no caminho)
import regras as R
import tmdb as T

AGORA = "2026-11-24T10:00:00"


def serie(**extra):
    det = T.detalhes(dict(apoio.SERIES[202]), "serie")
    det.update(extra)
    return det


class TestRegras(unittest.TestCase):
    def dados(self):
        return R.limpar_dados({})

    def test_limpar_dados_tira_o_que_nao_vale(self):
        d = R.limpar_dados({"rev": "x", "titulos": [{"id": "t00000001", "tipo": "filme", "nome": "  Um  ", "quem": ["person.ana", "x"], "nota": 9,
                                                     "situacao": "??", "capa": "../x.jpg", "visto_em": "ontem", "onde": {"link": "http://x", "assinatura": ["A", "", 3]}},
                                                    {"id": "t00000001", "tipo": "filme", "nome": "Repetido"}, {"id": "zz", "tipo": "filme", "nome": "x"},
                                                    {"id": "t00000002", "tipo": "livro", "nome": "x"}, {"id": "t00000003", "tipo": "serie", "nome": ""},
                                                    {"id": "t00000004", "tipo": "serie", "nome": "S", "temp": 3, "ep": 0,
                                                     "temporadas": [{"n": 2, "episodios": 5}, {"n": 1, "episodios": 4}, {"n": 0, "episodios": 9}, "x"]}, 5],
                              "ajustes": {"cor": "Azul!", "cor_dia": False, "correria": "sim"}})
        self.assertEqual([t["id"] for t in d["titulos"]], ["t00000001", "t00000004"])
        t = d["titulos"][0]
        self.assertEqual((t["nome"], t["quem"], t["nota"], t["situacao"], t["capa"], t["visto_em"]), ("Um", ["person.ana"], 5, "quero", "", None))
        self.assertEqual(t["onde"], {"assinatura": ["A", "3"], "gratis": [], "alugar": [], "comprar": [], "link": ""})
        s = d["titulos"][1]
        self.assertEqual(([x["n"] for x in s["temporadas"]], s["temp"], s["ep"]), ([1, 2], 0, 0))
        self.assertEqual(d["ajustes"], {"cor": "lilas", "cor_dia": False, "quem": True, "correria": False, "tipos": {"filme": True, "serie": True}})
        self.assertEqual(R.limpar_dados({"ajustes": {"tipos": {"filme": False, "serie": False}}})["ajustes"]["tipos"], {"filme": True, "serie": True}, "nunca os dois desligados")
        self.assertEqual(R.limpar_dados({"ajustes": {"tipos": {"filme": False}}})["ajustes"]["tipos"], {"filme": False, "serie": True})
        f = R.limpar_titulo({"id": "t00000009", "tipo": "filme", "nome": "F", "colecao": {"id": 7, "nome": " Saga "}})
        self.assertEqual(f["colecao"], {"id": 7, "nome": "Saga"})
        self.assertIsNone(R.limpar_titulo({"id": "t00000009", "tipo": "filme", "nome": "F", "colecao": {"id": "x"}})["colecao"])
        self.assertEqual(d["rev"], 0)
        self.assertEqual(R.limpar_dados(None)["titulos"], [])

    def test_criar_e_achar(self):
        d = self.dados()
        t, novo = R.criar(d, serie(), "vendo", ["person.ana"], AGORA)
        self.assertTrue(novo)
        self.assertRegex(t["id"], r"^t[0-9a-f]{8}$")
        self.assertEqual((t["situacao"], t["quem"], t["temp"], t["fim"]), ("vendo", ["person.ana"], 0, False))
        self.assertEqual([s["n"] for s in t["temporadas"]], [1, 2], "a temporada 0 (especiais) fica de fora")
        self.assertEqual(t["onde"]["assinatura"], ["Cine Lumen"])
        self.assertEqual(R.limpar_titulo(t), t, "o que o app cria é o que ele guarda")
        de_novo, novo = R.criar(d, serie(), "quero", [], AGORA)
        self.assertFalse(novo)
        self.assertIs(de_novo, t)
        f, _ = R.criar(d, T.detalhes(dict(apoio.FILMES[101]), "filme"), "quero", [], AGORA)
        self.assertEqual(f["duracao"], 132)
        self.assertIs(R.achar(d, t["id"]), t)
        self.assertIs(R.achar(d, "mar de estrelas"), t)
        self.assertIs(R.achar(d, "SEA OF STARS"), t)
        self.assertIs(R.achar(d, "grande"), f)
        with self.assertRaisesRegex(R.ErroRegra, "Nenhum título"):
            R.achar(d, "nada disso")
        with self.assertRaisesRegex(R.ErroRegra, "Diga qual"):
            R.achar(d, "")
        R.criar(d, dict(T.detalhes(dict(apoio.FILMES[103]), "filme"), nome="Mar Aberto", original=""), "quero", [], AGORA)
        with self.assertRaisesRegex(R.ErroRegra, "Mais de um título"):
            R.achar(d, "mar")
        with self.assertRaisesRegex(R.ErroRegra, "tipo"):
            R.criar(d, {"tipo": "livro"}, "quero", [], AGORA)
        with self.assertRaisesRegex(R.ErroRegra, "situação"):
            R.criar(d, dict(serie(), tmdb=999), "talvez", [], AGORA)

    def test_mudar(self):
        d = self.dados()
        t, _ = R.criar(d, serie(), "quero", [], AGORA)
        R.mudar(t, {"temp": 1, "ep": 2}, None, AGORA)
        self.assertEqual((t["temp"], t["ep"], t["situacao"]), (1, 2, "vendo"), "marcar um episódio começa a série")
        self.assertEqual(R.faltam(t), 3, "T1 E3, T2 E1 e T2 E2 já saíram")
        for campos, erro in (({"temp": 3, "ep": 1}, "não tem a temporada 3"), ({"temp": 1, "ep": 9}, "tem 3 episódios"), ({"temp": "1", "ep": 1}, "números"),
                             ({"nota": 6}, "1 a 5"), ({"nota": True}, "1 a 5"), ({"situacao": "talvez"}, "situação"), ({"quem": ["ana"]}, "person"),
                             ({"quem": ["person.zeca"]}, "não está na casa"), ("x", "objeto")):
            with self.assertRaisesRegex(R.ErroRegra, erro):
                R.mudar(t, campos, {"person.ana"}, AGORA)
        R.mudar(t, {"nota": 4, "notas": "boa", "quem": ["person.ana", "person.ana"]}, {"person.ana"}, AGORA)
        self.assertEqual((t["nota"], t["notas"], t["quem"]), (4, "boa", ["person.ana"]))
        R.mudar(t, {"situacao": "visto"}, None, AGORA)
        self.assertEqual((t["situacao"], t["visto_em"], t["temp"], t["ep"]), ("visto", "2026-11-24", 2, 2), "Visto vai até o último que saiu")
        R.mudar(t, {"situacao": "vendo"}, None, AGORA)
        self.assertIsNone(t["visto_em"])
        R.mudar(t, {"temp": 0, "ep": 5}, None, AGORA)
        self.assertEqual((t["temp"], t["ep"]), (0, 0))
        f, _ = R.criar(d, T.detalhes(dict(apoio.FILMES[101]), "filme"), "quero", [], AGORA)
        with self.assertRaisesRegex(R.ErroRegra, "só numa série"):
            R.mudar(f, {"temp": 1, "ep": 1}, None, AGORA)
        R.mudar(f, {"situacao": "visto"}, None, AGORA)
        self.assertEqual(f["visto_em"], "2026-11-24")

    def test_proximo_episodio(self):
        d = self.dados()
        t, _ = R.criar(d, serie(), "quero", [], AGORA)
        self.assertEqual(R.seguinte(t), (1, 1))
        R.proximo_ep(t, AGORA)
        self.assertEqual((t["temp"], t["ep"], t["situacao"]), (1, 1, "vendo"))
        R.proximo_ep(t, AGORA)
        R.proximo_ep(t, AGORA)
        R.proximo_ep(t, AGORA)
        self.assertEqual((t["temp"], t["ep"]), (2, 1), "do fim da temporada para a seguinte")
        R.proximo_ep(t, AGORA)
        with self.assertRaisesRegex(R.ErroRegra, "todos os episódios que saíram.*27/11/2026"):
            R.proximo_ep(t, AGORA)
        self.assertEqual(R.faltam(t), 0)
        acabou = T.detalhes(dict(apoio.SERIES[204]), "serie")
        c, _ = R.criar(d, acabou, "abandonado", [], AGORA)
        R.proximo_ep(c, AGORA)
        self.assertEqual(c["situacao"], "vendo")
        R.proximo_ep(c, AGORA)
        self.assertEqual((c["situacao"], c["visto_em"]), ("visto", "2026-11-24"), "o último episódio de uma série que acabou: Visto")
        f, _ = R.criar(d, T.detalhes(dict(apoio.FILMES[101]), "filme"), "quero", [], AGORA)
        with self.assertRaisesRegex(R.ErroRegra, "só numa série"):
            R.proximo_ep(f, AGORA)
        self.assertIsNone(R.faltam(f))
        sem = dict(c, temporadas=[], temp=0, ep=0)
        self.assertIsNone(R.seguinte(sem))
        fora = dict(c, temp=5, ep=1, temporadas=[{"n": 1, "episodios": 2}, {"n": 7, "episodios": 2}])
        self.assertEqual(R.seguinte(fora), (7, 1))
        self.assertIsNone(R.seguinte(dict(fora, temp=9)))
        self.assertTrue(R.ja_saiu(dict(c, ultimo=None), 9, 9))

    def test_data_br(self):
        self.assertEqual(R.data_br("2026-11-27"), "27/11/2026")
        self.assertEqual(R.data_br("logo"), "logo")
