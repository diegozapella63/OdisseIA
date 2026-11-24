# OdisseIA

Os filmes e as séries da casa: o que cada pessoa está vendo, já viu, quer ver ou abandonou, o episódio em que parou, a nota, os episódios que vão sair e onde assistir no Brasil.

## Primeiro passo: a chave do TMDB

Os filmes, as séries, as capas e onde assistir vêm do [TMDB](https://www.themoviedb.org/), de graça, para uso pessoal:

1. Crie uma conta no [TMDB](https://www.themoviedb.org/signup).
2. Em [Configurações › API](https://www.themoviedb.org/settings/api), peça uma chave de **uso pessoal** (Developer).
3. No OdisseIA, em **Mais › Configurações › Integrações › Filmes e séries (TMDB)**, cole a **Chave da API** ou o **Token de leitura da API** e toque em **Salvar e testar**.

A chave fica só no app (em `/data/segredos.json`); a tela mostra só o fim dela. Ela não vai no Exportar nem no Backup.

## Agora

- **Vendo agora**: o que está sendo visto, com o episódio em que parou e quantos já saíram e faltam. O botão com o episódio (**✓ T2 E6**) marca o seguinte como visto.
- **Novos episódios**: as séries da lista com episódio saindo nos próximos 30 dias.
- **Quero ver**: o que a casa quer ver (os mais recentes; **Ver todos** abre o Buscar).

## Adicionar (o + no meio da barra)

Abre nas **listas prontas** do TMDB: **Em alta** (na semana), **Mais populares**, **Mais bem avaliados**, **Coleções** e **Estreias** (os filmes nos cinemas do Brasil; nas séries, as que estão no ar). **Mostrar mais** traz a próxima página. Para procurar um título, escreva o nome: a busca é no TMDB, em português. Tudo, Filmes ou Séries filtra.

Em cada capa:
- **Já vi** (o visto): põe na lista como **Visto**. Numa série, marca a série inteira, até o último episódio que saiu. O que ainda não saiu não tem esse botão.
- **Quero ver** (o marcador): põe na lista como **Quero ver**.
- Tocar na capa abre o título (fora da lista, ele entra como Quero ver). O Voltar do celular volta para a lista.

O que já está na lista mostra a situação no canto da capa.

## Categorias

Em **Mais › Categorias** ficam as categorias da casa, uma lista para as séries e outra para os filmes (até 40 em cada). Escreva o nome e toque em **Adicionar** (ou Enter); o nome muda no próprio campo; a lixeira apaga (os títulos ficam sem categoria). O Buscar filtra pela categoria.

## Coleções de filmes

As sagas (os filmes de uma mesma história) aparecem na busca com a etiqueta **Coleção**, na lista pronta **Coleções** (as sagas dos filmes mais populares e mais bem avaliados) e no botão **Coleção** embaixo da capa de um filme que faz parte de uma. Na capa da coleção, o ✓ marca todos os filmes já lançados como Visto, e o marcador, todos como Quero ver, sem abrir. A coleção abre com todos os filmes, na ordem em que saíram: **Quero ver todos** põe os que faltam na lista; **Já vi todos** põe os que já saíram como Visto (e marca como Visto os que já estavam na lista).

## O título

- **Situação**: Quero ver ou Visto. Visto numa série marca até o último episódio que saiu. A série em Quero ver com algum episódio visto aparece em **Continuar vendo**, no Agora.
- **Parou em** (séries): a temporada e o último episódio visto. **Vi o T2 E6** marca o seguinte. No último episódio de uma série que acabou, ela vira **Visto** sozinha.
- **Categoria**: uma das categorias da casa (as de séries ou as de filmes), ou Nenhuma. Sem nenhuma criada, o botão **Criar categorias** leva a Mais › Categorias.
- **Quem**: quem da casa quer ver ou viu (as pessoas do Home Assistant); **Todos** marca a casa toda. Desliga em **Configurações › Opções › Quem vê**.
- **Onde assistir**: no Brasil, por assinatura, grátis, para alugar ou comprar. Dados da JustWatch, pelo TMDB.
- **Notas**: o que a casa achou, quem indicou.
- **Atualizar** busca de novo no TMDB (o app já atualiza sozinho: as séries que a casa vê ou quer ver, uma vez por dia; o resto, uma vez por semana).

## Buscar e Histórico

**Buscar** filtra a lista pelo nome e, em **Filtros** (que fecha e abre), pelo tipo, pela situação, pela categoria e pela pessoa. **Histórico** mostra o que a casa terminou de ver, mês a mês, numa aba para as séries e outra para os filmes.

## O que controlar

Em **Configurações › Opções › O que controlar**, ligue só as séries, só os filmes ou os dois. O que fica desligado some da tela e do CorrerIA; nada é apagado, e volta ao ligar de novo.

## Pelo CorrerIA

Com **Configurações › Integrações › CorrerIA** ligado, o CorrerIA (WhatsApp, Claude e Gemini) pode perguntar o que a casa está vendo, adicionar um filme ou uma série pelo nome (também uma série inteira já vista), uma coleção de filmes inteira, marcar o próximo episódio, a nota, a situação e quem vê, dizer onde assistir e mostrar as listas prontas (em alta, mais populares, mais bem avaliados e estreias).

## Dados

Em **Configurações › Dados**: **Exportar** (a lista e as capas num .zip), **Backup na pasta share** (`share/odisseia/backups`, os 10 últimos), **Importar**, **Versões anteriores** (as 5 últimas: uma por dia e antes de importar, restaurar ou apagar tudo) e **Começar do zero** (apaga a lista; a chave e as configurações ficam).

## Créditos

Este app usa a API do TMDB, mas não é endossado nem certificado pelo TMDB. Onde assistir: dados da [JustWatch](https://www.justwatch.com/br).
