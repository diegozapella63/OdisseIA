"""As ferramentas do CorrerIA (o WhatsApp, o Claude, o Gemini e a conversa do CorrerIA): ler e mudar os títulos com as
mesmas regras da tela (regras.py). O contrato é o mesmo de todos os apps da família: GET /api/integracao/ferramentas dá a
lista e POST {nome, argumentos, pessoa, cliente} chama uma; um argumento que não vale volta como erro (400) com a frase
do que vale, para a IA tentar de novo."""
from datetime import date, datetime, timedelta

import igdb as G
import regras as R
import tmdb as T

INSTRUCOES = ("OdisseIA: os filmes, as séries, os jogos e os livros da casa: o que cada pessoa quer ver ou já viu (as duas situações, "
              "quero e visto; num jogo, quero é Quero jogar e visto é Jogado; num livro, Quero ler e Lido), o episódio em que parou numa série (em "
              "andamento: em Quero ver, com algum episódio visto), a categoria (as da casa, uma lista para cada tipo), "
              "onde assistir no Brasil (dados da JustWatch) e as plataformas de um jogo. Os ids dos títulos "
              "começam com t. Para marcar o episódio seguinte ao último visto, use proximo_episodio; para um episódio "
              "certo, marcar com temporada e episodio. Para pôr um título novo, adicionar procura pelo nome (filmes e "
              "séries no TMDB, jogos no IGDB, livros na Open Library, também pelo autor ou pelo ISBN; diga o tipo; os livros "
              "não têm listas prontas nem coleções); uma série inteira já vista é adicionar com situacao visto "
              "(marca até o último episódio que saiu). Uma coleção inteira de uma vez (uma saga de filmes ou uma série "
              "de jogos): adicionar_colecao.")
SIT = list(R.SITUACOES)
TIPOS = list(R.TIPOS)


def _f(nome, titulo, descricao, props=None, obrig=(), grava=False, apaga=False):
    return {"nome": nome, "titulo": titulo, "descricao": descricao, "grava": grava, "apaga": apaga,
            "entrada": {"type": "object", "properties": props or {}, "required": list(obrig), "additionalProperties": False}}


