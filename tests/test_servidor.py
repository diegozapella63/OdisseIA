"""O servidor de verdade (HTTP) com o TMDB de mentira: a chave, a busca, adicionar, mudar, as capas, os Dados e o CorrerIA."""
import base64
import io
import json
import os
import unittest
import zipfile
from unittest import mock

from tests import apoio
from tests.apoio import S, pedir


class TestServidor(unittest.TestCase):
    def setUp(self):
        apoio.limpar()
        self.base = apoio.Servidor.subir()

    def get(self, rota, **k):
        return pedir(self.base, "GET", rota, **k)

    def post(self, rota, corpo=None, **k):
        return pedir(self.base, "POST", rota, corpo if corpo is not None else {}, **k)

    def chave(self):
        st, r = self.post("/api/tmdb", {"chave": apoio.CHAVE})
        self.assertEqual(st, 200, r)
        return r

    def add(self, tipo, n, situacao="quero"):
        st, r = self.post("/api/titulo", {"acao": "adicionar", "tipo": tipo, "tmdb": n, "situacao": situacao})
        self.assertEqual(st, 200, r)
        return r["titulo"]

    def test_estado_e_a_chave(self):
        st, e = self.get("/api/estado")
        self.assertEqual((st, e["versao"], e["tmdb"], e["titulos"], e["eu"]), (200, S.VERSAO, {"chave": False, "fim": "", "erro": ""}, [], "person.ana"))
        self.assertEqual([p["nome"] for p in e["pessoas"]], ["Ana", "Beto"])
        st, r = self.get("/api/busca?q=mar")
        self.assertEqual((st, r["erro"]), (502, "Falta a chave do TMDB (Mais › Configurações › Integrações)."))
        st, r = self.post("/api/tmdb", {"chave": "b" * 32})
        self.assertEqual(st, 502)
        self.assertIn("não aceitou", r["erro"])
        self.assertFalse(os.path.exists(S.SEGREDOS_ARQ), "a chave que não vale não fica")
        st, r = self.post("/api/tmdb", {"chave": "isto <não> é chave"})
        self.assertEqual(st, 400)
        r = self.chave()
        self.assertEqual(r["tmdb"], {"chave": True, "fim": "••••aaaa", "erro": ""})
        self.assertEqual(oct(os.stat(S.SEGREDOS_ARQ).st_mode & 0o777), "0o600")
        _, e = self.get("/api/estado")
        self.assertNotIn(apoio.CHAVE, json.dumps(e), "a chave nunca volta para a tela")
        self.assertEqual(self.post("/api/tmdb", {"chave": ""})[1]["tmdb"]["chave"], False)

    def test_buscar_adicionar_e_mudar(self):
        self.chave()
        st, r = self.get("/api/busca?q=mar")
        self.assertEqual([(x["nome"], x["ja"]) for x in r["resultados"]], [("Mar de Estrelas", None)])
        t = self.add("serie", 202, "vendo")
        self.assertEqual((t["nome"], t["quem"], t["situacao"]), ("Mar de Estrelas", ["person.ana"], "vendo"), "quem adiciona vê")
        st, capa = self.get("/api/capa/" + t["capa"])
        self.assertTrue(capa.startswith(b"\xff\xd8\xff"))
        self.assertEqual(self.get("/api/busca?q=mar")[1]["resultados"][0]["ja"], t["id"])
        st, r = self.post("/api/titulo", {"acao": "adicionar", "tipo": "serie", "tmdb": 202})
        self.assertEqual((r["novo"], r["titulo"]["id"]), (False, t["id"]))
        st, r = self.post("/api/titulo", {"acao": "proximo", "id": t["id"]})
        self.assertEqual((r["titulo"]["temp"], r["titulo"]["ep"]), (1, 1))
        st, r = self.post("/api/titulo", {"acao": "mudar", "id": t["id"], "campos": {"nota": 5, "quem": ["person.beto"]}})
        self.assertEqual((st, r["titulo"]["nota"], r["titulo"]["quem"]), (200, 5, ["person.beto"]))
        st, r = self.post("/api/titulo", {"acao": "mudar", "id": t["id"], "campos": {"quem": ["person.zeca"]}})
        self.assertEqual(st, 400)
        self.assertEqual(self.get("/api/rev")[1]["rev"], S.ler()["rev"])
        for corpo in ({"acao": "voar", "id": t["id"]}, {"acao": "mudar", "id": "t00000000", "campos": {}}, {"acao": "adicionar", "tipo": "filme", "tmdb": "x"},
                      {"acao": "adicionar", "tipo": "filme", "tmdb": 101, "situacao": "talvez"}):
            self.assertEqual(self.post("/api/titulo", corpo)[0], 400, corpo)
        st, r = self.post("/api/titulo", {"acao": "adicionar", "tipo": "filme", "tmdb": 999})
        self.assertEqual(st, 502)
        self.assertEqual(self.get("/api/estado")[1]["tmdb"]["erro"], "O TMDB não achou esse título.")

    def test_capas_da_busca(self):
        self.chave()
        st, img = self.get("/api/img/w185/estrelas.jpg")
        st2, img2 = self.get("/api/img/w185/estrelas.jpg")
        self.assertEqual((st, st2), (200, 200))
        self.assertTrue(img.startswith(b"\xff\xd8\xff"))
        self.assertEqual(len([p for p in apoio.TMDB.pedidos if p[0] == "/t/p/w185/estrelas.jpg"]), 1, "a segunda vem da memória")
        self.assertEqual(self.get("/api/img/w185/nada.jpg")[0], 404)
        self.assertEqual(self.get("/api/img/w500/estrelas.jpg")[0], 404, "só os tamanhos pequenos")
        self.assertEqual(self.get("/api/img/w92/../x.jpg")[0], 404)
        S.IMGS.clear()
        S.IMGS.update({str(i): b"" for i in range(300)})
        self.assertEqual(self.get("/api/img/w92/farol.jpg")[0], 200)
        self.assertEqual(len(S.IMGS), 300, "até 300 na memória")

    def test_atualizar_e_apagar(self):
        self.chave()
        t = self.add("serie", 202)
        os.remove(S.caminho_capa(t["capa"]))
        st, r = self.post("/api/titulo", {"acao": "atualizar", "id": t["id"]})
        self.assertEqual(st, 200)
        self.assertTrue(os.path.exists(S.caminho_capa(r["titulo"]["capa"])), "a capa que sumiu volta")
        st, r = self.post("/api/titulo", {"acao": "apagar", "id": t["id"]})
        self.assertEqual((st, r["titulo"]), (200, None))
        self.assertFalse(os.path.exists(S.caminho_capa(t["capa"])), "a capa sai junto")
        self.assertEqual(self.get("/api/capa/" + t["capa"])[0], 404)
        self.assertEqual(self.post("/api/titulo", {"acao": "atualizar", "id": t["id"]})[0], 400)

    def test_dados(self):
        self.chave()
        t = self.add("filme", 101)
        st, z = self.get("/api/dados/exportar")
        with zipfile.ZipFile(io.BytesIO(z)) as arq:
            self.assertEqual(sorted(arq.namelist()), sorted(["odisseia.json", "manifesto.json", "capas/" + t["capa"]]))
            self.assertNotIn(apoio.CHAVE.encode(), arq.read("odisseia.json"), "a chave não vai no arquivo")
        st, r = self.post("/api/dados/backup")
        self.assertEqual((st, len(r["backups"])), (200, 1))
        self.add("serie", 204)
        st, r = self.post("/api/dados/importar", {"arquivo": base64.b64encode(z).decode()})
        self.assertEqual(st, 200)
        e = self.get("/api/estado")[1]
        self.assertEqual([x["nome"] for x in e["titulos"]], ["A Grande Viagem"])
        versoes = self.get("/api/dados")[1]["versoes"]
        self.assertIn("antes de importar", [v["motivo"] for v in versoes])
        v = next(v for v in versoes if v["motivo"] == "antes de importar")
        st, r = self.post("/api/dados/restaurar", {"origem": "versao", "nome": v["nome"]})
        self.assertEqual(st, 200)
        self.assertEqual(sorted(x["nome"] for x in self.get("/api/estado")[1]["titulos"]), ["A Grande Viagem", "Casa no Morro"])
        st, r = self.post("/api/dados/restaurar", {"origem": "backup", "nome": self.get("/api/dados")[1]["backups"][0]["nome"]})
        self.assertEqual([x["nome"] for x in self.get("/api/estado")[1]["titulos"]], ["A Grande Viagem"])
        self.assertTrue(os.path.exists(S.caminho_capa(t["capa"])))
        st, r = self.post("/api/dados/importar", {"arquivo": base64.b64encode(json.dumps(S.ler()).encode()).decode()})
        self.assertEqual(st, 200, "também só o odisseia.json")
        for corpo, erro in (({"arquivo": "@@"}, "ler o arquivo"), ({"arquivo": base64.b64encode(b"PK\x03\x04lixo").decode()}, "abrir"),
                            ({"arquivo": base64.b64encode(b"[1]").decode()}, "não é um backup"), ({"arquivo": base64.b64encode(b"\xff").decode()}, "não é um backup")):
            st, r = self.post("/api/dados/importar", corpo)
            self.assertEqual(st, 400)
            self.assertIn(erro, r["erro"])
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as arq:
            arq.writestr("outro.json", "{}")
        self.assertIn("não é um backup", self.post("/api/dados/importar", {"arquivo": base64.b64encode(buf.getvalue()).decode()})[1]["erro"])
        self.assertEqual(self.post("/api/dados/restaurar", {"origem": "backup", "nome": "../x"})[0], 400)
        self.assertEqual(self.post("/api/dados/restaurar", {"origem": "backup", "nome": "odisseia-2000-01-01-000000.zip"})[0], 400)
        self.assertEqual(self.post("/api/dados/zerar", {})[0], 400)
        st, r = self.post("/api/dados/zerar", {"confirmar": True})
        self.assertEqual((st, self.get("/api/estado")[1]["titulos"]), (200, []))
        self.assertFalse(os.path.exists(S.caminho_capa(t["capa"])))
        self.assertTrue(self.get("/api/estado")[1]["tmdb"]["chave"], "a chave fica")
        nomes = iter(f"odisseia-2026-11-{i:02d}-120000.zip" for i in range(1, 13))
        with mock.patch.object(S, "nome_zip", lambda: next(nomes)):
            for _ in range(12):
                S.fazer_backup()
        self.assertEqual(len(S.backups()), 10)
        for _ in range(7):
            S.guardar_versao("teste")
        self.assertEqual(len(S.versoes()), 5)

    def test_ajustes(self):
        st, r = self.post("/api/ajustes", {"cor": "azul"})
        self.assertEqual((r["ajustes"]["cor"], r["ajustes"]["cor_dia"]), ("azul", False))
        self.assertEqual(self.post("/api/ajustes", {"cor": "Azul!"})[0], 400)
        self.assertEqual(self.post("/api/ajustes", {"quem": "sim"})[0], 400)
        self.assertFalse(self.post("/api/ajustes", {"quem": False})[1]["ajustes"]["quem"])

    def test_rotas_e_arquivos(self):
        st, html = self.get("/")
        self.assertIn(b"OdisseIA", html)
        self.assertEqual(self.get("/buscar")[1], html, "um caminho sem arquivo abre a tela")
        self.assertEqual(self.get("/../server.py")[0], 404)
        self.assertEqual(self.get("/nada.js")[0], 404)
        self.assertEqual(self.get("/api/nada")[0], 404)
        self.assertEqual(self.post("/api/nada")[0], 404)
        self.assertEqual(self.post("/api/titulo", [1])[0], 400)
        st, css = self.get("/styles.css")
        self.assertEqual(st, 200)
        self.assertEqual(pedir(self.base, "HEAD", "/")[0], 200)

    def test_fora_do_ingress(self):
        with mock.patch.object(S, "DEV", False), mock.patch.object(S, "PERMITIDOS", set()):
            self.assertEqual(self.get("/api/estado")[0], 403)

    def test_pessoas_do_home_assistant(self):
        estados = [{"entity_id": "person.ana", "attributes": {"friendly_name": "Ana Lima", "user_id": "u1"}}, {"entity_id": "light.sala"},
                   {"entity_id": "person.beto", "attributes": {}}]
        with mock.patch.object(S, "TOKEN", "x"), mock.patch.object(S, "ha_get", return_value=estados):
            S._pessoas.update(v=None, t=0)
            self.assertEqual(S.pessoas(), [{"id": "person.ana", "nome": "Ana Lima", "usuario": "u1"}, {"id": "person.beto", "nome": "beto", "usuario": ""}])
            self.assertEqual(S.eu("u1"), "person.ana")
        with mock.patch.object(S, "TOKEN", "x"), mock.patch.object(S, "ha_get", side_effect=OSError("fora")):
            S._pessoas.update(v=None, t=0)
            self.assertEqual(S.pessoas(), [])
        S._pessoas.update(v=None, t=0)

    def test_laco_escolhe_quem_atualizar(self):
        from datetime import datetime
        agora = datetime(2026, 11, 24, 10)
        base = {"tmdb": 1, "tipo": "serie", "situacao": "vendo", "tmdb_em": "2026-11-23T20:00:00"}
        self.assertFalse(S.precisa_atualizar(base, agora))
        self.assertTrue(S.precisa_atualizar(dict(base, tmdb_em="2026-11-23T09:00:00"), agora))
        self.assertFalse(S.precisa_atualizar(dict(base, tipo="filme", tmdb_em="2026-11-20T09:00:00"), agora))
        self.assertTrue(S.precisa_atualizar(dict(base, tipo="filme", tmdb_em="2026-11-10T09:00:00"), agora))
        self.assertFalse(S.precisa_atualizar(dict(base, situacao="abandonado", tmdb_em=""), agora))
        self.assertTrue(S.precisa_atualizar(dict(base, tmdb_em="ontem"), agora))
        self.assertFalse(S.precisa_atualizar(dict(base, tmdb=None), agora))


