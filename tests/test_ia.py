"""0.7.0 (o dono: "no topo das telas opções de chat e de falar igual os outros apps"; "toda a sorte de IA deve estar no
OdisseIA"): a Conversa (a IA com as ferramentas daqui: lê na hora, muda depois do Sim), uma foto na Conversa, o Falar, a
pesquisa na internet, a Memória da IA (a de todos os apps), o Uso da IA e a IA de cada uso. A IA simulada (no computador e
nos testes) e a de verdade com o Home Assistant de mentira (ha_post). Títulos e pessoas inventados."""
import base64
import json
import os
import unittest
from datetime import datetime
from unittest import mock

from tests import apoio
from tests.apoio import S

IA = S.IA


class Base(unittest.TestCase):
    def setUp(self):
        apoio.limpar()
        apoio.fixar_hoje(self)
        self.base = apoio.Servidor.subir()
        S.guardar_chave(apoio.CHAVE)

    def pedir(self, metodo, rota, corpo=None, cab=None):
        return apoio.pedir(self.base, metodo, rota, corpo, cab)

    def falar(self, texto, **mais):
        st, r = self.pedir("POST", "/api/conversa", dict({"texto": texto}, **mais))
        self.assertEqual(st, 200, r)
        return r


class TestConversa(Base):
    def test_uma_pergunta_le_e_responde(self):
        S.adicionar({"tipo": "filme", "tmdb": 101})
        r = self.falar("Quais filmes eu quero ver?")
        self.assertEqual([m["papel"] for m in r["mensagens"]], ["eu", "ia"])
        self.assertTrue(r["mensagens"][1]["texto"].startswith("Pelo que vi:"))
        self.assertIsNone(r["pendente"])
        self.assertEqual(self.pedir("GET", "/api/conversa")[1]["mensagens"], r["mensagens"], "fica guardada")

    def test_uma_mudanca_espera_o_sim(self):
        r = self.falar("quero ver Farol Distante")
        ia = r["mensagens"][-1]
        self.assertIn("Vou fazer isto:\n- Pôr Farol Distante na lista", ia["texto"])
        self.assertTrue(ia["sim"])
        self.assertEqual(r["pendente"][0]["ferramenta"], "adicionar")
        self.assertEqual(S.ler()["titulos"], [], "nada antes do Sim")
        st, r = self.pedir("POST", "/api/conversa/sim", {"sim": True})
        self.assertEqual(st, 200, r)
        self.assertEqual([t["nome"] for t in S.ler()["titulos"]], ["Farol Distante"])
        self.assertEqual(r["mensagens"][-1]["texto"], "Feito:\n- Adicionado: Farol Distante (2021) · filme · quero ver · Ana", "sem o id")
        self.assertEqual(r["mensagens"][-2].get("decidido"), "sim")
        self.assertNotIn("sim", r["mensagens"][-2])
        self.assertIsNone(r["pendente"])
        self.assertIsNone(S.CORRERIA.ultimo, "a Conversa daqui não conta como uso do CorrerIA")
        self.assertEqual(self.pedir("POST", "/api/conversa/sim", {"sim": True})[0], 400, "nada esperando o Sim")

    def test_o_nao_e_outra_mensagem_descartam(self):
        self.falar("quero ver Farol Distante")
        r = self.pedir("POST", "/api/conversa/sim", {"sim": False})[1]
        self.assertEqual(r["mensagens"][-1]["texto"], "Tudo bem, não mudei nada.")
        self.assertEqual(r["mensagens"][-2]["decidido"], "nao")
        self.falar("quero ver Farol Distante")
        r = self.falar("Oi")
        self.assertIsNone(r["pendente"], "outra mensagem descarta a mudança")
        self.assertFalse(any(m.get("sim") for m in r["mensagens"]))
        self.assertEqual(S.ler()["titulos"], [])

    def test_o_que_o_app_recusa_depois_do_sim_e_dito(self):
        self.falar("quero ver Um Título Que Não Existe")
        r = self.pedir("POST", "/api/conversa/sim", {"sim": True})[1]
        self.assertTrue(r["mensagens"][-1]["texto"].startswith("Não deu:\n- Pôr Um Título Que Não Existe na lista: "))
        self.assertTrue(r["mensagens"][-1]["erro"])

    def test_uma_foto_vai_para_a_ia(self):
        foto = base64.b64encode(apoio.CAPAS["/viagem.jpg"]).decode()
        r = self.falar("", anexo={"tipo": "image/jpeg", "b64": foto, "mini": "data:image/jpeg;base64,AAAA"})
        eu = r["mensagens"][0]
        self.assertEqual((eu["texto"], eu["foto"], eu["mini"]), ("", True, "data:image/jpeg;base64,AAAA"))
        self.assertIn("Pôr Farol Distante (filme) em Quero ver", r["mensagens"][1]["texto"])
        for anexo, parte in (({"tipo": "application/pdf", "b64": foto}, "Mande uma foto"), ({"tipo": "image/png", "b64": "!!"}, "Não consegui ler"),
                             ({"tipo": "image/png", "b64": ""}, "não veio")):
            st, e = self.pedir("POST", "/api/conversa", {"anexo": anexo})
            self.assertEqual(st, 400)
            self.assertIn(parte, e["erro"])
        self.assertIn("Escreva", self.pedir("POST", "/api/conversa", {"texto": "  "})[1]["erro"])

    def test_lembrar_vai_para_a_memoria_de_todos_os_apps_depois_do_sim(self):
        self.falar("lembre que a Ana não gosta de terror")
        self.assertEqual(self.pedir("GET", "/api/memoria-ia")[1]["lista"], [])
        r = self.pedir("POST", "/api/conversa/sim", {"sim": True})[1]
        self.assertIn("Guardei na Memória da IA: a Ana não gosta de terror", r["mensagens"][-1]["texto"])
        m = self.pedir("GET", "/api/memoria-ia")[1]
        self.assertEqual([(x["texto"], x["app"]) for x in m["lista"]], [("a Ana não gosta de terror", "OdisseIA")])
        self.assertTrue(os.path.exists(S.MEMORIA_ARQ))

    def test_nova_conversa_e_a_ia_desligada(self):
        self.falar("Oi")
        self.assertEqual(self.pedir("POST", "/api/conversa/nova", {})[1], {"mensagens": [], "pendente": None})
        self.pedir("POST", "/api/ajustes", {"ia": False})
        st, e = self.pedir("POST", "/api/conversa", {"texto": "Oi"})
        self.assertEqual((st, e["erro"]), (409, "A IA está desligada no OdisseIA (Configurações › Integrações › IA)."))
        self.assertEqual(self.pedir("POST", "/api/fala", b"\0" * 32000, {"Content-Type": "application/octet-stream"})[0], 409)

    def test_um_erro_da_ia_fica_na_conversa(self):
        with mock.patch.object(S, "IA_MOCK", False), mock.patch.object(S, "ha_post", side_effect=IA.ErroIA('{"code": 503, "status": "UNAVAILABLE"}')):
            r = self.falar("Oi")
        self.assertEqual(r["mensagens"][-1]["texto"], "Não consegui responder agora: " + S.IA_FORA)
        self.assertTrue(r["mensagens"][-1]["erro"])


