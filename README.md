# OdisseIA

![OdisseIA](odisseia/logo.png)

Um app (add-on) do Home Assistant para os filmes e as séries da casa, da família de apps da CorrerIA Code.

- **Agora**: o que a casa está vendo, o episódio em que cada um parou, os episódios que vão sair e o que quer ver.
- **Adicionar** pelo nome, com a capa, em português (TMDB).
- **Situação, episódio, nota, quem vê e onde assistir no Brasil** (dados da JustWatch).
- **Buscar** e **Vistos** (mês a mês).
- **Pelo CorrerIA**: no WhatsApp, no Claude e no Gemini.
- Exportar, backup, importar e versões anteriores; tema claro e escuro e a cor da casa.

## Instalar

No Home Assistant: **Configurações › Aplicativos › Loja de aplicativos › ⋮ › Repositórios**, adicione
`https://github.com/diegozapella63/OdisseIA` e instale o **OdisseIA**. Depois, ponha a chave grátis do TMDB em
**Mais › Configurações › Integrações** (veja a aba Documentação).

## Desenvolvimento

```
python3 dev/rodar.py   # http://127.0.0.1:8099, com um TMDB de mentira (títulos inventados)
tests/run.sh           # os testes (a tela precisa do playwright)
```

As instruções para quem mexe no código (pessoas ou IAs) estão em [AGENTS.md](AGENTS.md).

Este app usa a API do TMDB, mas não é endossado nem certificado pelo TMDB.
