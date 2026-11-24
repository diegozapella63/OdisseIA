# Instruções para quem for mexer neste repositório (pessoas ou IAs)

OdisseIA é um app (add-on) do Home Assistant para os filmes e as séries da casa: o que cada pessoa está vendo, já viu,
quer ver ou abandonou, o episódio em que parou, a nota, os episódios que vão sair e onde assistir no Brasil. Os dados dos
títulos vêm do TMDB (com a chave grátis de cada casa); onde assistir é da JustWatch, pelo TMDB. Faz parte de uma família de
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
odisseia/app/ferramentas.py   as ferramentas do CorrerIA (resumo, buscar, ver, adicionar, marcar, proximo_episodio, apagar)
odisseia/app/www/             a tela: index.html, app.js (JavaScript puro, sem build), styles.css, fontes; selectsheet.js,
                              hatema.js e textareas.js são cópias dos outros apps (ainda fora do tools/iguais.py da família)
tests/                        testes (unittest; a tela com playwright); tests/apoio.py tem o TMDB de mentira (títulos inventados)
dev/rodar.py                  o app no computador com o TMDB de mentira
tools/cobertura.py            a cobertura de linhas do servidor (fica acima de 95%)
tools/fazer_logo.py           desenha odisseia/icon.png e odisseia/logo.png
```

Os dados ficam em `/data/odisseia.json` (`{versao, rev, titulos, ajustes}`; cada gravação soma 1 em `rev`, e a tela confere
`/api/rev` a cada 20 s), as capas em `/data/capas/<id>.jpg`, a chave do TMDB em `/data/segredos.json` (600; nunca volta
para a tela, só o fim `••••abcd`), as versões automáticas em `/data/versoes` (as 5 últimas: uma por dia e antes de
importar, restaurar ou apagar tudo) e os backups em `share/odisseia/backups` (os 10 últimos). Um título:
`{id: t + 8 hex, tipo: filme|serie, tmdb, nome, original, ano, capa, capa_tmdb, sinopse, generos, situacao:
quero|vendo|visto|abandonado, quem: [person.*], nota: 0..5, notas, visto_em, tmdb_em, onde: {assinatura, gratis, alugar,
comprar, link}}` e, na série, `temporadas: [{n, episodios}]` (sem a 0, dos especiais), `temp`/`ep` (o último visto; 0/0
nenhum), `proximo` e `ultimo` (`{data, temp, ep, nome}`) e `fim`. O laço do servidor atualiza pelo TMDB as séries vistas ou
queridas uma vez por dia e o resto uma vez por semana (os abandonados, não).

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
- A barra de baixo: **Agora**, **Buscar**, o **+** (Adicionar, só o ícone), **Histórico** e **Mais**.
- **Inativos no fim, recolhidos**: os **Abandonados (n)** no fim do Buscar, recolhidos (abrem num toque).
- **Caixas de seleção no visual do app** (`selectsheet.js`): a temporada e o episódio são `<select class="inp select">`.
- Dados de exemplo e de testes sempre inventados (Ana, Beto, títulos inventados): nunca a lista real do dono.

**Padrão da família (igual em todos os apps)**
- Barra de baixo: a primeira aba é **Agora** (onde o app abre, com o ícone do relógio; nada de Início); o botão do meio é **Adicionar** (no EconomIA, a ação principal dele), só com o ícone, sem o texto embaixo (o nome fica no `aria-label`); **Buscar**, quando houver, é a 2ª aba; **Mais** é a última, com o ícone de três pontos.
- **Ícones**: toda seção (cartão) começa com o cabeçalho, o ícone e o título; o título de cada tela, de cada grupo (como Imóveis e Veículos) e de cada janela (Novo cômodo, Nova despesa… e a lista de uma caixa de seleção) também tem o ícone; dentro de uma seção, toda linha com título (uma chave, uma escolha, um campo, um recolhido como **Últimas chamadas**) tem um ícone pequeno antes do título; e todo botão com texto tem ícone (Cancelar, Salvar, Voltar, Hoje…). Assim dá para ver onde cada parte começa. Aqui: `cab()` e `card()` (o cabeçalho com o ícone), `lbl()` (o ícone pequeno antes do título de cada campo) e `ICONE_TELA`; o `padrao()` do `tests/test_tela.py` confere os cartões e os botões.
- **Seções**: cada seção principal é um cartão (o fundo, a borda e os cantos arredondados, como no GerencIA), sem linha no fim; entre as linhas de opções de uma seção não há linha (o ícone de cada uma marca onde começa); as listas de dados (mensagens, conversas, conexões) têm a linha fina entre as entradas, sem a do fim.
- **Abas**: quando as abas não cabem na largura, a ponta de onde há mais some aos poucos, com uma seta.
- **Contrair e expandir**: toda seção (cartão) fecha e abre num toque no cabeçalho, com a seta no canto; o aparelho lembra as que ficaram fechadas. Aqui: o `cab()` com `data-dobra` e `odisseia-fechadas` no localStorage.
- **Sub-opções**: o que só vale com uma chave ligada (o Horário e o A cada do Conferir sozinho, o Quem recebe e o Testar do Avisar no celular, uma lista como Apps detectados) fica num quadro recuado logo abaixo dela, para ver de qual opção é.
- Nada de avisos que só incham a tela: o que a própria tela já mostra, o que a pessoa confere de qualquer jeito ou um limite do app do celular ("a galeria manda uma foto por vez", "Você confere antes de criar", "a IA encontra…") fica de fora (a aba Documentação pode explicar).
- Botões de ação (Novo…, Verificar de novo, Salvar e testar…) na largura do cartão no celular, dois lado a lado dividindo a linha; no computador, com a largura fixa do app (250 ou 280 px). Campos de texto livre que podem ficar longos (o que foi, títulos, descrições, nomes de tarefas, de cômodos, de blocos, de categorias) são caixas de texto que mostram tudo e aumentam puxando o canto (`textareas.js`), nunca uma linha que corta o texto; o Enter salva quando o campo é de uma linha só.
- **Mais** é um menu: as funções do app, depois **Configurações** e por último **Sobre**. Os relatórios se chamam **Relatório de/do …**.
- **Configurações** em 4 abas, nesta ordem: **Integrações › Dados › Aparência › Opções**; abre em Integrações. Nenhuma função do app vira aba.
- **Integrações**, nesta ordem: os outros apps da família › CorrerIA › **IA** (o Usar IA e a IA de cada uso: **Para conversar**, **Para ler fotos e PDFs** e, onde há busca na web, **Para pesquisar na internet**; cada uma é uma tarefa de IA do Home Assistant, e a de fotos ou de pesquisa vazia é igual à de conversar) › Falar › Uso da IA › Sensores.
- IA: as entradas se chamam **Colar mensagem**, **Escolher fotos** (ou **Escolher fotos ou PDF**, onde PDF vale) e **Digitalizar com IA**; a conversa recomeça em **Nova conversa**; o Voltar do celular fecha a Conversa.
- Palavras: **Apagar** (nunca Excluir); **Testar no meu celular**; **Home Assistant Cloud** (não Nabu Casa); recolhidos como **Nome (n)**; o CHANGELOG começa com "# Mudanças".
- Avisos no celular (todos chegam como Home Assistant): o título começa pelo nome do app, uma vez só ("ResolvIA · 📅 Vence hoje"), e o ícone pequeno é o do app (`notification_icon`); o canal e o grupo de cada aviso ficam como estão (o canal guarda o som e a importância que a pessoa escolheu no Android).
- **Dados**: Exportar › Backup na pasta share › Importar › Versões anteriores › Onde ficam os dados › Começar do zero.
- **Aparência**: o tema vale no aparelho (começa em Sistema); o fundo e os cartões são os do tema do Home Assistant (`hatema.js`, igual em todos os apps: publica `--ha-bg-light`, `--ha-card-light`, `--ha-bg-dark` e `--ha-card-dark`, as do modo de agora lidas do Home Assistant e as do outro, do tema padrão dele; os cinzas, como linhas e campos, saem do cartão misturado com o texto, `color-mix`, nunca uma cor fixa puxada para a cor do app); a cor do app vale para a casa toda; uma paleta só, de 12 cores (Vermelho, Coral, Laranja, Ouro, Verde, Menta, Turquesa, Azul, Índigo, Lilás, Rosa, Grafite); a Cor do dia é a mesma em todos os apps (as 11 sem o Grafite, pelo número do dia).

0.2.0 (o dono: "adicionar uma série inteira como vista"; "uma série inteira de filmes"; "os mais vistos, os mais bem avaliados... listas prontas onde eu clico e marco como visto"; "pensa num processo bem legal para ficar bonito e prático"; "Vistos? e se for jogos?"; "nas opções poder dizer o que quer controlar"):
- O Adicionar (`folhaAdicionar`) abre nas listas prontas (`tmdb.LISTAS`, `TMDB.lista`, `GET /api/lista?nome&tipo&pagina` → `{resultados, mais}`; `zip_longest` intercala filmes e séries) e mostra as capas em grade (`cartaz`/`grade`, `.cartazes`): na capa, **Quero ver** (`cz-quero`) e **Já vi** (`cz-visto`; fora o que ainda não saiu, pela `data`); `cz-abrir` abre o título por cima (`abrirFolha(f, true)`). Sem o foco no campo ao abrir.
- As janelas em pilha (`S.folhas`, o estado do histórico `{folha: profundidade}`): uma aberta de dentro de outra volta para ela no Voltar; `.folha.fixa` não sobe de novo quando a mesma janela é pintada outra vez.
- Coleções de filmes: `TMDB.colecoes` (na busca, até 2 na frente, `tipo: colecao`), `TMDB.colecao`, `colecao` do filme (`belongs_to_collection`), `GET /api/colecao?id` e `POST /api/titulo {acao: adicionar_colecao, colecao, situacao: quero|visto}` (`server.adicionar_colecao`: Visto só os que já saíram e marca os que estavam; Quero ver não mexe nos que estavam).
- **Histórico** (`telaHistorico`, `odisseia-historico`): uma aba por tipo ligado.
- **O que controlar** (`ajustes.tipos`, `R.tipos_ligados`, `R.conferir_tipo`): o tipo desligado sai do `/api/estado`, da busca e das listas (`tipo_de_busca`, `so_ligados`) e do que as ferramentas veem (e volta inteiro ao gravar); pelo menos um fica ligado.
- Ferramentas novas: `lista_pronta` e `adicionar_colecao` (`texto_lista`, `texto_colecao`).

## Conversa com o dono

Respostas curtas, em português. Ao terminar uma mudança: o que mudou, a versão e se está publicado. Ele usa o app do Home
Assistant no Android: pense no Voltar do celular, no teclado e na câmera.
