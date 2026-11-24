"""As ferramentas do CorrerIA (o WhatsApp, o Claude, o Gemini e a conversa do CorrerIA): ler e mudar os títulos com as
mesmas regras da tela (regras.py). O contrato é o mesmo de todos os apps da família: GET /api/integracao/ferramentas dá a
lista e POST {nome, argumentos, pessoa, cliente} chama uma; um argumento que não vale volta como erro (400) com a frase
do que vale, para a IA tentar de novo."""
from datetime import date, datetime, timedelta

import regras as R
import tmdb as T

INSTRUCOES = ("OdisseIA: os filmes e as séries da casa: o que cada pessoa quer ver ou já viu (as duas situações, quero e "
              "visto), o episódio em que parou numa série (em andamento: em Quero ver, com algum episódio visto), a "
              "categoria (as da casa, uma lista para filmes e outra para séries) e onde assistir no Brasil (dados da "
              "JustWatch). Os ids dos títulos "
              "começam com t. Para marcar o episódio seguinte ao último visto, use proximo_episodio; para um episódio "
              "certo, marcar com temporada e episodio. Para pôr um título novo, adicionar procura pelo nome no TMDB; uma "
              "série inteira já vista é adicionar com situacao visto (marca até o último episódio que saiu). Uma coleção "
              "de filmes (uma saga) inteira, de uma vez: adicionar_colecao.")
SIT = list(R.SITUACOES)


def _f(nome, titulo, descricao, props=None, obrig=(), grava=False, apaga=False):
    return {"nome": nome, "titulo": titulo, "descricao": descricao, "grava": grava, "apaga": apaga,
            "entrada": {"type": "object", "properties": props or {}, "required": list(obrig), "additionalProperties": False}}


