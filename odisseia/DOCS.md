# OdisseIA

Os filmes, as séries e os jogos da casa: o que cada pessoa quer ver (ou jogar) e já viu (ou jogou), o episódio em que parou, a categoria, os episódios e os jogos que vão sair, onde assistir no Brasil e em que plataformas jogar.

## Primeiro passo: a chave do TMDB

Os filmes, as séries, as capas e onde assistir vêm do [TMDB](https://www.themoviedb.org/), de graça, para uso pessoal:

1. Crie uma conta no [TMDB](https://www.themoviedb.org/signup).
2. Em [Configurações › API](https://www.themoviedb.org/settings/api), peça uma chave de **uso pessoal** (Developer).
3. No OdisseIA, em **Mais › Configurações › Integrações › Filmes e séries (TMDB)**, cole a **Chave da API** ou o **Token de leitura da API** e toque em **Salvar e testar**.

A chave fica só no app (em `/data/segredos.json`); a tela mostra só o fim dela. Ela não vai no Exportar nem no Backup.

## Os jogos: a conta do IGDB

Os jogos e as capas deles vêm do [IGDB](https://www.igdb.com/), da Twitch, de graça:

1. Entre no [Twitch Developers](https://dev.twitch.tv/console) com uma conta da Twitch (ela precisa da verificação em duas etapas ligada).
2. Em **Aplicativos › Registrar seu aplicativo**: um nome qualquer, o endereço `http://localhost`, a categoria **Application Integration** e o tipo de cliente **Confidencial**.
3. Abra o app criado, copie o **Client ID** e toque em **Novo segredo** para ter o **Client Secret**.
4. No OdisseIA, em **Mais › Configurações › Integrações › Jogos (IGDB)**, cole os dois e toque em **Salvar e testar**.

Os dois ficam só no app (em `/data/segredos.json`), como a chave do TMDB. Os nomes e as sinopses dos jogos vêm em inglês: o IGDB não tem português.

## Agora

- **Continuar vendo**: as séries em Quero ver com algum episódio visto, com o episódio em que parou e quantos já saíram e faltam. O botão com o episódio (**✓ T2 E6**) marca o seguinte como visto.
- **Novos episódios**: as séries da lista com episódio saindo nos próximos 30 dias.
- **Jogos que vão sair**: os jogos em Quero jogar que ainda não saíram, com a data.
- **Quero ver** e **Quero jogar**: o que a casa quer ver e jogar (os mais recentes; **Ver todos** abre o Buscar).

## Adicionar (o + no meio da barra)

Abre nas **listas prontas**: **Em alta**, **Mais populares**, **Mais bem avaliados**, **Coleções** e **Estreias** (os filmes nos cinemas do Brasil; nas séries, as que estão no ar). Nos jogos, a popularidade do IGDB (**Em alta** e **Mais jogados**), os **Mais bem avaliados**, as **Coleções** e os **Lançamentos** dos últimos 90 dias. **Mostrar mais** traz a próxima página. Para procurar, escreva o nome: os filmes e as séries no TMDB, em português; os jogos no IGDB. **Tudo**, **Filmes**, **Séries** ou **Jogos** filtra (Tudo mistura os que têm a conta posta).

Em cada capa:
- **Já vi** (o visto; num jogo, **Já joguei**): põe na lista como **Visto** (**Jogado**). Numa série, marca a série inteira, até o último episódio que saiu. O que ainda não saiu não tem esse botão.
- **Quero ver** (o marcador; num jogo, **Quero jogar**): põe na lista.
- Tocar na capa abre o título (fora da lista, ele entra como Quero ver). O Voltar do celular volta para a lista.

O que já está na lista mostra a situação no canto da capa.

## Categorias

Em **Mais › Categorias** ficam as categorias da casa, uma lista para cada tipo (até 40 em cada), cada uma com uma cor. **Nova categoria** abre o nome e a cor (começa numa cor que nenhuma usa); tocar numa categoria muda o nome e a cor, ou apaga (os títulos ficam sem categoria). No título, a categoria aparece na cor dela; **Nova** cria uma ali mesmo. O Buscar e o Vistos filtram pela categoria.

## Coleções

As sagas de filmes e as séries de jogos aparecem na busca com a etiqueta **Coleção**, na lista pronta **Coleções** (as sagas dos filmes mais populares e mais bem avaliados) e no botão **Coleção** embaixo da capa de um filme que faz parte de uma. Na capa da coleção, o ✓ marca todos os já lançados como Visto (Jogado), e o marcador, todos como Quero ver (jogar), sem abrir. A coleção abre com todos, na ordem em que saíram: **Quero ver todos** (**Quero jogar todos**) põe os que faltam na lista; **Já vi todos** (**Já joguei todos**) põe os que já saíram como Visto (e marca como Visto os que já estavam na lista). Numa série de jogos entram os jogos de verdade: as remasterizações, os pacotes e os conteúdos extras ficam de fora. Antes, a **Categoria de todos** escolhe a categoria que todos ganham (os novos e os que já estavam na lista); cada capa que já está na lista mostra a categoria dela, para mudar uma a uma.

## O título

Cada campo da janela (Situação, Categoria, Quem, Onde assistir, Sinopse…) fecha e abre pelo título, com a seta no canto; fechado, o escolhido aparece ao lado do título (**Situação · Quero ver**, **Parou em · Temporada 1 · Episódio 3**), e o aparelho lembra os fechados, em todos os títulos.

- **Situação**: Quero ver ou Visto (num jogo, Quero jogar ou Jogado). Visto numa série marca até o último episódio que saiu. A série em Quero ver com algum episódio visto aparece em **Continuar vendo**, no Agora.
- **Parou em** (séries): a temporada e o último episódio visto. **Vi o T2 E6** marca o seguinte. No último episódio de uma série que acabou, ela vira **Visto** sozinha.
- **Categoria**: Sem categoria ou uma das categorias da casa do tipo do título, com a bolinha na cor dela; **Nova** cria uma ali mesmo.
- **Quem**: quem da casa quer ver ou viu (as pessoas do Home Assistant); **Todos** marca a casa toda. Desliga em **Configurações › Opções › Quem vê**.
- **Onde assistir**: no Brasil, por assinatura, grátis, para alugar ou comprar. Dados da JustWatch, pelo TMDB. Num jogo, **Onde jogar**: as plataformas, pelo IGDB.
- **Notas**: o que a casa achou, quem indicou.
- **Atualizar** busca de novo no TMDB ou no IGDB (o app já atualiza sozinho: as séries que a casa vê ou quer ver e os jogos que ainda vão sair, uma vez por dia; o resto, uma vez por semana).

## Buscar e Concluídos

**Buscar** filtra a lista pelo nome e, em **Filtros** (que fecha e abre), pelo tipo, pela situação, pela categoria (também **Sem categoria**; ativa depois de escolher Filmes, Séries ou Jogos, porque as categorias são de cada tipo) e pela pessoa. **Concluídos** mostra o que está salvo como visto (e jogado), o mais recente primeiro, numa aba para cada tipo, com o filtro da categoria em cima.

Nos dois, em cima da lista:
- **Capas** ou **Lista**: a lista menor, sem as capas, um título por linha. O aparelho lembra.
- **Agrupar por**: Nenhum, **Categoria** (na ordem das categorias; Sem categoria no fim) ou **Gênero** (o primeiro gênero de cada título). Cada grupo mostra quantos títulos tem e fecha num toque; o título Agrupar por fecha o bloco (com o escolhido ao lado). O aparelho lembra.
- **A categoria em cada linha**, na cor dela, ou **+ Categoria**: o toque abre só a escolha da categoria daquele título.
- **Selecionar**: toque nos títulos (ou segure o dedo num) e **Alterar** muda de uma vez a **Categoria** e **Quem**; cada campo começa em **Manter**. **Apagar** tira os títulos marcados da lista. Depois, o aviso tem o **Desfazer**. Uma seleção é de um tipo só (as categorias são de cada tipo). O Voltar do celular sai do Selecionar.

## O que controlar

Em **Configurações › Opções › O que controlar**, ligue as séries, os filmes e os jogos (pelo menos um). O que fica desligado some da tela e do CorrerIA; nada é apagado, e volta ao ligar de novo.

## A IA: Conversa e Falar

Com uma IA no Home Assistant (uma tarefa de IA, como Google Gemini ou OpenAI, em **Configurações › Dispositivos e serviços**), o alto de toda tela tem a **Conversa** e o **Falar**:

- **Conversa**: pergunte sobre a lista da casa (o que ver ou jogar, em que episódio vocês pararam, o que vai sair, onde assistir) ou peça para pôr, marcar, mudar a categoria ou apagar um título. A IA lê a lista na hora; para mudar, ela mostra o que vai fazer e espera você tocar em **Sim** (em **Não**, nada muda; outra mensagem também descarta). Ela também pesquisa na internet o que a lista não tem (críticas, se vale a pena, quando sai a próxima temporada) e guarda na **Memória da IA** o que você pedir para lembrar ("a Ana não gosta de terror"). **Nova conversa** recomeça; o Voltar do celular fecha. Com a conversa vazia, aparecem 6 **perguntas prontas**: é só tocar; depois, o ✨ ao lado da caixa abre as mesmas. Em **Editar perguntas**, toque numa para mudar o texto, o ✕ tira e **Adicionar** põe outra; embaixo, as **Mais perguntas** trazem 20 modelos (um toque põe); **Padrão** volta às de início. Ficam guardadas no aparelho.
- **Escolher fotos** (o botão da foto, na Conversa): a foto de um pôster, de um print de um streaming, da capa de um jogo ou de uma lista escrita; a IA vê a foto e propõe pôr os títulos na lista.
- **Falar** (o microfone): fale e toque em ✓; o que você falou vira texto pela fala para texto do Home Assistant e vai para a Conversa. Precisa do Home Assistant aberto por um endereço seguro (https).

Em **Mais › Configurações › Integrações**:

- **IA**: **Usar IA** (desligado, a Conversa e o Falar somem em todos os aparelhos) e a IA de cada uso: **Para conversar**, **Para ler fotos** e **Para pesquisar na internet** (a de fotos e a de pesquisar vazias são a de conversar; para pesquisar, a IA precisa da busca na web ligada no Home Assistant).
- **Memória da IA**: uma memória só, da casa, compartilhada por todos os apps: o que você escreve aqui a IA lembra em toda conversa, em qualquer um deles.
- **Falar**: quem transforma a fala em texto. Em **Fala para texto**, **Automático** (o do Home Assistant Cloud, senão o primeiro que entende o microfone) ou um dos motores do Home Assistant; se o escolhido sumir, o app usa o automático e avisa. Sem nenhum, como configurar.
- **Uso da IA**: as chamadas do app para a IA (hoje, 7 dias e este mês) e as últimas, com o motivo de cada erro. Os tokens são estimados. No fim, o site onde ver o consumo de cada IA em uso.
- **Sensores no Home Assistant** (desligados de início; não dependem da IA): para usar em painéis e automações. `sensor.odisseia_quero_ver` (quantos em Quero ver, por tipo), `sensor.odisseia_em_andamento` (as séries em andamento e onde cada uma parou), `sensor.odisseia_proximo_episodio` (a data do próximo episódio, com a série e o episódio), `sensor.odisseia_proximo_jogo` (a data do próximo jogo em Quero jogar) e `sensor.odisseia_concluidos_no_mes` (quantos foram vistos ou jogados neste mês). Mudam a cada gravação; desligar tira os sensores do Home Assistant.

## Pelo CorrerIA

Com **Configurações › Integrações › CorrerIA** ligado, o CorrerIA (WhatsApp, Claude e Gemini) pode perguntar o que a casa está vendo e jogando, adicionar um filme, uma série ou um jogo pelo nome (também uma série inteira já vista), uma coleção inteira (de filmes ou de jogos), marcar o próximo episódio, a categoria, a situação e quem vê (também de vários de uma vez), dizer onde assistir e em que plataformas jogar, mostrar as listas prontas, dizer os episódios e os jogos que vão sair e criar, renomear e apagar as categorias.

## Dados

Em **Configurações › Dados**: **Exportar** (a lista e as capas num .zip), **Backup na pasta share** (`share/odisseia/backups`, os 10 últimos), **Importar**, **Versões anteriores** (as 5 últimas: uma por dia e antes de importar, restaurar ou apagar tudo) e **Começar do zero** (apaga a lista; as chaves e as configurações ficam).

## Créditos

Este app usa a API do TMDB, mas não é endossado nem certificado pelo TMDB. Onde assistir: dados da [JustWatch](https://www.justwatch.com/br). Os jogos: dados do [IGDB](https://www.igdb.com/).
