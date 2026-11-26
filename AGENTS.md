# Instruções para quem for mexer neste repositório (pessoas ou IAs)

> Leia também o `PADROES.md`: os padrões da família, iguais em todos os apps. Este arquivo diz o que é só deste app e como cada padrão é feito aqui.

OdisseIA é um app (add-on) do Home Assistant para os filmes, as séries e os jogos da casa: o que cada pessoa quer ver (ou
jogar) e já viu (ou jogou), o episódio em que parou, a categoria, os episódios e os jogos que vão sair e onde assistir no
Brasil. Os filmes e as séries vêm do TMDB (com a chave grátis de cada casa; onde assistir é da JustWatch, pelo TMDB); os
jogos, do IGDB (com o Client ID e o Client Secret de um app grátis da casa no Twitch Developers). Faz parte de uma família de
apps do mesmo dono, que conversam entre si pelo Home Assistant:

| App | Repositório | O que é |
|---|---|---|
| OdisseIA | `diegozapella63/OdisseIA` (este) | filmes e séries da casa |
| CronologIA | `diegozapella63/cronologia-ha` | calendário, rotinas, remédios, placar |
| ResolvIA | `diegozapella63/resolvia-ha` | listas de tarefas, pontos, repetição |
| InventarIA | `diegozapella63/inventario-ha` | inventário da casa |
| GerencIA | `diegozapella63/gerencia-ha` | finanças (sabe quais assinaturas a casa paga) |
| EconomIA | `diegozapella63/economia-ha` | lista de compras e preços |
| MemorIA | `diegozapella63/memoria-ha` | cadernos de anotação |
| CorrerIA | `diegozapella63/CorrerIA-ha` | o WhatsApp, o Claude e o Gemini: usa as ferramentas daqui |

O Home Assistant instala direto do GitHub (`repository.yaml` + `odisseia/config.yaml`), a partir da branch `main`: o que
está em `main` é o que os usuários recebem. No `config.yaml`, `panel_admin: false`: a lista é da casa toda.

## Estrutura

```
odisseia/config.yaml          versão (o único lugar onde ela é escrita) e opções do app
odisseia/CHANGELOG.md         o que mudou em cada versão (o HA mostra ao atualizar; começa com "# Mudanças")
odisseia/DOCS.md              manual do usuário (aba Documentação no HA)
odisseia/app/server.py        servidor HTTP (Python, só biblioteca padrão): dados, capas, TMDB, Dados, CorrerIA
odisseia/app/regras.py        as regras dos títulos (limpar, achar, criar, mudar, próximo episódio): as mesmas da tela e do CorrerIA
odisseia/app/tmdb.py          o TMDB: busca, detalhes em pt-BR, onde assistir no Brasil (JustWatch), capas; a chave v3 ou o token v4
odisseia/app/igdb.py          o IGDB: o acesso pela Twitch (na memória), a busca (com as coleções), as listas (a popularidade do
                              IGDB), as coleções, os detalhes e as capas; consultas em Apicalypse (POST)
odisseia/app/ferramentas.py   as ferramentas do CorrerIA (resumo, buscar, ver, adicionar, marcar, proximo_episodio, apagar)
odisseia/app/ia.py            a Conversa: a IA do Home Assistant com as ferramentas daqui (lê na hora, muda depois do Sim)
odisseia/app/fala.py          o Falar: a fala para texto do Home Assistant (o arquivo do CorrerIA)
odisseia/app/uso.py           o Uso da IA (o do CorrerIA); memoria_ia.py: a Memória da IA de todos os apps (a dos outros apps em Python)
odisseia/app/www/             a tela: index.html, app.js (JavaScript puro, sem build), styles.css, fontes; selectsheet.js,
                              hatema.js e textareas.js são os dos outros apps (tools/iguais.py)
tests/                        testes (unittest; a tela com playwright); tests/apoio.py tem o TMDB e o IGDB de mentira (inventados)
dev/rodar.py                  o app no computador com o TMDB de mentira
tools/cobertura.py            a cobertura de linhas do servidor (fica acima de 95%)
tools/fazer_logo.py           desenha odisseia/icon.png e odisseia/logo.png
tools/prints_readme.py        refaz as capturas do README (docs/*.png) com a casa do dev/rodar.py (o TMDB e o IGDB de mentira)
tools/iguais.py               os arquivos iguais aos dos outros apps (o PADROES.md, as caixas de seleção, o fala.py, o uso.py…)
```

