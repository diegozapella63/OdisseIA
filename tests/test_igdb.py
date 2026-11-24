"""O igdb.py contra o IGDB de mentira (jogos inventados): o acesso pela Twitch, a busca, as listas, as coleções, os
detalhes, as capas e os erros, sempre em português."""
import time
import unittest
from unittest import mock

from tests import apoio
from tests.apoio import S

G = S.G


def cliente(cid=apoio.IGDB_ID, seg=apoio.IGDB_SEGREDO, **kw):
    return G.IGDB(cid, seg, S.IGDB_API, S.IGDB_TOKEN, S.IGDB_IMG, **kw)


class TestIGDB(unittest.TestCase):
    def setUp(self):
        apoio.limpar()

    def test_acesso_pela_twitch(self):
        c = cliente()
        self.assertTrue(c.testar())
        n = apoio.TMDB.n_token
        c.buscar("torre")
        self.assertEqual(apoio.TMDB.n_token, n, "o acesso fica guardado (um para o app todo)")
        apoio.TMDB.tokens.clear()  # o acesso venceu: um novo, uma vez
        self.assertTrue(c.buscar("ilha"))
        self.assertEqual(apoio.TMDB.n_token, n + 1)
        with self.assertRaisesRegex(G.ErroIGDB, "não aceitou o Client ID"):
            cliente(seg="errado0000000").testar()
        with self.assertRaisesRegex(G.ErroIGDB, "Falta a conta do IGDB"):
            cliente("", "").buscar("torre")

    def test_acesso_que_vence_de_novo(self):
        c = cliente()
        c.testar()
        with mock.patch.object(G.IGDB, "_token", return_value="velho"):
            with self.assertRaisesRegex(G.ErroIGDB, "não aceitou o acesso"):
                c.buscar("torre")

    def test_respostas_estranhas_da_twitch(self):
        c = cliente()
        for corpo, erro in ((b'{"x": 1}', "não mandou o acesso"), (b"[]", "não mandou o acesso")):
            with mock.patch("urllib.request.urlopen") as u:
                u.return_value.__enter__.return_value.read.return_value = corpo
                with self.assertRaisesRegex(G.ErroIGDB, erro):
                    c._token(novo=True)
        with mock.patch("urllib.request.urlopen") as u:
            u.return_value.__enter__.return_value.read.return_value = b'{"access_token": "abc", "expires_in": "nada"}'
            self.assertEqual(c._token(novo=True), "abc")
        self.assertLess(G._TOKENS[(c.cliente, c.segredo, c.token_url)][1], time.time() + 3700, "sem a validade, uma hora")
        import urllib.error
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError("u", 500, "x", {}, None)):
            with self.assertRaisesRegex(G.ErroIGDB, r"Twitch respondeu com erro \(500\)"):
                c._token(novo=True)
        with mock.patch("urllib.request.urlopen", side_effect=OSError("sem rede")):
            with self.assertRaisesRegex(G.ErroIGDB, "falar com a Twitch"):
                c._token(novo=True)

    def test_erros_do_igdb(self):
        c = cliente()
        c.testar()
        for st, erro in ((429, "pediu um tempo"), (500, r"erro \(500\)")):
            apoio.TMDB.falha_igdb = st
            with self.assertRaisesRegex(G.ErroIGDB, erro):
                c.buscar("torre")
        apoio.TMDB.falha_igdb = 0
        with mock.patch("urllib.request.urlopen", side_effect=OSError("sem rede")):
            with self.assertRaisesRegex(G.ErroIGDB, "falar com o IGDB"):
                c._pedir("games", "fields name;")
        with mock.patch("urllib.request.urlopen") as u:
            u.return_value.__enter__.return_value.read.return_value = b'{"nao": "lista"}'
            self.assertEqual(c._pedir("games", "fields name;"), [])

    def test_busca(self):
        c = cliente()
        rs = c.buscar("torre")
        self.assertEqual([(r["tipo"], r["nome"]) for r in rs], [("colecao_jogos", "Saga da Torre"), ("jogo", "Torre do Relógio"), ("jogo", "Torre do Relógio 2"),
                                                                 ("jogo", "Torre do Relógio 3"), ("jogo", "Torre do Relógio Remasterizado")],
                         "a coleção na frente; sem DLC, pacote nem edição")
        self.assertEqual(rs[0]["capa"], "co1torre", "a capa da coleção é a do jogo em que ela apareceu")
        self.assertEqual(rs[1]["colecao"], {"id": 501, "nome": "Saga da Torre", "capa": "co1torre"})
        self.assertEqual((rs[1]["ano"], rs[1]["data"]), (2021, "2021-06-15"))
        self.assertEqual(c.buscar("x"), [], "pelo menos duas letras")
        self.assertEqual([r["nome"] for r in c.buscar('ilha "dos')], [], "as aspas saem da consulta")
        self.assertEqual([r["nome"] for r in c.buscar("ilha")], ["Ilha dos Ventos"])

    def test_listas(self):
        c = cliente()
        rs, mais = c.lista("alta")
        self.assertEqual([r["nome"] for r in rs], ["Ilha dos Ventos", "Torre do Relógio", "Torre do Relógio 2"], "na ordem da popularidade, sem a trilha (DLC)")
        self.assertFalse(mais)
        self.assertEqual([r["nome"] for r in c.lista("populares", "x")[0]], ["Torre do Relógio"])
        self.assertEqual([r["nome"] for r in c.lista("avaliados", 2)[0]], [], "a página 2 está vazia")
        self.assertEqual([r["nome"] for r in c.lista("avaliados")[0]], ["Ilha dos Ventos", "Torre do Relógio"])
        self.assertEqual([r["nome"] for r in c.lista("estreias")[0]], ["Ilha dos Ventos"])
        for nome in ("colecoes", "nada"):
            with self.assertRaisesRegex(G.ErroIGDB, "Lista desconhecida"):
                c.lista(nome)

    def test_colecao_detalhes_e_capas(self):
        c = cliente()
        col = c.colecao("501")
        self.assertEqual(col["nome"], "Saga da Torre")
        self.assertEqual([(j["nome"], j["data"]) for j in col["itens"]], [("Torre do Relógio", "2021-06-15"), ("Torre do Relógio 2", "2024-03-01"), ("Torre do Relógio 3", "2027-03-01")],
                         "só os jogos de verdade (sem a remasterização nem o pacote), na ordem em que saíram")
        with self.assertRaisesRegex(G.ErroIGDB, "não tem o número"):
            c.colecao("x")
        with self.assertRaisesRegex(G.ErroIGDB, "não achou essa coleção"):
            c.colecao(999)
        d = c.detalhes(701)
        self.assertEqual((d["plataformas"], d["generos"], d["link"]), (["PC", "PlayStation 5"], ["Puzzle", "Adventure"], "https://www.igdb.com/games/torre-do-relogio"))
        self.assertEqual(c.detalhes(705)["plataformas"], ["Nintendo Switch", "Navegador"])
        self.assertEqual(c.detalhes(705)["link"], "", "um endereço que não é do IGDB fica de fora")
        with self.assertRaisesRegex(G.ErroIGDB, "não tem o número"):
            c.detalhes("x")
        with self.assertRaisesRegex(G.ErroIGDB, "não achou esse jogo"):
            c.detalhes(999)
        self.assertEqual(sorted(c.varios([701, 702, 999])), [701, 702])
        self.assertEqual(c.por_ids([]), [])
        self.assertTrue(c.imagem("co1torre"))
        for capa, tam in (("co4torre", "t_cover_big"), ("nada", "t_cover_big"), ("../x", "t_cover_big"), ("co1torre", "t_1080p"), ("", "t_cover_big")):
            self.assertIsNone(c.imagem(capa, tam), capa)

    def test_formatos(self):
        self.assertEqual(G._tipo({"game_type": {"id": 8}}), 8)
        self.assertEqual(G._tipo({"category": 2}), 2)
        self.assertEqual(G._tipo({"game_type": True}), 0)
        self.assertEqual(G._data({"first_release_date": "x"}), "")
        self.assertFalse(G.valido({"id": 1, "name": " "}, {0}))
        self.assertEqual(G.plataformas({"platforms": ["x", {"name": "Mac"}, {"name": ""}]}), ["Mac"])
        self.assertEqual(G.resumo({"id": 3, "name": "Sem nada", "cover": {"image_id": "ruim!"}, "collections": [{"id": 1}]})["capa"], "")


if __name__ == "__main__":
    unittest.main()