_TIT = {"type": "string", "description": "O id do título (t…) ou o nome."}
_QUEM = {"type": "array", "items": {"type": "string"}, "description": "Os nomes das pessoas da casa (troca a lista); «todos» põe a casa toda."}
_CAT = {"type": "string", "description": "O nome de uma categoria da casa (as do tipo do título); vazio tira."}
_SIT = {"type": "string", "enum": SIT, "description": "quero (Quero ver; num jogo, Quero jogar; num livro, Quero ler) ou visto (num jogo, Jogado; num livro, Lido)."}
FERRAMENTAS = [
    _f("resumo", "Resumo", "Quantos títulos há em cada situação, as séries em andamento (com o episódio e quantos faltam), "
       "os episódios que vão sair nos próximos 14 dias, os jogos em Quero jogar que saem nos próximos 30 dias e as categorias da casa."),
    _f("buscar", "Buscar na lista", "Os títulos da lista da casa, com filtros. Sem filtro, os mais recentes. Com onde, só os que estão "
       "num serviço (Netflix, Max, Prime Video…) por assinatura ou de graça, pelo que a JustWatch sabe; com por_servico, em vez da "
       "lista, quantos títulos de cada assinatura (dos filtrados): para saber que serviço a casa usa e qual sobra.",
       {"texto": {"type": "string", "description": "Parte do nome."}, "tipo": {"type": "string", "enum": TIPOS},
        "situacao": _SIT, "pessoa": {"type": "string", "description": "O nome de quem vê ou viu."},
        "categoria": {"type": "string", "description": "O nome de uma categoria da casa."},
        "onde": {"type": "string", "description": "O nome de um serviço (parte do nome vale: netflix, prime)."},
        "por_servico": {"type": "boolean", "description": "true: quantos títulos de cada assinatura, no lugar da lista."},
        "limite": {"type": "integer", "minimum": 1, "maximum": 50}}),
    _f("ver", "Ver um título", "Tudo de um título: a sinopse, os gêneros, as temporadas, o episódio, a categoria, as notas, "
       "onde assistir no Brasil e, num jogo, as plataformas.", {"titulo": _TIT}, ["titulo"]),
    _f("lista_pronta", "Lista pronta", "Uma lista pronta (filmes e séries do TMDB, jogos do IGDB): em alta, mais populares "
       "(num jogo, os mais jogados), mais bem avaliados, coleções ou estreias (os filmes nos cinemas do Brasil, as séries "
       "no ar, os jogos lançados nos últimos 90 dias), com o que já está na lista da casa. Para sugerir o que ver ou jogar.",
       {"lista": {"type": "string", "enum": list(T.LISTAS)}, "tipo": {"type": "string", "enum": TIPOS}}, ["lista"]),
    _f("adicionar", "Adicionar", "Procura o filme, a série (no TMDB), o jogo (no IGDB) ou o livro (na Open Library; com tipo livro, o nome pode ser o "
       "título, o autor ou o ISBN, o número do código de barras) e põe na lista da casa (o que combina com o tipo e o ano). "
       "Se já está na lista, diz.",
       {"nome": {"type": "string"}, "tipo": {"type": "string", "enum": TIPOS},
        "ano": {"type": "integer", "minimum": 1880, "maximum": 2100}, "situacao": _SIT, "quem": _QUEM, "categoria": _CAT},
       ["nome"], grava=True),
    _f("adicionar_colecao", "Adicionar uma coleção", "Procura uma coleção pelo nome (uma saga de filmes no TMDB ou uma série "
       "de jogos no IGDB) e põe tudo dela na lista. Com situacao visto, só os que já saíram, e os que já estavam na lista "
       "viram Visto (num jogo, Jogado).",
       {"nome": {"type": "string"}, "tipo": {"type": "string", "enum": ["filme", "jogo"], "description": "filme (de início) ou jogo."},
        "situacao": _SIT, "categoria": {"type": "string", "description": "O nome de uma categoria da casa (as do tipo): vale para todos; vazio tira."}}, ["nome"], grava=True),
    # 0.15.0 (o dono: "pode adicionar esses também"): o que ver ou jogar hoje
    _f("sugerir", "O que ver hoje", "Sugere o que ver ou jogar da lista da casa, sem pesquisar nada: primeiro as séries em andamento "
       "com episódio para ver, depois o que está em Quero ver numa assinatura ou de graça e combina com os gêneros que a casa "
       "mais viu. Dá para filtrar pelo tipo, por quem e por um serviço.",
       {"tipo": {"type": "string", "enum": TIPOS}, "quem": _QUEM,
        "servico": {"type": "string", "description": "Só o que está nesse serviço (o nome ou parte dele)."},
        "quantos": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Padrão: 5."}}),
    _f("marcar", "Marcar", "Muda a situação (quero ou visto), a categoria, o episódio (temporada e episodio, numa série), "
       "quem vê e as notas de um título.",
       {"titulo": _TIT, "situacao": _SIT, "categoria": _CAT,
        "temporada": {"type": "integer", "minimum": 0}, "episodio": {"type": "integer", "minimum": 0}, "quem": _QUEM,
        "notas": {"type": "string"}}, ["titulo"], grava=True),
    _f("marcar_varios", "Marcar vários", "Muda de uma vez a categoria, quem vê e a situação de vários títulos (os ids ou os "
       "nomes). A categoria vale para os títulos do tipo dela.",
       {"titulos": {"type": "array", "items": {"type": "string"}, "description": "Os ids (t…) ou os nomes."}, "situacao": _SIT,
        "categoria": _CAT, "quem": _QUEM}, ["titulos"], grava=True),
    _f("proximo_episodio", "Próximo episódio", "Marca como visto o episódio seguinte ao último visto de uma série.",
       {"titulo": _TIT}, ["titulo"], grava=True),
    # 0.6.0 (o dono: "todas", das que faltavam): as categorias, como em Mais › Categorias
    _f("categoria", "Criar, renomear ou apagar categoria", "As categorias da casa, de cada tipo (as de agora estão no resumo): "
       "nova (com o nome), renomear (o nome e o novo_nome) ou apagar (os títulos dela ficam sem categoria). A cor da nova é a "
       "menos usada.",
       {"acao": {"type": "string", "enum": ["nova", "renomear", "apagar"]}, "tipo": {"type": "string", "enum": TIPOS},
        "nome": {"type": "string"}, "novo_nome": {"type": "string"}}, ["acao", "tipo", "nome"], grava=True),
    # 0.14.0 (o dono, às ferramentas que faltavam: "pode seguir em todas"): o Apagar do Selecionar
    _f("apagar_varios", "Apagar vários", "Tira de uma vez vários títulos da lista da casa (os ids ou os nomes). Se um deles não "
       "é achado, nenhum sai.",
       {"titulos": {"type": "array", "items": {"type": "string"}, "description": "Os ids (t…) ou os nomes."}}, ["titulos"],
       grava=True, apaga=True),
    _f("apagar", "Apagar", "Tira um título da lista da casa.", {"titulo": _TIT}, ["titulo"], grava=True, apaga=True),
]
POR_NOME = {f["nome"]: f for f in FERRAMENTAS}


class ErroFerramenta(ValueError):
    pass


def lista():
    return [dict(f) for f in FERRAMENTAS]


def conferir(nome, args):
    """Os argumentos valem pelo esquema da ferramenta (os que não existem, os obrigatórios e os tipos)."""
    f = POR_NOME[nome]
    args = args if isinstance(args, dict) else {}
    props = f["entrada"]["properties"]
    sobra = [k for k in args if k not in props]
    if sobra:
        raise ErroFerramenta(f"Argumento desconhecido: {', '.join(sobra)}. Valem: {', '.join(props) or 'nenhum'}.")
    falta = [k for k in f["entrada"]["required"] if args.get(k) in (None, "")]
    if falta:
        raise ErroFerramenta("Falta: " + ", ".join(falta) + ".")
    for k, v in args.items():
        p = props[k]
        if p["type"] == "integer" and (not isinstance(v, int) or isinstance(v, bool)):
            raise ErroFerramenta(f"{k} é um número inteiro.")
        if p["type"] == "string" and not isinstance(v, str):
            raise ErroFerramenta(f"{k} é um texto.")
        if p["type"] == "array" and (not isinstance(v, list) or any(not isinstance(x, str) for x in v)):
            raise ErroFerramenta(f"{k} é uma lista de nomes.")
        if "enum" in p and v not in p["enum"]:
            raise ErroFerramenta(f"{k} vale: {', '.join(p['enum'])}.")
        if p["type"] == "integer" and ("minimum" in p and v < p["minimum"] or "maximum" in p and v > p["maximum"]):
            raise ErroFerramenta(f"{k} vai de {p['minimum']} a {p['maximum']}." if "maximum" in p else f"{k} é {p['minimum']} ou mais.")
    return args


def ids_de(nomes, pessoas):
    """Os ids das pessoas pelos nomes (o primeiro nome basta, sem acento nem maiúsculas); «todos» é a casa toda."""
    if any(R.sem_acento(n) in ("todos", "todas", "a casa toda") for n in nomes):
        return [p["id"] for p in pessoas]
    out = []
    for n in nomes:
        alvo = R.sem_acento(n)
        p = next((p for p in pessoas if alvo in (R.sem_acento(p["nome"]), R.sem_acento(p["nome"]).split(" ")[0], p["id"])), None)
        if not p:
            raise ErroFerramenta(f"«{n}» não é uma pessoa da casa. Valem: {', '.join(x['nome'] for x in pessoas) or 'nenhuma'}.")
        out.append(p["id"])
    return out


def nomes_de(ids, pessoas):
    m = {p["id"]: p["nome"] for p in pessoas}
    return [m.get(i, i.split(".", 1)[-1].replace("_", " ").title()) for i in ids]


def linha(t, pessoas, d=None):
    s = f"{t['id']} | {t['nome']}" + (f" ({t['ano']})" if t["ano"] else "") + f" · {R.TIPOS[t['tipo']].lower()} · {R.nome_sit(t['tipo'], t['situacao']).lower()}"
    if t["tipo"] == "livro" and t.get("autores"):
        s += " · " + t["autores"][0]
    if t["tipo"] == "serie" and t["temp"]:
        s += f" · parou em {R.ep_txt(t['temp'], t['ep'])}"
        f = R.faltam(t)
        if f:
            s += f" · faltam {f}"
    cat = R.nome_categoria(d, t) if d else ""
    if cat:
        s += f" · {cat}"
    if t["quem"]:
        s += " · " + ", ".join(nomes_de(t["quem"], pessoas))
    return s


def _onde(t):
    o = t.get("onde") or {}
    partes = [f"{n}: {', '.join(o[k])}" for k, n in (("assinatura", "assinatura"), ("gratis", "grátis"), ("alugar", "alugar"), ("comprar", "comprar")) if o.get(k)]
    return ("Onde assistir no Brasil (JustWatch): " + "; ".join(partes) + ".") if partes else "Onde assistir: nada no Brasil, pelo que a JustWatch sabe."


def texto_sugestoes(d, a, pessoas, agora):
    """0.15.0: o que ver ou jogar hoje, da lista: as séries em andamento com episódio para ver, depois o Quero ver, o que está
    numa assinatura ou de graça na frente e, entre eles, o que combina com os gêneros que a casa mais viu."""
    quantos = max(1, min(10, int(a.get("quantos") or 5)))
    hoje = agora[:10]
    ts = [t for t in d["titulos"] if t["situacao"] == "quero" and (not a.get("tipo") or t["tipo"] == a["tipo"])]
    ts = [t for t in ts if not (t["tipo"] == "jogo" and t.get("data") and t["data"] > hoje)]  # o jogo que ainda não saiu
    if a.get("quem"):
        quem = set(ids_de(a["quem"], pessoas))
        ts = [t for t in ts if not t["quem"] or quem & set(t["quem"])]
    serv = R.sem_acento(a.get("servico") or "")

    def onde(t):
        o = t.get("onde") or {}
        return [n for n in list(o.get("assinatura") or []) + list(o.get("gratis") or []) if not serv or serv in R.sem_acento(n)]
    if serv:
        ts = [t for t in ts if onde(t)]
    gosto = {}
    for t in d["titulos"]:
        if t["situacao"] == "visto":
            for g in t.get("generos") or []:
                gosto[g] = gosto.get(g, 0) + 1

    def nota(t):
        vendo = R.em_andamento(t) and bool(R.faltam(t))
        return (0 if vendo else 1, 0 if (onde(t) or t["tipo"] in ("jogo", "livro")) else 1, -sum(gosto.get(g, 0) for g in t.get("generos") or []), R.sem_acento(t["nome"]))
    ts.sort(key=nota)
    if not ts:
        return "Nada na lista para sugerir com esses filtros."
    linhas = [f"{min(quantos, len(ts))} de {len(ts)} {'título' if len(ts) == 1 else 'títulos'} para hoje:"]
    for t in ts[:quantos]:
        porque = []
        if R.em_andamento(t) and R.faltam(t):
            porque.append(f"em andamento, parou em {R.ep_txt(t['temp'], t['ep'])}")
        if onde(t):
            porque.append("em " + ", ".join(dict.fromkeys(onde(t))))
        elif t["tipo"] in ("filme", "serie"):
            porque.append("em nenhuma assinatura")
        comuns = [g for g in t.get("generos") or [] if gosto.get(g)]
        if comuns:
            porque.append("a casa já viu bastante " + ", ".join(comuns[:2]).lower())
        linhas.append(f"- {t['id']} | {t['nome']}" + (f" ({t['ano']})" if t["ano"] else "") + f" · {R.TIPOS[t['tipo']].lower()}" + (": " + "; ".join(porque) if porque else ""))
    return "\n".join(linhas)


def texto_servicos(ts, a):
    """0.13.0: quantos títulos de cada assinatura (por_servico do buscar), o que mais tem primeiro, e os que não estão em nenhuma."""
    conta, exemplos = {}, {}
    fora = 0
    for t in ts:
        nomes = list(dict.fromkeys((t.get("onde") or {}).get("assinatura") or []))
        if not nomes:
            fora += 1
        for n in nomes:
            conta[n] = conta.get(n, 0) + 1
            exemplos.setdefault(n, []).append(t["nome"])
    if not ts:
        return "Nenhum título com esses filtros."
    filtro = R.nome_sit(a["tipo"], a["situacao"]).lower() if a.get("tipo") and a.get("situacao") else ""
    out = [f"{len(ts)} títulos" + (f" ({filtro})" if filtro else "") + ", por assinatura (pelo que a JustWatch sabe):"]
    for n, k in sorted(conta.items(), key=lambda x: (-x[1], R.sem_acento(x[0]))):
        out.append(f"- {n}: {k} " + ("título" if k == 1 else "títulos") + " (" + ", ".join(exemplos[n][:4]) + (", …" if k > 4 else "") + ")")
    if fora:
        out.append(f"- Em nenhuma assinatura: {fora}")
    return "\n".join(out)


def resumo(d, pessoas, hoje=None):
    hoje = hoje or date.today()
    ts = d["titulos"]
    if not ts:
        return "A lista da casa está vazia."
    cont = "; ".join(f"{R.PLURAIS[tp]}: " + ", ".join(f"{sum(1 for t in ts if t['tipo'] == tp and t['situacao'] == k)} {R.nome_sit(tp, k).lower()}" for k in R.SITUACOES)
                     for tp in R.TIPOS if any(t["tipo"] == tp for t in ts))
    out = [f"{len(ts)} títulos ({cont})."]
    vendo = [t for t in ts if R.em_andamento(t)]
    if vendo:
        out.append("Séries em andamento:")
        out += ["- " + linha(t, pessoas, d) for t in vendo[:12]]
    ate = (hoje + timedelta(days=14)).isoformat()
    prox = sorted((t for t in ts if t["tipo"] == "serie" and t.get("proximo")
                   and hoje.isoformat() <= t["proximo"]["data"] <= ate), key=lambda t: t["proximo"]["data"])
    if prox:
        out.append("Episódios que saem nos próximos 14 dias:")
        out += [f"- {R.data_br(t['proximo']['data'])}: {t['nome']} {R.ep_txt(t['proximo']['temp'], t['proximo']['ep'])}" for t in prox[:12]]
    # 0.9.0: os jogos em Quero jogar que saem nos próximos 30 dias (a etapa Vão sair das rondas do CorrerIA 1.37.0)
    ate_j = (hoje + timedelta(days=30)).isoformat()
    jogos = sorted((t for t in ts if t["tipo"] == "jogo" and t["situacao"] == "quero" and t.get("data") and hoje.isoformat() <= t["data"] <= ate_j),
                   key=lambda t: t["data"])
    if jogos:
        out.append("Jogos que saem nos próximos 30 dias:")
        out += [f"- {R.data_br(t['data'])}: {t['nome']}" + (f" ({', '.join(t['plataformas'][:3])})" if t.get("plataformas") else "") for t in jogos[:12]]
    cats = [f"{R.PLURAIS[k]}: {', '.join(c['nome'] for c in d['categorias'][k])}" for k in R.TIPOS if d.get("categorias", {}).get(k)]
    if cats:
        out.append("Categorias da casa: " + "; ".join(cats) + ".")
    return "\n".join(out)


def chamar(nome, args, d, pessoas, pessoa=None, det=None, agora=None):
    """(texto, mudou). det: os detalhes do TMDB que o server.py já procurou (só no adicionar)."""
    if nome not in POR_NOME:
        raise KeyError(nome)
    a = conferir(nome, args)
    agora = agora or datetime.now().isoformat(timespec="seconds")
    try:
        if nome == "resumo":
            return resumo(d, pessoas, date.fromisoformat(agora[:10])), False
        if nome == "sugerir":
            return texto_sugestoes(d, a, pessoas, agora), False
        if nome == "buscar":
            ts = d["titulos"]
            if a.get("texto"):
                alvo = R.sem_acento(a["texto"])
                ts = [t for t in ts if alvo in R.sem_acento(t["nome"]) or alvo in R.sem_acento(t["original"])]
            if a.get("tipo"):
                ts = [t for t in ts if t["tipo"] == a["tipo"]]
            if a.get("situacao"):
                ts = [t for t in ts if t["situacao"] == a["situacao"]]
            if a.get("pessoa"):
                pid = ids_de([a["pessoa"]], pessoas)[0]
                ts = [t for t in ts if pid in t["quem"]]
            if a.get("categoria"):
                alvo = R.sem_acento(a["categoria"])
                ts = [t for t in ts if R.sem_acento(R.nome_categoria(d, t)) == alvo]
            if a.get("onde"):  # 0.13.0: por assinatura ou de graça, num serviço
                alvo = R.sem_acento(a["onde"])
                ts = [t for t in ts if any(alvo in R.sem_acento(n) for k in ("assinatura", "gratis") for n in (t.get("onde") or {}).get(k) or [])]
            if a.get("por_servico") is True:
                return texto_servicos(ts, a), False
            ts = sorted(ts, key=lambda t: t["atualizado"], reverse=True)
            lim = a.get("limite") or 20
            if not ts:
                return "Nenhum título com esses filtros.", False
            com_onde = bool(a.get("onde"))
            return "\n".join([f"{len(ts)} títulos" + (f" (os {lim} mais recentes)" if len(ts) > lim else "") + ":"]
                              + ["- " + linha(t, pessoas, d) + (" · " + _onde(t) if com_onde else "") for t in ts[:lim]]), False
        t = R.achar(d, a.get("titulo")) if "titulo" in a else None
        if nome == "ver":
            out = [linha(t, pessoas, d)]
            if t["generos"]:
                out.append("Gêneros: " + ", ".join(t["generos"]) + ".")
            if t["tipo"] == "filme" and t.get("duracao"):
                out.append(f"Duração: {t['duracao']} min.")
            if t["tipo"] == "livro":
                if t.get("autores"):
                    out.append(("Autores: " if len(t["autores"]) > 1 else "Autor: ") + ", ".join(t["autores"]) + ".")
                if t.get("paginas"):
                    out.append(f"Páginas: {t['paginas']}.")
                if t.get("isbn"):
                    out.append(f"ISBN: {t['isbn']}.")
            if t["tipo"] == "jogo":
                if t.get("plataformas"):
                    out.append("Plataformas: " + ", ".join(t["plataformas"]) + ".")
                if t.get("data"):
                    out.append(("Sai em " if t["data"] > agora[:10] else "Saiu em ") + R.data_br(t["data"]) + ".")
            if t["tipo"] in ("filme", "jogo") and t.get("colecao"):
                out.append(f"Coleção: {t['colecao']['nome']}.")
            if t["tipo"] == "serie":
                if t["temporadas"]:
                    out.append("Temporadas: " + ", ".join(f"T{s['n']} ({s['episodios']} ep.)" for s in t["temporadas"]) + (" · terminou" if t["fim"] else "") + ".")
                if t.get("ultimo"):
                    out.append(f"Último que saiu: {R.ep_txt(t['ultimo']['temp'], t['ultimo']['ep'])}" + (f" em {R.data_br(t['ultimo']['data'])}" if t["ultimo"]["data"] else "") + ".")
                if t.get("proximo"):
                    out.append(f"Próximo: {R.ep_txt(t['proximo']['temp'], t['proximo']['ep'])} em {R.data_br(t['proximo']['data'])}.")
            if t["tipo"] in ("filme", "serie"):
                out.append(_onde(t))
            if t["sinopse"]:
                out.append("Sinopse: " + t["sinopse"])
            if t["notas"]:
                out.append("Notas da casa: " + t["notas"])
            return "\n".join(out), False
        if nome == "adicionar":
            if not det:
                onde = "IGDB" if a.get("tipo") == "jogo" else "TMDB" if a.get("tipo") or "jogo" not in R.tipos_ligados(d) else "TMDB nem no IGDB"
                raise ErroFerramenta(f"Não achei «{a['nome']}» no {onde}.")
            quem = ids_de(a["quem"], pessoas) if "quem" in a else ([pessoa] if pessoa and pessoa in {p["id"] for p in pessoas} else [])
            cat = R.achar_categoria(d, det["tipo"], a["categoria"]) if a.get("categoria") else ""
            novo, criou = R.criar(d, det, a.get("situacao") or "quero", quem, agora)
            if not criou:
                return f"Já está na lista: {linha(novo, pessoas, d)}", False
            if cat:
                novo["categoria"] = cat
            return f"Adicionado: {linha(novo, pessoas, d)}", True
        if nome == "marcar":
            campos = {k: a[k] for k in ("situacao", "notas") if k in a}
            if "categoria" in a:
                campos["categoria"] = R.achar_categoria(d, t["tipo"], a["categoria"])
            if "temporada" in a or "episodio" in a:
                campos["temp"], campos["ep"] = a.get("temporada", t.get("temp", 0)), a.get("episodio", t.get("ep", 0))
            if "quem" in a:
                campos["quem"] = ids_de(a["quem"], pessoas)
            if not campos:
                raise ErroFerramenta("Diga o que mudar: situacao, categoria, temporada e episodio, quem ou notas.")
            R.mudar(t, campos, {p["id"] for p in pessoas}, agora)
            return f"Feito: {linha(t, pessoas, d)}", True
        if nome == "marcar_varios":
            ts = list({id(t): t for t in (R.achar(d, x) for x in a["titulos"])}.values())
            if not ts:
                raise ErroFerramenta("Diga quais títulos.")
            base = {k: a[k] for k in ("situacao",) if k in a}
            if "quem" in a:
                base["quem"] = ids_de(a["quem"], pessoas)
            if not base and "categoria" not in a:
                raise ErroFerramenta("Diga o que mudar: situacao, categoria ou quem.")
            itens = []
            for t in ts:
                c = dict(base)
                if "categoria" in a:
                    c["categoria"] = R.achar_categoria(d, t["tipo"], a["categoria"])
                itens.append({"id": t["id"], "campos": c})
            R.lote(d, itens, {p["id"] for p in pessoas}, agora)
            return "\n".join([f"Feito em {len(ts)} {'título' if len(ts) == 1 else 'títulos'}:"] + ["- " + linha(t, pessoas, d) for t in ts]), True
        if nome == "proximo_episodio":
            R.proximo_ep(t, agora)
            return f"Feito: {t['nome']} {R.ep_txt(t['temp'], t['ep'])} visto." + (" A série acabou: ficou como Visto." if t["situacao"] == "visto" else ""), True
        if nome == "categoria":
            tipo, acao = a["tipo"], a["acao"]
            if tipo not in R.tipos_ligados(d):
                raise ErroFerramenta(f"Os {R.PLURAIS[tipo]} estão desligados (Mais › Configurações › Opções › O que controlar).")
            if acao == "nova":
                c = R.mudar_categorias(d, {"acao": "nova", "tipo": tipo, "nome": a["nome"]})
                return f"Categoria criada nos {R.PLURAIS[tipo]}: {c['nome']}.", True
            cid = R.achar_categoria(d, tipo, a["nome"])
            velho = R.nome_categoria(d, {"tipo": tipo, "categoria": cid})
            if acao == "renomear":
                if not str(a.get("novo_nome") or "").strip():
                    raise ErroFerramenta("Falta: novo_nome.")
                c = R.mudar_categorias(d, {"acao": "renomear", "id": cid, "nome": a["novo_nome"]})
                return f"Categoria renomeada: {velho} → {c['nome']}.", True
            n = sum(1 for t in d["titulos"] if t.get("categoria") == cid)
            R.mudar_categorias(d, {"acao": "apagar", "id": cid})
            return f"Categoria apagada: {velho}." + (f" {n} {'título ficou' if n == 1 else 'títulos ficaram'} sem categoria." if n else ""), True
        if nome == "apagar_varios":
            ts = list({id(t): t for t in (R.achar(d, x) for x in a["titulos"])}.values())
            if not ts:
                raise ErroFerramenta("Diga quais títulos.")
            fora = {t["id"] for t in ts}
            d["titulos"] = [x for x in d["titulos"] if x["id"] not in fora]
            return "\n".join([f"{'Apagado' if len(ts) == 1 else 'Apagados'} {len(ts)} {'título' if len(ts) == 1 else 'títulos'}:"] + ["- " + t["nome"] for t in ts]), True
        if nome == "apagar":  # a última: o nome já foi conferido
            d["titulos"] = [x for x in d["titulos"] if x["id"] != t["id"]]
            return f"Apagado: {t['nome']}.", True
    except R.ErroRegra as e:
        raise ErroFerramenta(str(e))


def melhor(resultados, nome, tipo=None, ano=None):
    """O resultado da busca do TMDB que combina com o pedido: o tipo e o ano mandam; depois o nome igual; senão o primeiro."""
    rs = [r for r in resultados if not tipo or r["tipo"] == tipo]
    if ano:
        rs = [r for r in rs if r.get("ano") in (ano, ano - 1, ano + 1)] or rs
    alvo = R.sem_acento(nome)
    iguais = [r for r in rs if alvo in (R.sem_acento(r["nome"]), R.sem_acento(r["original"]))]
    return (iguais or rs or [None])[0]


def texto_colecao(res, situacao):
    """O que adicionar uma coleção fez, numa frase."""
    jogo = res.get("tipo") == "jogo"
    sit, visto = R.nome_sit(res.get("tipo") or "filme", situacao), R.nome_sit(res.get("tipo") or "filme", "visto")
    partes = []
    if res["novos"]:
        um, varios = ("jogo posto", "jogos postos") if jogo else ("filme posto", "filmes postos")
        partes.append(f"{res['novos']} {um if res['novos'] == 1 else varios} na lista como {sit}")
    if res["marcados"]:
        partes.append(f"{res['marcados']} {'marcado' if res['marcados'] == 1 else 'marcados'} como {visto}")
    if res["ja"]:
        partes.append(f"{res['ja']} já {'estava' if res['ja'] == 1 else 'estavam'} na lista")
    if res["fora"]:
        partes.append(f"{res['fora']} ainda não {'saiu' if res['fora'] == 1 else 'saíram'}")
    cat = f" Categoria de todos: {res['categoria'] or 'nenhuma'}." if "categoria" in res else ""
    return f"{res['nome']}: " + (", ".join(partes) if partes else "nada a mudar") + "." + cat


COLECOES = {"colecao": "coleção de filmes", "colecao_jogos": "coleção de jogos"}


def texto_lista(nome, rs, tipo=""):
    """Uma lista pronta em linhas, dizendo o que a casa já tem."""
    titulo = (G.LISTAS if tipo == "jogo" else T.LISTAS)[nome]
    if not rs:
        return f"{titulo}: nada agora."
    fontes = sorted({"IGDB" if r["tipo"] in ("jogo", "colecao_jogos") else "TMDB" for r in rs}, reverse=True)
    out = [f"{titulo} ({' e '.join(fontes)}):"]
    for r in rs:
        s = f"- {r['nome']}" + (f" ({r['ano']})" if r["ano"] else "") + f" · {COLECOES.get(r['tipo']) or R.TIPOS[r['tipo']].lower()}"
        if r.get("situacao"):
            s += f" · na lista: {R.nome_sit(r['tipo'], r['situacao']).lower()}"
        out.append(s)
    return "\n".join(out)