class TestIADeVerdade(Base):
    """O caminho com o Home Assistant: o pedido (a Memória da IA na frente, a guarda no fim, a IA de cada uso, a foto como
    anexo pela pasta media) e o Uso da IA."""

    def setUp(self):
        super().setUp()
        self.pedidos = []
        self.media = os.path.join(apoio.PASTA, "media")
        os.makedirs(self.media, exist_ok=True)
        for p in (mock.patch.object(S, "IA_MOCK", False), mock.patch.object(S, "MEDIA_ROOT", self.media)):
            p.start()
            self.addCleanup(p.stop)

    def ha(self, respostas):
        def post(caminho, corpo, timeout=180):
            self.pedidos.append((caminho, json.loads(json.dumps(corpo))))
            if corpo.get("attachments"):
                nome = corpo["attachments"][0]["media_content_id"].rsplit("/", 1)[1]
                self.assertTrue(os.path.exists(os.path.join(self.media, "odisseia", "ia-temp", nome)), "a foto está na pasta media durante o pedido")
            r = respostas.pop(0)
            if isinstance(r, Exception):
                raise r
            return {"service_response": {"data": r}}
        return mock.patch.object(S, "ha_post", side_effect=post)

    def test_le_responde_e_registra_o_uso(self):
        S.adicionar({"tipo": "filme", "tmdb": 101})
        self.pedir("POST", "/api/memoria-ia", {"acao": "nova", "texto": "Sexta é dia de filme"})
        self.pedir("POST", "/api/ajustes", {"ia_conversa": "ai_task.conversa", "ia_pesquisa": "ai_task.busca"})
        with self.ha([{"chamar": [{"ferramenta": "odisseia_buscar", "argumentos": "{\"situacao\": \"quero\"}"}, {"ferramenta": "nao_existe"}], "resposta": ""},
                      {"chamar": [{"ferramenta": "pesquisar", "argumentos": {"json": "{\"pesquisa\": \"críticas de A Grande Viagem\"}"}}]},
                      "A crítica gostou.",
                      '```json\n{"resposta": "Você quer ver *A Grande Viagem*; a crítica gostou."}\n```']):
            r = self.falar("O que eu quero ver?")
        self.assertEqual(r["mensagens"][-1]["texto"], "Você quer ver *A Grande Viagem*; a crítica gostou.")
        caminho, p1 = self.pedidos[0]
        self.assertEqual(caminho, "/services/ai_task/generate_data?return_response")
        self.assertEqual((p1["task_name"], p1["entity_id"]), ("OdisseIA", "ai_task.conversa"))
        self.assertTrue(p1["instructions"].startswith(S.memoria_ia.para_a_ia(S.MEMORIA_ARQ)))
        self.assertTrue(p1["instructions"].endswith(S.IA_SO_MATERIAL))
        self.assertIn("Pessoa: O que eu quero ver?", p1["instructions"])
        p2 = self.pedidos[1][1]["instructions"]
        self.assertIn('buscar({"situacao": "quero"}) → 1 títulos:', p2)
        self.assertIn("A Grande Viagem (2019)", p2)
        self.assertIn("nao_existe → ERRO: essa ferramenta não existe", p2)
        self.assertEqual(self.pedidos[2][1]["entity_id"], "ai_task.busca", "a pesquisa vai pela IA de pesquisar")
        self.assertIn("críticas de A Grande Viagem", self.pedidos[2][1]["instructions"])
        self.assertIn("pesquisar({\"pesquisa\": \"críticas de A Grande Viagem\"}) → A crítica gostou.", self.pedidos[3][1]["instructions"])
        u = self.pedir("GET", "/api/uso")[1]
        self.assertEqual((u["hoje"]["chamadas"], u["hoje"]["tipos"]), (4, {"conversa": 3, "pesquisa": 1}))
        self.assertEqual(u["ultimas"][0]["ia"], "ai_task.conversa")

    def test_a_foto_vai_como_anexo_pela_ia_de_fotos(self):
        self.pedir("POST", "/api/ajustes", {"ia_fotos": "ai_task.fotos"})
        foto = base64.b64encode(apoio.CAPAS["/viagem.jpg"]).decode()
        with self.ha([{"resposta": "É um pôster do Farol Distante. Quer pôr na lista?"}]):
            r = self.falar("o que é isto?", anexo={"tipo": "image/jpeg", "b64": foto})
        p = self.pedidos[0][1]
        self.assertEqual(p["entity_id"], "ai_task.fotos")
        self.assertEqual(p["attachments"][0]["media_content_type"], "image/jpeg")
        self.assertIn("você vê a foto", p["instructions"])
        self.assertEqual(os.listdir(os.path.join(self.media, "odisseia", "ia-temp")), [], "a foto sai depois")
        self.assertTrue(r["mensagens"][-1]["texto"].startswith("É um pôster"))
        self.assertEqual(self.pedir("GET", "/api/uso")[1]["hoje"]["tipos"], {"foto": 1})

    def test_as_guardas_antes_do_sim(self):
        """A mudança com argumento errado volta para a IA; dizer que fez sem chamar volta; apagar de uma foto sem pedir volta."""
        S.adicionar({"tipo": "filme", "tmdb": 101})
        t = S.ler()["titulos"][0]["id"]
        with self.ha([{"chamar": [{"ferramenta": "marcar", "argumentos": {"titulo": t, "situacao": "vista"}}]},
                      {"resposta": "Pronto, marquei como visto!"},
                      {"chamar": [{"ferramenta": "marcar", "argumentos": {"titulo": t, "situacao": "visto"}, "resumo": "Marcar A Grande Viagem como Visto"}],
                       "resposta": "Já marquei. Pode confirmar?"}]):
            r = self.falar("já vi A Grande Viagem")
        p2 = self.pedidos[1][1]["instructions"]
        self.assertIn("situacao: «vista» não vale; vale: quero, visto", p2)
        self.assertIn("ERRO: você escreveu que fez ou vai fazer uma mudança", self.pedidos[2][1]["instructions"])
        self.assertEqual(r["mensagens"][-1]["texto"], "Vou fazer isto:\n- Marcar A Grande Viagem como Visto\n\nToque em *Sim* para confirmar.")
        self.pedidos.clear()
        foto = base64.b64encode(apoio.CAPAS["/viagem.jpg"]).decode()
        with self.ha([{"chamar": [{"ferramenta": "apagar", "argumentos": {"titulo": t}}]}, {"resposta": "Vi o pôster."}]):
            r = self.falar("o que é isto?", anexo={"tipo": "image/jpeg", "b64": foto})
        self.assertIn("a pessoa não falou em apagar", self.pedidos[1][1]["instructions"])
        self.assertIsNone(r["pendente"])

    def test_a_cota_e_sem_resposta(self):
        with self.ha([IA.ErroIA("429 RESOURCE_EXHAUSTED")]):
            self.assertEqual(self.falar("Oi")["mensagens"][-1]["texto"], "Não consegui responder agora: " + S.IA_COTA)
        with self.ha([None]):
            self.assertEqual(self.falar("Oi")["mensagens"][-1]["texto"], "Não consegui responder agora: A IA não devolveu resposta.")
        u = self.pedir("GET", "/api/uso")[1]["hoje"]
        self.assertEqual((u["chamadas"], u["cota"], u["erros"]), (2, 1, 1))


