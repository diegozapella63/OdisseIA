/* OdisseIA · a tela (JavaScript puro, sem build). Os filmes e as séries da casa: Agora (o que a casa está vendo, os
   episódios que vão sair e o que quer ver), Buscar, o + (procura no TMDB), Histórico e Mais (Configurações e Sobre).
   Ações por data-a; tudo vem de /api/estado e as mudanças voltam pelo /api/titulo. */
(function () {
  'use strict';
  const $ = s => document.querySelector(s);
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const IC = {
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    mais: '<circle cx="12" cy="12" r="1.6" fill="currentColor"/><circle cx="19" cy="12" r="1.6" fill="currentColor"/><circle cx="5" cy="12" r="1.6" fill="currentColor"/>',
    film: '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 3v18M17 3v18M3 7.5h4M3 12h18M3 16.5h4M17 7.5h4M17 16.5h4"/>',
    tv: '<rect x="2" y="7" width="20" height="15" rx="2"/><path d="m17 2-5 5-5-5"/>',
    play: '<path d="M7 4.5v15a1 1 0 0 0 1.5.9l12-7.5a1 1 0 0 0 0-1.8l-12-7.5A1 1 0 0 0 7 4.5z"/>',
    skip: '<path d="M5 4.5v15l11-7.5z"/><path d="M19 5v14"/>',
    bookmark: '<path d="M19 21l-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>',
    visto: '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
    ban: '<circle cx="12" cy="12" r="9"/><path d="m5.6 5.6 12.8 12.8"/>',
    calendar: '<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M8 2v4M16 2v4M3 10h18"/>',
    star: '<path d="M12 2.5l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z"/>',
    user: '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    x: '<path d="M18 6 6 18M6 6l12 12"/>',
    trash: '<path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6"/>',
    refresh: '<path d="M21 12a9 9 0 0 1-15.5 6.2L3 16M3 12A9 9 0 0 1 18.5 5.8L21 8"/><path d="M21 3v5h-5M3 21v-5h5"/>',
    gear: '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>',
    info: '<circle cx="12" cy="12" r="9"/><path d="M12 16v-4M12 8h.01"/>',
    layers: '<path d="m12 2 10 5-10 5L2 7l10-5Z"/><path d="m2 17 10 5 10-5M2 12l10 5 10-5"/>',
    key: '<circle cx="7.5" cy="15.5" r="4.5"/><path d="m10.7 12.3 9.8-9.8M17 6l3 3M14.5 8.5l2 2"/>',
    database: '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/>',
    baixar: '<path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/>',
    subir: '<path d="M12 21V9"/><path d="m7 14 5-5 5 5"/><path d="M5 3h14"/>',
    arquivo: '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/>',
    palette: '<circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>',
    contrast: '<circle cx="12" cy="12" r="10"/><path d="M12 18a6 6 0 0 0 0-12v12z"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>',
    moon: '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
    phone: '<rect width="14" height="20" x="5" y="2" rx="2"/><path d="M12 18h.01"/>',
    toggle: '<rect x="2" y="6" width="20" height="12" rx="6"/><circle cx="16" cy="12" r="3"/>',
    chev: '<path d="m9 18 6-6-6-6"/>',
    back: '<path d="m15 18-6-6 6-6"/>',
    'external-link': '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    zap: '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
    chat: '<path d="M21 12a8 8 0 0 1-11.7 7.1L4 20.5l1.4-4.9A8 8 0 1 1 21 12Z"/>',
    hourglass: '<path d="M5 22h14M5 2h14"/><path d="M17 22v-4.2a2 2 0 0 0-.6-1.4L12 12l-4.4 4.4a2 2 0 0 0-.6 1.4V22"/><path d="M7 2v4.2a2 2 0 0 0 .6 1.4L12 12l4.4-4.4a2 2 0 0 0 .6-1.4V2"/>',
    'calendar-days': '<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M8 2v4M16 2v4M3 10h18M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01"/>',
    'list-checks': '<path d="M13 5h8M13 12h8M13 19h8"/><path d="m3 17 2 2 4-4M3 7l2 2 4-4"/>',
    wallet: '<path d="M4 7h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a1 1 0 0 1-1-1V7Z"/><path d="M4 7V6a2 2 0 0 1 2-2h10"/><circle cx="16" cy="13.5" r="1.3"/>',
    package: '<path d="M11 21.7a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.7l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.7z"/><path d="M12 22V12M3.3 7 12 12l8.7-5"/>',
    receipt: '<path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z"/><path d="M8 8h8M8 12h8M8 16h5"/>',
    'book-open': '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
    sliders: '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
    nota: '<path d="M12 20h9"/><path d="M16.4 3.6a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    texto: '<path d="M4 6h16M4 12h16M4 18h10"/>',
    list: '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
    tag: '<path d="M12.6 2.6A2 2 0 0 0 11.2 2H4a2 2 0 0 0-2 2v7.2a2 2 0 0 0 .6 1.4l8.7 8.7a2.4 2.4 0 0 0 3.4 0l6.6-6.6a2.4 2.4 0 0 0 0-3.4z"/><circle cx="7.5" cy="7.5" r=".5" fill="currentColor"/>',
    globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
  };
  const ic = (n, cls = 'ic') => `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${IC[n] || ''}</svg>`;
  const guardada = k => { try { return localStorage.getItem(k); } catch (e) { return null; } };
  const guardar = (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* sem armazenamento: só nesta vez */ } };
  const lerJSON = (k, padrao) => { try { return JSON.parse(guardada(k) || '') || padrao; } catch (e) { return padrao; } };

  // 0.3.0 (o dono: "pode tirar a opção de vendo, só vou controlar visto e quero ver")
  const SIT = { quero: ['Quero ver', 'bookmark'], visto: ['Visto', 'visto'] };
  const TIPO = { filme: ['Filme', 'film'], serie: ['Série', 'tv'], colecao: ['Coleção de filmes', 'layers'] };
  const ABAS = [['integracoes', 'Integrações', 'layers'], ['dados', 'Dados', 'database'], ['aparencia', 'Aparência', 'palette'], ['opcoes', 'Opções', 'toggle']];
  const S = {
    e: null, tela: 'agora', aba: guardada('odisseia-aba') || 'integracoes', tema: guardada('odisseia-tema') || 'auto',
    folha: null, folhas: [], col: null, hist: guardada('odisseia-historico') || 'serie', busca: Object.assign({ texto: '', tipo: '', situacao: '', quem: '', categoria: '' }, lerJSON('odisseia-busca', {})),
    add: { q: '', tipo: '', res: null, erro: '', buscando: false, lista: 'alta', listas: {} }, aband: false, tempEsc: {}, conf: '', dados: null, trocarChave: false,
  };
  const api = {
    get: rota => fetch('api/' + rota, { cache: 'no-store' }).then(ok),
    post: (rota, corpo) => fetch('api/' + rota, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(corpo || {}) }).then(ok),
  };
  async function ok(r) {
    let j = null;
    try { j = await r.json(); } catch (e) { /* sem corpo */ }
    if (!r.ok) throw new Error((j && j.erro) || `Erro ${r.status}`);
    return j;
  }
  function toast(t) {
    const el = $('#toast');
    el.textContent = t;
    el.classList.add('on');
    clearTimeout(toast.t);
    toast.t = setTimeout(() => el.classList.remove('on'), Math.min(9000, Math.max(2600, String(t).length * 55)));
  }

  /* ---------- tema e cor (como nos outros apps) */
  function temaHA() {
    try {
      if (window.parent && window.parent !== window) {
        const ha = window.parent.document.querySelector('home-assistant');
        const dm = ha && ha.hass && ha.hass.themes && ha.hass.themes.darkMode;
        if (typeof dm === 'boolean') return dm ? 'dark' : 'light';
      }
    } catch (e) { /* fora do Home Assistant */ }
    return window.matchMedia && matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  }
  function aplicarTema() {
    const t = S.tema === 'claro' ? 'light' : S.tema === 'escuro' ? 'dark' : temaHA();
    if (document.documentElement.dataset.theme !== t) document.documentElement.dataset.theme = t;
  }
  // a paleta da família: as 12 cores, nesta ordem e com estes nomes, em todos os apps
  const PALETA = [['vermelho', 'Vermelho', '#FF5A4F', '#C42A1F'], ['coral', 'Coral', '#FF8A65', '#C2410C'], ['laranja', 'Laranja', '#FFA23E', '#B45309'],
    ['ouro', 'Ouro', '#F2C14E', '#8A6100'], ['verde', 'Verde', '#8BD45F', '#3F7A17'], ['menta', 'Menta', '#4ED3A6', '#0E7A57'],
    ['turquesa', 'Turquesa', '#3CCBDA', '#0B7285'], ['azul', 'Azul', '#62B5FF', '#0B67A8'], ['indigo', 'Índigo', '#8F9BFF', '#3D4BC2'],
    ['lilas', 'Lilás', '#B99BFF', '#6D3FD6'], ['rosa', 'Rosa', '#FF77A9', '#BE185D'], ['grafite', 'Grafite', '#B5B9C2', '#4E5560']]
    .map(([id, nome, fill, ink]) => ({ id, nome, fill, ink }));
  // a Cor do dia: as 11 sem o Grafite, pelo número do dia na data local (a mesma em todos os apps no mesmo dia)
  function corDoDia(d = new Date()) {
    const L = PALETA.filter(c => c.id !== 'grafite'), n = Math.floor(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 864e5);
    return L[((n % L.length) + L.length) % L.length].id;
  }
  function corAtual() {
    const a = (S.e && S.e.ajustes) || lerJSON('odisseia-cor', {});
    return a.cor_dia !== false ? corDoDia() : (PALETA.some(c => c.id === a.cor) ? a.cor : 'lilas');
  }
  function aplicarCor() {
    const c = PALETA.find(x => x.id === corAtual()), r = document.documentElement.style;
    r.setProperty('--accent', c.fill);
    r.setProperty('--accent-ink', c.ink);
    if (S.e) guardar('odisseia-cor', JSON.stringify({ cor: S.e.ajustes.cor, cor_dia: S.e.ajustes.cor_dia }));
  }
  aplicarTema();
  aplicarCor();
  setInterval(aplicarTema, 2000);
  setInterval(aplicarCor, 60000);
  window.__selectSheet && (window.__selectSheet.icon = sel => sel.dataset.ic ? ic(sel.dataset.ic) : '');

  /* ---------- datas e textos */
  const hojeISO = () => (S.e && S.e.hoje) || new Date().toISOString().slice(0, 10);
  function dia(iso) {
    if (!iso) return '';
    const d = new Date(iso + 'T12:00:00'), h = new Date(hojeISO() + 'T12:00:00'), n = Math.round((d - h) / 864e5);
    if (n === 0) return 'hoje';
    if (n === 1) return 'amanhã';
    if (n === -1) return 'ontem';
    return d.toLocaleDateString('pt-BR', { weekday: 'short', day: '2-digit', month: '2-digit' }).replace('.', '');
  }
  const ep = (t, e) => `T${t} E${e}`;
  const duracao = m => m ? (m >= 60 ? `${Math.floor(m / 60)}h${m % 60 ? ' ' + String(m % 60).padStart(2, '0') : ''}` : `${m} min`) : '';
  const semAcento = s => String(s || '').normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const plural = (n, um, varios) => `${n} ${n === 1 ? um : varios}`;
  const pessoa = id => ((S.e && S.e.pessoas) || []).find(p => p.id === id);
  const inicial = id => { const p = pessoa(id); return (p ? p.nome : id.replace('person.', '')).trim().charAt(0).toUpperCase(); };
  const site = (href, texto) => `<a href="${href}" target="_blank" rel="noopener noreferrer">${texto}</a>`;

  // as mesmas contas do regras.py (o servidor confere de novo)
  function episodiosAte(t, temp, e) {
    let n = 0;
    for (const s of t.temporadas || []) { if (s.n < temp) n += s.episodios; else if (s.n === temp) n += Math.min(e, s.episodios); }
    return n;
  }
  function faltam(t) {
    if (t.tipo !== 'serie' || !t.ultimo) return null;
    return Math.max(0, episodiosAte(t, t.ultimo.temp, t.ultimo.ep) - (t.temp ? episodiosAte(t, t.temp, t.ep) : 0));
  }
  function seguinte(t) {
    const ts = t.temporadas || [];
    if (!ts.length) return null;
    if (!t.temp) return [ts[0].n, 1];
    const i = ts.findIndex(s => s.n === t.temp);
    if (i >= 0) return t.ep < ts[i].episodios ? [ts[i].n, t.ep + 1] : (ts[i + 1] ? [ts[i + 1].n, 1] : null);
    const d = ts.find(s => s.n > t.temp);
    return d ? [d.n, 1] : null;
  }
  const jaSaiu = (t, s) => !t.ultimo || s[0] < t.ultimo.temp || (s[0] === t.ultimo.temp && s[1] <= t.ultimo.ep);
  // os tipos que a casa controla (Opções › O que controlar)
  const ligados = () => Object.keys(TIPO).filter(k => k !== 'colecao' && S.e.ajustes.tipos[k]);
  const podeProximo = t => { const s = t.tipo === 'serie' && seguinte(t); return s && jaSaiu(t, s) ? s : null; };

  /* ---------- pedaços da tela */
  const fechadas = () => new Set(lerJSON('odisseia-fechadas', []));
  // toda seção (cartão) contrai e expande num toque no cabeçalho; o aparelho lembra as fechadas
  const cab = (icone, titulo, chave, extra = '') => `<div class="rot" role="button" tabindex="0" data-dobra="${esc(chave || titulo)}" aria-expanded="${!fechadas().has(chave || titulo)}"><span class="rot-ic">${ic(icone)}</span><h2>${titulo}</h2>${extra}<span class="dobra-ic" aria-hidden="true">${ic('chev', 'ic-s')}</span></div>`;
  const card = (id, icone, titulo, corpo, chave) => `<section class="card${fechadas().has(chave || titulo) ? ' fechada' : ''}" id="${id}">${cab(icone, titulo, chave)}${corpo}</section>`;
  const lbl = (icone, titulo, para) => para ? `<label for="${para}">${ic(icone, 'ic-s')}${titulo}</label>` : `<span class="lbl">${ic(icone, 'ic-s')}${titulo}</span>`;
  const ICONE_TELA = { Agora: 'clock', Buscar: 'search', 'Histórico': 'visto', Mais: 'mais', Categorias: 'tag', 'Configurações': 'gear', Sobre: 'info' };
  const topo = (titulo, volta, extra = '') => `<header class="cab-tela">${volta ? `<button class="voltar" data-a="voltar">${ic('back', 'ic-s')}${volta}</button>` : extra}<h1><span class="rot-ic tela-ic" aria-hidden="true">${ic(ICONE_TELA[titulo])}</span>${titulo}</h1></header>`;
  const capa = (t, g) => t.capa ? `<img class="capa${g ? ' g' : ''}" src="api/capa/${esc(t.capa)}" alt="" loading="lazy">` : `<span class="capa${g ? ' g' : ''}">${ic(TIPO[t.tipo][1])}</span>`;
  const avs = ids => ids && ids.length && S.e.ajustes.quem ? `<span class="pessoas-mini">${ids.map(i => `<span class="av" title="${esc((pessoa(i) || {}).nome || i)}">${esc(inicial(i))}</span>`).join('')}</span>` : '';

  const emAndamento = t => t.tipo === 'serie' && t.situacao === 'quero' && !!t.temp;
  const nomeCat = t => ((S.e.categorias[t.tipo] || []).find(c => c.id === t.categoria) || {}).nome || '';
  function meta(t) {
    const p = [];
    if (emAndamento(t)) {
      p.push(`parou em ${ep(t.temp, t.ep)}`);
      const f = faltam(t);
      if (f) p.push(`faltam ${f}`);
    } else if (t.tipo === 'serie') {
      p.push('Série' + (t.temporadas && t.temporadas.length ? ' · ' + plural(t.temporadas.length, 'temporada', 'temporadas') : ''));
      if (t.ano) p.push(t.ano);
    } else {
      p.push('Filme');
      if (t.duracao) p.push(duracao(t.duracao));
      if (t.ano) p.push(t.ano);
    }
    if (nomeCat(t)) p.push(nomeCat(t));
    return p.join(' · ');
  }
  function linhaTit(t, opts = {}) {
    const s = opts.mais1 && podeProximo(t);
    return `<li class="linha-tit"><button class="tit" data-a="abrir" data-id="${t.id}">${capa(t)}<span class="t-txt"><b>${esc(t.nome)}</b>
      <small class="${opts.dest ? 'dest' : ''}">${opts.sub != null ? opts.sub : esc(meta(t))}</small>${avs(t.quem) ? `<small>${avs(t.quem)}</small>` : ''}</span></button>
      ${s ? `<button class="mais1" data-a="proximo" data-id="${t.id}" aria-label="Vi o ${ep(s[0], s[1])}">${ic('check', 'ic-s')}${ep(s[0], s[1])}</button>` : ''}</li>`;
  }
  const lista = (ts, opts) => `<ul class="titulos">${ts.map(t => linhaTit(t, opts)).join('')}</ul>`;
  const ordem = ts => ts.slice().sort((a, b) => String(b.atualizado).localeCompare(String(a.atualizado)));

  /* ---------- Agora */
  function telaAgora() {
    const e = S.e, ts = e.titulos, eu = pessoa(e.eu);
    const ola = `<p class="eyebrow"><span class="brand">Odisse<span>IA</span></span>${eu ? ` · olá, ${esc(eu.nome.split(' ')[0])}` : ''}</p>`;
    let h = topo('Agora', '', ola);
    if (!e.tmdb.chave) {
      h += card('comeco', 'key', 'Comece aqui', `<p class="lead">Para procurar os filmes e as séries, o app usa o TMDB, de graça. Crie a sua chave no ${site('https://www.themoviedb.org/settings/api', 'TMDB')} e cole em Configurações.</p>
        <div class="acoes"><button class="btn pri" data-a="ir-config" data-v="integracoes">${ic('key', 'ic-s')}Pôr a chave</button></div>`);
    }
    if (!ts.length) {
      return h + card('vazia', 'film', 'A lista está vazia', `<p class="lead">Ponha o que a casa quer ver e o que já viu.</p>
        <div class="acoes"><button class="btn pri" data-a="adicionar">${ic('plus', 'ic-s')}Adicionar</button></div>`);
    }
    const vendo = ordem(ts.filter(emAndamento));
    if (vendo.length) h += card('vendo', 'play', `Continuar vendo <span class="cont">${vendo.length}</span>`, lista(vendo, { mais1: true }), 'Continuar vendo');
    const ate = new Date(hojeISO() + 'T12:00:00'); ate.setDate(ate.getDate() + 30);
    const ateISO = ate.toISOString().slice(0, 10);
    const novos = ts.filter(t => t.tipo === 'serie' && t.proximo && t.proximo.data >= hojeISO() && t.proximo.data <= ateISO)
      .sort((a, b) => a.proximo.data.localeCompare(b.proximo.data));
    if (novos.length) {
      h += card('episodios', 'calendar', 'Novos episódios', `<ul class="titulos">${novos.map(t => linhaTit(t, { dest: true, sub: `${ep(t.proximo.temp, t.proximo.ep)} · ${esc(dia(t.proximo.data))}` })).join('')}</ul>`);
    }
    const quero = ordem(ts.filter(t => t.situacao === 'quero' && !emAndamento(t)));
    if (quero.length) {
      h += card('quero', 'bookmark', `Quero ver <span class="cont">${quero.length}</span>`, lista(quero.slice(0, 6)) +
        (quero.length > 6 ? `<div class="acoes ver-todos"><button class="btn out" data-a="ver-quero">${ic('list', 'ic-s')}Ver todos</button></div>` : ''), 'Quero ver');
    }
    return h;
  }

  /* ---------- Buscar */
  function filtrados() {
    const b = S.busca, alvo = semAcento(b.texto.trim());
    return ordem(S.e.titulos.filter(t => (!alvo || semAcento(t.nome).includes(alvo) || semAcento(t.original).includes(alvo))
      && (!b.tipo || t.tipo === b.tipo || !ligados().includes(b.tipo)) && (!b.quem || t.quem.includes(b.quem))
      && (!b.situacao || t.situacao === b.situacao) && (!b.categoria || t.categoria === b.categoria)));
  }
  // 0.3.0 (o dono: "a parte de filtros deixa no mesmo padrão dos outros apps"): a busca, o Filtros que fecha e abre (o
  // aparelho lembra) e as caixas de seleção lado a lado, como no InventarIA e no ResolvIA
  function telaBuscar() {
    const b = S.busca, e = S.e, tipos = ligados(), aberto = guardada('odisseia-filtros') !== 'fechado';
    const caixa = (id, ic_, rot, opcoes, atual) => `<select class="inp select" id="${id}" data-ic="${ic_}" aria-label="${rot}">${opcoes}</select>`;
    const opt = (v, n, atual) => `<option value="${esc(v)}"${v === atual ? ' selected' : ''}>${esc(n)}</option>`;
    const cats = tipos.filter(k => !b.tipo || k === b.tipo).filter(k => (e.categorias[k] || []).length);
    const sel = [];
    if (tipos.length > 1) sel.push(caixa('f-tipo', 'film', 'Tipo', opt('', 'Filmes e séries', b.tipo) + opt('filme', 'Filmes', b.tipo) + opt('serie', 'Séries', b.tipo)));
    sel.push(caixa('f-sit', 'layers', 'Situação', opt('', 'Todas as situações', b.situacao) + opt('quero', 'Quero ver', b.situacao) + opt('visto', 'Vistos', b.situacao)));
    if (cats.length) {
      sel.push(caixa('f-cat', 'tag', 'Categoria', opt('', 'Todas as categorias', b.categoria) + cats.map(k => cats.length > 1
        ? `<optgroup label="${k === 'filme' ? 'Filmes' : 'Séries'}">${e.categorias[k].map(c => opt(c.id, c.nome, b.categoria)).join('')}</optgroup>`
        : e.categorias[k].map(c => opt(c.id, c.nome, b.categoria)).join('')).join('')));
    }
    if (e.ajustes.quem && e.pessoas.length > 1) sel.push(caixa('f-quem', 'users', 'Quem', opt('', 'Todas as pessoas', b.quem) + e.pessoas.map(p => opt(p.id, p.nome.split(' ')[0], b.quem)).join('')));
    const ts = filtrados();
    let h = topo('Buscar') + `<section class="sbar"><label class="busca">${ic('search')}<input id="b-texto" type="search" placeholder="Nome do filme ou da série" value="${esc(b.texto)}" enterkeyhint="search" autocomplete="off">${b.texto ? `<button class="limpar" data-a="b-limpar" aria-label="Limpar">${ic('x', 'ic-s')}</button>` : ''}</label>
      <button class="filtros-h" data-a="filtros" aria-expanded="${aberto}">${ic('sliders', 'ic-s')}<span>Filtros</span>${ic('chev', 'ic-s seta')}</button>
      <div class="sfiltros n${sel.length}"${aberto ? '' : ' hidden'}>${sel.join('')}</div></section>`;
    const corpo = ts.length ? lista(ts, { mais1: true }) : `<p class="vazio">${e.titulos.length ? 'Nenhum título com esses filtros.' : 'A lista está vazia.'}</p>`;
    return h + card('resultado', 'list', `Títulos <span class="cont">${ts.length}</span>`, corpo, 'Títulos');
  }

  /* ---------- Histórico: o que a casa já viu, por mês, numa aba para cada tipo (0.2.0, o dono: "e se for jogos?") */
  const HIST = [['serie', 'Séries', 'tv', 'Nenhuma série vista'], ['filme', 'Filmes', 'film', 'Nenhum filme visto']];
  function telaHistorico() {
    const abas = HIST.filter(([k]) => ligados().includes(k));
    const aba = abas.some(([k]) => k === S.hist) ? S.hist : abas[0][0], vaz = HIST.find(([k]) => k === aba)[3];
    const vistos = S.e.titulos.filter(t => t.situacao === 'visto' && t.tipo === aba).sort((a, b) => String(b.visto_em || '').localeCompare(String(a.visto_em || '')));
    let h = topo('Histórico') + (abas.length < 2 ? '' : `<div class="abas" role="tablist">${abas.map(([k, n, i]) => `<button role="tab" aria-selected="${aba === k}" class="${aba === k ? 'on' : ''}" data-a="hist" data-v="${k}">${ic(i, 'ic-s')}${n}</button>`).join('')}</div>`);
    if (!vistos.length) return h + card('nada-visto', HIST.find(([k]) => k === aba)[2], vaz, '<p class="lead">O que a casa terminar de ver aparece aqui, mês a mês.</p>', 'nada-visto');
    const grupos = new Map();
    for (const t of vistos) {
      const k = t.visto_em ? t.visto_em.slice(0, 7) : '';
      if (!grupos.has(k)) grupos.set(k, []);
      grupos.get(k).push(t);
    }
    for (const [k, ts] of grupos) {
      const nome = k ? new Date(k + '-15T12:00:00').toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' }).replace(/^./, c => c.toUpperCase()) : 'Sem data';
      h += card('m-' + (k || 'sem'), 'calendar', `${nome} <span class="cont">${ts.length}</span>`, lista(ts), 'historico-' + (k || 'sem'));
    }
    return h;
  }

  /* ---------- Mais, Configurações e Sobre */
  function telaMais() {
    const linha = (a, icone, titulo, txt) => `<button class="linha" data-a="${a}"><span class="rot-ic">${ic(icone)}</span><span class="linha-t"><b>${titulo}</b><small>${txt}</small></span>${ic('chev', 'ic-s chev')}</button>`;
    return topo('Mais') + `<section class="card linha-card">${linha('ir-categorias', 'tag', 'Categorias', 'As categorias dos filmes e das séries.')}${linha('ir-config', 'gear', 'Configurações', 'Integrações, dados, aparência e opções.')}${linha('sobre', 'info', 'Sobre', 'CorrerIA Code, os apps e o GitHub.')}</section>`;
  }
  // 0.3.0 (o dono: "tirar a opção de nota e colocar um campo de categoria... vou poder definir categorias para filme, outra
  // para séries e outra para jogos"): uma lista por tipo ligado; o nome muda no próprio campo (o Enter salva)
  const EXEMPLO_CAT = { filme: 'Ex.: Para ver em família', serie: 'Ex.: Para ver a dois' };
  function telaCategorias() {
    let h = topo('Categorias', 'Mais');
    for (const [k, nome, icone] of [['serie', 'Séries', 'tv'], ['filme', 'Filmes', 'film']].filter(([k]) => ligados().includes(k))) {
      const cs = S.e.categorias[k] || [];
      const linhas = cs.map(c => `<li class="cat-l">${S.conf === 'cat:' + c.id ? confirma(`Apagar «${c.nome}»? Os títulos ficam sem categoria.`, 'cat-apagar', 'trash', 'Apagar', `data-id="${c.id}"`)
        : `<textarea class="inp umalinha" rows="1" data-cat="${c.id}" maxlength="40" aria-label="Nome da categoria">${esc(c.nome)}</textarea><button class="fechar" data-a="conf" data-v="cat:${c.id}" aria-label="Apagar ${esc(c.nome)}">${ic('trash', 'ic-s')}</button>`}</li>`).join('');
      h += card('cat-' + k, icone, `${nome} <span class="cont">${cs.length}</span>`, `${cs.length ? `<ul class="cats">${linhas}</ul>` : '<p class="vazio">Nenhuma categoria ainda.</p>'}
        <div class="campo" style="margin-top:16px">${lbl('plus', 'Nova categoria', 'nova-' + k)}<textarea class="inp umalinha" rows="1" id="nova-${k}" maxlength="40" placeholder="${EXEMPLO_CAT[k]}" enterkeyhint="done"></textarea></div>
        <div class="acoes"><button class="btn pri" data-a="cat-nova" data-k="${k}">${ic('plus', 'ic-s')}Adicionar</button></div>`, 'Categorias de ' + nome);
    }
    return h;
  }
  async function categorias(corpo) {
    try { const r = await api.post('categorias', corpo); S.e.categorias = r.categorias; S.e.rev = r.rev; S.conf = ''; render(); return true; } catch (err) { toast(err.message); return false; }
  }
  function cardTMDB() {
    const t = S.e.tmdb, mostrar = !t.chave || S.trocarChave;
    return card('tmdb', 'film', 'Filmes e séries (TMDB)', `<p class="lead">De onde vêm os filmes, as séries, as capas e onde assistir. A conta do ${site('https://www.themoviedb.org/signup', 'TMDB')} é grátis; a chave fica em ${site('https://www.themoviedb.org/settings/api', 'Configurações › API')} (uso pessoal).</p>
      ${t.chave ? `<p class="status${t.erro ? ' erro' : ''}">${t.erro ? esc(t.erro) : `Chave ${esc(t.fim)} · funcionando`}</p>` : ''}
      ${mostrar ? `<div class="campo">${lbl('key', 'Chave da API ou token de leitura', 'f-chave')}<input class="inp" id="f-chave" type="password" autocomplete="off" spellcheck="false" placeholder="Cole aqui"></div>
        <div class="acoes${t.chave ? ' dois' : ''}">${t.chave ? `<button class="btn out" data-a="chave-cancelar">${ic('x', 'ic-s')}Cancelar</button>` : ''}<button class="btn pri" data-a="chave-salvar">${ic('check', 'ic-s')}Salvar e testar</button></div>`
        : `<div class="acoes dois"><button class="btn out" data-a="chave-apagar">${ic('trash', 'ic-s')}Apagar</button><button class="btn pri" data-a="chave-trocar">${ic('key', 'ic-s')}Trocar</button></div>`}`);
  }
  function cardCorrerIA() {
    const c = S.e.correria, u = c.ultimo;
    return card('correria', 'chat', 'CorrerIA', `<div class="linha-sw"><div><b>${ic('zap', 'ic-s')}Usar pelo CorrerIA</b><span>Pergunte e marque o que viu pelo WhatsApp, pelo Claude ou pelo Gemini, com o CorrerIA.</span></div>
      <button class="sw${c.ligado ? ' on' : ''}" data-a="aj" data-k="correria" role="switch" aria-checked="${c.ligado}" aria-label="Usar pelo CorrerIA"></button></div>
      ${c.ligado && u ? `<p class="lead" style="margin:12px 0 0">Último uso: ${esc(u.app)}, ${esc(dia(u.em.slice(0, 10)))} às ${esc(u.em.slice(11, 16))}.</p>` : ''}`);
  }
  const tamanho = n => n >= 1048576 ? (n / 1048576).toFixed(1).replace('.', ',') + ' MB' : Math.max(1, Math.round(n / 1024)) + ' KB';
  const quando = iso => `${dia(iso.slice(0, 10))} às ${iso.slice(11, 16)}`;
  const confirma = (texto, a, icone, rotulo, extra = '') => `<div class="conf-box"><p>${esc(texto)}</p><div class="acoes dois"><button class="btn out" data-a="conf-nao">${ic('x', 'ic-s')}Cancelar</button><button class="btn pri" data-a="${a}" ${extra}>${ic(icone, 'ic-s')}${rotulo}</button></div></div>`;
  function zips(origem, l) {
    return `<ul class="zips">${l.map(x => {
      const k = `${origem}:${x.nome}`;
      return `<li><span>${esc(quando(x.em))}<small>${esc(tamanho(x.tamanho))}${x.motivo ? ' · ' + esc(x.motivo) : ''}</small></span>
        ${S.conf === k ? confirma('Trocar tudo o que há agora por este?', 'restaurar', 'refresh', 'Restaurar', `data-origem="${origem}" data-nome="${esc(x.nome)}"`)
          : `<button class="btn out" data-a="conf" data-v="${esc(k)}">${ic('refresh', 'ic-s')}Restaurar</button>`}</li>`;
    }).join('')}</ul>`;
  }
  function abaDados() {
    if (!S.dados) { S.dados = { backups: [], versoes: [] }; api.get('dados').then(r => { S.dados = r; render(); }).catch(err => toast(err.message)); }
    const d = S.dados;
    return card('exportar', 'baixar', 'Exportar', `<p class="lead">Um arquivo com a lista e as capas. A chave do TMDB não vai junto.</p>
        <div class="acoes"><a class="btn pri" href="api/dados/exportar" download>${ic('baixar', 'ic-s')}Baixar</a></div>`)
      + card('backup', 'arquivo', 'Backup na pasta share', `<p class="lead">Em <code>share/odisseia/backups</code>, os 10 últimos.</p>
        <div class="acoes"><button class="btn pri" data-a="backup">${ic('arquivo', 'ic-s')}Fazer backup agora</button></div>${d.backups.length ? zips('backup', d.backups) : ''}`)
      + card('importar', 'subir', 'Importar', `<p class="lead">O arquivo de um Exportar ou de um backup. Troca tudo o que há agora.</p>
        ${S.importar ? confirma(`Trocar tudo pelo arquivo ${S.importar.nome}?`, 'importar', 'subir', 'Importar') : `<div class="acoes"><button class="btn pri" data-a="escolher">${ic('subir', 'ic-s')}Escolher arquivo</button></div>`}`)
      + (d.versoes.length ? card('versoes', 'clock', `Versões anteriores (${d.versoes.length})`, zips('versao', d.versoes), 'Versões anteriores') : '')
      + card('onde', 'database', 'Onde ficam os dados', '<p class="lead">Na pasta <code>/data</code> do app, que entra no backup do Home Assistant: <code>odisseia.json</code> (a lista), <code>capas</code> e <code>segredos.json</code> (a chave do TMDB).</p>')
      + card('zerar', 'trash', 'Começar do zero', `<p class="lead">Apaga a lista e as capas. A chave do TMDB e as configurações ficam.</p>
        ${S.conf === 'zerar' ? confirma('Apagar a lista toda agora?', 'zerar', 'trash', 'Apagar') : `<div class="acoes"><button class="btn out" data-a="conf" data-v="zerar">${ic('trash', 'ic-s')}Começar do zero</button></div>`}`);
  }
  const TEMAS = [['auto', 'Sistema', 'phone'], ['claro', 'Claro', 'sun'], ['escuro', 'Escuro', 'moon']];
  const TAG = 'M8 0h20a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H8L0 13V7z', FURO = 'M9.7 10a2.7 2.7 0 1 0-5.4 0a2.7 2.7 0 1 0 5.4 0z';
  function abaAparencia() {
    const a = S.e.ajustes, atual = corAtual();
    return card('tema', 'contrast', 'Tema', `<p class="lead">Cada aparelho guarda a sua escolha. Sistema segue o do Home Assistant.</p>
        <div class="temas" role="radiogroup" aria-label="Tema">${TEMAS.map(([k, n, i]) => `<button role="radio" aria-checked="${S.tema === k}" class="${S.tema === k ? 'on' : ''}" data-a="tema" data-v="${k}">${ic(i)}<span>${n}</span></button>`).join('')}</div>`)
      + card('cor', 'palette', 'Cor do app', `<p class="lead">Vale para todos os aparelhos.</p>
        <div class="linha-sw"><div><b>${ic('calendar', 'ic-s')}Cor do dia</b><span>Muda a cor do app todo dia, a mesma em todos os apps.</span></div>
          <button class="sw${a.cor_dia ? ' on' : ''}" data-a="aj" data-k="cor_dia" role="switch" aria-checked="${a.cor_dia}" aria-label="Cor do dia"></button></div>
        <div class="cores" role="radiogroup" aria-label="Cor do app">${PALETA.map(c => `<button class="tsw${c.id === atual ? ' on' : ''}" role="radio" aria-checked="${c.id === atual}" style="--a:${c.fill}" data-a="cor" data-v="${c.id}">
          <svg viewBox="-5 -5 40 30" aria-hidden="true"><path class="sw-ring" d="${TAG}"/><path class="sw-gap" d="${TAG}"/><path class="sw-fill" d="${TAG + FURO}"/><path class="sw-check" d="m14.6 10.3 3.2 3.2 6.5-6.9"/></svg><span>${c.nome}</span></button>`).join('')}</div>`);
  }
  function abaOpcoes() {
    const a = S.e.ajustes, so = ligados().length === 1;
    const tipo = (k, icone, nome, txt) => `<div class="linha-sw"><div><b>${ic(icone, 'ic-s')}${nome}</b><span>${so && a.tipos[k] ? 'Pelo menos um fica ligado.' : txt}</span></div>
      <button class="sw${a.tipos[k] ? ' on' : ''}" data-a="aj-tipo" data-k="${k}" role="switch" aria-checked="${a.tipos[k]}" aria-label="${nome}"${so && a.tipos[k] ? ' disabled' : ''}></button></div>`;
    return card('controlar', 'layers', 'O que controlar', `<p class="lead">Desligado some da tela e do CorrerIA; nada é apagado.</p>
      ${tipo('serie', 'tv', 'Séries', 'O episódio em que cada um parou e os que vão sair.')}${tipo('filme', 'film', 'Filmes', 'Os filmes e as coleções (as sagas).')}`) + card('quem-ve', 'users', 'Quem vê', `<div class="linha-sw"><div><b>${ic('users', 'ic-s')}Marcar quem vê</b><span>Cada título diz quem da casa está vendo ou já viu.</span></div>
      <button class="sw${a.quem ? ' on' : ''}" data-a="aj" data-k="quem" role="switch" aria-checked="${a.quem}" aria-label="Marcar quem vê"></button></div>`);
  }
  function telaConfig() {
    const abas = `<div class="abas" role="tablist">${ABAS.map(([k, n, i]) => `<button role="tab" aria-selected="${S.aba === k}" class="${S.aba === k ? 'on' : ''}" data-a="aba" data-v="${k}">${ic(i, 'ic-s')}${n}</button>`).join('')}</div>`;
    const corpo = S.aba === 'dados' ? abaDados() : S.aba === 'aparencia' ? abaAparencia() : S.aba === 'opcoes' ? abaOpcoes() : cardTMDB() + cardCorrerIA();
    return topo('Configurações', 'Mais') + abas + corpo;
  }
  const GITHUB = 'https://github.com/diegozapella63';
  const PRODUTOS = [
    ['CronologIA', 'cronologia-ha', 'calendar-days', 'Agenda da família, remédios, rotinas e placar.'],
    ['ResolvIA', 'resolvia-ha', 'list-checks', 'Listas de tarefas com prazos, pontos e repetição.'],
    ['GerencIA', 'gerencia-ha', 'wallet', 'Finanças da casa: caixa, cartões e investimentos.'],
    ['InventarIA', 'inventario-ha', 'package', 'Inventário da casa: cômodos, itens e valores.'],
    ['EconomIA', 'economia-ha', 'receipt', 'Lista de compras com o melhor preço perto de casa.'],
    ['MemorIA', 'memoria-ha', 'book-open', 'Cadernos de anotação que abrem na hora certa.'],
    ['OdisseIA', 'OdisseIA', 'play', 'Os filmes e as séries da casa: o que ver e onde.'],
    ['CorrerIA', 'CorrerIA-ha', 'chat', 'Pergunte e peça a qualquer app, no chat ou no WhatsApp.'],
  ];
  const marcaNome = n => `<span class="sb-wm">${n.slice(0, -2)}<span>${n.slice(-2)}</span></span>`;
  function telaSobre() {
    return topo('Sobre', 'Mais') + `<div class="sobre-topo"><span class="sb-raio" aria-hidden="true">${ic('zap')}</span>
        <h2 class="sb-nome">Correr<span>IA</span> Code</h2><p class="sb-oque">desenvolvimento de softwares</p><p class="sb-lema">Feito na correria, rodado pela IA.</p></div>
      ${card('porque', 'hourglass', 'Por que CorrerIA?', '<p class="sb-txt">Porque eu sou um programador sem tempo: vivo na correria. Então eu uso a IA para rodar tudo isso aqui. Ela escreve, testa e publica; eu dou as ideias e reclamo dos botões tortos.</p>')}
      ${card('apps', 'layers', 'Os apps', `<ul class="sb-apps" aria-label="Os apps">${PRODUTOS.map(([n, repo, i, txt]) => `<li><a class="sb-app" href="${GITHUB}/${repo}" target="_blank" rel="noopener">
        <span class="rot-ic" aria-hidden="true">${ic(i)}</span><span class="mb"><b>${marcaNome(n)}${repo === 'OdisseIA' ? `<em class="sb-aqui">Este app · v${esc(S.e.versao)}</em>` : ''}</b><span>${txt}</span></span>${ic('external-link', 'sb-ext')}</a></li>`).join('')}</ul>`)}
      ${card('creditos', 'globe', 'De onde vêm os dados', `<p class="sb-txt">Os filmes, as séries e as capas vêm do ${site('https://www.themoviedb.org/', 'TMDB')}. Este app usa a API do TMDB, mas não é endossado nem certificado pelo TMDB. Onde assistir: dados da ${site('https://www.justwatch.com/br', 'JustWatch')}.</p>`)}
      <a class="btn pri sb-github" href="${GITHUB}" target="_blank" rel="noopener">${ic('external-link', 'ic-s')}Meu GitHub</a>`;
  }

  /* ---------- as janelas: Adicionar e o título aberto */
  // 0.2.0 (o dono: "pensa num processo bem legal para ficar bonito e prático"): o Adicionar abre nas listas prontas do
  // TMDB (Em alta, Mais populares, Mais bem avaliados, Estreias) e mostra as capas em grade; em cada capa, Quero ver (o
  // marcador) e Já vi (o visto, que numa série marca até o último episódio que saiu), sem sair da janela. Tocar na capa
  // abre o título (e, fora da lista, põe como Quero ver); uma coleção abre os filmes dela.
  const LISTAS = [['alta', 'Em alta', 'zap'], ['populares', 'Mais populares', 'users'], ['avaliados', 'Mais bem avaliados', 'star'], ['colecoes', 'Coleções', 'layers'], ['estreias', 'Estreias', 'calendar']];
  // as Coleções só com os filmes ligados e fora de Séries
  const listas = () => LISTAS.filter(([k]) => k !== 'colecoes' || (ligados().includes('filme') && S.add.tipo !== 'serie'));
  function cartaz(r, i, o) {
    // o que ainda não saiu (um filme da coleção, uma estreia futura) não tem o Já vi
    const col = r.tipo === 'colecao', sit = r.situacao && SIT[r.situacao], saiu = r.saiu !== false && !(r.data && r.data > hojeISO());
    const img = r.capa ? `<img src="api/img/w185${esc(r.capa)}" alt="" loading="lazy">` : `<span class="cz-sem">${ic(TIPO[r.tipo][1])}</span>`;
    const meta = [r.ano, col ? 'Coleção' : TIPO[r.tipo][0], saiu ? '' : (r.data ? 'sai em ' + new Date(r.data + 'T12:00:00').toLocaleDateString('pt-BR') : 'sem data')].filter(Boolean).join(' · ');
    return `<li class="cz${r.situacao === 'visto' ? ' feito' : ''}"><div class="cz-quadro"><button class="cz-capa" data-a="cz-abrir" data-o="${o}" data-i="${i}" aria-label="${esc(r.nome)}">${img}
        ${sit ? `<span class="cz-sit">${ic(sit[1], 'ic-s')}${sit[0]}</span>` : col ? `<span class="cz-sit">${ic('layers', 'ic-s')}Coleção</span>` : ''}</button>
      ${col ? `<span class="cz-acoes">${r.situacao ? '' : `<button class="cz-bt" data-a="cz-col-todos" data-v="quero" data-o="${o}" data-i="${i}" aria-label="Quero ver todos de ${esc(r.nome)}">${ic('bookmark', 'ic-s')}</button>`}
        ${r.situacao === 'visto' ? '' : `<button class="cz-bt vi" data-a="cz-col-todos" data-v="visto" data-o="${o}" data-i="${i}" aria-label="Já vi todos de ${esc(r.nome)}">${ic('check', 'ic-s')}</button>`}</span>`
      : `<span class="cz-acoes">${r.ja ? '' : `<button class="cz-bt" data-a="cz-quero" data-o="${o}" data-i="${i}" aria-label="Quero ver ${esc(r.nome)}">${ic('bookmark', 'ic-s')}</button>`}
        ${r.situacao === 'visto' || !saiu ? '' : `<button class="cz-bt vi" data-a="cz-visto" data-o="${o}" data-i="${i}" aria-label="Já vi ${esc(r.nome)}">${ic('check', 'ic-s')}</button>`}</span>`}</div>
      <b class="cz-nome">${esc(r.nome)}</b><small>${esc(meta)}</small>
      ${r.tipo === 'filme' && r.colecao && o !== 'col' ? `<button class="cz-col" data-a="cz-colecao" data-id="${r.colecao.id}">${ic('layers', 'ic-s')}Coleção</button>` : ''}</li>`;
  }
  const grade = (rs, o) => `<ul class="cartazes">${rs.map((r, i) => cartaz(r, i, o)).join('')}</ul>`;
  function folhaAdicionar() {
    const a = S.add, semChave = !S.e.tmdb.chave, busca = a.q.trim().length >= 2;
    const seg = ligados().length > 1 ? `<div class="seg">${[['', 'Tudo'], ['filme', 'Filmes'], ['serie', 'Séries']].map(([v, n]) => `<button class="${a.tipo === v ? 'on' : ''}" data-a="add-tipo" data-v="${v}">${n}</button>`).join('')}</div>` : '';
    let res = '';
    if (semChave) res = `<p class="lead" style="margin-top:14px">Falta a chave do TMDB.</p><div class="acoes"><button class="btn pri" data-a="ir-config" data-v="integracoes">${ic('key', 'ic-s')}Pôr a chave</button></div>`;
    else if (busca) {
      if (a.erro) res = `<p class="status erro" style="margin-top:14px">${esc(a.erro)}</p>`;
      else if (!a.res) res = '<p class="vazio" style="margin-top:14px">Procurando…</p>';
      else if (!a.res.length) res = '<p class="vazio" style="margin-top:14px">Nada com esse nome no TMDB.</p>';
      else res = grade(a.res, 'busca');
    } else {
      const L = a.listas[a.lista + ':' + a.tipo];
      if (!listas().some(([k]) => k === a.lista)) a.lista = 'alta';
      res = `<div class="chips" role="tablist" aria-label="Listas prontas">${listas().map(([k, n, i]) => `<button class="chip${a.lista === k ? ' on' : ''}" role="tab" aria-selected="${a.lista === k}" data-a="add-lista" data-v="${k}">${ic(i, 'ic-s')}${n}</button>`).join('')}</div>`;
      if (!L || (!L.itens.length && L.carregando)) res += '<p class="vazio" style="margin-top:14px">Abrindo…</p>';
      else if (L.erro && !L.itens.length) res += `<p class="status erro" style="margin-top:14px">${esc(L.erro)}</p>`;
      else res += grade(L.itens, 'lista') + (L.mais ? `<div class="acoes" style="margin-top:16px"><button class="btn out" data-a="add-mais"${L.carregando ? ' disabled' : ''}>${ic('plus', 'ic-s')}Mostrar mais</button></div>` : '');
      if (!L) carregarLista();
    }
    return { titulo: 'Adicionar', icone: 'plus', alta: true, corpo: `<label class="busca" style="margin-bottom:12px">${ic('search')}<input id="add-q" type="search" placeholder="Nome do filme ou da série" value="${esc(a.q)}" enterkeyhint="search" autocomplete="off"${semChave ? ' disabled' : ''}>${a.q ? `<button class="limpar" data-a="add-limpar" aria-label="Limpar">${ic('x', 'ic-s')}</button>` : ''}</label>
      ${seg}${res}` };
  }
  function folhaTitulo(t) {
    const e = S.e, pode = podeProximo(t);
    const info = [t.ano, TIPO[t.tipo][0], t.tipo === 'filme' ? duracao(t.duracao) : (t.temporadas.length ? plural(t.temporadas.length, 'temporada', 'temporadas') : ''), t.tipo === 'serie' && t.fim ? 'terminou' : ''].filter(Boolean).join(' · ');
    let h = `<div class="topo-tit">${capa(t, true)}<div class="info">${t.original && t.original !== t.nome ? `<span class="orig">${esc(t.original)}</span>` : ''}<span class="meta">${esc(info)}</span>
      ${t.generos.length ? `<span class="gens">${t.generos.map(g => `<span class="tag">${esc(g)}</span>`).join('')}</span>` : ''}</div></div>`;
    h += `<div class="campo">${lbl('layers', 'Situação')}<div class="escolhas">${Object.entries(SIT).map(([k, [n, i]]) => `<button class="escolha${t.situacao === k ? ' on' : ''}" data-a="sit" data-v="${k}">${ic(i, 'ic-s')}${n}</button>`).join('')}</div></div>`;
    if (t.tipo === 'serie' && t.temporadas.length) {
      const tempSel = S.tempEsc[t.id] != null ? S.tempEsc[t.id] : t.temp;
      const temp = t.temporadas.find(s => s.n === tempSel);
      const f = faltam(t);
      const linhas = [];
      if (t.temp) linhas.push(f ? `Faltam ${plural(f, 'episódio', 'episódios')} que já saíram.` : 'Em dia com o que já saiu.');
      if (t.proximo) linhas.push(`Próximo: ${ep(t.proximo.temp, t.proximo.ep)}, ${dia(t.proximo.data)}${/^(hoje|amanhã|ontem)$/.test(dia(t.proximo.data)) ? '' : ''}.`);
      h += `<div class="campo">${lbl('play', 'Parou em')}<div class="ep-box"><div class="ep-sel">
        <select class="inp select" id="f-temp" data-ic="tv" aria-label="Temporada"><option value="0"${tempSel ? '' : ' selected'}>Nenhum ainda</option>${t.temporadas.map(s => `<option value="${s.n}"${s.n === tempSel ? ' selected' : ''}>Temporada ${s.n}</option>`).join('')}</select>
        <select class="inp select" id="f-ep" data-ic="list" aria-label="Episódio"${temp ? '' : ' disabled'}>${temp ? (tempSel !== t.temp ? '<option value="" selected>Episódio…</option>' : '') + Array.from({ length: temp.episodios }, (_, i) => `<option value="${i + 1}"${tempSel === t.temp && t.ep === i + 1 ? ' selected' : ''}>Episódio ${i + 1}</option>`).join('') : '<option>Episódio</option>'}</select></div>
        ${linhas.length ? `<p class="ep-info">${esc(linhas.join(' '))}</p>` : ''}
        ${pode ? `<div class="acoes"><button class="btn pri" data-a="proximo" data-id="${t.id}">${ic('check', 'ic-s')}Vi o ${ep(pode[0], pode[1])}</button></div>` : ''}</div></div>`;
    }
    if (t.tipo === 'filme' && t.colecao) {
      h += `<div class="campo">${lbl('layers', 'Coleção')}<div class="acoes"><button class="btn out" data-a="abrir-colecao" data-id="${t.colecao.id}">${ic('layers', 'ic-s')}${esc(t.colecao.nome)}</button></div></div>`;
    }
    const cats = S.e.categorias[t.tipo] || [];
    h += `<div class="campo">${lbl('tag', 'Categoria')}${cats.length ? `<div class="escolhas">${[{ id: '', nome: 'Nenhuma' }, ...cats].map(c => `<button class="escolha${(t.categoria || '') === c.id ? ' on' : ''}" data-a="cat" data-v="${c.id}">${ic(c.id ? ((t.categoria || '') === c.id ? 'check' : 'tag') : 'x', 'ic-s')}${esc(c.nome)}</button>`).join('')}</div>`
      : `<div class="acoes"><button class="btn out" data-a="ir-categorias">${ic('tag', 'ic-s')}Criar categorias</button></div>`}</div>`;
    if (e.ajustes.quem && e.pessoas.length) {
      const todos = e.pessoas.every(p => t.quem.includes(p.id));
      h += `<div class="campo">${lbl('users', 'Quem')}<div class="escolhas">${e.pessoas.length > 1 ? `<button class="escolha${todos ? ' on' : ''}" data-a="quem-todos">${ic(todos ? 'check' : 'users', 'ic-s')}Todos</button>` : ''}${e.pessoas.map(p => `<button class="escolha${t.quem.includes(p.id) ? ' on' : ''}" data-a="quem" data-v="${esc(p.id)}">${ic(t.quem.includes(p.id) ? 'check' : 'user', 'ic-s')}${esc(p.nome.split(' ')[0])}</button>`).join('')}</div></div>`;
    }
    const o = t.onde || {}, partes = [['assinatura', 'Assinatura'], ['gratis', 'Grátis'], ['alugar', 'Alugar'], ['comprar', 'Comprar']].filter(([k]) => (o[k] || []).length);
    h += `<div class="campo">${lbl('tv', 'Onde assistir')}${partes.length ? `<dl class="onde">${partes.map(([k, n]) => `<div><dt>${n}</dt><dd>${esc(o[k].join(', '))}</dd></div>`).join('')}</dl>` : '<p class="vazio">Nada no Brasil, pelo que a JustWatch sabe.</p>'}
      <p class="credito">Dados da ${o.link ? site(esc(o.link), 'JustWatch') : 'JustWatch'}${t.tmdb_em ? `, de ${esc(dia(t.tmdb_em.slice(0, 10)))}` : ''}.</p></div>`;
    if (t.sinopse) h += `<div class="campo">${lbl('texto', 'Sinopse')}<p class="sinopse">${esc(t.sinopse)}</p></div>`;
    h += `<div class="campo">${lbl('nota', 'Notas', 'f-notas')}<textarea class="inp" id="f-notas" rows="3" placeholder="O que a casa achou, quem indicou…">${esc(t.notas)}</textarea></div>`;
    const pe = S.conf === 'apagar:' + t.id ? `<p class="conf">Apagar «${esc(t.nome)}» da lista?</p><button class="btn out" data-a="conf-nao">${ic('x', 'ic-s')}Cancelar</button><button class="btn perigo" data-a="apagar" data-id="${t.id}">${ic('trash', 'ic-s')}Apagar</button>`
      : `<button class="btn out" data-a="conf" data-v="apagar:${t.id}">${ic('trash', 'ic-s')}Apagar</button><button class="btn out" data-a="atualizar" data-id="${t.id}"${t.tmdb ? '' : ' disabled'}>${ic('refresh', 'ic-s')}Atualizar</button>`;
    return { titulo: t.nome, icone: TIPO[t.tipo][1], corpo: h, pe };
  }
  function folhaColecao(f) {
    const c = S.col && S.col.id === f.id ? S.col : null;
    if (!c) {
      S.col = { id: f.id, dados: null, erro: '' };
      api.get('colecao?id=' + f.id).then(r => { if (S.col && S.col.id === f.id) { S.col.dados = r.colecao; render(); } })
        .catch(err => { if (S.col && S.col.id === f.id) { S.col.erro = err.message; render(); } });
      return { titulo: 'Coleção de filmes', icone: 'layers', corpo: '<p class="vazio">Abrindo…</p>' };
    }
    if (c.erro) return { titulo: 'Coleção de filmes', icone: 'layers', corpo: `<p class="status erro">${esc(c.erro)}</p>` };
    if (!c.dados) return { titulo: 'Coleção de filmes', icone: 'layers', corpo: '<p class="vazio">Abrindo…</p>' };
    const d = c.dados, saiu = d.filmes.filter(x => x.saiu);
    const pe = `<button class="btn out" data-a="col-todos" data-v="quero"${d.filmes.every(x => x.ja) ? ' disabled' : ''}>${ic('bookmark', 'ic-s')}Quero ver todos</button>
      <button class="btn pri" data-a="col-todos" data-v="visto"${saiu.every(x => x.situacao === 'visto') ? ' disabled' : ''}>${ic('visto', 'ic-s')}Já vi todos</button>`;
    return { titulo: d.nome, icone: 'layers', alta: true, pe, corpo: `${d.sinopse ? `<p class="sinopse">${esc(d.sinopse)}</p>` : ''}
      <div class="campo" style="margin-top:14px">${lbl('film', plural(d.filmes.length, 'filme', 'filmes'))}${grade(d.filmes, 'col')}</div>` };
  }
  function pintarJanela() {
    const el = $('#janela');
    const f = S.folha;
    const t = f && f.tipo === 'titulo' ? S.e.titulos.find(x => x.id === f.id) : null;
    if (!f || (f.tipo === 'titulo' && !t)) {
      if (el.innerHTML) el.innerHTML = '';
      document.body.classList.remove('com-folha');
      return;
    }
    const j = f.tipo === 'adicionar' ? folhaAdicionar() : f.tipo === 'colecao' ? folhaColecao(f) : folhaTitulo(t);
    const corpoAntes = el.querySelector('.folha-corpo'), rolou = corpoAntes && corpoAntes.dataset.k === (f.tipo + (f.id || '')) ? corpoAntes.scrollTop : 0;
    const foco = document.activeElement && el.contains(document.activeElement) ? document.activeElement.id : '';
    const sel = foco && document.activeElement.selectionStart;
    // a mesma janela pintada de novo (um toque, a lista que chegou) não sobe outra vez
    const fixa = corpoAntes && corpoAntes.dataset.k === (f.tipo + (f.id || ''));
    el.innerHTML = `<div class="veu" data-a="fechar"></div><div class="folha${j.alta ? ' alta' : ''}${fixa ? ' fixa' : ''}" role="dialog" aria-modal="true" aria-label="${esc(j.titulo)}">
      <div class="folha-cab"><h2><span class="folha-ic">${ic(j.icone)}</span><span class="folha-tt">${esc(j.titulo)}</span></h2><button class="fechar" data-a="fechar" aria-label="Fechar">${ic('x')}</button></div>
      <div class="folha-corpo" data-k="${f.tipo + (f.id || '')}">${j.corpo}</div>${j.pe ? `<div class="folha-pe">${j.pe}</div>` : ''}</div>`;
    document.body.classList.add('com-folha');
    const corpo = el.querySelector('.folha-corpo');
    if (rolou) corpo.scrollTop = rolou;
    if (foco && $('#' + foco)) { const x = $('#' + foco); x.focus({ preventScroll: true }); try { if (sel != null) x.setSelectionRange(sel, sel); } catch (e) { /* sem seleção */ } }
  }

  /* ---------- a barra de baixo e a lateral (o padrão da família) */
  const NAV = [['agora', 'Agora', 'clock'], ['buscar', 'Buscar', 'search'], ['+', 'Adicionar', 'plus'], ['historico', 'Histórico', 'visto'], ['mais', 'Mais', 'mais']];
  const aba = () => (['config', 'sobre', 'categorias'].includes(S.tela) ? 'mais' : S.tela);
  function pintarNav() {
    $('#nav').innerHTML = `<div class="in">${NAV.map(([k, n, i]) => k === '+' ? `<button class="add" data-a="adicionar" aria-label="Adicionar"><span class="pill">${ic(i)}</span></button>`
      : `<button class="${aba() === k ? 'on' : ''}" data-a="ir" data-v="${k}"${aba() === k ? ' aria-current="page"' : ''}>${ic(i)}<span>${n}</span></button>`).join('')}</div>`;
    const ts = S.e.titulos, n = k => ts.filter(t => t.situacao === k).length;
    $('#lado').innerHTML = `<div class="side-brand">Odisse<span>IA</span></div><nav class="side-nav">${NAV.map(([k, nome, i]) => k === '+' ? `<button class="side-link add" data-a="adicionar">${ic(i)}Adicionar</button>`
      : `<button class="side-link" data-a="ir" data-v="${k}"${aba() === k ? ' aria-current="page"' : ''}>${ic(i)}${nome}</button>`).join('')}</nav>
      <div class="side-h">Na lista</div><nav class="side-nav">${Object.entries(SIT).map(([k, [nome, i]]) => `<button class="side-link" data-a="lado-sit" data-v="${k}">${ic(i)}${nome}<span class="side-num">${n(k)}</span></button>`).join('')}</nav>
      <div class="side-foot">OdisseIA v${esc(S.e.versao)}</div>`;
  }

  function render() {
    if (!S.e) return;
    document.body.dataset.tela = S.tela;
    const h = S.tela === 'buscar' ? telaBuscar() : S.tela === 'historico' ? telaHistorico() : S.tela === 'mais' ? telaMais() : S.tela === 'categorias' ? telaCategorias() : S.tela === 'config' ? telaConfig() : S.tela === 'sobre' ? telaSobre() : telaAgora();
    const app = $('#app');
    const foco = document.activeElement && app.contains(document.activeElement) ? document.activeElement.id : '';
    const sel = foco && document.activeElement.selectionStart;
    app.innerHTML = h;
    if (foco && $('#' + foco)) { const x = $('#' + foco); x.focus({ preventScroll: true }); try { if (sel != null) x.setSelectionRange(sel, sel); } catch (e) { /* sem seleção */ } }
    pintarNav();
    pintarJanela();
  }

  /* ---------- o histórico (o Voltar do celular fecha a janela ou volta à tela de antes) */
  function ir(tela, sem) {
    if (tela === S.tela && !S.folha) return;
    S.tela = tela;
    S.folha = null;
    S.folhas = [];
    S.conf = '';
    if (!sem) history.pushState({ t: tela }, '');
    render();
    window.scrollTo(0, 0);
  }
  // sobre: a janela abre por cima da de agora (uma coleção a partir da busca, um filme a partir da coleção) e o Voltar
  // do celular, o X e o Esc voltam para a de baixo; sem sobre, troca a de agora
  function abrirFolha(f, sobre) {
    S.conf = '';
    if (S.folhas.length && sobre) { S.folhas.push(f); history.pushState({ t: S.tela, folha: S.folhas.length }, ''); }
    else if (S.folhas.length) { S.folhas[S.folhas.length - 1] = f; history.replaceState({ t: S.tela, folha: S.folhas.length }, ''); }
    else { S.folhas = [f]; history.pushState({ t: S.tela, folha: 1 }, ''); }
    S.folha = f;
    render();
  }
  function fecharFolha() {
    if (history.state && history.state.folha) history.back();
    else { S.folhas = []; S.folha = null; render(); }
  }
  window.addEventListener('popstate', ev => {
    const st = ev.state || { t: 'agora' };
    if (window.__selectSheet && window.__selectSheet.isOpen()) return;
    S.folhas = S.folhas.slice(0, st.folha || 0);
    S.folha = S.folhas[S.folhas.length - 1] || null;
    S.conf = '';
    if (st.t && st.t !== S.tela) { S.tela = st.t; window.scrollTo(0, 0); }
    render();
  });

  /* ---------- as ações */
  function trocar(t) {
    const i = S.e.titulos.findIndex(x => x.id === t.id);
    if (i >= 0) S.e.titulos[i] = t; else S.e.titulos.unshift(t);
  }
  async function mudar(id, campos) {
    try {
      const r = await api.post('titulo', { acao: 'mudar', id, campos });
      trocar(r.titulo);
      S.e.rev = r.rev;
      render();
    } catch (err) { toast(err.message); }
  }
  async function carregar() {
    const e = await api.get('estado');
    S.e = e;
    aplicarCor();
    render();
  }
  function carregarLista(mais) {
    const a = S.add, k = a.lista + ':' + a.tipo, L = a.listas[k] || (a.listas[k] = { itens: [], pagina: 0, mais: false, carregando: false, erro: '' });
    if (L.carregando || !S.e.tmdb.chave) return;
    L.carregando = true;
    api.get(`lista?nome=${a.lista}&tipo=${a.tipo}&pagina=${L.pagina + 1}`).then(r => {
      const vistos = new Set(L.itens.map(x => x.tipo + x.tmdb));
      L.itens.push(...r.resultados.filter(x => !vistos.has(x.tipo + x.tmdb)));
      L.pagina += 1; L.mais = r.mais; L.erro = '';
    }).catch(err => { L.erro = err.message; }).then(() => { L.carregando = false; render(); });
    if (mais) render();
  }
  let buscaT = 0, buscaN = 0;
  function buscarTMDB() {
    clearTimeout(buscaT);
    const q = S.add.q.trim();
    if (q.length < 2) { S.add.res = null; S.add.erro = ''; S.add.buscando = false; render(); return; }
    buscaT = setTimeout(async () => {
      const n = ++buscaN;
      S.add.buscando = true;
      render();
      try {
        const r = await api.get(`busca?q=${encodeURIComponent(q)}&tipo=${S.add.tipo}`);
        if (n !== buscaN) return;
        S.add.res = r.resultados;
        S.add.erro = '';
      } catch (err) {
        if (n !== buscaN) return;
        S.add.erro = err.message;
        S.add.res = null;
      }
      S.add.buscando = false;
      render();
    }, 400);
  }
  // o item de uma capa: da busca, da lista pronta ou da coleção aberta
  function itemDe(el) {
    const i = +el.dataset.i, o = el.dataset.o;
    return o === 'col' ? S.col.dados.filmes[i] : o === 'busca' ? S.add.res[i] : S.add.listas[S.add.lista + ':' + S.add.tipo].itens[i];
  }
  async function adicionarUm(r, situacao) {
    const x = await api.post('titulo', { acao: 'adicionar', tmdb: r.tmdb, tipo: r.tipo || 'filme', situacao });
    trocar(x.titulo);
    r.ja = x.titulo.id;
    r.situacao = x.titulo.situacao;
    if (!x.novo) toast('Já estava na lista.');
    return x;
  }
  // o mesmo texto do ferramentas.texto_colecao (o CorrerIA)
  function textoColecao(r, situacao) {
    const p = [];
    if (r.novos) p.push(`${r.novos} ${r.novos === 1 ? 'filme posto' : 'filmes postos'} na lista`);
    if (r.marcados) p.push(`${r.marcados} ${r.marcados === 1 ? 'marcado' : 'marcados'} como Visto`);
    if (r.fora) p.push(`${r.fora} ainda não ${r.fora === 1 ? 'saiu' : 'saíram'}`);
    return `${r.nome}: ${p.length ? p.join(', ') : 'nada a mudar'}.` + (r.novos && situacao === 'visto' ? '' : '');
  }
  const salvarBusca = () => guardar('odisseia-busca', JSON.stringify({ tipo: S.busca.tipo, situacao: S.busca.situacao, quem: S.busca.quem, categoria: S.busca.categoria }));

  const ACOES = {
    ir: el => ir(el.dataset.v),
    voltar: () => history.back(),
    // abre nas listas prontas, sem o foco no campo (o teclado não sobe por cima delas)
    adicionar: () => { S.add = { q: '', tipo: '', res: null, erro: '', buscando: false, lista: guardada('odisseia-lista') || 'alta', listas: {} }; abrirFolha({ tipo: 'adicionar' }); },
    fechar: () => fecharFolha(),
    abrir: el => abrirFolha({ tipo: 'titulo', id: el.dataset.id }),
    'add-tipo': el => { S.add.tipo = el.dataset.v; if (S.add.q.trim().length >= 2) { S.add.res = null; buscarTMDB(); } render(); },
    'add-lista': el => { S.add.lista = el.dataset.v; guardar('odisseia-lista', S.add.lista); render(); },
    'add-mais': () => carregarLista(true),
    'add-limpar': () => { S.add.q = ''; S.add.res = null; render(); },
    'cz-abrir': async el => {
      const r = itemDe(el);
      if (r.tipo === 'colecao') { S.col = null; abrirFolha({ tipo: 'colecao', id: r.tmdb }, true); return; }
      if (r.ja) { abrirFolha({ tipo: 'titulo', id: r.ja }, true); return; }
      el.disabled = true;
      try { const x = await adicionarUm(r, 'quero'); abrirFolha({ tipo: 'titulo', id: x.titulo.id }, true); } catch (err) { el.disabled = false; toast(err.message); }
    },
    'cz-quero': async el => {
      const r = itemDe(el);
      el.disabled = true;
      try { const x = await adicionarUm(r, 'quero'); toast(`${x.titulo.nome}: Quero ver.`); render(); } catch (err) { el.disabled = false; toast(err.message); }
    },
    // uma série inteira (até o último episódio que saiu) ou um filme, já como Visto, sem sair da janela
    'cz-visto': async el => {
      const r = itemDe(el);
      el.disabled = true;
      try {
        let t;
        if (r.ja) {
          const x = await api.post('titulo', { acao: 'mudar', id: r.ja, campos: { situacao: 'visto' } });
          trocar(x.titulo); S.e.rev = x.rev; t = x.titulo; r.situacao = 'visto';
        } else t = (await adicionarUm(r, 'visto')).titulo;
        toast(`${t.nome}: Visto` + (t.tipo === 'serie' && t.temp ? `, até ${ep(t.temp, t.ep)}.` : '.'));
        render();
      } catch (err) { el.disabled = false; toast(err.message); }
    },
    'abrir-colecao': el => { S.col = null; abrirFolha({ tipo: 'colecao', id: +el.dataset.id }, true); },
    'cz-colecao': el => { S.col = null; abrirFolha({ tipo: 'colecao', id: +el.dataset.id }, true); },
    // a coleção inteira de uma vez, sem abrir: Já vi todos (os que já saíram) ou Quero ver todos
    'cz-col-todos': async el => {
      const r = itemDe(el), sit = el.dataset.v;
      el.disabled = true;
      try {
        const x = await api.post('titulo', { acao: 'adicionar_colecao', colecao: r.tmdb, situacao: sit });
        r.situacao = sit;
        toast(textoColecao(x, sit));
        await carregar();
      } catch (err) { el.disabled = false; toast(err.message); }
    },
    'col-todos': async el => {
      el.disabled = true;
      try {
        const r = await api.post('titulo', { acao: 'adicionar_colecao', colecao: S.col.id, situacao: el.dataset.v });
        toast(textoColecao(r, el.dataset.v));
        S.col = null;
        await carregar();
      } catch (err) { el.disabled = false; toast(err.message); }
    },
    sit: el => mudar(S.folha.id, { situacao: el.dataset.v }),
    cat: el => mudar(S.folha.id, { categoria: el.dataset.v }),
    'quem-todos': () => { const t = S.e.titulos.find(x => x.id === S.folha.id), todos = S.e.pessoas.every(p => t.quem.includes(p.id)); mudar(t.id, { quem: todos ? [] : S.e.pessoas.map(p => p.id) }); },
    'ir-categorias': () => { if (S.folha) { S.folha = null; S.folhas = []; history.replaceState({ t: S.tela }, ''); } ir('categorias'); },
    quem: el => { const t = S.e.titulos.find(x => x.id === S.folha.id), p = el.dataset.v; mudar(t.id, { quem: t.quem.includes(p) ? t.quem.filter(x => x !== p) : [...t.quem, p] }); },
    proximo: async el => {
      try {
        const r = await api.post('titulo', { acao: 'proximo', id: el.dataset.id });
        trocar(r.titulo);
        delete S.tempEsc[r.titulo.id];
        S.e.rev = r.rev;
        toast(`${r.titulo.nome}: ${ep(r.titulo.temp, r.titulo.ep)} visto.` + (r.titulo.situacao === 'visto' ? ' A série acabou.' : ''));
        render();
      } catch (err) { toast(err.message); }
    },
    atualizar: async el => {
      el.disabled = true;
      try { const r = await api.post('titulo', { acao: 'atualizar', id: el.dataset.id }); trocar(r.titulo); toast('Atualizado pelo TMDB.'); render(); } catch (err) { el.disabled = false; toast(err.message); }
    },
    conf: el => { S.conf = el.dataset.v; render(); },
    'conf-nao': () => { S.conf = ''; S.importar = null; render(); },
    apagar: async el => {
      try {
        await api.post('titulo', { acao: 'apagar', id: el.dataset.id });
        S.e.titulos = S.e.titulos.filter(t => t.id !== el.dataset.id);
        S.conf = '';
        toast('Apagado.');
        fecharFolha();
      } catch (err) { toast(err.message); }
    },
    filtros: () => { guardar('odisseia-filtros', guardada('odisseia-filtros') === 'fechado' ? 'aberto' : 'fechado'); render(); },
    'b-limpar': () => { S.busca.texto = ''; render(); },
    'ver-quero': () => { S.busca.situacao = 'quero'; S.busca.texto = ''; salvarBusca(); ir('buscar'); },
    'lado-sit': el => { S.busca.texto = ''; S.busca.situacao = el.dataset.v; salvarBusca(); S.tela === 'buscar' ? render() : ir('buscar'); },
    'ir-config': el => { if (el.dataset.v) { S.aba = el.dataset.v; guardar('odisseia-aba', S.aba); } if (S.folha) { S.folha = null; S.folhas = []; history.replaceState({ t: S.tela }, ''); } ir('config'); },
    sobre: () => ir('sobre'),
    hist: el => { S.hist = el.dataset.v; guardar('odisseia-historico', S.hist); render(); },
    aba: el => { S.aba = el.dataset.v; S.conf = ''; guardar('odisseia-aba', S.aba); render(); },
    tema: el => { S.tema = el.dataset.v; guardar('odisseia-tema', S.tema); aplicarTema(); render(); },
    cor: async el => { try { S.e.ajustes = (await api.post('ajustes', { cor: el.dataset.v })).ajustes; aplicarCor(); render(); } catch (err) { toast(err.message); } },
    aj: async el => {
      const k = el.dataset.k;
      try {
        S.e.ajustes = (await api.post('ajustes', { [k]: !S.e.ajustes[k] })).ajustes;
        if (k === 'correria') S.e.correria.ligado = S.e.ajustes.correria;
        aplicarCor();
        render();
      } catch (err) { toast(err.message); }
    },
    'aj-tipo': async el => {
      try { S.e.ajustes = (await api.post('ajustes', { tipos: { [el.dataset.k]: !S.e.ajustes.tipos[el.dataset.k] } })).ajustes; S.add.listas = {}; await carregar(); } catch (err) { toast(err.message); }
    },
    'cat-nova': async el => {
      const k = el.dataset.k, campo = $('#nova-' + k), nome = (campo.value || '').trim();
      if (!nome) { toast('Escreva o nome da categoria.'); campo.focus(); return; }
      if (await categorias({ acao: 'nova', tipo: k, nome })) { const c = $('#nova-' + k); if (c) c.focus({ preventScroll: true }); }
    },
    'cat-apagar': el => categorias({ acao: 'apagar', id: el.dataset.id }),
    'chave-salvar': async el => {
      const v = ($('#f-chave') || {}).value || '';
      if (!v.trim()) { toast('Cole a chave do TMDB.'); return; }
      el.disabled = true;
      try { S.e.tmdb = (await api.post('tmdb', { chave: v })).tmdb; S.trocarChave = false; toast('Chave do TMDB funcionando.'); render(); } catch (err) { el.disabled = false; toast(err.message); }
    },
    'chave-trocar': () => { S.trocarChave = true; render(); },
    'chave-cancelar': () => { S.trocarChave = false; render(); },
    'chave-apagar': async () => { try { S.e.tmdb = (await api.post('tmdb', { chave: '' })).tmdb; render(); } catch (err) { toast(err.message); } },
    backup: async el => { el.disabled = true; try { const r = await api.post('dados/backup'); S.dados.backups = r.backups; toast('Backup feito.'); render(); } catch (err) { el.disabled = false; toast(err.message); } },
    restaurar: async el => {
      try { await api.post('dados/restaurar', { origem: el.dataset.origem, nome: el.dataset.nome }); S.conf = ''; S.dados = null; toast('Restaurado.'); await carregar(); } catch (err) { toast(err.message); }
    },
    escolher: () => $('#dados-arquivo').click(),
    importar: async () => {
      try { await api.post('dados/importar', { arquivo: S.importar.b64 }); S.importar = null; S.dados = null; toast('Importado.'); await carregar(); } catch (err) { toast(err.message); }
    },
    zerar: async () => { try { await api.post('dados/zerar', { confirmar: true }); S.conf = ''; S.dados = null; toast('A lista foi apagada.'); await carregar(); } catch (err) { toast(err.message); } },
  };
  document.addEventListener('click', ev => {
    const el = ev.target.closest('[data-a]');
    if (el && ACOES[el.dataset.a] && !el.disabled) { ev.preventDefault(); ACOES[el.dataset.a](el); return; }
    const dobra = ev.target.closest('[data-dobra]');
    if (dobra) {
      const F = fechadas(), k = dobra.dataset.dobra;
      if (F.has(k)) F.delete(k); else F.add(k);
      guardar('odisseia-fechadas', JSON.stringify([...F]));
      render();
    }
  });
  document.addEventListener('keydown', ev => {
    if ((ev.key === 'Enter' || ev.key === ' ') && ev.target.matches('[data-dobra]')) { ev.preventDefault(); ev.target.click(); }
    if (ev.key === 'Escape' && S.folha && !(window.__selectSheet && window.__selectSheet.isOpen())) fecharFolha();
    if (ev.key === 'Enter' && ev.target.id === 'f-chave') { ev.preventDefault(); ACOES['chave-salvar']($('[data-a="chave-salvar"]')); }
    // as categorias: um campo de uma linha só, o Enter salva
    if (ev.key === 'Enter' && !ev.shiftKey && ev.target.matches('textarea.umalinha')) {
      ev.preventDefault();
      if (ev.target.id && ev.target.id.startsWith('nova-')) ACOES['cat-nova']($(`[data-a="cat-nova"][data-k="${ev.target.id.slice(5)}"]`));
      else ev.target.blur();
    }
  });
  document.addEventListener('input', ev => {
    const id = ev.target.id;
    if (id === 'b-texto') { S.busca.texto = ev.target.value; render(); }
    if (id === 'add-q') { S.add.q = ev.target.value; buscarTMDB(); }
  });
  document.addEventListener('change', ev => {
    const id = ev.target.id, t = S.folha && S.e.titulos.find(x => x.id === S.folha.id);
    if (id === 'f-temp' && t) {
      const n = +ev.target.value;
      if (!n) { delete S.tempEsc[t.id]; mudar(t.id, { temp: 0, ep: 0 }); return; }
      S.tempEsc[t.id] = n;
      render();
    }
    if (id === 'f-ep' && t && ev.target.value) {
      const temp = S.tempEsc[t.id] != null ? S.tempEsc[t.id] : t.temp;
      delete S.tempEsc[t.id];
      mudar(t.id, { temp, ep: +ev.target.value });
    }
    if (id === 'f-notas' && t && ev.target.value !== t.notas) mudar(t.id, { notas: ev.target.value });
    if (ev.target.dataset && ev.target.dataset.cat) {
      const c = Object.values(S.e.categorias).flat().find(x => x.id === ev.target.dataset.cat), nome = ev.target.value.trim();
      if (c && nome && nome !== c.nome) categorias({ acao: 'renomear', id: c.id, nome });
      else if (c && !nome) { ev.target.value = c.nome; }
    }
    const filtro = { 'f-tipo': 'tipo', 'f-sit': 'situacao', 'f-cat': 'categoria', 'f-quem': 'quem' }[id];
    if (filtro) {
      S.busca[filtro] = ev.target.value;
      if (filtro === 'tipo' && S.busca.categoria && !(S.e.categorias[S.busca.tipo] || []).some(c => c.id === S.busca.categoria) && S.busca.tipo) S.busca.categoria = '';
      salvarBusca();
      render();
    }
    if (id === 'dados-arquivo' && ev.target.files[0]) {
      const f = ev.target.files[0], r = new FileReader();
      r.onload = () => { S.importar = { nome: f.name, b64: String(r.result).split(',')[1] || '' }; render(); };
      r.readAsDataURL(f);
      ev.target.value = '';
    }
  });

  // a lista muda pelo CorrerIA ou em outro aparelho: a tela vê pela revisão (a cada 20 s, com a tela à vista)
  setInterval(async () => {
    if (!S.e || document.visibilityState !== 'visible' || document.activeElement && /^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName)) return;
    try { const r = await api.get('rev'); if (r.rev !== S.e.rev) await carregar(); } catch (e) { /* sem conexão agora */ }
  }, 20000);

  history.replaceState({ t: 'agora' }, '');
  carregar().catch(err => { $('#app').innerHTML = `<p class="boot">Não consegui abrir: ${esc(err.message)}</p>`; });
})();