class TestCorrerIA(unittest.TestCase):
    def setUp(self):
        apoio.limpar()
        apoio.fixar_hoje(self)
        self.base = apoio.Servidor.subir()

    def ferr(self, metodo, corpo=None, chave=None):
        cab = {"Authorization": "Bearer " + (chave or S.CORRERIA.chave()), "X-App": "CorrerIA"}
        return pedir(self.base, metodo, "/api/integracao/ferramentas", corpo, cab=cab)

    def usar(self, nome, argumentos=None, pessoa=None):
        return self.ferr("POST", {"nome": nome, "argumentos": argumentos or {}, "pessoa": pessoa or {"id": "person.beto", "nome": "Beto"}, "cliente": "WhatsApp"})

    def test_ligar_e_usar(self):
        self.assertEqual(self.ferr("GET")[0], 401, "desligado")
        pedir(self.base, "POST", "/api/ajustes", {"correria": True})
        arq = os.path.join(S.SHARE_DIR, "correria.json")
        c = json.load(open(arq, encoding="utf-8"))
        self.assertEqual((c["app"], c["nome"], c["url"], c["ferramentas"], c["chave"]), ("odisseia", "OdisseIA", "http://odisseia-teste:8099", "/api/integracao/ferramentas", S.CORRERIA.chave()))
        self.assertEqual(oct(os.stat(arq).st_mode & 0o777), "0o600")
        self.assertEqual(self.ferr("GET", chave="errada")[0], 401)
        st, r = self.ferr("GET")
        self.assertEqual([f["nome"] for f in r["ferramentas"]], ["resumo", "buscar", "ver", "adicionar", "marcar", "proximo_episodio", "apagar"])
        self.assertEqual(self.usar("resumo")[1]["texto"], "A lista da casa está vazia.")
        self.assertIn("Falta a chave do TMDB", self.usar("adicionar", {"nome": "Mar de Estrelas"})[1]["erro"])
        pedir(self.base, "POST", "/api/tmdb", {"chave": apoio.CHAVE})
        st, r = self.usar("adicionar", {"nome": "mar de estrelas", "situacao": "vendo"})
        self.assertEqual(st, 200, r)
        self.assertRegex(r["texto"], r"^Adicionado: t[0-9a-f]{8} \| Mar de Estrelas \(2023\) · série · vendo · Beto$")
        t = S.ler()["titulos"][0]
        self.assertTrue(t["capa"] and os.path.exists(S.caminho_capa(t["capa"])))
        self.assertIn("Já está na lista", self.usar("adicionar", {"nome": "Mar de Estrelas"})[1]["texto"])
        self.assertIn("Não achei", self.usar("adicionar", {"nome": "Nada Assim", "tipo": "filme"})[1]["erro"])
        r = self.usar("adicionar", {"nome": "The Long Trip", "ano": 2020, "quem": ["ana", "Beto"]})[1]
        self.assertIn("A Grande Viagem (2019) · filme · quero ver · Ana, Beto", r["texto"])
        self.assertIn("parou em T1 E1", self.usar("proximo_episodio", {"titulo": "mar"})[1]["texto"] + self.usar("buscar", {"tipo": "serie"})[1]["texto"])
        r = self.usar("marcar", {"titulo": "Mar de Estrelas", "temporada": 2, "episodio": 2, "nota": 4})[1]
        self.assertIn("parou em T2 E2 · nota 4", r["texto"])
        self.assertIn("todos os episódios que saíram", self.usar("proximo_episodio", {"titulo": "mar"})[1]["erro"])
        r = self.usar("resumo")[1]["texto"]
        self.assertIn("2 títulos: 1 quero ver, 1 vendo, 0 visto, 0 abandonado.", r)
        self.assertIn("27/11/2026: Mar de Estrelas T2 E3", r)
        v = self.usar("ver", {"titulo": "grande viagem"})[1]["texto"]
        self.assertIn("Onde assistir no Brasil (JustWatch): assinatura: Cine Lumen; alugar: Loja Pipoca.", v)
        self.assertIn("Duração: 132 min.", v)
        v = self.usar("ver", {"titulo": "mar"})[1]["texto"]
        self.assertIn("Temporadas: T1 (3 ep.), T2 (4 ep.).", v)
        self.assertIn("Próximo: T2 E3 em 27/11/2026.", v)
        self.assertEqual(self.usar("buscar", {"pessoa": "ana"})[1]["texto"].count("\n- "), 1)
        self.assertEqual(self.usar("buscar", {"texto": "zzz"})[1]["texto"], "Nenhum título com esses filtros.")
        self.assertIn("Apagado: A Grande Viagem.", self.usar("apagar", {"titulo": "A Grande Viagem"})[1]["texto"])
        self.assertEqual(len(S.ler()["titulos"]), 1)
        self.assertEqual(S.CORRERIA.ultimo["app"], "WhatsApp")
        for args, erro in (({"titulo": "mar", "cor": "x"}, "Argumento desconhecido: cor"), ({}, "Falta: titulo"), ({"titulo": 3}, "texto"),
                           ({"titulo": "mar", "nota": "4"}, "inteiro"), ({"titulo": "mar", "nota": 9}, "vai de 0 a 5"),
                           ({"titulo": "mar", "situacao": "x"}, "situacao vale"), ({"titulo": "mar", "quem": "ana"}, "lista de nomes"),
                           ({"titulo": "mar", "quem": ["Zeca"]}, "não é uma pessoa"), ({"titulo": "mar"}, "Diga o que mudar"), ({"titulo": "nada"}, "Nenhum título")):
            st, r = self.usar("marcar", args)
            self.assertEqual(st, 400, args)
            self.assertIn(erro, r["erro"], args)
        self.assertEqual(self.usar("voar")[0], 404)
        pedir(self.base, "POST", "/api/ajustes", {"correria": False})
        self.assertFalse(os.path.exists(arq))
        self.assertEqual(self.ferr("GET")[0], 401)


