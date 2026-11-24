# Testes

- `tests/run.sh`: todos (servidor e tela). A tela precisa do playwright: `pip install playwright && python -m playwright install chromium`.
- `tests/run.sh --cobertura`: a cobertura de linhas do servidor (`odisseia/app/*.py`), que fica acima de 95%.

| Arquivo | O que confere |
|---|---|
| `apoio.py` | o TMDB de mentira (títulos e capas inventados) e o servidor numa porta livre |
| `test_regras.py` | limpar, achar, criar, mudar, o próximo episódio e a série que acaba |
| `test_tmdb.py` | a chave nas duas formas, a busca, os detalhes, onde assistir no Brasil, as capas e os erros |
| `test_servidor.py` | as rotas: a chave, adicionar, mudar, as capas, os Dados, o laço, o CorrerIA |
| `test_tela.py` | a tela no Chromium: adicionar, marcar, o Voltar, Buscar, Vistos, Configurações, Sobre, 320 px e o computador |
| `test_versao.py` | a versão do config.yaml e a seção do CHANGELOG |