Os dados ficam em `/data/odisseia.json` (`{versao, rev, titulos, categorias, ajustes}`; cada gravação soma 1 em `rev`, e a
tela confere `/api/rev` a cada 20 s), as capas em `/data/capas/<id>.jpg`, a chave do TMDB e a conta do IGDB em
`/data/segredos.json` (600; nunca voltam para a tela, só o fim `••••abcd`), as versões automáticas em `/data/versoes` (as 5 últimas: uma por dia e antes de
importar, restaurar ou apagar tudo) e os backups em `share/odisseia/backups` (os 10 últimos). Um título:
`{id: t + 8 hex, tipo: filme|serie|jogo, tmdb, nome, original, ano, capa, capa_tmdb, sinopse, generos, situacao:
quero|visto, quem: [person.*], categoria (c + 6 hex ou ""), notas, visto_em, tmdb_em, onde: {assinatura, gratis, alugar,
comprar, link}}`, no filme `colecao: {id, nome, capa}` e, na série, `temporadas: [{n, episodios}]` (sem a 0, dos especiais), `temp`/`ep` (o último visto; 0/0
nenhum), `proximo` e `ultimo` (`{data, temp, ep, nome}`) e `fim`; no jogo, sem `onde`, `capa_tmdb` e `tmdb_em`, com
`igdb`, `capa_igdb`, `igdb_em`, `data`, `plataformas`, `link` e `colecao`. O laço do servidor (`uma_volta`) atualiza as
séries em Quero ver e os jogos que vão sair uma vez por dia e o resto uma vez por semana.

## Rodar no computador

```
python3 dev/rodar.py          # http://127.0.0.1:8099, com o TMDB de mentira e Ana e Beto
python3 dev/rodar.py --vazio  # sem títulos
```

À mão: `ODISSEIA_DEV=1 ODISSEIA_DATA=/tmp/o/data ODISSEIA_SHARE=/tmp/o/share python3 odisseia/app/server.py` (o TMDB de
verdade, com a sua chave em Configurações). `ODISSEIA_TMDB` e `ODISSEIA_TMDB_IMG` trocam o TMDB, `ODISSEIA_PORTA` a porta,
`ODISSEIA_URL_INTERNA` o endereço que o CorrerIA usa e `ODISSEIA_HA_API` o Home Assistant.

## Checklist de toda mudança

1. `git pull --rebase` antes de começar.
2. Implementar. Servidor: só biblioteca padrão do Python. Tela: `odisseia/app/www/app.js` (um IIFE; ações por `data-a`
   em `ACOES`; janelas por `abrirFolha`/`fecharFolha`). Uma regra nova dos títulos vai no `regras.py` (a tela e o CorrerIA
   usam a mesma). Toda mudança pensada também para a IA e o CorrerIA (as ferramentas do `ferramentas.py`).
3. Testar: `tests/run.sh` (servidor e tela) e `tests/run.sh --cobertura` (acima de 95% das linhas). Toda mudança ou bug
   corrigido vem com o teste dele.
4. Subir a versão só em `odisseia/config.yaml` (`version:`); o servidor lê de lá e o `tests/test_versao.py` confere o
   CHANGELOG. Correção = patch (0.1.0 → 0.1.1); novidade = minor (0.1.x → 0.2.0).
5. `odisseia/CHANGELOG.md`: nova seção no topo, em português, do ponto de vista de quem usa.
6. `odisseia/DOCS.md` quando muda o comportamento ou aparece algo novo.
7. Commit em `main` com mensagem em português ("OdisseIA 0.2.0: ..."), `git pull --rebase` e push. O GitHub roda os
   testes a cada push (aba Actions).

## Arquivos iguais em todos os apps

A lista fica em `tools/iguais.py` e as regras, em **Arquivos iguais** e **Os apps conversam** do `PADROES.md`.

## Como os apps conversam

