# OdisseIA

![OdisseIA](odisseia/logo.png)

Um app (add-on) do Home Assistant para os filmes, as séries e os jogos da casa, da família de apps da CorrerIA Code.

- **Agora**: o que a casa está vendo, o episódio em que cada um parou, os episódios e os jogos que vão sair e o que quer ver ou jogar.
- **Adicionar** pelo nome ou pelas listas prontas, com a capa: filmes e séries em português (TMDB), jogos (IGDB); uma série ou uma coleção inteira de uma vez.
- **Situação, episódio, categoria (com cor), quem vê, onde assistir no Brasil** (dados da JustWatch) e **onde jogar**.
- **Buscar** e **Vistos**, em capas ou em lista, com o Selecionar para mudar vários de uma vez.
- **Pelo CorrerIA**: no WhatsApp, no Claude e no Gemini.
- Exportar, backup, importar e versões anteriores; tema claro e escuro e a cor da casa.

## Instalação

1. No Home Assistant: **Configurações → Aplicativos → Loja de aplicativos**.
2. No menu **⋮ → Repositórios**, adicione:
   ```
   https://github.com/diegozapella63/OdisseIA
   ```
3. Procure **OdisseIA** na loja, toque em **Instalar** e depois em **Iniciar**.
4. Ative **Mostrar na barra lateral** e ponha a chave grátis do TMDB em **Mais › Configurações › Integrações** (o passo a passo está na aba **Documentação**).

[![Adicionar o repositório ao Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fdiegozapella63%2FOdisseIA)

## Desenvolvimento

```
python3 dev/rodar.py   # http://127.0.0.1:8099, com um TMDB e um IGDB de mentira (títulos e jogos inventados)
tests/run.sh           # os testes (a tela precisa do playwright)
```

As instruções para quem mexe no código (pessoas ou IAs) estão em [AGENTS.md](AGENTS.md).

Este app usa a API do TMDB, mas não é endossado nem certificado pelo TMDB. Os jogos: dados do IGDB.
