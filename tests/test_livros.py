"""0.16.0: os livros. O livros.py contra a Open Library de mentira (livros, autores e ISBN inventados), o tipo livro nas
regras, no servidor (a busca pelo nome, pelo autor e pelo ISBN, adicionar, a capa, atualizar, o laço) e nas ferramentas."""
import os
import unittest
from datetime import datetime
from unittest import mock

from tests import apoio
from tests.apoio import S, pedir

L, R = S.L, S.R


def cliente(**kw):
    return L.Livros(S.OL_API, S.OL_IMG, intervalo=0, **kw)


class TestOpenLibrary(unittest.TestCase):
    def setUp(self):
        apoio.limpar()

    def test_isbn_e_numero(self):
        self.assertEqual(L.isbn_de("978-65-00000-01-7"), "9786500000017")
        self.assertEqual(L.isbn_de("650000001x"), "650000001X")
        self.assertEqual((L.isbn_de("farol"), L.isbn_de("12345"), L.isbn_de(None)), ("", "", ""))
        self.assertEqual((L.numero("/works/OL901W"), L.numero("/authors/OL1A"), L.numero(None)), (901, 0, 0))

    def test_buscar_pelo_nome_pelo_autor_e_pelo_isbn(self):
        c = cliente()
        r = c.buscar("farol das")
        self.assertEqual([(x["ol"], x["nome"], x["autores"], x["ano"], x["capa"], x["paginas"], x["isbn"]) for x in r],
                         [(901, "O Farol das Marés", ["Ana Autora"], 2001, "5001", 320, "9786500000017")])
        self.assertEqual({x["ol"] for x in c.buscar("ana autora")}, {901, 902})
        self.assertEqual([x["ol"] for x in c.buscar("978-65-00000-02-4")], [902], "o número do código de barras")
        pedido = next(p for p in reversed(apoio.TMDB.pedidos) if p[0] == "/ol/search.json")
        self.assertEqual(pedido[1]["q"], "isbn:9786500000024")
        self.assertIn("OdisseIA", apoio.TMDB.ua_ol, "o app se identifica, como a Open Library pede")
        self.assertNotIn("@", apoio.TMDB.ua_ol, "sem e-mail de ninguém")
        self.assertEqual(c.buscar("  "), [])
        self.assertEqual(c.buscar("estranho"), [], "o que não é uma obra fica de fora")

    def test_o_nome_da_edicao_em_portugues(self):
        r = cliente().buscar("glass")[0]
        self.assertEqual((r["nome"], r["original"]), ("O Farol de Vidro", "The Glass Lighthouse"))
        sem = L.do_doc({"key": "/works/OL5W", "title": "Só o nome", "first_publish_year": "x", "cover_i": True, "isbn": "x", "editions": {"docs": "x"}})
        self.assertEqual((sem["nome"], sem["original"], sem["ano"], sem["capa"], sem["isbn"], sem["autores"]), ("Só o nome", "", None, "", "", []))
        self.assertIsNone(L.do_doc({"key": "/works/OL5W", "title": " "}))
        self.assertIsNone(L.do_doc("x"))

    def test_detalhes_com_a_sinopse(self):
        c = cliente()
        d = c.detalhes(901)
        self.assertEqual((d["nome"], d["sinopse"], d["link"]), ("O Farol das Marés", "Uma faroleira e o mar que não devolve nada.", "https://openlibrary.org/works/OL901W"))
        self.assertEqual(c.detalhes(902)["sinopse"], "Um mistério numa torre.")
        self.assertEqual(c.detalhes(903)["sinopse"], "")
        for n in (0, True, "901"):
            with self.assertRaisesRegex(L.ErroLivros, "não veio da Open Library"):
                c.detalhes(n)
        with self.assertRaisesRegex(L.ErroLivros, "não tem esse livro"):
            c.detalhes(999)
        # a página da obra que falha não derruba o resto
        with mock.patch.dict(apoio.SINOPSES_LIVROS, clear=True):
            self.assertEqual(c.detalhes(901)["sinopse"], "")

    def test_erros_em_portugues(self):
        c = cliente()
        for cod, txt in ((429, "esperar um pouco"), (403, "esperar um pouco"), (500, "respondeu com erro \\(500\\)"), (404, "não tem esse livro")):
            apoio.TMDB.falha_ol = cod
            with self.assertRaisesRegex(L.ErroLivros, txt):
                c.buscar("farol")
        apoio.TMDB.falha_ol = 0
        with self.assertRaisesRegex(L.ErroLivros, "Sem resposta"):
            L.Livros("http://127.0.0.1:9", S.OL_IMG, timeout=1, intervalo=0).buscar("farol")

    def test_capas(self):
        c = cliente()
        self.assertTrue(c.imagem("5001").startswith(b"\xff\xd8"))
        self.assertIsNone(c.imagem("5999"))
        self.assertIsNone(c.imagem("../x"))
        self.assertIsNone(c.imagem("5001", "w185"))
        self.assertIsNone(L.Livros(S.OL_API, "http://127.0.0.1:9", timeout=1).imagem("5001"))

    def test_um_pedido_de_cada_vez_com_intervalo(self):
        c = L.Livros(S.OL_API, S.OL_IMG, intervalo=0.2)
        with mock.patch.object(L.time, "sleep") as dorme:
            c.buscar("farol")
            c.buscar("torre")
        self.assertTrue(dorme.called, "o segundo pedido espera o intervalo")
        self.assertLessEqual(dorme.call_args[0][0], 0.2)