class TestFalarEAjustes(Base):
    def test_falar(self):
        cab = {"Content-Type": "application/octet-stream"}
        st, r = self.pedir("POST", "/api/fala", b"\0" * 100, cab)
        self.assertEqual((st, r["erro"]), (400, "Não ouvi nada. Toque no microfone e fale."))
        st, r = self.pedir("POST", "/api/fala", b"\0" * 32000, cab)
        self.assertEqual((st, r["texto"]), (200, "Quais séries estão em andamento?"))

    def test_ia_info_e_a_ia_de_cada_uso(self):
        i = self.pedir("GET", "/api/ia?novo=1")[1]
        self.assertEqual((i["ligada"], i["pronta"], i["entidades"][0]["id"], i["fala"]["pronta"]), (True, True, "ai_task.simulada", True))
        st, e = self.pedir("POST", "/api/ajustes", {"ia_fotos": "camera.sala"})
        self.assertEqual(st, 400)
        self.assertIn("ai_task", e["erro"])
        self.pedir("POST", "/api/ajustes", {"ia_conversa": "ai_task.x", "ia_fotos": ""})
        a = S.ler()["ajustes"]
        self.assertEqual((a["ia_conversa"], a["ia_fotos"], S.ia_ent(S.ler(), "fotos"), S.ia_ent(S.ler(), "pesquisa")), ("ai_task.x", "", "ai_task.x", "ai_task.x"))
        with mock.patch.object(S, "IA_MOCK", False):
            i = S.ia_info(True)
        self.assertEqual((i["pronta"], i["motivo"]), (False, "Fora do Home Assistant não há IA."))

    def test_memoria(self):
        st, r = self.pedir("POST", "/api/memoria-ia", {"acao": "nova", "texto": "Beto prefere jogos de corrida"})
        self.assertEqual((st, r["max"], r["lista"][0]["texto"]), (200, 60, "Beto prefere jogos de corrida"))
        st, r = self.pedir("POST", "/api/memoria-ia", {"acao": "apagar", "id": r["lista"][0]["id"]})
        self.assertEqual(r["lista"], [])
        self.assertEqual(self.pedir("POST", "/api/memoria-ia", {"acao": "nova", "texto": ""})[0], 400)