if __name__ == "__main__":
    unittest.main()


class TestBordas(unittest.TestCase):
    def setUp(self):
        apoio.limpar()
        self.base = apoio.Servidor.subir()

    def test_laco_atualiza_e_para_sem_internet(self):
        S.guardar_chave(apoio.CHAVE)
        S.adicionar({"tipo": "serie", "tmdb": 202, "situacao": "vendo"})
        d = S.ler()
        d["titulos"][0]["tmdb_em"] = "2000-01-01T00:00:00"
        d["titulos"][0]["proximo"] = None
        S.salvar(d)
        voltas = []

        def dormir(s):
            voltas.append(s)
            if len(voltas) > 3:
                raise SystemExit
        with mock.patch.object(S.time, "sleep", dormir), self.assertRaises(SystemExit):
            S.laco()
        self.assertEqual(S.ler()["titulos"][0]["proximo"]["ep"], 3, "o laço buscou o próximo episódio")
        d = S.ler()
        d["titulos"][0]["tmdb_em"] = "2000-01-01T00:00:00"
        S.salvar(d)
        voltas.clear()
        with mock.patch.object(S.time, "sleep", dormir), mock.patch.object(S, "TMDB_API", "http://127.0.0.1:9/3"), self.assertRaises(SystemExit):
            S.laco()
        voltas.clear()
        with mock.patch.object(S.time, "sleep", dormir), mock.patch.object(S, "ler", side_effect=RuntimeError("quebrou")), self.assertRaises(SystemExit):
            S.laco()

    def test_conexao_e_pessoa_pelo_nome(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ODISSEIA_URL_INTERNA")
            url, _ = S.CORRERIA.endereco()
        self.assertTrue(url.startswith("http://") and url.endswith(":8099"))
        S.CORRERIA.chave()
        outra = S.Conexao()
        self.assertEqual(outra.chave(), S.CORRERIA.chave(), "a chave fica no /data")
        with mock.patch.object(S, "_gravar", side_effect=OSError("cheio")):
            S.CORRERIA.publicar(True)
        S.guardar_chave(apoio.CHAVE)
        r = S.usar_ferramenta({"nome": "adicionar", "argumentos": {"nome": "Farol"}, "pessoa": {"nome": "ana"}})
        self.assertIn("· Ana", r["texto"])
        r = S.usar_ferramenta({"nome": "marcar", "argumentos": {"titulo": "farol", "notas": "Vimos no feriado."}})
        self.assertIn("Notas da casa: Vimos no feriado.", S.usar_ferramenta({"nome": "ver", "argumentos": {"titulo": "farol"}})["texto"])
        self.assertIn("1 títulos", S.usar_ferramenta({"nome": "buscar", "argumentos": {"situacao": "quero"}})["texto"])
        with mock.patch.object(S, "TMDB_API", "http://127.0.0.1:9/3"), self.assertRaisesRegex(S.ferramentas.ErroFerramenta, "internet"):
            S.usar_ferramenta({"nome": "adicionar", "argumentos": {"nome": "Mar"}})

    def test_o_que_sobra(self):
        os.makedirs(S.VERSOES, exist_ok=True)
        open(os.path.join(S.VERSOES, "lixo.txt"), "w").close()
        self.assertEqual(S.versoes(), [])
        S.guardar_versao("sem arquivo")
        self.assertEqual(S.versoes(), [], "sem dados ainda, nenhuma versão")
        with open(S.SEGREDOS_ARQ, "w") as f:
            f.write("{quebrado")
        self.assertEqual(S.segredos(), {})
        with open(S.SEGREDOS_ARQ, "w") as f:
            f.write("[1]")
        self.assertEqual(S.segredos(), {})
        d = S.ler()
        d["titulos"].append(S.R.limpar_titulo({"id": "t0000000a", "tipo": "filme", "nome": "Feito à mão"}))
        S.salvar(d)
        self.assertEqual(pedir(self.base, "POST", "/api/titulo", {"acao": "atualizar", "id": "t0000000a"})[1]["erro"], "Esse título não veio do TMDB.")
        self.assertEqual(pedir(self.base, "POST", "/api/titulo", {"acao": "x"} | {"pad": "a" * (S.MAX_CORPO + 10)})[0], 400)
        with mock.patch.object(S, "TOKEN", apoio.TOKEN), mock.patch.object(S, "HA_API", f"http://127.0.0.1:{apoio.TMDB.porta}/3"):
            self.assertEqual(S.ha_get("/authentication"), {"success": True})
        t = {"id": "t0000000b", "capa": "t0000000b.png"}
        S.gravar_capa(t, b"\xff\xd8\xff\xe0x")
        self.assertEqual(t["capa"], "t0000000b.jpg", "a capa que muda de formato troca o arquivo")
        S.apagar_capa("t0000000b.jpg")
        S.apagar_capa("t0000000b.jpg")
        self.assertIsNone(S.gravar_capa(t, None))
        with open(S.caminho_capa("t0000000c.png"), "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\nx")
        st, b = pedir(self.base, "GET", "/api/capa/t0000000c.png")
        self.assertEqual((st, b[:4]), (200, b"\x89PNG"))

    def test_main(self):
        srv = mock.MagicMock()
        with mock.patch.object(S, "ThreadingHTTPServer", return_value=srv) as cls, mock.patch.object(S.threading, "Thread") as th:
            S.main()
        cls.assert_called_once()
        th.return_value.start.assert_called_once()
        srv.serve_forever.assert_called_once()