- **CorrerIA → OdisseIA** (o contrato de todos os apps da família; ver o AGENTS.md do CorrerIA): com **Mais ›
  Configurações › Integrações › CorrerIA** ligado (`ajustes.correria`, desligado de início), este app grava
  `share/odisseia/correria.json` (`app: odisseia`, `nome`, `assunto`, `versao`, `url`, `ip_url`, `chave`, `ferramentas`,
  `gravado_em`; 600; a chave em `/data/correria.key`) e responde, só com `Authorization: Bearer <chave>`, em
  `GET /api/integracao/ferramentas` → `{versao, instrucoes, ferramentas}` e `POST {nome, argumentos, pessoa, cliente}` →
  `{texto}` (400 `{erro}` com o que vale; 404 ferramenta desconhecida). O `adicionar` procura no TMDB pelo nome
  (`ferramentas.melhor`: o tipo e o ano mandam, depois o nome igual).
- O TMDB pede o crédito: o Sobre e Integrações dizem que os dados vêm do TMDB e que o app não é endossado por ele; onde
  assistir diz "Dados da JustWatch" (obrigatório no TMDB).

## Como o dono gosta (interface)

- Tudo em português do Brasil, sem palavras em inglês na tela. **Menos é mais**: textos curtos, sem avisos repetidos.
- Celular primeiro (390 px; nada passa da largura em 320 px); com 1000 px ou mais, a barra lateral (`#lado`) no lugar da de
  baixo e as janelas no meio. Tema claro e escuro.
- A barra de baixo: **Agora**, **Buscar**, o **+** (Adicionar, só o ícone), **Concluídos** e **Mais**.
- **Inativos no fim, recolhidos**: os **Abandonados (n)** no fim do Buscar, recolhidos (abrem num toque).
- **Caixas de seleção no visual do app** (`selectsheet.js`): a temporada e o episódio são `<select class="inp select">`.
- Dados de exemplo e de testes sempre inventados (Ana, Beto, títulos inventados): nunca a lista real do dono.

**Padrão da família**: as regras de todos os apps estão no `PADROES.md` (igual nos 8 repositórios; leia antes de mexer). Como cada uma é feita aqui:
- Ícones: `cab()` e `card()` (o cabeçalho com o ícone), `lbl()` (o ícone pequeno antes do título de cada campo) e `ICONE_TELA`; o `padrao()` do `tests/test_tela.py` confere os cartões e os botões.
- Contrair e expandir: o `cab()` com `data-dobra` e `odisseia-fechadas` no localStorage.

0.2.0 (o dono: "adicionar uma série inteira como vista"; "uma série inteira de filmes"; "os mais vistos, os mais bem avaliados... listas prontas onde eu clico e marco como visto"; "pensa num processo bem legal para ficar bonito e prático"; "Vistos? e se for jogos?"; "nas opções poder dizer o que quer controlar"):
- O Adicionar (`folhaAdicionar`) abre nas listas prontas (`tmdb.LISTAS`, `TMDB.lista`, `GET /api/lista?nome&tipo&pagina` → `{resultados, mais}`; `zip_longest` intercala filmes e séries) e mostra as capas em grade (`cartaz`/`grade`, `.cartazes`): na capa, **Quero ver** (`cz-quero`) e **Já vi** (`cz-visto`; fora o que ainda não saiu, pela `data`); `cz-abrir` abre o título por cima (`abrirFolha(f, true)`). Sem o foco no campo ao abrir.
- As janelas em pilha (`S.folhas`, o estado do histórico `{folha: profundidade}`): uma aberta de dentro de outra volta para ela no Voltar; `.folha.fixa` não sobe de novo quando a mesma janela é pintada outra vez.
- Coleções de filmes: `TMDB.colecoes` (na busca, até 2 na frente, `tipo: colecao`), `TMDB.colecao`, `colecao` do filme (`belongs_to_collection`), `GET /api/colecao?id` e `POST /api/titulo {acao: adicionar_colecao, colecao, situacao: quero|visto}` (`server.adicionar_colecao`: Visto só os que já saíram e marca os que estavam; Quero ver não mexe nos que estavam).
- **Histórico** (`telaHistorico`, `odisseia-historico`): uma aba por tipo ligado.
- **O que controlar** (`ajustes.tipos`, `R.tipos_ligados`, `R.conferir_tipo`): o tipo desligado sai do `/api/estado`, da busca e das listas (`tipo_de_busca`, `so_ligados`) e do que as ferramentas veem (e volta inteiro ao gravar); pelo menos um fica ligado.
- Ferramentas novas: `lista_pronta` e `adicionar_colecao` (`texto_lista`, `texto_colecao`).

