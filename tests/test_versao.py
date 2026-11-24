"""A versão fica num lugar só (odisseia/config.yaml): o servidor lê de lá e o CHANGELOG começa por ela."""
import os
import re
import unittest

try:
    import yaml  # o GitHub instala; no computador, sem ele, fica só a conferência de cada linha
except ImportError:
    yaml = None

from tests.apoio import RAIZ, S


class TestVersao(unittest.TestCase):
    def test_versao_num_lugar_so(self):
        cfg = open(os.path.join(RAIZ, "odisseia", "config.yaml"), encoding="utf-8").read()
        v = re.search(r'^version: "([\d.]+)"$', cfg, re.M).group(1)
        self.assertEqual(S.VERSAO, v)
        log = open(os.path.join(RAIZ, "odisseia", "CHANGELOG.md"), encoding="utf-8").read()
        self.assertTrue(log.startswith(f"# Mudanças\n\n## {v}\n"), "o CHANGELOG começa pela versão do config.yaml")

    def test_config_e_um_yaml_que_o_home_assistant_le(self):
        """0.1.1 (o dono: adicionou o repositório e o app não aparecia na loja): um «: » solto na descrição quebrava o YAML
        e o Home Assistant pulava o app. Cada valor sem aspas não pode ter «: » nem « #»; com o PyYAML, o arquivo todo."""
        for arq in (os.path.join(RAIZ, "odisseia", "config.yaml"), os.path.join(RAIZ, "repository.yaml")):
            texto = open(arq, encoding="utf-8").read()
            for n, linha in enumerate(texto.splitlines(), 1):
                m = re.match(r"^\s*[A-Za-z_]+:\s+(.+)$", linha)
                if m and not m.group(1).startswith(('"', "'")):
                    self.assertNotRegex(m.group(1), r": | #", f"{os.path.basename(arq)}, linha {n}: ponha o valor entre aspas")
            if yaml:
                d = yaml.safe_load(texto)
                self.assertIsInstance(d, dict)
                if arq.endswith("config.yaml"):
                    for k in ("name", "version", "slug", "description", "arch", "ingress", "ingress_port", "panel_icon", "url"):
                        self.assertIn(k, d)
                    self.assertEqual(d["slug"], "odisseia")