class TestAgente(unittest.TestCase):
    """O agente sozinho: o JSON de volta, os argumentos, a validação e o que passa do limite."""

    def test_extrair_e_argumentos(self):
        self.assertEqual(IA.extrair_json('texto {"resposta": "oi"} mais'), {"resposta": "oi"})
        self.assertEqual(IA.extrair_json('{"resposta": "linha \\n quebrada'), {"resposta": "linha \n quebrada"}, "um JSON sem fechar: a resposta, limpa")
        self.assertEqual(IA.extrair_json("só texto"), {"resposta": "só texto"})
        self.assertEqual(IA.argumentos_de('{"a": 1}'), {"a": 1})
        self.assertEqual(IA.argumentos_de({"json": '{"json": "{\\"b\\": 2}"}'}), {"b": 2})
        self.assertEqual(IA.argumentos_de("não é json"), {})
        self.assertEqual(IA.argumentos_de([1]), {})

    def test_validar(self):
        e = {"properties": {"n": {"type": "integer"}, "s": {"type": "string", "enum": ["a", "b"]}}, "required": ["n"]}
        self.assertEqual(IA.validar(e, {"n": True, "s": "c", "x": 1}), ["n tem de ser integer", "s: «c» não vale; vale: a, b", "x não existe nesta ferramenta (os campos: n, s)"])
        self.assertEqual(IA.validar(e, {}), ["falta n"])
        self.assertEqual(IA.validar(e, "x"), ["mande os argumentos como um objeto"])

    def test_mais_mudancas_que_o_limite_e_leituras_demais(self):
        lidas = []
        respostas = [{"chamar": [{"ferramenta": "ver", "argumentos": {"titulo": str(i)}} for i in range(6)]},
                     {"chamar": [{"ferramenta": "apagar", "argumentos": {"titulo": str(i)}} for i in range(14)]}]
        ag = IA.Agente(S.ferramentas.lista(), lambda n, a: (lidas.append(a) or "ok", False), lambda i, f: respostas.pop(0))
        r = ag.responder([{"papel": "eu", "texto": "apague tudo"}], {}, datetime(2026, 11, 24, 10))
        self.assertEqual(len(lidas), 4, "no máximo 4 leituras por vez")
        self.assertEqual(len(r["pendente"]), IA.MAX_ACOES)
        self.assertIn("(Mais 2 ficam para depois", r["resposta"])
        self.assertTrue(r["pendente"][0]["resumo"].startswith("Apagar (titulo: 0)"))

    def test_sem_resposta_nas_rodadas(self):
        ag = IA.Agente(S.ferramentas.lista(), lambda n, a: ("ok", False), lambda i, f: {"resposta": ""})
        self.assertEqual(ag.responder([{"papel": "eu", "texto": "oi"}], {})["resposta"], IA.SEM_RESPOSTA)
        ag = IA.Agente(S.ferramentas.lista(), lambda n, a: ("ok", False), lambda i, f: {"resposta": "Adicionei!"})
        self.assertEqual(ag.responder([{"papel": "eu", "texto": "oi"}], {})["resposta"], IA.SEM_MUDANCA)

    def test_o_pedido_do_sim_no_historico_vira_nota(self):
        t = "Ok.\n\nVou fazer isto:\n- Pôr X\n\nToque em *Sim* para confirmar."
        self.assertEqual(IA.sem_o_pedido_do_sim(t), "Ok.\n\n(O app mostrou esta mudança, com os botões Sim e Não:\n- Pôr X)")


if __name__ == "__main__":
    unittest.main()