0.3.0 (o dono: "pode tirar a opção de vendo, só vou controlar visto e quero ver"; "tirar a opção de nota e colocar um campo de categoria... configurável"; "Quem ter opção para todos"; "uma opção direta nessa tela para eu clicar e abrir a coleção"; "o + também deve aparecer coleções"; "a parte de filtros deixa no mesmo padrão dos outros apps"):
- `R.SITUACOES` só `quero` e `visto` (o `limpar_titulo` passa o resto para quero); `R.em_andamento` (série em quero com episódio) é o **Continuar vendo** do Agora e as séries em andamento do `resumo`.
- Categorias: `d["categorias"] = {filme: [{id, nome}], serie: [...]}` (até 40; `R.mudar_categorias`, `POST /api/categorias {acao: nova|renomear|apagar}`), `t.categoria`, `R.achar_categoria` (pelo nome, nas ferramentas), `R.nome_categoria`; a tela em **Mais › Categorias** (`telaCategorias`, `textarea.umalinha`: o Enter salva). A nota saiu (e o argumento `nota` das ferramentas).
- Quem: **Todos** (`quem-todos`); nas ferramentas, «todos» (`ids_de`).
- A coleção de cada filme nas listas e na busca (`com_colecao`: os detalhes em `DETALHES`, 12 horas, 8 de cada vez com `ThreadPoolExecutor`); a lista pronta **Coleções** (`lista_colecoes`: as coleções dos filmes populares e mais bem avaliados, até a página 5); na capa: `cz-colecao` (abre) e `cz-col-todos` (Já vi todos / Quero ver todos, pelo `adicionar_colecao`).
- Buscar no padrão dos outros apps: `.sbar`, `.filtros-h` (`odisseia-filtros` no aparelho) e `.sfiltros` (as caixas `#f-tipo`, `#f-sit`, `#f-cat`, `#f-quem`).