class TestLivrosNaCasa(unittest.TestCase):
    def setUp(self):
        apoio.limpar()
        apoio.fixar_hoje(self)
        self.base = apoio.Servidor.subir()

    def ligar(self):
        st, r = pedir(self.base, "POST", "/api/ajustes", {"tipos": {"livro": True}})
        self.assertEqual((st, r["ajustes"]["tipos"]["livro"]), (200, True))

    def test_comeca_desligado(self):
        self.assertEqual(S.ler()["ajustes"]["tipos"], {"filme": True, "serie": True, "jogo": True, "livro": False})
        self.assertEqual(R.limpar_dados({"ajustes": {"tipos": {"filme": False, "serie": False, "jogo": False}}})["ajustes"]["tipos"],
                         {"filme": True, "serie": True, "jogo": True, "livro": False}, "nenhum ligado: os de sempre")
        st, r = pedir(self.base, "POST", "/api/titulo", {"acao": "adicionar", "tipo": "livro", "ol": 901})
        self.assertEqual(st, 400)
        self.assertIn("desligados", r["erro"])

    def test_buscar_adicionar_e_ver(self):
        self.ligar()
        st, r = pedir(self.base, "GET", "/api/busca?q=farol%20das&tipo=livro")
        self.assertEqual((st, [(x["tipo"], x["ol"], x["ja"]) for x in r["resultados"]]), (200, [("livro", 901, None)]))
        # o ISBN, com os outros tipos ligados e sem conta nenhuma: só a Open Library responde
        st, r = pedir(self.base, "GET", "/api/busca?q=9786500000017&tipo=")
        self.assertEqual((st, [x["ol"] for x in r["resultados"]]), (200, [901]))
        st, cap = pedir(self.base, "GET", "/api/img/ol_M/5001.jpg")
        self.assertEqual((st, cap[:2]), (200, b"\xff\xd8"))
        self.assertEqual(pedir(self.base, "GET", "/api/img/ol_M/5999.jpg")[0], 404)
        st, r = pedir(self.base, "POST", "/api/titulo", {"acao": "adicionar", "tipo": "livro", "ol": 901, "situacao": "quero"})
        t = r["titulo"]
        self.assertEqual((st, r["novo"], t["tipo"], t["ol"], t["nome"], t["autores"], t["paginas"], t["isbn"], t["capa_ol"], t["ano"]),
                         (200, True, "livro", 901, "O Farol das Marés", ["Ana Autora"], 320, "9786500000017", "5001", 2001))
        self.assertEqual(t["sinopse"], "Uma faroleira e o mar que não devolve nada.")
        self.assertTrue(os.path.exists(S.caminho_capa(t["capa"])), "a capa fica guardada")
        for k in ("onde", "tmdb_em", "capa_tmdb"):
            self.assertNotIn(k, t)
        self.assertIsNone(t["tmdb"])
        st, r = pedir(self.base, "POST", "/api/titulo", {"acao": "adicionar", "tipo": "livro", "ol": 901})
        self.assertEqual((r["novo"], r["titulo"]["id"]), (False, t["id"]), "o mesmo livro não entra duas vezes")
        self.assertEqual(pedir(self.base, "GET", "/api/busca?q=farol%20das&tipo=livro")[1]["resultados"][0]["ja"], t["id"])
        self.assertEqual(pedir(self.base, "POST", "/api/titulo", {"acao": "adicionar", "tipo": "livro", "ol": "901"})[0], 400)
        # Lido, a categoria dos livros e o que o arquivo guarda
        st, c = pedir(self.base, "POST", "/api/categorias", {"acao": "nova", "tipo": "livro", "nome": "Para ler nas férias"})
        self.assertEqual(st, 200)
        cat = S.ler()["categorias"]["livro"][0]
        st, r = pedir(self.base, "POST", "/api/titulo", {"acao": "mudar", "id": t["id"], "campos": {"situacao": "visto", "categoria": cat["id"]}})
        self.assertEqual((st, r["titulo"]["situacao"], r["titulo"]["categoria"]), (200, "visto", cat["id"]))
        self.assertEqual(R.nome_sit("livro", "visto"), "Lido")
        self.assertEqual(R.nome_sit("livro", "quero"), "Quero ler")
        limpo = R.limpar_titulo(dict(S.ler()["titulos"][0], isbn="x", capa_ol="../x", link="http://x", paginas="muitas"))
        self.assertEqual((limpo["isbn"], limpo["capa_ol"], limpo["link"], limpo["paginas"]), ("", "", "", None))

    def test_livro_sem_capa_e_atualizar(self):
        self.ligar()
        t = pedir(self.base, "POST", "/api/titulo", {"acao": "adicionar", "tipo": "livro", "ol": 902, "situacao": "visto"})[1]["titulo"]
        self.assertEqual((t["capa"], t["autores"], t["situacao"]), ("", ["Beto Escritor", "Ana Autora"], "visto"))
        S.DETALHES.clear()
        with mock.patch.dict(apoio.LIVROS[902], {"cover_i": 5003, "number_of_pages_median": 180}):
            st, r = pedir(self.base, "POST", "/api/titulo", {"acao": "atualizar", "id": t["id"]})
        self.assertEqual((st, r["titulo"]["capa_ol"], r["titulo"]["paginas"], bool(r["titulo"]["capa"])), (200, "5003", 180, True))
        self.assertEqual(r["titulo"]["ol_em"], apoio.HOJE)
        # um livro que não veio da Open Library não tem o que atualizar
        d = S.ler()
        d["titulos"][0]["ol"] = None
        S.salvar(d)
        st, r = pedir(self.base, "POST", "/api/titulo", {"acao": "atualizar", "id": t["id"]})
        self.assertEqual((st, r["erro"]), (400, "Esse título não veio da Open Library."))

    def test_o_laco_olha_os_livros_de_mes_em_mes(self):
        agora = datetime(2026, 11, 24, 10)
        t = {"tipo": "livro", "ol": 901, "situacao": "quero", "ol_em": "2026-11-10T10:00:00"}
        self.assertFalse(S.precisa_atualizar(t, agora))
        self.assertTrue(S.precisa_atualizar(dict(t, ol_em="2026-10-20T10:00:00"), agora))
        self.assertFalse(S.precisa_atualizar(dict(t, ol=None), agora))
        self.ligar()
        pedir(self.base, "POST", "/api/titulo", {"acao": "adicionar", "tipo": "livro", "ol": 901})
        d = S.ler()
        d["titulos"][0]["ol_em"] = "2026-01-01T00:00:00"
        S.salvar(d)
        S.DETALHES.clear()
        with mock.patch.object(S.time, "sleep"):
            S.uma_volta(agora)
        self.assertEqual(S.ler()["titulos"][0]["ol_em"], apoio.HOJE)
        # a Open Library pedindo para esperar para o laço ali
        d = S.ler()
        d["titulos"][0]["ol_em"] = "2026-01-01T00:00:00"
        S.salvar(d)
        apoio.TMDB.falha_ol = 429
        with mock.patch.object(S.time, "sleep"), mock.patch.object(S, "log") as log:
            S.uma_volta(agora)
        self.assertIn("esperar", str(log.call_args[0][2]))

    def test_sem_listas_prontas(self):
        self.ligar()
        st, r = pedir(self.base, "GET", "/api/lista?nome=alta&tipo=livro")
        self.assertEqual((st, r), (200, {"resultados": [], "mais": False}))
        self.assertEqual(S.fontes("livro"), (False, False, True))
        self.assertEqual(S.fontes("livro", livros=False), (False, False, False))
        self.assertEqual(S.fontes(""), (False, False, True), "sem as contas, sobram os livros")
        pedir(self.base, "POST", "/api/ajustes", {"tipos": {"livro": False}})
        self.assertEqual(S.fontes(""), (True, False, False), "sem nenhuma fonte, a dos filmes diz o que falta")

    def test_a_open_library_fora_do_ar(self):
        self.ligar()
        apoio.TMDB.falha_ol = 500
        st, r = pedir(self.base, "GET", "/api/busca?q=farol&tipo=livro")
        self.assertEqual(st, 502 if st == 502 else 400)
        self.assertIn("Open Library", r["erro"])

    def test_ferramentas(self):
        self.ligar()
        usar = lambda nome, a=None: S.usar_ferramenta({"nome": nome, "argumentos": a or {}, "pessoa": {"nome": "ana"}})["texto"]  # noqa: E731
        r = usar("adicionar", {"nome": "Farol das Marés", "tipo": "livro"})
        self.assertIn("O Farol das Marés", r)
        self.assertIn("Quero ler", r.replace("quero ler", "Quero ler"))
        r = usar("adicionar", {"nome": "9786500000024", "tipo": "livro", "situacao": "visto"})
        self.assertIn("A Torre de Vidro", r)
        ver = usar("ver", {"titulo": "torre de vidro"})
        self.assertIn("Autores: Beto Escritor, Ana Autora.", ver)
        self.assertIn("ISBN: 9786500000024.", ver)
        self.assertNotIn("Onde assistir", ver)
        ver = usar("ver", {"titulo": "farol das"})
        self.assertIn("Autor: Ana Autora.", ver)
        self.assertIn("Páginas: 320.", ver)
        lista = usar("buscar", {"tipo": "livro"})
        self.assertIn("· livro · quero ler · Ana Autora", lista)
        self.assertIn("· livro · lido", lista)
        self.assertIn("livros: 1 quero ler, 1 lido", usar("resumo"))
        self.assertIn("O Farol das Marés", usar("sugerir", {"tipo": "livro"}))
        self.assertNotIn("nenhuma assinatura", usar("sugerir", {"tipo": "livro"}))
        self.assertIn("Lido", usar("marcar", {"titulo": "farol das", "situacao": "visto"}).replace("lido", "Lido"))
        self.assertIn("Categoria criada nos livros", usar("categoria", {"acao": "nova", "tipo": "livro", "nome": "Clássicos"}))
        self.assertIn("nada agora", usar("lista_pronta", {"lista": "alta", "tipo": "livro"}))
        nomes = {f["nome"]: f for f in S.ferramentas.FERRAMENTAS}
        self.assertIn("livro", nomes["adicionar"]["entrada"]["properties"]["tipo"]["enum"])
        self.assertIn("Open Library", S.ferramentas.INSTRUCOES)


if __name__ == "__main__":
    unittest.main()
