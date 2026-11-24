"""A versão fica num lugar só (odisseia/config.yaml): o servidor lê de lá e o CHANGELOG começa por ela."""
import os
import re
import unittest

from tests.apoio import RAIZ, S


class TestVersao(unittest.TestCase):
    def test_versao_num_lugar_so(self):
        cfg = open(os.path.join(RAIZ, "odisseia", "config.yaml"), encoding="utf-8").read()
        v = re.search(r'^version: "([\d.]+)"$', cfg, re.M).group(1)
        self.assertEqual(S.VERSAO, v)
        log = open(os.path.join(RAIZ, "odisseia", "CHANGELOG.md"), encoding="utf-8").read()
        self.assertTrue(log.startswith(f"# Mudanças\n\n## {v}\n"), "o CHANGELOG começa pela versão do config.yaml")