0.4.0 (o dono: "cadê os jogos?"; "colocar cor, fazer no mesmo padrão dos outros apps"; "não precisa ser histórico essa aba, pode ser aqui o que está salvo como visto, e daí permitir visualizar modo lista menor, ter opção de alteração em massa de categorias"; "e também o quem"; "o nome ali, D ou T, deixar no final, na direita, na mesma linha de cima"; "filtro por categoria aqui"; "a seleção de categorias nas opções de adicionar e alterar deve ser igual a outros apps"; "de onde vêm os dados não faz sentido ficar no sobre"):
- Jogos: `tipo: jogo` (`R.TIPOS`, `R.PLURAIS`), `igdb` (o número), `capa_igdb` (o image_id), `igdb_em`, `data` (o lançamento), `plataformas`, `link` e `colecao: {id, nome, capa}`; sem `onde`, `tmdb`, `capa_tmdb` nem `tmdb_em`. `R.fonte(tipo)` ("igdb" ou "tmdb"), `R.de_fonte` (o `de_tmdb` de antes), `R.nome_sit` (`SIT_JOGO`: Quero jogar e Jogado; o valor gravado é o mesmo, quero e visto). A conta em `segredos.json` (`igdb_id`, `igdb_segredo`; `POST /api/igdb {cliente, segredo}`, testada antes de guardar; `estado.igdb`). `ODISSEIA_IGDB`, `ODISSEIA_TWITCH` e `ODISSEIA_IGDB_IMG` trocam os endereços (os testes). Os tipos dos jogos (`game_type`, o `category` de antes): `NA_BUSCA`, `NAS_LISTAS` e `NA_COLECAO`.
- Tudo mistura as fontes: `fontes(tipo)` (sem tipo, as dos ligados com a conta posta) e `juntar(chamadas)` (as coleções na frente, depois um de cada fonte; uma que falha fica de fora se outra deu certo), no `buscar` e no `lista_pronta`; `lista_colecoes_jogos`; as capas da busca em `/api/img/t_cover_big/<image_id>.jpg`; `colecao(n, tipo)` e `adicionar_colecao` com `tipo` (as coleções devolvem `itens`, não mais `filmes`); `uma_volta` (o laço) para a fonte que ficou sem a conta ou sem internet.
- Vistos (`telaVistos`, `#/vistos` no lugar do Histórico, `odisseia-vistos` e `odisseia-vistos-cat` no aparelho): o mais recente primeiro, o filtro `.filtro-cat`. `listaSel` (Vistos e Buscar): `.ssum` com `.modo` (Capas ou Lista, `odisseia-modo`; a Lista é `linhaTit(..., {curta})`) e o Selecionar (`S.sel`, um tipo só, `{sel: 1}` no histórico, o Voltar sai; segurar o dedo, `contextmenu`, começa); o `.selbar` abre `folhaLote` (Categoria e Quem, cada um com Manter) → `POST /api/titulo {acao: lote, itens: [{id, campos}]}` (`R.lote`, tudo ou nada) e o `toast(..., {rotulo: 'Desfazer', fazer})`.
- Categorias com cor (`cor`, uma das 12 da paleta, `R.CORES`; sem cor, `R.cor_livre`; `{acao: editar, id, nome?, cor?}`): `telaCategorias` (as linhas com o ícone na cor, como no MemorIA) e `folhaCategoria` (o nome e as cores); no título e no Alterar, `pickCat` (`.escolha.cor` com a `.dot`, escolhida no fundo da cor dela) e a **Nova** ali mesmo (`S.novaCat`); na linha, `.t-l1` (o nome e quem) e `tagCat` (`.cat-tag`).
- O crédito do TMDB foi do Sobre para o cartão dele, em Integrações; o cabeçalho das telas e o `.voltar` como os do GerencIA.
- Ferramenta `marcar_varios` (`R.lote`); `adicionar`, `lista_pronta` e `adicionar_colecao` com `tipo: jogo`.

0.5.0 (o dono: "vistos fica estranho para jogos"; "colocar a categoria em cada linha ali"; "ter opção de agrupar por categoria do filme, e pelo gênero"; "antes do já vi todos, as opções de categorias para selecionar a categoria de todos ou individual"; "e falta de opções de retrair, igual os outros apps"; "só deve habilitar o filtro de categorias se eu selecionar só filmes, séries ou jogos"):
- A aba **Concluídos** (a rota continua `vistos`). `tagCatToque` (`.cat-tag.toque`, `.vazia`: + Categoria; um `span` com `data-a="cat-rapida"` dentro do botão da linha) abre `folhaCatTitulo` (o `campoCategoria`, o mesmo do título; escolhida, fecha); as linhas do `listaSel` têm `catToque`.
- **Agrupar por** (`.agrupar`, `odisseia-agrupar`: '', categoria, genero; `grupos(ts, ag)`; `.grupo`/`.grupo-h`, os fechados em `odisseia-grupos`).
- Buscar: a categoria só com um tipo (`catDaBusca`; com todos os tipos, a caixa `#f-cat` fica `disabled`; mudar o tipo limpa a categoria).
- Coleção: `S.colCat` (Manter ou uma categoria, `col-cat`) → `adicionar_colecao {categoria}` (vale para tudo o que entra; `res.categoria` é o nome); a etiqueta de cada capa que já está na lista. A ferramenta `adicionar_colecao` aceita `categoria`.
- Os campos das janelas fecham pelo título (`pintarJanela`: `.dobra-campo`, `data-campo` com o título, `odisseia-campos`; `.campo.fechado`).

0.6.0 (o dono, à lista do que a IA não fazia: "todas"): a ferramenta `categoria` (`acao`: nova, renomear com `novo_nome`, apagar; `tipo` e `nome`), pelo `R.mudar_categorias` da tela; um tipo desligado é erro. Teste: `TestNovidades060`.