_TIT = {"type": "string", "description": "O id do título (t…) ou o nome."}
_QUEM = {"type": "array", "items": {"type": "string"}, "description": "Os nomes das pessoas da casa (troca a lista); «todos» põe a casa toda."}
_CAT = {"type": "string", "description": "O nome de uma categoria da casa (as de filmes ou as de séries); vazio tira."}
FERRAMENTAS = [
    _f("resumo", "Resumo", "Quantos títulos há em cada situação, as séries em andamento (com o episódio e quantos faltam), "
       "os episódios que vão sair nos próximos 14 dias e as categorias da casa."),
    _f("buscar", "Buscar na lista", "Os títulos da lista da casa, com filtros. Sem filtro, os mais recentes.",
       {"texto": {"type": "string", "description": "Parte do nome."}, "tipo": {"type": "string", "enum": ["filme", "serie"]},
        "situacao": {"type": "string", "enum": SIT}, "pessoa": {"type": "string", "description": "O nome de quem vê ou viu."},
        "categoria": {"type": "string", "description": "O nome de uma categoria da casa."},
        "limite": {"type": "integer", "minimum": 1, "maximum": 50}}),
    _f("ver", "Ver um título", "Tudo de um título: a sinopse, os gêneros, as temporadas, o episódio, a categoria, as notas e "
       "onde assistir no Brasil.", {"titulo": _TIT}, ["titulo"]),
    _f("lista_pronta", "Lista pronta", "Uma lista pronta do TMDB (em alta na semana, mais populares, mais bem avaliados ou "
       "estreias: os filmes nos cinemas do Brasil, as séries no ar), com o que já está na lista da casa. Para sugerir o que ver.",
       {"lista": {"type": "string", "enum": list(T.LISTAS)}, "tipo": {"type": "string", "enum": ["filme", "serie"]}}, ["lista"]),
    _f("adicionar", "Adicionar", "Procura o filme ou a série pelo nome no TMDB e põe na lista da casa (o primeiro que "
       "combina com o tipo e o ano). Se já está na lista, diz.",
       {"nome": {"type": "string"}, "tipo": {"type": "string", "enum": ["filme", "serie"]},
        "ano": {"type": "integer", "minimum": 1880, "maximum": 2100}, "situacao": {"type": "string", "enum": SIT}, "quem": _QUEM, "categoria": _CAT},
       ["nome"], grava=True),
    _f("adicionar_colecao", "Adicionar uma coleção", "Procura uma coleção de filmes (uma saga) pelo nome no TMDB e põe "
       "todos os filmes dela na lista. Com situacao visto, só os que já saíram, e os que já estavam na lista viram Visto.",
       {"nome": {"type": "string"}, "situacao": {"type": "string", "enum": ["quero", "visto"]}}, ["nome"], grava=True),
    _f("marcar", "Marcar", "Muda a situação (quero ou visto), a categoria, o episódio (temporada e episodio, numa série), "
       "quem vê e as notas de um título.",
       {"titulo": _TIT, "situacao": {"type": "string", "enum": SIT}, "categoria": _CAT,
        "temporada": {"type": "integer", "minimum": 0}, "episodio": {"type": "integer", "minimum": 0}, "quem": _QUEM,
        "notas": {"type": "string"}}, ["titulo"], grava=True),
    _f("proximo_episodio", "Próximo episódio", "Marca como visto o episódio seguinte ao último visto de uma série.",
       {"titulo": _TIT}, ["titulo"], grava=True),
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
    s = f"{t['id']} | {t['nome']}" + (f" ({t['ano']})" if t["ano"] else "") + f" · {R.TIPOS[t['tipo']].lower()} · {R.SITUACOES[t['situacao']].lower()}"
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


def resumo(d, pessoas, hoje=None):
    hoje = hoje or date.today()
    ts = d["titulos"]
    if not ts:
        return "A lista da casa está vazia."
    cont = ", ".join(f"{sum(1 for t in ts if t['situacao'] == k)} {n.lower()}" for k, n in R.SITUACOES.items())
    out = [f"{len(ts)} títulos: {cont}."]
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
    cats = [f"{'filmes' if k == 'filme' else 'séries'}: {', '.join(c['nome'] for c in d['categorias'][k])}" for k in R.TIPOS if d.get("categorias", {}).get(k)]
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
            ts = sorted(ts, key=lambda t: t["atualizado"], reverse=True)
            lim = a.get("limite") or 20
            if not ts:
                return "Nenhum título com esses filtros.", False
            return "\n".join([f"{len(ts)} títulos" + (f" (os {lim} mais recentes)" if len(ts) > lim else "") + ":"] + ["- " + linha(t, pessoas, d) for t in ts[:lim]]), False
        t = R.achar(d, a.get("titulo")) if "titulo" in a else None
        if nome == "ver":
            out = [linha(t, pessoas, d)]
            if t["generos"]:
                out.append("Gêneros: " + ", ".join(t["generos"]) + ".")
            if t["tipo"] == "filme" and t.get("duracao"):
                out.append(f"Duração: {t['duracao']} min.")
            if t["tipo"] == "serie":
                if t["temporadas"]:
                    out.append("Temporadas: " + ", ".join(f"T{s['n']} ({s['episodios']} ep.)" for s in t["temporadas"]) + (" · terminou" if t["fim"] else "") + ".")
                if t.get("ultimo"):
                    out.append(f"Último que saiu: {R.ep_txt(t['ultimo']['temp'], t['ultimo']['ep'])}" + (f" em {R.data_br(t['ultimo']['data'])}" if t["ultimo"]["data"] else "") + ".")
                if t.get("proximo"):
                    out.append(f"Próximo: {R.ep_txt(t['proximo']['temp'], t['proximo']['ep'])} em {R.data_br(t['proximo']['data'])}.")
            out.append(_onde(t))
            if t["sinopse"]:
                out.append("Sinopse: " + t["sinopse"])
            if t["notas"]:
                out.append("Notas da casa: " + t["notas"])
            return "\n".join(out), False
        if nome == "adicionar":
            if not det:
                raise ErroFerramenta(f"Não achei «{a['nome']}» no TMDB.")
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
        if nome == "proximo_episodio":
            R.proximo_ep(t, agora)
            return f"Feito: {t['nome']} {R.ep_txt(t['temp'], t['ep'])} visto." + (" A série acabou: ficou como Visto." if t["situacao"] == "visto" else ""), True
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
    sit = "Visto" if situacao == "visto" else "Quero ver"
    partes = []
    if res["novos"]:
        partes.append(f"{res['novos']} {'filme posto' if res['novos'] == 1 else 'filmes postos'} na lista como {sit}")
    if res["marcados"]:
        partes.append(f"{res['marcados']} {'marcado' if res['marcados'] == 1 else 'marcados'} como Visto")
    if res["ja"]:
        partes.append(f"{res['ja']} já {'estava' if res['ja'] == 1 else 'estavam'} na lista")
    if res["fora"]:
        partes.append(f"{res['fora']} ainda não {'saiu' if res['fora'] == 1 else 'saíram'}")
    return f"{res['nome']}: " + (", ".join(partes) if partes else "nada a mudar") + "."


def texto_lista(nome, rs):
    """Uma lista pronta do TMDB em linhas, dizendo o que a casa já tem."""
    if not rs:
        return f"{T.LISTAS[nome]}: nada agora."
    out = [f"{T.LISTAS[nome]} (TMDB):"]
    for r in rs:
        s = f"- {r['nome']}" + (f" ({r['ano']})" if r["ano"] else "") + f" · {R.TIPOS[r['tipo']].lower()}"
        if r.get("situacao"):
            s += f" · na lista: {R.SITUACOES[r['situacao']].lower()}"
        out.append(s)
    return "\n".join(out)
