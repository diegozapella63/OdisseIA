"""O servidor de verdade (HTTP) com o TMDB de mentira: a chave, a busca, adicionar, mudar, as capas, os Dados e o CorrerIA."""
import base64
import io
import json
import os
import time
import unittest
import zipfile
from datetime import date
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
        t = self.add("serie", 202, "quero")
        self.assertEqual((t["nome"], t["quem"], t["situacao"]), ("Mar de Estrelas", ["person.ana"], "quero"), "quem adiciona vê")
        st, capa = self.get("/api/capa/" + t["capa"])
        self.assertTrue(capa.startswith(b"\xff\xd8\xff"))
        self.assertEqual(self.get("/api/busca?q=mar")[1]["resultados"][0]["ja"], t["id"])
        st, r = self.post("/api/titulo", {"acao": "adicionar", "tipo": "serie", "tmdb": 202})
        self.assertEqual((r["novo"], r["titulo"]["id"]), (False, t["id"]))
        st, r = self.post("/api/titulo", {"acao": "proximo", "id": t["id"]})
        self.assertEqual((r["titulo"]["temp"], r["titulo"]["ep"]), (1, 1))
        st, r = self.post("/api/categorias", {"acao": "nova", "tipo": "serie", "nome": "Para ver a dois"})
        cat = r["categorias"]["serie"][0]["id"]
        st, r = self.post("/api/titulo", {"acao": "mudar", "id": t["id"], "campos": {"categoria": cat, "quem": ["person.beto"]}})
        self.assertEqual((st, r["titulo"]["categoria"], r["titulo"]["quem"]), (200, cat, ["person.beto"]))
        self.assertEqual(self.post("/api/titulo", {"acao": "mudar", "id": t["id"], "campos": {"categoria": "c000000"}})[0], 400)
        self.assertEqual(self.post("/api/categorias", {"acao": "nova", "tipo": "serie", "nome": "para ver a dois"})[0], 400)
        self.assertEqual(self.get("/api/estado")[1]["categorias"]["serie"][0]["nome"], "Para ver a dois")
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
        base = {"tmdb": 1, "tipo": "serie", "situacao": "quero", "tmdb_em": "2026-11-23T20:00:00"}
        self.assertFalse(S.precisa_atualizar(base, agora))
        self.assertTrue(S.precisa_atualizar(dict(base, tmdb_em="2026-11-23T09:00:00"), agora))
        self.assertFalse(S.precisa_atualizar(dict(base, tipo="filme", tmdb_em="2026-11-20T09:00:00"), agora))
        self.assertTrue(S.precisa_atualizar(dict(base, tipo="filme", tmdb_em="2026-11-10T09:00:00"), agora))
        self.assertFalse(S.precisa_atualizar(dict(base, situacao="visto", tmdb_em="2026-11-20T09:00:00"), agora), "a série vista: de semana em semana")
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
        self.assertEqual([f["nome"] for f in r["ferramentas"]], ["resumo", "buscar", "ver", "lista_pronta", "adicionar", "adicionar_colecao", "sugerir", "marcar", "marcar_varios", "proximo_episodio", "categoria", "apagar_varios", "apagar"])
        self.assertEqual(self.usar("resumo")[1]["texto"], "A lista da casa está vazia.")
        self.assertIn("Falta a chave do TMDB", self.usar("adicionar", {"nome": "Mar de Estrelas"})[1]["erro"])
        pedir(self.base, "POST", "/api/tmdb", {"chave": apoio.CHAVE})
        st, r = self.usar("adicionar", {"nome": "mar de estrelas", "situacao": "quero"})
        self.assertEqual(st, 200, r)
        self.assertRegex(r["texto"], r"^Adicionado: t[0-9a-f]{8} \| Mar de Estrelas \(2023\) · série · quero ver · Beto$")
        t = S.ler()["titulos"][0]
        self.assertTrue(t["capa"] and os.path.exists(S.caminho_capa(t["capa"])))
        self.assertIn("Já está na lista", self.usar("adicionar", {"nome": "Mar de Estrelas"})[1]["texto"])
        self.assertIn("Não achei", self.usar("adicionar", {"nome": "Nada Assim", "tipo": "filme"})[1]["erro"])
        r = self.usar("adicionar", {"nome": "The Long Trip", "ano": 2020, "quem": ["ana", "Beto"]})[1]
        self.assertIn("A Grande Viagem (2019) · filme · quero ver · Ana, Beto", r["texto"])
        self.assertIn("parou em T1 E1", self.usar("proximo_episodio", {"titulo": "mar"})[1]["texto"] + self.usar("buscar", {"tipo": "serie"})[1]["texto"])
        pedir(self.base, "POST", "/api/categorias", {"acao": "nova", "tipo": "serie", "nome": "Para ver a dois"})
        r = self.usar("marcar", {"titulo": "Mar de Estrelas", "temporada": 2, "episodio": 2, "categoria": "para ver a dois"})[1]
        self.assertIn("parou em T2 E2 · Para ver a dois", r["texto"])
        self.assertEqual(self.usar("buscar", {"categoria": "Para ver a dois"})[1]["texto"].count("\n- "), 1)
        self.assertIn("Ana, Beto", self.usar("marcar", {"titulo": "mar", "quem": ["todos"]})[1]["texto"], "«todos» é a casa toda")
        self.assertIn("todos os episódios que saíram", self.usar("proximo_episodio", {"titulo": "mar"})[1]["erro"])
        r = self.usar("resumo")[1]["texto"]
        self.assertIn("2 títulos (filmes: 1 quero ver, 0 visto; séries: 1 quero ver, 0 visto).", r)
        self.assertIn("Séries em andamento:\n- ", r)
        self.assertIn("Categorias da casa: séries: Para ver a dois.", r)
        self.assertIn("27/11/2026: Mar de Estrelas T2 E3", r)
        v = self.usar("ver", {"titulo": "grande viagem"})[1]["texto"]
        self.assertIn("Onde assistir no Brasil (JustWatch): assinatura: Cine Lumen; alugar: Loja Pipoca.", v)
        self.assertIn("Duração: 132 min.", v)
        # 0.13.0: onde (o serviço) e por_servico (quantos de cada assinatura)
        r = self.usar("buscar", {"onde": "lumen", "tipo": "filme"})[1]["texto"]
        self.assertIn("A Grande Viagem", r)
        self.assertIn("Onde assistir no Brasil (JustWatch): assinatura: Cine Lumen", r)
        self.assertEqual(self.usar("buscar", {"onde": "pipoca"})[1]["texto"], "Nenhum título com esses filtros.", "alugar não conta")
        r = self.usar("buscar", {"situacao": "quero", "por_servico": True})[1]["texto"]
        self.assertIn(", por assinatura (pelo que a JustWatch sabe):", r)
        self.assertIn("- Cine Lumen: ", r)
        self.assertEqual(self.usar("buscar", {"texto": "zzz", "por_servico": True})[1]["texto"], "Nenhum título com esses filtros.")
        v = self.usar("ver", {"titulo": "mar"})[1]["texto"]
        self.assertIn("Temporadas: T1 (3 ep.), T2 (4 ep.).", v)
        self.assertIn("Próximo: T2 E3 em 27/11/2026.", v)
        self.assertEqual(self.usar("buscar", {"pessoa": "ana"})[1]["texto"].count("\n- "), 2, "a série é de todos agora")
        self.assertEqual(self.usar("buscar", {"texto": "zzz"})[1]["texto"], "Nenhum título com esses filtros.")
        self.assertIn("Apagado: A Grande Viagem.", self.usar("apagar", {"titulo": "A Grande Viagem"})[1]["texto"])
        self.assertEqual(len(S.ler()["titulos"]), 1)
        self.assertEqual(S.CORRERIA.ultimo["app"], "WhatsApp")
        for args, erro in (({"titulo": "mar", "cor": "x"}, "Argumento desconhecido: cor"), ({}, "Falta: titulo"), ({"titulo": 3}, "texto"),
                           ({"titulo": "mar", "temporada": "2"}, "inteiro"), ({"titulo": "mar", "temporada": -1}, "temporada é 0 ou mais"),
                           ({"titulo": "mar", "categoria": "Terror"}, "não é uma categoria"), ({"titulo": "mar", "nota": 4}, "Argumento desconhecido: nota"),
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
        S.adicionar({"tipo": "serie", "tmdb": 202, "situacao": "quero"})
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
        self.assertEqual(th.return_value.start.call_count, 2, "o laço dos títulos e o dos sensores")
        srv.serve_forever.assert_called_once()


class TestNovidades020(unittest.TestCase):
    """0.2.0: Já vi (a série inteira), as coleções, as listas prontas e O que controlar."""

    def setUp(self):
        apoio.limpar()
        apoio.fixar_hoje(self)
        self.base = apoio.Servidor.subir()
        S.guardar_chave(apoio.CHAVE)

    def get(self, rota):
        return pedir(self.base, "GET", rota)

    def post(self, rota, corpo):
        return pedir(self.base, "POST", rota, corpo)

    def test_serie_inteira_como_vista(self):
        st, r = self.post("/api/titulo", {"acao": "adicionar", "tipo": "serie", "tmdb": 202, "situacao": "visto"})
        t = r["titulo"]
        self.assertEqual((t["situacao"], t["temp"], t["ep"], t["visto_em"]), ("visto", 2, 2, "2026-11-24"))

    def test_listas_prontas(self):
        st, r = self.get("/api/lista?nome=populares")
        self.assertEqual((st, [x["tipo"] for x in r["resultados"]], r["mais"]), (200, ["filme", "serie", "filme", "serie"], True))
        self.post("/api/titulo", {"acao": "adicionar", "tipo": "filme", "tmdb": 101, "situacao": "visto"})
        r = self.get("/api/lista?nome=populares&tipo=filme&pagina=1")[1]
        self.assertEqual((r["resultados"][0]["situacao"], r["resultados"][1]["ja"]), ("visto", None))
        self.assertFalse(self.get("/api/lista?nome=populares&tipo=filme&pagina=2")[1]["mais"])
        self.assertEqual(self.get("/api/lista?nome=nada")[0], 400)
        self.assertEqual(len(self.get("/api/lista?nome=alta&pagina=x")[1]["resultados"]), 2, "a página que não é número é a primeira")

    def test_colecao(self):
        self.post("/api/titulo", {"acao": "adicionar", "tipo": "filme", "tmdb": 101, "situacao": "quero"})
        st, r = self.get("/api/colecao?id=301")
        c = r["colecao"]
        self.assertEqual([(f["nome"], f["saiu"], f["situacao"]) for f in c["itens"]],
                         [("A Grande Viagem", True, "quero"), ("A Grande Viagem 2", True, None), ("A Grande Viagem 3", False, None)])
        self.assertEqual(self.get("/api/colecao?id=x")[0], 400)
        st, r = self.post("/api/titulo", {"acao": "adicionar_colecao", "colecao": 301, "situacao": "visto"})
        self.assertEqual((r["novos"], r["marcados"], r["ja"], r["fora"]), (1, 1, 0, 1))
        ts = {t["nome"]: t for t in S.ler()["titulos"]}
        self.assertEqual(sorted(ts), ["A Grande Viagem", "A Grande Viagem 2"], "o que ainda não saiu fica de fora")
        self.assertTrue(all(t["situacao"] == "visto" for t in ts.values()))
        self.assertEqual(ts["A Grande Viagem"]["colecao"], {"id": 301, "nome": "Coleção A Grande Viagem", "capa": "/viagem.jpg"})
        st, r = self.post("/api/titulo", {"acao": "adicionar_colecao", "colecao": 301, "situacao": "quero"})
        self.assertEqual((r["novos"], r["ja"]), (1, 2), "Quero ver não mexe no que já estava")
        self.assertEqual(S.ler()["titulos"][0]["nome"], "A Grande Viagem 3")
        rev = S.ler()["rev"]
        st, r = self.post("/api/titulo", {"acao": "adicionar_colecao", "colecao": 301, "situacao": "quero"})
        self.assertEqual((r["novos"], S.ler()["rev"]), (0, rev), "nada a mudar, nada gravado")
        for corpo in ({"acao": "adicionar_colecao", "colecao": "x"}, {"acao": "adicionar_colecao", "colecao": 301, "situacao": "abandonado"}):
            self.assertEqual(self.post("/api/titulo", corpo)[0], 400)

    def test_o_que_controlar(self):
        self.post("/api/titulo", {"acao": "adicionar", "tipo": "filme", "tmdb": 101})
        self.post("/api/titulo", {"acao": "adicionar", "tipo": "serie", "tmdb": 202})
        st, r = self.post("/api/ajustes", {"tipos": {"filme": False, "jogo": False}})
        self.assertEqual(r["ajustes"]["tipos"], {"filme": False, "serie": True, "jogo": False, "livro": False})
        self.assertEqual([t["tipo"] for t in self.get("/api/estado")[1]["titulos"]], ["serie"])
        self.assertEqual(len(S.ler()["titulos"]), 2, "desligar não apaga")
        self.assertEqual(self.post("/api/ajustes", {"tipos": {"serie": False}})[1]["erro"], "Deixe pelo menos um ligado.")
        self.assertEqual(self.post("/api/ajustes", {"tipos": {"musica": True}})[0], 400)
        st, r = self.post("/api/titulo", {"acao": "adicionar", "tipo": "filme", "tmdb": 103})
        self.assertEqual((st, r["erro"]), (400, "Filmes estão desligados em Opções › O que controlar."))
        self.assertEqual(self.post("/api/titulo", {"acao": "adicionar_colecao", "colecao": 301})[0], 400)
        self.assertEqual({x["tipo"] for x in self.get("/api/busca?q=grande")[1]["resultados"]}, set(), "sem filmes nem coleções")
        self.assertEqual({x["tipo"] for x in self.get("/api/lista?nome=populares")[1]["resultados"]}, {"serie"})
        r = S.usar_ferramenta({"nome": "buscar", "argumentos": {}})["texto"]
        self.assertNotIn("Grande Viagem", r)
        S.usar_ferramenta({"nome": "apagar", "argumentos": {"titulo": "mar"}})
        self.assertEqual([t["nome"] for t in S.ler()["titulos"]], ["A Grande Viagem"], "o filme escondido continua guardado")
        with self.assertRaisesRegex(S.ferramentas.ErroFerramenta, "desligados"):
            S.usar_ferramenta({"nome": "adicionar", "argumentos": {"nome": "Farol", "tipo": "filme"}})
        r = S.usar_ferramenta({"nome": "adicionar", "argumentos": {"nome": "casa no morro"}})["texto"]
        self.assertIn("Casa no Morro", r, "com um tipo só, ele vale")

    def test_ferramentas_novas(self):
        r = S.usar_ferramenta({"nome": "lista_pronta", "argumentos": {"lista": "avaliados", "tipo": "serie"}})["texto"]
        self.assertEqual(r, "Mais bem avaliados (TMDB):\n- Mar de Estrelas (2023) · série\n- Casa no Morro (2018) · série")
        r = S.usar_ferramenta({"nome": "adicionar_colecao", "argumentos": {"nome": "grande viagem", "situacao": "visto"}})["texto"]
        self.assertEqual(r, "Coleção A Grande Viagem: 2 filmes postos na lista como Visto, 1 ainda não saiu.")
        r = S.usar_ferramenta({"nome": "adicionar_colecao", "argumentos": {"nome": "grande viagem"}})["texto"]
        self.assertEqual(r, "Coleção A Grande Viagem: 1 filme posto na lista como Quero ver, 2 já estavam na lista.")
        r = S.usar_ferramenta({"nome": "lista_pronta", "argumentos": {"lista": "populares", "tipo": "filme"}})["texto"]
        self.assertIn("A Grande Viagem (2019) · filme · na lista: visto", r)
        with self.assertRaisesRegex(S.ferramentas.ErroFerramenta, "Não achei a coleção"):
            S.usar_ferramenta({"nome": "adicionar_colecao", "argumentos": {"nome": "zzz"}})
        with mock.patch.object(S, "TMDB_API", "http://127.0.0.1:9/3"):
            for nome, args in (("lista_pronta", {"lista": "alta"}), ("adicionar_colecao", {"nome": "x"})):
                with self.assertRaisesRegex(S.ferramentas.ErroFerramenta, "internet"):
                    S.usar_ferramenta({"nome": nome, "argumentos": args})
        self.assertEqual(S.ferramentas.texto_lista("alta", []), "Em alta: nada agora.")
        self.assertEqual(S.ferramentas.texto_colecao({"nome": "X", "novos": 0, "marcados": 1, "ja": 1, "fora": 2}, "visto"),
                         "X: 1 marcado como Visto, 1 já estava na lista, 2 ainda não saíram.")
        self.assertEqual(S.ferramentas.texto_colecao({"nome": "X", "novos": 0, "marcados": 0, "ja": 0, "fora": 0}, "quero"), "X: nada a mudar.")


class TestNovidades030(unittest.TestCase):
    """0.3.0: a coleção de cada filme nas listas, a lista pronta Coleções e as categorias."""

    def setUp(self):
        apoio.limpar()
        apoio.fixar_hoje(self)
        self.base = apoio.Servidor.subir()
        S.guardar_chave(apoio.CHAVE)

    def test_colecao_de_cada_filme(self):
        r = pedir(self.base, "GET", "/api/lista?nome=populares&tipo=filme&pagina=2")[1]
        self.assertEqual([(x["nome"], (x.get("colecao") or {}).get("id")) for x in r["resultados"]], [("A Grande Viagem 3", 301), ("Farol Distante", None)])
        pedir(self.base, "GET", "/api/lista?nome=populares&tipo=filme")
        n = len([p for p in apoio.TMDB.pedidos if p[0] == "/3/movie/101"])
        pedir(self.base, "GET", "/api/busca?q=grande")
        self.assertEqual(len([p for p in apoio.TMDB.pedidos if p[0] == "/3/movie/101"]), n, "os detalhes ficam guardados")
        self.assertNotIn("colecao", pedir(self.base, "GET", "/api/lista?nome=populares&tipo=serie")[1]["resultados"][0])
        with mock.patch.object(S, "detalhes", side_effect=S.T.ErroTMDB("x")):
            self.assertIsNone(S.com_colecao([{"tipo": "filme", "tmdb": 1}])[0]["colecao"])
        S.DETALHES.update({(str(i), i): (0, {}) for i in range(3001)})
        S.DETALHES.pop(("filme", 103), None)
        S.detalhes("filme", 103)
        self.assertEqual(len(S.DETALHES), 1, "passou de 3000: começa de novo")

    def test_lista_de_colecoes(self):
        r = pedir(self.base, "GET", "/api/lista?nome=colecoes")[1]
        self.assertEqual([(x["tipo"], x["nome"], x["capa"]) for x in r["resultados"]], [("colecao", "Coleção A Grande Viagem", "/viagem.jpg")], "uma vez só")
        self.assertTrue(r["mais"])
        self.assertFalse(pedir(self.base, "GET", "/api/lista?nome=colecoes&pagina=9")[1]["mais"])
        self.assertTrue(pedir(self.base, "GET", "/api/lista?nome=colecoes&pagina=x")[1]["mais"])
        pedir(self.base, "POST", "/api/ajustes", {"tipos": {"filme": False}})
        self.assertEqual(pedir(self.base, "GET", "/api/lista?nome=colecoes")[1], {"resultados": [], "mais": False})

    def test_categorias(self):
        st, r = pedir(self.base, "POST", "/api/categorias", {"acao": "nova", "tipo": "filme", "nome": "Clássicos"})
        c = r["categorias"]["filme"][0]
        self.assertEqual((st, c["nome"]), (200, "Clássicos"))
        S.adicionar({"tipo": "filme", "tmdb": 101})
        t = S.ler()["titulos"][0]
        pedir(self.base, "POST", "/api/titulo", {"acao": "mudar", "id": t["id"], "campos": {"categoria": c["id"]}})
        st, r = pedir(self.base, "POST", "/api/categorias", {"acao": "renomear", "id": c["id"], "nome": "Os clássicos"})
        self.assertEqual(r["categorias"]["filme"][0]["nome"], "Os clássicos")
        st, r = pedir(self.base, "POST", "/api/categorias", {"acao": "apagar", "id": c["id"]})
        self.assertEqual((r["categorias"]["filme"], S.ler()["titulos"][0]["categoria"]), ([], ""))
        self.assertEqual(pedir(self.base, "POST", "/api/categorias", {"acao": "voar"})[0], 400)
        pedir(self.base, "POST", "/api/categorias", {"acao": "nova", "tipo": "filme", "nome": "Suspense"})
        r = S.usar_ferramenta({"nome": "adicionar", "argumentos": {"nome": "farol", "categoria": "suspense"}})["texto"]
        self.assertIn("Farol Distante (2021) · filme · quero ver · Suspense", r)
        with self.assertRaisesRegex(S.ferramentas.ErroFerramenta, "não é uma categoria"):
            S.usar_ferramenta({"nome": "adicionar", "argumentos": {"nome": "grande viagem 2", "categoria": "Terror"}})


class TestNovidades040(unittest.TestCase):
    """0.4.0: os jogos (o IGDB), o Alterar de vários títulos e a cor das categorias."""

    def setUp(self):
        apoio.limpar()
        apoio.fixar_hoje(self)
        self.base = apoio.Servidor.subir()
        S.guardar_chave(apoio.CHAVE)
        S.guardar_igdb(apoio.IGDB_ID, apoio.IGDB_SEGREDO)

    def get(self, rota):
        return pedir(self.base, "GET", rota)

    def post(self, rota, corpo):
        return pedir(self.base, "POST", rota, corpo)

    def test_conta_do_igdb(self):
        S.guardar_igdb("", "")
        self.assertEqual(self.get("/api/estado")[1]["igdb"], {"chave": False, "fim": "", "erro": ""})
        self.assertEqual(self.post("/api/igdb", {"cliente": "curto", "segredo": "x"})[0], 400)
        st, r = self.post("/api/igdb", {"cliente": apoio.IGDB_ID, "segredo": "segredoerrado0000"})
        self.assertEqual((st, "Twitch não aceitou" in r["erro"]), (502, True))
        self.assertEqual(S.conta_igdb(), ("", ""), "uma conta que não vale não fica guardada")
        st, r = self.post("/api/igdb", {"cliente": apoio.IGDB_ID, "segredo": apoio.IGDB_SEGREDO})
        self.assertEqual(r["igdb"], {"chave": True, "fim": "••••abcd", "erro": ""})
        self.assertNotIn(apoio.IGDB_SEGREDO, json.dumps(self.get("/api/estado")[1]), "o segredo nunca volta para a tela")
        self.assertEqual(self.post("/api/igdb", {})[1]["igdb"]["chave"], False)
        st, r = self.get("/api/busca?q=torre&tipo=jogo")
        self.assertEqual((st, "Falta a conta do IGDB" in r["erro"]), (502, True))
        self.assertIn("Falta a conta", self.get("/api/estado")[1]["igdb"]["erro"] or "Falta a conta", "sem conta, sem erro guardado")

    def test_busca_e_listas_com_os_jogos(self):
        st, r = self.get("/api/busca?q=torre&tipo=jogo")
        self.assertEqual([x["tipo"] for x in r["resultados"]][:2], ["colecao_jogos", "jogo"])
        st, r = self.get("/api/busca?q=grande")
        self.assertEqual({x["tipo"] for x in r["resultados"]}, {"colecao", "filme"}, "Tudo: os filmes e as séries do TMDB com os jogos do IGDB")
        st, r = self.get("/api/busca?q=i")
        self.assertEqual(r["resultados"], [])
        st, r = self.get("/api/lista?nome=alta")
        tipos = [x["tipo"] for x in r["resultados"]]
        self.assertEqual(tipos[:2], ["filme", "jogo"], "um de cada fonte por vez")
        self.assertIn("serie", tipos)
        st, r = self.get("/api/lista?nome=populares&tipo=jogo")
        self.assertEqual([x["nome"] for x in r["resultados"]], ["Torre do Relógio"])
        st, r = self.get("/api/lista?nome=colecoes&tipo=jogo")
        self.assertEqual([(x["tipo"], x["nome"]) for x in r["resultados"]], [("colecao_jogos", "Saga da Torre")])
        st, r = self.get("/api/lista?nome=colecoes")
        self.assertEqual([x["tipo"] for x in r["resultados"]], ["colecao", "colecao_jogos"])
        apoio.TMDB.falha_igdb = 500
        st, r = self.get("/api/lista?nome=alta")
        self.assertEqual((st, {x["tipo"] for x in r["resultados"]}), (200, {"filme", "serie"}), "o IGDB fora do ar: fica o TMDB")
        st, r = self.get("/api/lista?nome=alta&tipo=jogo")
        self.assertEqual(st, 502)
        apoio.TMDB.falha_igdb = 0
        S.guardar_chave("")
        st, r = self.get("/api/lista?nome=alta")
        self.assertEqual({x["tipo"] for x in r["resultados"]}, {"jogo"}, "sem a chave do TMDB, Tudo traz só os jogos")
        S.guardar_igdb("", "")
        st, r = self.get("/api/lista?nome=alta")
        self.assertEqual((st, "chave do TMDB" in r["erro"]), (502, True), "sem nenhuma conta, diz o que falta")
        self.post("/api/ajustes", {"tipos": {"filme": False, "serie": False}})
        st, r = self.get("/api/lista?nome=alta")
        self.assertIn("conta do IGDB", r["erro"], "só os jogos ligados: a conta do IGDB")
        self.assertEqual(self.get("/api/lista?nome=colecoes")[1]["erro"], "Falta a conta do IGDB (Mais › Configurações › Integrações).")

    def test_adicionar_jogos_e_colecao(self):
        st, r = self.post("/api/titulo", {"acao": "adicionar", "tipo": "jogo", "igdb": 701, "situacao": "visto"})
        t = r["titulo"]
        self.assertEqual((t["nome"], t["situacao"], t["plataformas"], t["colecao"]["nome"], t["visto_em"]), ("Torre do Relógio", "visto", ["PC", "PlayStation 5"], "Saga da Torre", "2026-11-24"))
        self.assertTrue(t["capa"] and os.path.exists(S.caminho_capa(t["capa"])))
        self.assertNotIn("onde", t)
        self.assertFalse(self.post("/api/titulo", {"acao": "adicionar", "tipo": "jogo", "igdb": 701})[1]["novo"])
        self.assertEqual(self.post("/api/titulo", {"acao": "adicionar", "tipo": "jogo", "tmdb": 701})[0], 400)
        st, r = self.get("/api/colecao?id=501&tipo=jogo")
        self.assertEqual([(x["nome"], x["situacao"], x["saiu"]) for x in r["colecao"]["itens"]],
                         [("Torre do Relógio", "visto", True), ("Torre do Relógio 2", None, True), ("Torre do Relógio 3", None, False)])
        st, r = self.post("/api/titulo", {"acao": "adicionar_colecao", "colecao": 501, "tipo": "jogo", "situacao": "visto"})
        self.assertEqual((r["novos"], r["ja"], r["fora"], r["tipo"]), (1, 1, 1, "jogo"))
        st, r = self.post("/api/titulo", {"acao": "adicionar_colecao", "colecao": 501, "tipo": "jogo", "situacao": "quero"})
        self.assertEqual(r["novos"], 1)
        self.assertEqual(sorted((x["nome"], x["situacao"]) for x in S.ler()["titulos"]),
                         [("Torre do Relógio", "visto"), ("Torre do Relógio 2", "visto"), ("Torre do Relógio 3", "quero")])
        self.assertEqual(self.post("/api/titulo", {"acao": "adicionar_colecao", "colecao": 501, "tipo": "musica"})[0], 400)
        jogo = next(x for x in S.ler()["titulos"] if x["igdb"] == 701)
        d = S.ler()
        next(x for x in d["titulos"] if x["igdb"] == 701)["capa_igdb"] = "co9velha"
        S.salvar(d)
        st, r = self.post("/api/titulo", {"acao": "atualizar", "id": jogo["id"]})
        self.assertEqual((r["titulo"]["capa_igdb"], r["titulo"]["igdb_em"]), ("co1torre", apoio.HOJE))
        d = S.ler()
        d["titulos"][0]["igdb"] = None
        S.salvar(d)
        self.assertEqual(self.post("/api/titulo", {"acao": "atualizar", "id": d["titulos"][0]["id"]})[1]["erro"], "Esse título não veio do IGDB.")
        st, dado = self.get("/api/img/t_cover_big/co1torre.jpg")
        self.assertEqual((st, dado[:3]), (200, b"\xff\xd8\xff"))
        self.assertEqual(self.get("/api/img/t_cover_big/nada.jpg")[0], 404)

    def test_laco_com_os_jogos(self):
        from datetime import datetime
        S.adicionar({"tipo": "jogo", "igdb": 703, "situacao": "quero"})
        S.adicionar({"tipo": "jogo", "igdb": 702, "situacao": "visto"})
        S.adicionar({"tipo": "filme", "tmdb": 101, "situacao": "visto"})
        agora = datetime(2026, 11, 25, 10)
        ts = {t["nome"]: t for t in S.ler()["titulos"]}
        self.assertTrue(S.precisa_atualizar(ts["Torre do Relógio 3"], agora), "o jogo que vai sair: de dia em dia")
        self.assertFalse(S.precisa_atualizar(ts["Torre do Relógio 2"], agora), "o que já saiu: de semana em semana")
        d = S.ler()
        for t in d["titulos"]:
            t["igdb_em" if t["tipo"] == "jogo" else "tmdb_em"] = "2000-01-01T00:00:00"
        d["titulos"][0]["igdb_em"] = "quebrado"
        S.salvar(d)
        self.assertTrue(S.precisa_atualizar(S.ler()["titulos"][0], agora))
        S.guardar_chave("")
        with mock.patch.object(S.time, "sleep"):
            S.uma_volta(agora)
        ts = {t["nome"]: t for t in S.ler()["titulos"]}
        self.assertEqual((ts["Torre do Relógio 2"]["igdb_em"], ts["A Grande Viagem"]["tmdb_em"]), (apoio.HOJE, "2000-01-01T00:00:00"), "sem a chave do TMDB, só os jogos")
        d = S.ler()
        for t in d["titulos"]:
            t["igdb_em"] = "2000-01-01T00:00:00"
        S.salvar(d)
        apoio.TMDB.falha_igdb = 401
        with mock.patch.object(S.time, "sleep"), mock.patch.object(S, "atualizar", wraps=S.atualizar) as a:
            S.uma_volta(agora)
        self.assertEqual(a.call_count, 1, "o IGDB não aceitou o acesso: para nos jogos")

    def test_alterar_varios(self):
        for n in (101, 103):
            S.adicionar({"tipo": "filme", "tmdb": n, "situacao": "visto"}, "person.ana")
        S.adicionar({"tipo": "serie", "tmdb": 202})
        d = S.ler()
        c = S.R.mudar_categorias(d, {"acao": "nova", "tipo": "filme", "nome": "Clássicos"})
        S.salvar(d)
        ids = [t["id"] for t in S.ler()["titulos"] if t["tipo"] == "filme"]
        st, r = self.post("/api/titulo", {"acao": "lote", "itens": [{"id": i, "campos": {"categoria": c["id"], "quem": ["person.beto"], "notas": "não muda"}} for i in ids]})
        self.assertEqual([(t["categoria"], t["quem"], t["notas"]) for t in r["titulos"]], [(c["id"], ["person.beto"], "")] * 2)
        self.assertEqual(r["rev"], S.ler()["rev"])
        serie = next(t for t in S.ler()["titulos"] if t["tipo"] == "serie")
        st, r = self.post("/api/titulo", {"acao": "lote", "itens": [{"id": ids[0], "campos": {"categoria": ""}}, {"id": serie["id"], "campos": {"categoria": c["id"]}}]})
        self.assertEqual(st, 400, "a categoria é a do tipo de cada título")
        self.assertEqual(next(t for t in S.ler()["titulos"] if t["id"] == ids[0])["categoria"], c["id"], "tudo ou nada")
        for itens in ([], "x", [{"id": "t00000000"}], ["x"]):
            self.assertEqual(self.post("/api/titulo", {"acao": "lote", "itens": itens})[0], 400, itens)
        self.assertEqual(self.post("/api/titulo", {"acao": "lote", "itens": [{"id": ids[0], "campos": {"quem": ["person.zeca"]}}]})[0], 400)

    def test_apagar_varios_e_desfazer(self):
        """0.10.0 (o padrão da família): o Apagar do Selecionar, com o Desfazer: os títulos voltam inteiros, com as capas."""
        for n in (101, 103, 105):
            S.adicionar({"tipo": "filme", "tmdb": n, "situacao": "visto"}, "person.ana")
        ts = S.ler()["titulos"]
        ids = [t["id"] for t in ts[:2]]
        capa = ts[0]["capa"]
        self.assertTrue(capa and os.path.exists(S.caminho_capa(capa)))
        st, r = self.post("/api/titulo", {"acao": "apagar_varios", "ids": ids})
        self.assertEqual((st, sorted(t["id"] for t in r["apagados"]), len(S.ler()["titulos"])), (200, sorted(ids), 1))
        self.assertFalse(os.path.exists(S.caminho_capa(capa)), "a capa vai para a pasta lixo")
        self.assertTrue(os.path.exists(os.path.join(S.CAPAS, "lixo", capa)))
        st, v = self.post("/api/titulo", {"acao": "restaurar", "titulos": r["apagados"]})
        self.assertEqual((st, len(v["titulos"]), len(S.ler()["titulos"])), (200, 2, 3))
        self.assertTrue(os.path.exists(S.caminho_capa(capa)), "o Desfazer traz a capa de volta")
        self.assertEqual(self.post("/api/titulo", {"acao": "restaurar", "titulos": r["apagados"]})[1]["titulos"], [], "o que já está na lista não entra duas vezes")
        # sem a capa no lixo, o título volta sem ela (o laço baixa de novo); um que não está na lista é erro, e nada sai
        st, r = self.post("/api/titulo", {"acao": "apagar_varios", "ids": ids[:1]})
        os.remove(os.path.join(S.CAPAS, "lixo", capa))
        self.assertEqual(self.post("/api/titulo", {"acao": "restaurar", "titulos": r["apagados"]})[1]["titulos"][0]["capa"], "")
        self.assertEqual(self.post("/api/titulo", {"acao": "apagar_varios", "ids": [ids[0], "t00000000"]})[0], 400)
        self.assertEqual(len(S.ler()["titulos"]), 3)
        for ruim in ({"acao": "apagar_varios", "ids": []}, {"acao": "apagar_varios"}, {"acao": "restaurar", "titulos": "x"}):
            self.assertEqual(self.post("/api/titulo", ruim)[0], 400, ruim)
        # as capas no lixo há mais de um dia saem de vez no próximo Apagar
        velha = os.path.join(S.CAPAS, "lixo", "t0000000a.jpg")
        with open(velha, "wb") as f:
            f.write(b"x")
        os.utime(velha, (time.time() - 3 * 86400,) * 2)
        self.post("/api/titulo", {"acao": "apagar_varios", "ids": ids[1:2]})
        self.assertFalse(os.path.exists(velha))

    def test_cor_das_categorias(self):
        st, r = self.post("/api/categorias", {"acao": "nova", "tipo": "jogo", "nome": "Para jogar junto"})
        self.assertEqual(r["categorias"]["jogo"][0]["cor"], "vermelho", "a primeira cor livre")
        st, r = self.post("/api/categorias", {"acao": "nova", "tipo": "jogo", "nome": "Difíceis", "cor": "azul"})
        c = r["categorias"]["jogo"][1]
        self.assertEqual(c["cor"], "azul")
        st, r = self.post("/api/categorias", {"acao": "editar", "id": c["id"], "cor": "verde"})
        self.assertEqual((r["categorias"]["jogo"][1]["nome"], r["categorias"]["jogo"][1]["cor"]), ("Difíceis", "verde"), "editar só a cor")
        st, r = self.post("/api/categorias", {"acao": "editar", "id": c["id"], "nome": "Muito difíceis"})
        self.assertEqual(r["categorias"]["jogo"][1]["nome"], "Muito difíceis")
        self.assertEqual(self.post("/api/categorias", {"acao": "editar", "id": c["id"], "cor": "pink"})[1]["erro"], "Cor desconhecida.")
        self.assertEqual(self.post("/api/categorias", {"acao": "editar", "id": c["id"], "nome": ""})[0], 400)
        lista = [{"cor": x} for x in S.R.CORES[:-1]]
        self.assertEqual(S.R.cor_livre(lista), S.R.CORES[0], "todas usadas: de novo do começo")

    def test_ferramentas_com_os_jogos(self):
        f = S.usar_ferramenta
        r = f({"nome": "adicionar", "argumentos": {"nome": "Torre do Relógio", "tipo": "jogo", "situacao": "visto"}})["texto"]
        self.assertIn("Torre do Relógio (2021) · jogo · jogado", r)
        self.assertTrue(S.ler()["titulos"][0]["capa"])
        r = f({"nome": "adicionar", "argumentos": {"nome": "ilha dos ventos"}})["texto"]
        self.assertIn("Ilha dos Ventos (2025) · jogo · quero jogar", r, "sem tipo, procura nos dois")
        self.assertIn("Já está na lista", f({"nome": "adicionar", "argumentos": {"nome": "ilha dos ventos", "tipo": "jogo"}})["texto"])
        with self.assertRaisesRegex(S.ferramentas.ErroFerramenta, "no IGDB"):
            f({"nome": "adicionar", "argumentos": {"nome": "zzzz", "tipo": "jogo"}})
        with self.assertRaisesRegex(S.ferramentas.ErroFerramenta, "no TMDB nem no IGDB"):
            f({"nome": "adicionar", "argumentos": {"nome": "zzzz"}})
        r = f({"nome": "ver", "argumentos": {"titulo": "Torre do Relógio"}})["texto"]
        self.assertIn("Plataformas: PC, PlayStation 5.", r)
        self.assertIn("Saiu em 15/06/2021.", r)
        self.assertIn("Coleção: Saga da Torre.", r)
        self.assertNotIn("Onde assistir", r)
        r = f({"nome": "lista_pronta", "argumentos": {"lista": "populares", "tipo": "jogo"}})["texto"]
        self.assertEqual(r, "Mais jogados (IGDB):\n- Torre do Relógio (2021) · jogo · na lista: jogado")
        r = f({"nome": "lista_pronta", "argumentos": {"lista": "colecoes"}})["texto"]
        self.assertIn("(TMDB e IGDB)", r)
        self.assertIn("Saga da Torre · coleção de jogos", r)
        self.assertEqual(f({"nome": "lista_pronta", "argumentos": {"lista": "estreias", "tipo": "serie"}})["texto"].split("\n")[0], "Estreias (TMDB):")
        r = f({"nome": "adicionar_colecao", "argumentos": {"nome": "saga da torre", "tipo": "jogo", "situacao": "visto"}})["texto"]
        self.assertEqual(r, "Saga da Torre: 1 jogo posto na lista como Jogado, 1 já estava na lista, 1 ainda não saiu.")
        with self.assertRaisesRegex(S.ferramentas.ErroFerramenta, "coleção «nada» no IGDB"):
            f({"nome": "adicionar_colecao", "argumentos": {"nome": "nada", "tipo": "jogo"}})
        r = f({"nome": "resumo", "argumentos": {}})["texto"]
        self.assertIn("jogos: 1 quero jogar, 2 jogado", r)
        d = S.ler()
        S.R.mudar_categorias(d, {"acao": "nova", "tipo": "jogo", "nome": "Favoritos"})
        S.salvar(d)
        r = f({"nome": "marcar_varios", "argumentos": {"titulos": ["Torre do Relógio", "Torre do Relógio 2", "Torre do Relógio"], "categoria": "favoritos", "quem": ["todos"]}})["texto"]
        self.assertTrue(r.startswith("Feito em 2 títulos:"))
        self.assertEqual({t["categoria"] for t in S.ler()["titulos"] if t["nome"].startswith("Torre do Relógio") and t["nome"] != "Torre do Relógio 3"}, {S.ler()["categorias"]["jogo"][0]["id"]})
        with self.assertRaisesRegex(S.ferramentas.ErroFerramenta, "Diga o que mudar"):
            f({"nome": "marcar_varios", "argumentos": {"titulos": ["Ilha dos Ventos"]}})
        with self.assertRaisesRegex(S.ferramentas.ErroFerramenta, "Diga quais"):
            f({"nome": "marcar_varios", "argumentos": {"titulos": [], "situacao": "visto"}})
        r = f({"nome": "marcar_varios", "argumentos": {"titulos": ["Ilha dos Ventos"], "situacao": "visto"}})["texto"]
        self.assertIn("jogado", r)
        # 0.14.0: o Apagar do Selecionar pelo CorrerIA (tudo ou nada)
        antes = len(S.ler()["titulos"])
        with self.assertRaises(S.ferramentas.ErroFerramenta):
            f({"nome": "apagar_varios", "argumentos": {"titulos": ["Torre do Relógio", "Não existe esse"]}})
        with self.assertRaisesRegex(S.ferramentas.ErroFerramenta, "Diga quais"):
            f({"nome": "apagar_varios", "argumentos": {"titulos": []}})
        self.assertEqual(len(S.ler()["titulos"]), antes)
        r = f({"nome": "apagar_varios", "argumentos": {"titulos": ["Torre do Relógio", "Torre do Relógio 2", "Torre do Relógio"]}})["texto"]
        self.assertEqual(r, "Apagados 2 títulos:\n- Torre do Relógio\n- Torre do Relógio 2")
        self.assertEqual(len(S.ler()["titulos"]), antes - 2)
        apaga = {x["nome"]: x["apaga"] for x in S.ferramentas.FERRAMENTAS}
        self.assertTrue(apaga["apagar_varios"])
        S.R.lote(S.ler(), [{"id": S.ler()["titulos"][0]["id"], "campos": "x"}], None)


class TestNovidades050(unittest.TestCase):
    """0.5.0: a categoria de todos numa coleção."""

    def setUp(self):
        apoio.limpar()
        apoio.fixar_hoje(self)
        self.base = apoio.Servidor.subir()
        S.guardar_chave(apoio.CHAVE)

    def test_categoria_de_todos_na_colecao(self):
        S.adicionar({"tipo": "filme", "tmdb": 101, "situacao": "visto"})
        d = S.ler()
        c = S.R.mudar_categorias(d, {"acao": "nova", "tipo": "filme", "nome": "Sagas"})
        S.salvar(d)
        st, r = pedir(self.base, "POST", "/api/titulo", {"acao": "adicionar_colecao", "colecao": 301, "situacao": "visto", "categoria": c["id"]})
        self.assertEqual((st, r["categoria"], r["novos"], r["ja"]), (200, "Sagas", 1, 1))
        self.assertEqual({t["categoria"] for t in S.ler()["titulos"]}, {c["id"]})
        rev = S.ler()["rev"]
        st, r = pedir(self.base, "POST", "/api/titulo", {"acao": "adicionar_colecao", "colecao": 301, "situacao": "visto", "categoria": c["id"]})
        self.assertEqual(S.ler()["rev"], rev, "nada a mudar, nada gravado")
        for cat in ("c999999", 3):
            self.assertEqual(pedir(self.base, "POST", "/api/titulo", {"acao": "adicionar_colecao", "colecao": 301, "categoria": cat})[1]["erro"], "Categoria desconhecida.")
        r = S.usar_ferramenta({"nome": "adicionar_colecao", "argumentos": {"nome": "grande viagem", "categoria": ""}})["texto"]
        self.assertTrue(r.endswith("Categoria de todos: nenhuma."), r)
        self.assertEqual({t["categoria"] for t in S.ler()["titulos"]}, {""})
        with self.assertRaisesRegex(S.ferramentas.ErroFerramenta, "não é uma categoria"):
            S.usar_ferramenta({"nome": "adicionar_colecao", "argumentos": {"nome": "grande viagem", "categoria": "Nada"}})


class TestNovidades060(unittest.TestCase):
    """0.6.0: as categorias pelo CorrerIA (criar, renomear e apagar)."""

    def setUp(self):
        apoio.limpar()
        apoio.fixar_hoje(self)
        self.base = apoio.Servidor.subir()
        S.guardar_chave(apoio.CHAVE)

    def usar(self, **a):
        return S.usar_ferramenta({"nome": "categoria", "argumentos": a})["texto"]

    def test_criar_renomear_e_apagar(self):
        self.assertEqual(self.usar(acao="nova", tipo="filme", nome="Para a família"), "Categoria criada nos filmes: Para a família.")
        c = S.ler()["categorias"]["filme"][0]
        self.assertIn(c["cor"], S.R.CORES)
        with self.assertRaisesRegex(S.ferramentas.ErroFerramenta, "já existe"):
            self.usar(acao="nova", tipo="filme", nome="para a familia")
        S.adicionar({"tipo": "filme", "tmdb": 101, "situacao": "visto"})
        d = S.ler()
        d["titulos"][0]["categoria"] = c["id"]
        S.salvar(d)
        self.assertEqual(self.usar(acao="renomear", tipo="filme", nome="para a família", novo_nome="Família"), "Categoria renomeada: Para a família → Família.")
        with self.assertRaisesRegex(S.ferramentas.ErroFerramenta, "novo_nome"):
            self.usar(acao="renomear", tipo="filme", nome="Família")
        with self.assertRaisesRegex(S.ferramentas.ErroFerramenta, "não é uma categoria de séries"):
            self.usar(acao="apagar", tipo="serie", nome="Família")
        self.assertEqual(self.usar(acao="apagar", tipo="filme", nome="Família"), "Categoria apagada: Família. 1 título ficou sem categoria.")
        self.assertEqual(S.ler()["titulos"][0]["categoria"], "")
        d = S.ler()
        d["ajustes"]["tipos"] = {"filme": True, "serie": True, "jogo": False}
        S.salvar(d)
        with self.assertRaisesRegex(S.ferramentas.ErroFerramenta, "jogos estão desligados"):
            self.usar(acao="nova", tipo="jogo", nome="Corrida")


class TestNovidades090(unittest.TestCase):
    """0.9.0: a Fala para texto escolhida, os sensores no Home Assistant e os jogos que vão sair no resumo."""

    def setUp(self):
        apoio.limpar()
        apoio.fixar_hoje(self)
        self.base = apoio.Servidor.subir()

    def casa(self):
        d = S.ler()
        d["titulos"] = [S.R.limpar_titulo(t) for t in (
            {"id": "t00000001", "tipo": "serie", "nome": "Mar de Estrelas", "situacao": "quero", "temp": 1, "ep": 3,
             "temporadas": [{"n": 1, "episodios": 8}], "proximo": {"data": "2026-12-02", "temp": 1, "ep": 5, "nome": "O farol"}},
            {"id": "t00000002", "tipo": "jogo", "nome": "Corrida no Vale", "situacao": "quero", "data": "2026-12-10", "plataformas": ["PC", "Console"]},
            {"id": "t00000003", "tipo": "jogo", "nome": "Ilha Antiga", "situacao": "quero", "data": "2027-03-01"},
            {"id": "t00000004", "tipo": "filme", "nome": "Farol Distante", "situacao": "visto", "visto_em": "2026-11-20"},
            {"id": "t00000005", "tipo": "filme", "nome": "Casa no Morro", "situacao": "quero"})]
        S.salvar(d)
        return S.ler()

    def test_fala_e_sensores_nos_ajustes(self):
        st, r = pedir(self.base, "POST", "/api/ajustes", {"fala": "stt.faster_whisper"})
        self.assertEqual((st, r["ajustes"]["fala"], r["ajustes"]["sensores"]), (200, "stt.faster_whisper", False))
        self.assertEqual(pedir(self.base, "POST", "/api/ajustes", {"fala": "light.sala"})[0], 400)
        self.assertEqual(pedir(self.base, "POST", "/api/ajustes", {"sensores": "sim"})[0], 400)
        st, ia = pedir(self.base, "GET", "/api/ia")
        self.assertEqual((ia["fala_escolha"], ia["fala"]["escolha_sumiu"], ia["fala"]["automatico"]), ("stt.faster_whisper", True, "Fala simulada (teste)"))
        pedir(self.base, "POST", "/api/ajustes", {"fala": "stt.outra_simulada"})
        self.assertEqual(pedir(self.base, "GET", "/api/ia")[1]["fala"]["nome"], "Outra fala simulada")
        self.assertEqual(S.R.limpar_dados({"ajustes": {"fala": "x", "sensores": 1}})["ajustes"]["fala"], "", "o que não é stt.… fica vazio")

    def test_os_sensores(self):
        d = self.casa()
        e = S.estados_sensores(d, date(2026, 11, 24))
        self.assertEqual(e["sensor.odisseia_quero_ver"]["state"], 4)
        self.assertEqual({k: e["sensor.odisseia_quero_ver"]["attributes"][k] for k in ("filmes", "séries", "jogos")}, {"filmes": 1, "séries": 1, "jogos": 2})
        self.assertEqual((e["sensor.odisseia_em_andamento"]["state"], e["sensor.odisseia_em_andamento"]["attributes"]["series"]),
                         (1, [{"nome": "Mar de Estrelas", "parou": "T1 E3"}]))
        ep = e["sensor.odisseia_proximo_episodio"]
        self.assertEqual((ep["state"], ep["attributes"]["serie"], ep["attributes"]["episodio"], ep["attributes"]["device_class"]),
                         ("2026-12-02", "Mar de Estrelas", "T1 E5", "date"))
        jg = e["sensor.odisseia_proximo_jogo"]
        self.assertEqual((jg["state"], jg["attributes"]["jogo"], len(jg["attributes"]["proximos"])), ("2026-12-10", "Corrida no Vale", 2))
        self.assertEqual((e["sensor.odisseia_concluidos_no_mes"]["state"], e["sensor.odisseia_concluidos_no_mes"]["attributes"]["titulos"]), (1, ["Farol Distante"]))
        d["ajustes"]["tipos"]["jogo"] = False
        e = S.estados_sensores(d, date(2026, 11, 24))
        self.assertEqual((e["sensor.odisseia_quero_ver"]["state"], e["sensor.odisseia_proximo_jogo"]["state"]), (2, "unknown"), "um tipo desligado sai das contas")
        # publicar: desligado, nada; ligado, os cinco; o mesmo de novo, nada; forçado, de novo
        enviados = []
        with mock.patch.object(S, "TOKEN", "x"), mock.patch.object(S, "ha_post", lambda c, corpo, timeout=0: enviados.append(c)), \
                mock.patch.object(S, "sensores_depois", lambda d: None):
            self.assertEqual(S.publicar_sensores(), 0)
            d = S.ler()
            d["ajustes"]["sensores"] = True
            S.salvar(d)
            S._sensores.update(sig=None)
            self.assertEqual(S.publicar_sensores(), 5)
            self.assertEqual(enviados[-5:], ["/states/" + x for x in S.SENSORES])
            self.assertEqual(S.publicar_sensores(), 0, "nada mudou")
            self.assertEqual(S.publicar_sensores(forcar=True), 5)
        with mock.patch.object(S, "TOKEN", "x"), mock.patch.object(S, "ha_post", side_effect=S.IA.ErroIA("fora")):
            self.assertEqual(S.publicar_sensores(forcar=True), 0)
        self.assertEqual(S.publicar_sensores(), 0, "fora do Home Assistant")
        apagados = []
        with mock.patch.object(S, "TOKEN", "x"), mock.patch.object(S.urllib.request, "urlopen", lambda req, timeout=0: apagados.append(req.get_method()) or io.BytesIO(b"")):
            S.remover_sensores()
        self.assertEqual(apagados, ["DELETE"] * 5)
        S.remover_sensores()  # sem o token, nada
        corridas = []
        with mock.patch.object(S, "TOKEN", "x"), mock.patch.object(S.threading, "Thread", lambda target, **k: mock.Mock(start=lambda: corridas.append(target))):
            S.sensores_depois({"ajustes": {"sensores": True}})
            S.sensores_depois({"ajustes": {"sensores": False}})
        self.assertEqual(corridas, [S.publicar_sensores])
        # ligar e desligar na tela: publica já, ou tira do Home Assistant
        corridas = []
        with mock.patch.object(S.threading, "Thread", lambda target, **k: mock.Mock(start=lambda: corridas.append(target))):
            S.mudar_ajustes({"sensores": False})
            S.mudar_ajustes({"sensores": True})
        self.assertEqual(corridas, [S.remover_sensores, S.publicar_sensores])

    def test_o_resumo_com_os_jogos_que_vao_sair(self):
        d = self.casa()
        t = S.ferramentas.resumo(d, [], date(2026, 11, 24))
        self.assertIn("Jogos que saem nos próximos 30 dias:\n- 10/12/2026: Corrida no Vale (PC, Console)", t)
        self.assertNotIn("Ilha Antiga", t, "só os próximos 30 dias")


class TestPorServico(unittest.TestCase):
    """0.13.0: o por_servico do buscar (a etapa Assinaturas em uso das rondas do CorrerIA 1.39.0)."""

    def test_conta_cada_assinatura_e_os_de_fora(self):
        import ferramentas as F
        ts = [{"nome": f"T{i}", "onde": {"assinatura": ["Cine Lumen"] + (["Tela Azul"] if i < 2 else [])}} for i in range(6)]
        ts.append({"nome": "Sem", "onde": {"alugar": ["Loja Pipoca"]}})
        r = F.texto_servicos(ts, {"tipo": "filme", "situacao": "quero"})
        self.assertEqual(r.splitlines(), ["7 títulos (quero ver), por assinatura (pelo que a JustWatch sabe):",
                                          "- Cine Lumen: 6 títulos (T0, T1, T2, T3, …)", "- Tela Azul: 2 títulos (T0, T1)",
                                          "- Em nenhuma assinatura: 1"])
        self.assertEqual(F.texto_servicos([], {}), "Nenhum título com esses filtros.")


class TestSugerir(unittest.TestCase):
    """0.15.0: o que ver hoje, da lista da casa (sem pesquisar nada)."""

    def test_em_andamento_depois_o_que_esta_numa_assinatura_e_combina(self):
        import ferramentas as F
        def t(i, nome, tipo="filme", sit="quero", **k):
            return dict({"id": f"t{i:08d}", "nome": nome, "original": nome, "ano": 2020, "tipo": tipo, "situacao": sit, "quem": [], "temp": 0, "ep": 0,
                         "temporadas": [], "generos": [], "onde": {}}, **k)
        d = {"titulos": [
            t(1, "Visto Um", sit="visto", generos=["Drama"]), t(2, "Visto Dois", sit="visto", generos=["Drama", "Comédia"]),
            t(3, "Sem Serviço", generos=["Drama"]),
            t(4, "Na Assinatura", generos=["Terror"], onde={"assinatura": ["Cine Lumen"]}),
            t(5, "Combina", generos=["Drama"], onde={"gratis": ["Tela Azul"]}, quem=["person.beto"]),
            t(6, "Série Andando", tipo="serie", temp=1, ep=2, temporadas=[{"n": 1, "episodios": 8}], ultimo={"data": "2026-01-01", "temp": 1, "ep": 8, "nome": ""}),
            t(7, "Jogo Que Vai Sair", tipo="jogo", data="2027-01-01"), t(8, "Jogo Lançado", tipo="jogo", data="2024-01-01")]}
        ps = [{"id": "person.ana", "nome": "Ana"}, {"id": "person.beto", "nome": "Beto"}]
        r = F.texto_sugestoes(d, {}, ps, "2026-11-27T20:00:00").splitlines()
        self.assertEqual(r[0], "5 de 5 títulos para hoje:")
        self.assertTrue(r[1].startswith("- t00000006 | Série Andando (2020) · série: em andamento, parou em "), r[1])
        self.assertEqual(r[2], "- t00000005 | Combina (2020) · filme: em Tela Azul; a casa já viu bastante drama")
        self.assertEqual([x.split(" | ")[1].split(" (")[0] for x in r[3:]], ["Jogo Lançado", "Na Assinatura", "Sem Serviço"])
        self.assertIn("em nenhuma assinatura", r[5])
        self.assertEqual(F.texto_sugestoes(d, {"servico": "lumen", "quantos": 3}, ps, "2026-11-27T20:00:00").splitlines(),
                         ["1 de 1 título para hoje:", "- t00000004 | Na Assinatura (2020) · filme: em Cine Lumen"])
        self.assertEqual(len(F.texto_sugestoes(d, {"tipo": "filme", "quem": ["ana"]}, ps, "2026-11-27T20:00:00").splitlines()), 3, "os de todos, sem o que é só do Beto")
        self.assertEqual(F.texto_sugestoes(d, {"tipo": "jogo", "servico": "x"}, ps, "2026-11-27"), "Nada na lista para sugerir com esses filtros.")
        self.assertEqual(F.chamar("sugerir", {"quantos": 1}, d, ps, None, None, "2026-11-27T20:00:00")[1], False)