0.7.0 (o dono: "no topo das telas opções de chat e de falar igual os outros apps"; "toda a sorte de IA deve estar no OdisseIA"): a IA.
- Servidor: `ia.py` (o `Agente`, com o modelo do CorrerIA: as ferramentas do `ferramentas.py` mais `pesquisar` e `lembrar`; as leituras rodam na hora, até 4 rodadas, e as mudanças viram o `pendente` que espera o Sim; `validar` confere os argumentos antes, e as guardas tiram o «já fiz» e o «Toque em Sim» escritos pela IA e o apagar que veio de uma foto ou pesquisa; `simulado` no computador e nos testes), `fala.py` (o do CorrerIA), `uso.py` (o do CorrerIA) e `memoria_ia.py` (o dos outros apps em Python). No `server.py`: `ia_chamar` (o `ai_task.generate_data` com a Memória da IA na frente e o `IA_SO_MATERIAL` no fim; a foto como anexo pela pasta media, `IA_TMP_REL`; o Uso da IA), `ia_ent` (a IA de cada uso: `ajustes.ia_conversa`, `ia_fotos`, `ia_pesquisa`; `R.IA_RE`), `ia_info` (`GET /api/ia`), `conversar`/`confirmar`/`nova_conversa` (`/data/conversa.json`, a da casa, as últimas 60; `POST /api/conversa`, `/api/conversa/sim {sim}`, `/api/conversa/nova`), `usar_na_conversa` (o `usar_ferramenta` com `cliente: OdisseIA`, que não conta como uso do CorrerIA: `de_fora`), `POST /api/fala` (PCM de 16 kHz), `GET /api/uso` e `GET`/`POST /api/memoria-ia`. `ajustes.ia` começa ligado; `IA_MOCK` (`ODISSEIA_IA_MOCK` ou o computador sem o Home Assistant). O `config.yaml` mapeia a pasta media.
- Tela: `barraTopo()` no `topo()` de toda tela (a marca, o olá, `.chat-top` e `.mic-top`, só com `iaOn()`/`falaOn()`); a janela `conversa` (`folhaConversa`, `.folha.conversa`: as perguntas prontas `IDEIAS`, as mensagens com `md()`, o Sim e o Não, Nova conversa, `.conv-pe` com Escolher fotos, `lerFoto`/`encolher`, e o Falar ou o Enviar; no celular, o Enter é uma linha nova); o Falar (`Gravador`, `falarConversa`, `pararFala`); Integrações: `cardIA` (com o `.sub-box`), `cardMemoria`, `cardFalar` e `cardUso`. Testes: `tests/test_ia.py`, `tests/test_fala.py`, `tests/test_memoria_ia.py` e `test_a_ia_conversa_falar_e_integracoes` no `tests/test_tela.py`.

0.8.0 (o dono: "esse adicionar com essas opçõezinhas de retrair tem que mostrar o que foi selecionado do ladinho, quando eu retraio"; vale em todos os apps): no `pintarJanela`, cada `.dobra-campo` leva a `.fl-val` com o escolhido (`valorCampo`: os botões marcados, senão a caixa de seleção, senão o texto), que só aparece com o campo fechado. O `corpo()` lê e joga fora um pedido grande demais (até 4 vezes o limite) antes do 400: no GitHub, o `test_o_que_sobra` recebia um «Broken pipe». Teste: `test_categoria_na_linha_agrupar_e_campos` (o Quem fechado) no `tests/test_tela.py`.

0.9.0 (o dono: "cadê a opção para alterar o falar igual os outros apps?"; "no OdisseIA criar também sensores do Home Assistant"): `ajustes.fala` (`R.STT_RE`, `stt.…` ou vazio = automático): `fala.py` com `todos(formato)` (a lista dos motores que aceitam o áudio, o automático primeiro; guardada 5 minutos), `motor(formato, escolha)`, `status(formato, escolha)` (`opcoes`, `automatico`, `escolha_sumiu`) e `texto(..., escolha)`; o `ia_info` leva `fala_escolha`; na tela, `#fala-motor` (`data-aj-sel="fala"`: depois de gravar, o `carregarIA()`). Sensores: `ajustes.sensores` (desligado de início), `SENSORES`, `estados_sensores(d, hoje)` (pelos tipos ligados), `publicar_sensores(forcar)` (o `POST /api/states/<sensor>`, só o que mudou ou a cada 15 minutos, pelo `laco_sensores`), `remover_sensores()` (desligar), `sensores_depois(d)` (no `salvar`, em segundo plano); na tela, `cardSensores()` no fim de Integrações (fora do Usar IA). O `resumo` do CorrerIA leva os jogos em Quero jogar que saem nos próximos 30 dias (a etapa Vão sair do CorrerIA 1.37.0). Testes: `TestNovidades090` no `tests/test_servidor.py`, `test_escolher_a_fala_para_texto` no `tests/test_fala.py` e o `test_a_ia_conversa_falar_e_integracoes`.

