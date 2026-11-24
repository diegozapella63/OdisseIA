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

Escreva o nome: a busca é no TMDB, em português. Tudo, Filme ou Série filtra. Um toque põe o título na lista como **Quero ver** e abre ele. **Na lista** mostra o que já está lá.

## O título

- **Situação**: Quero ver, Vendo, Visto ou Abandonado. Visto numa série marca até o último episódio que saiu.
- **Parou em** (séries): a temporada e o último episódio visto. **Vi o T2 E6** marca o seguinte. No último episódio de uma série que acabou, ela vira **Visto** sozinha.
- **Nota**: de 1 a 5 estrelas (tocar de novo na mesma tira).
- **Quem**: quem da casa está vendo ou viu (as pessoas do Home Assistant). Desliga em **Configurações › Opções › Quem vê**.
- **Onde assistir**: no Brasil, por assinatura, grátis, para alugar ou comprar. Dados da JustWatch, pelo TMDB.
- **Notas**: o que a casa achou, quem indicou.
- **Atualizar** busca de novo no TMDB (o app já atualiza sozinho: as séries que a casa vê ou quer ver, uma vez por dia; o resto, uma vez por semana).

## Buscar e Vistos

**Buscar** filtra a lista pelo nome, pelo tipo, pela situação e pela pessoa. Os **Abandonados** ficam recolhidos no fim. **Vistos** mostra o que a casa terminou de ver, mês a mês.

## Pelo CorrerIA

Com **Configurações › Integrações › CorrerIA** ligado, o CorrerIA (WhatsApp, Claude e Gemini) pode perguntar o que a casa está vendo, adicionar um filme ou uma série pelo nome, marcar o próximo episódio, a nota, a situação e quem vê, e dizer onde assistir.

## Dados

Em **Configurações › Dados**: **Exportar** (a lista e as capas num .zip), **Backup na pasta share** (`share/odisseia/backups`, os 10 últimos), **Importar**, **Versões anteriores** (as 5 últimas: uma por dia e antes de importar, restaurar ou apagar tudo) e **Começar do zero** (apaga a lista; a chave e as configurações ficam).

## Créditos

Este app usa a API do TMDB, mas não é endossado nem certificado pelo TMDB. Onde assistir: dados da [JustWatch](https://www.justwatch.com/br).