// O teclado do celular: ao abrir uma janela, o campo recebe o foco enquanto ela ainda sobe, e o navegador rola as páginas
// em volta do app (a do Home Assistant) para "mostrar" o campo: a barra de cima some e a janela fica fora do lugar, até
// um toque. Aqui, quando um campo de texto recebe o foco (e quando o teclado muda a altura da tela), as páginas em volta
// voltam para o começo. A página do próprio app não é tocada. O mesmo código em todos os apps da família (teclado.js).
(function (win) {
  if (!win || win.__tecladoCalmo) return;
  win.__tecladoCalmo = true;
  const voltar = () => {
    for (const w of [win.parent, win.top]) {
      try {
        if (!w || w === win) continue;
        const el = w.document && w.document.scrollingElement;
        if (w.scrollY || (el && el.scrollTop)) w.scrollTo(0, 0);
      } catch (e) { /* outra origem: não dá para mexer */ }
    }
  };
  let ate = 0;
  const ciclo = () => { voltar(); if (Date.now() < ate) win.setTimeout(ciclo, 60); };
  win.addEventListener("focusin", (e) => {
    const t = (e.composedPath && e.composedPath()[0]) || e.target;
    if (!t || !/^(INPUT|TEXTAREA)$/.test(t.tagName || "")) return;
    const parado = Date.now() >= ate;
    ate = Date.now() + 900; // a janela sobe em 0,3 s e o teclado, logo depois
    if (parado) ciclo();
  }, true);
  if (win.visualViewport) win.visualViewport.addEventListener("resize", voltar);
})(window);