0.10.0 (a revisão dos padrões da família, `PADROES.md`): as **perguntas prontas** da Conversa (`PERGUNTAS`, 26 gerais: as 6 primeiras à vista e 20 modelos; `perguntas()`, `odisseia-perguntas` no aparelho; `blocoPerguntas`: os chips e o **Editar perguntas**, `perg-*`; com mensagens, o ✨ `perg-rapidas` e o `.conv-rapidas` em cima da caixa; `abrirPerguntas`/`fecharPerguntas`: a entrada `{painel: 1}` no histórico, que o Voltar fecha; o X da Conversa com elas abertas volta as duas, `history.go(-2)`; o `abrirConversa` fecha as duas: a Conversa abre sempre no chat). O **Apagar** do Selecionar (`sel-apagar`, `.selbar.dois`): `POST /api/titulo {acao: apagar_varios, ids}` → `{apagados, rev}` (as capas vão para `capas/lixo`, um dia, `LIXO_DIAS`) e o Desfazer, `{acao: restaurar, titulos}` (`R.limpar_titulo`; a capa volta do lixo ou o laço baixa de novo). O **Uso da IA** termina com o site de cada provedor em uso (`PROVEDORES_IA`, `provedoresIA`, como no GerencIA). O `fala.py` e o `uso.py` são iguais aos do CorrerIA (`tools/iguais.py`; `Fala(..., exemplo=)` é o texto da fala simulada daqui). Testes: `test_apagar_varios_e_desfazer` no `tests/test_servidor.py` e os do Selecionar e da Conversa no `tests/test_tela.py`.

0.11.0 (o dono: "do mesmo jeito que criamos esse agrupar por… [nos Consumíveis do InventarIA]… se tiver alguma já fora do padrão, deixa nesse padrão"): no `listaSel`, o `.agrupar` com o título `.agrupar-l` (`agrupar-dobra`, `odisseia-agrupar-fechado` no aparelho; fechado, a `.agrupar-val`) e o `.modo.agrupar-seg` (`AG`: Nenhum, Categoria e Gênero, com ícone, do mesmo tamanho); cada `.grupo-h` com o `.grupo-ic` (na cor da categoria, `.cor`), o nome e o `.cont` («N títulos»). Teste: `test_categoria_na_linha_agrupar_e_campos`.

0.12.0 (o dono: "cada tela tem tamanho de fonte diferente… documenta nos padrões.md e aplica ele em todos os apps"; "os filtros lá de cima devem poder ser retraídos igual os outros filtros"): `agruparBloco()` (o `AG` com o Nenhum por último) sai do `listaSel` e vai na `.sbar`, logo embaixo do Filtros, no Buscar e no Concluídos; no Concluídos, a categoria dentro do `#vistos-filtros` (`odisseia-vistos-filtros`); fechado, o `.filtros-val` (`filtrosVal(caixas)` no Buscar: o escolhido de cada caixa). O `.filtros-h` e o `.agrupar-l` no padrão do **O alto das listas** do `PADROES.md` (40 px, 15 px, peso 500, o ícone de 18 px na cor do app, o escolhido em cinza); o `.grupo-ic` com 36 px. Teste: `test_categoria_na_linha_agrupar_e_campos`.

0.12.1 (o dono: "faz também nos outros de mostrar o que foi selecionado ao retrair"): o `filtrosVal` sem nada escolhido diz o que vale na primeira caixa.

## Conversa com o dono

Respostas curtas, em português. Ao terminar uma mudança: o que mudou, a versão e se está publicado. Ele usa o app do Home
Assistant no Android: pense no Voltar do celular, no teclado e na câmera.
