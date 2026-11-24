"""tmdb.py com o TMDB de mentira: a chave nas duas formas, a busca, os detalhes em português, onde assistir no Brasil e as capas."""
import unittest
from unittest import mock

from tests import apoio
import tmdb as T


def cliente(chave=apoio.CHAVE):
    return T.TMDB(chave, f"http://127.0.0.1:{apoio.TMDB.porta}/3", f"http://127.0.0.1:{apoio.TMDB.porta}/t/p")


class TestTMDB(unittest.TestCase):
    def test_chave_nas_duas_formas(self):
        self.assertTrue(cliente().testar())
        self.assertEqual(apoio.TMDB.pedidos[-1][1]["api_key"], apoio.CHAVE)
        self.assertTrue(cliente(apoio.TOKEN).testar())
        self.assertEqual(apoio.TMDB.pedidos[-1][2], "Bearer " + apoio.TOKEN, "o token de leitura vai no cabeçalho")
        self.assertNotIn("api_key", apoio.TMDB.pedidos[-1][1])
        with self.assertRaisesRegex(T.ErroTMDB, "não aceitou a chave"):
            cliente("b" * 32).testar()
        with self.assertRaisesRegex(T.ErroTMDB, "Falta a chave"):
            cliente("").buscar("mar")

    def test_buscar(self):
        rs = cliente().buscar("mar")
        self.assertEqual([(r["tipo"], r["nome"]) for r in rs], [("serie", "Mar de Estrelas")])
        self.assertEqual(apoio.TMDB.pedidos[-1][1]["language"], "pt-BR")
        self.assertEqual([r["tipo"] for r in cliente().buscar("ana")], [], "pessoas ficam de fora")
        self.assertEqual([r["nome"] for r in cliente().buscar("a", "filme")], [])
        self.assertEqual([r["nome"] for r in cliente().buscar("farol", "filme")], ["Farol Distante"])
        self.assertEqual([p[0] for p in apoio.TMDB.pedidos[-2:]], ["/3/search/movie", "/3/search/collection"])
        self.assertEqual([r["tipo"] for r in cliente().buscar("casa", "serie")], ["serie"])

    def test_detalhes(self):
        f = cliente().detalhes("filme", 101)
        self.assertEqual((f["nome"], f["original"], f["ano"], f["duracao"], f["capa"]), ("A Grande Viagem", "The Long Trip", 2019, 132, "/viagem.jpg"))
        self.assertEqual(f["onde"], {"assinatura": ["Cine Lumen"], "gratis": [], "alugar": ["Loja Pipoca"], "comprar": [],
                                     "link": "https://www.themoviedb.org/movie/101/watch?locale=BR"}, "só o Brasil")
        s = cliente().detalhes("serie", 202)
        self.assertEqual((s["temporadas"], s["fim"]), ([{"n": 1, "episodios": 3}, {"n": 2, "episodios": 4}], False))
        self.assertEqual(s["proximo"], {"data": "2026-11-27", "temp": 2, "ep": 3, "nome": "O Farol"})
        c = cliente().detalhes("serie", 204)
        self.assertEqual((c["fim"], c["proximo"], c["capa"]), (True, None, ""))
        with self.assertRaisesRegex(T.ErroTMDB, "não achou"):
            cliente().detalhes("filme", 999)
        with self.assertRaisesRegex(T.ErroTMDB, "número"):
            cliente().detalhes("filme", "x")
        self.assertIsNone(T._ep({"season_number": "x"}))

    def test_erros_e_capas(self):
        self.assertTrue(cliente().imagem("/viagem.jpg").startswith(b"\xff\xd8\xff"))
        self.assertIsNone(cliente().imagem("/nao-existe.jpg"))
        self.assertIsNone(cliente().imagem("../x.jpg"))
        self.assertIsNone(cliente().imagem("/viagem.jpg", "original"))
        fora = T.TMDB(apoio.CHAVE, "http://127.0.0.1:9/3", "http://127.0.0.1:9", timeout=2)
        with self.assertRaisesRegex(T.ErroTMDB, "internet"):
            fora.testar()
        self.assertIsNone(fora.imagem("/viagem.jpg"))


class TestTMDBBordas(unittest.TestCase):
    def test_respostas_estranhas(self):
        with self.assertRaisesRegex(T.ErroTMDB, "não aceitou a chave"):
            cliente(apoio.CHAVE_RECUSADA).testar()
        with self.assertRaisesRegex(T.ErroTMDB, "pediu um tempo"):
            cliente().detalhes("filme", 429)
        with self.assertRaisesRegex(T.ErroTMDB, r"erro \(500\)"):
            cliente().detalhes("filme", 500)
        self.assertEqual([(r["nome"], r["capa"]) for r in cliente().buscar("estranho")], [("Estranho", "")], "o que não é título sai; a capa estranha também")
        self.assertIsNone(cliente().imagem("/texto.jpg"), "só JPG e PNG")
        self.assertEqual(T.onde({"watch/providers": {"results": {"BR": "x"}}})["assinatura"], [])
        self.assertIsNone(T.detalhes({"runtime": "x"}, "filme")["duracao"])
        s = T.detalhes({"seasons": [{"season_number": "x"}, None, {"season_number": 1, "episode_count": 0}], "next_episode_to_air": {"air_date": "logo", "season_number": 1, "episode_number": 1}}, "serie")
        self.assertEqual((s["temporadas"], s["proximo"]), ([], None))


class TestColecoes(unittest.TestCase):
    def test_colecoes(self):
        rs = cliente().buscar("grande viagem")
        self.assertEqual([(r["tipo"], r["nome"]) for r in rs][:2], [("colecao", "Coleção A Grande Viagem"), ("filme", "A Grande Viagem")], "a coleção vem na frente")
        self.assertEqual([r["tipo"] for r in cliente().buscar("grande viagem", "serie")], [], "numa série, sem coleções")
        self.assertEqual([r["nome"] for r in cliente().buscar("grande", "colecao")], ["Coleção A Grande Viagem"])
        c = cliente().colecao(301)
        self.assertEqual([(f["nome"], f["data"]) for f in c["filmes"]], [("A Grande Viagem", "2019-05-10"), ("A Grande Viagem 2", "2022-07-01"), ("A Grande Viagem 3", "2027-06-01")])
        self.assertEqual((c["nome"], c["capa"]), ("Coleção A Grande Viagem", "/viagem.jpg"))
        self.assertEqual(cliente().detalhes("filme", 101)["colecao"], {"id": 301, "nome": "Coleção A Grande Viagem", "capa": "/viagem.jpg"})
        self.assertIsNone(cliente().detalhes("filme", 103)["colecao"])
        with self.assertRaisesRegex(T.ErroTMDB, "número"):
            cliente().colecao("x")
        with self.assertRaisesRegex(T.ErroTMDB, "não achou"):
            cliente().colecao(999)
        fora = T.TMDB(apoio.CHAVE, f"http://127.0.0.1:{apoio.TMDB.porta}/3", "")
        with mock.patch.object(fora, "colecoes", side_effect=T.ErroTMDB("x")):
            self.assertEqual([r["tipo"] for r in fora.buscar("grande viagem")], ["filme", "filme", "filme"], "sem as coleções, os filmes")
