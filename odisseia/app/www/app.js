/* OdisseIA · a tela (JavaScript puro, sem build). Os filmes, as séries e os jogos da casa: Agora (o que a casa está
   vendo, os episódios e os jogos que vão sair e o que quer ver ou jogar), Buscar, o + (procura no TMDB e no IGDB),
   Vistos e Mais (Categorias, Configurações e Sobre).
   Ações por data-a; tudo vem de /api/estado e as mudanças voltam pelo /api/titulo. */
(function () {
  'use strict';
  const $ = s => document.querySelector(s);
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const IC = {
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    gauge: '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
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
    camera: '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3z"/><circle cx="12" cy="13" r="3"/>',
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
    sparkles: '<path d="M11 3.5 12.8 9l5.7 1.8-5.7 1.8L11 18.3l-1.8-5.7-5.7-1.8L9.2 9z"/><path d="M19 3v4M17 5h4"/>',
    back: '<path d="m15 18-6-6 6-6"/>',
    'external-link': '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    zap: '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
    chat: '<path d="M21 12a8 8 0 0 1-11.7 7.1L4 20.5l1.4-4.9A8 8 0 1 1 21 12Z"/>',
    mic: '<rect x="9" y="2.5" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3.5"/>',
    send: '<path d="m21.5 2.5-9 19-2.5-8.5L1.5 10z"/><path d="m21.5 2.5-11.5 10.5"/>',
    chart: '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
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
    image: '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.1-3.1a2 2 0 0 0-2.8 0L6 21"/>',
    igual: '<path d="M5 9h14M5 15h14"/>',
    gamepad: '<path d="M6 11h4M8 9v4M15 12h.01M18 10h.01"/><path d="M17.32 5H6.68a4 4 0 0 0-3.98 3.59C2.6 9.42 2 14.46 2 16a3 3 0 0 0 3 3c1 0 1.5-.5 2-1l1.41-1.41A2 2 0 0 1 9.83 16h4.34a2 2 0 0 1 1.41.59L17 18c.5.5 1 1 2 1a3 3 0 0 0 3-3c0-1.55-.6-6.58-.7-7.26A4 4 0 0 0 17.32 5z"/>',
  };
  const ic = (n, cls = 'ic') => `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${IC[n] || ''}</svg>`;
  const guardada = k => { try { return localStorage.getItem(k); } catch (e) { return null; } };
  const guardar = (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* sem armazenamento: só nesta vez */ } };
  const lerJSON = (k, padrao) => { try { return JSON.parse(guardada(k) || '') || padrao; } catch (e) { return padrao; } };

  // 0.3.0 (o dono: "pode tirar a opção de vendo, só vou controlar visto e quero ver")
  const SIT = { quero: ['Quero ver', 'bookmark'], visto: ['Visto', 'visto'] };
  const TIPO = { filme: ['Filme', 'film'], serie: ['Série', 'tv'], jogo: ['Jogo', 'gamepad'], livro: ['Livro', 'book-open'], colecao: ['Coleção de filmes', 'layers'], colecao_jogos: ['Coleção de jogos', 'layers'] };
  const NOMES = { filme: 'Filmes', serie: 'Séries', jogo: 'Jogos', livro: 'Livros' };
  const ehTV = k => k === 'filme' || k === 'serie';
  // 0.4.0 (o dono: "cadê os jogos?"): num jogo, as mesmas duas situações com os nomes de jogo
  const ehJogo = r => r.tipo === 'jogo' || r.tipo === 'colecao_jogos';
  const ref = r => ehJogo(r) ? r.igdb : r.tipo === 'livro' ? r.ol : r.tmdb;
  // 0.16.0 (o dono: "Ótima ideia controlar os livros também"): num livro, Quero ler e Lido
  const sitN = (tipo, k) => tipo === 'jogo' || tipo === 'colecao_jogos' ? { quero: 'Quero jogar', visto: 'Jogado' }[k] : tipo === 'livro' ? { quero: 'Quero ler', visto: 'Lido' }[k] : SIT[k][0];
  const ABAS = [['integracoes', 'Integrações', 'layers'], ['dados', 'Dados', 'database'], ['aparencia', 'Aparência', 'palette'], ['opcoes', 'Opções', 'toggle']];
  const S = {
    e: null, tela: 'agora', aba: guardada('odisseia-aba') || 'integracoes', tema: guardada('odisseia-tema') || 'auto',
    folha: null, folhas: [], col: null, hist: guardada('odisseia-vistos') || 'serie', vcat: lerJSON('odisseia-vistos-cat', {}), sel: null, lote: null, catf: null, busca: Object.assign({ texto: '', tipo: '', situacao: '', quem: '', categoria: '' }, lerJSON('odisseia-busca', {})),
    add: { q: '', tipo: '', res: null, erro: '', buscando: false, lista: 'alta', listas: {} }, aband: false, tempEsc: {}, conf: '', dados: null, trocarChave: false,
    ia: null, conv: null, ch: { texto: '', anexo: null, enviando: false, fala: '', rolar: false, rapidas: false, editando: null }, mem: null, uso: null,
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
  // acao: {rotulo, fazer} (o Desfazer, como nos outros apps)
  function toast(t, acao) {
    const el = $('#toast');
    el.innerHTML = `<span class="toast-t">${esc(t)}</span>${acao ? `<button type="button" class="toast-a">${ic('back', 'ic-s')}${esc(acao.rotulo)}</button>` : ''}`;
    el.classList.toggle('com-acao', !!acao);
    el.classList.add('on');
    clearTimeout(toast.t);
    const fechar = () => el.classList.remove('on', 'com-acao');
    if (acao) el.querySelector('.toast-a').onclick = () => { clearTimeout(toast.t); fechar(); acao.fazer(); };
    toast.t = setTimeout(fechar, acao ? 6000 : Math.min(9000, Math.max(2600, String(t).length * 55)));
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
  // a cor de uma categoria (0.4.0, o dono: "colocar cor, fazer no mesmo padrão dos outros apps"): a paleta da família
  const corDe = id => PALETA.find(c => c.id === id) || PALETA[PALETA.length - 1];
  const estiloCor = id => { const c = corDe(id); return `--c:${c.fill};--ci:${c.ink}`; };
  const corLivre = lista => { const u = new Set(lista.map(c => c.cor)), L = PALETA.slice(0, -1); return (L.find(c => !u.has(c.id)) || L[lista.length % L.length]).id; };
  // 0.4.0 (o dono: "a seleção de categorias nas opções de adicionar e alterar deve ser igual a outros apps"): a escolha de
  // uma categoria é como a das listas do ResolvIA e a das categorias do MemorIA: a bolinha na cor dela e, escolhida, o
  // fundo na cor dela
  const pickCat = (a, c, on, extra = '') => `<button class="escolha cor${on ? ' on' : ''}" style="${estiloCor(c.cor)}" data-a="${a}" data-v="${c.id}" aria-pressed="${on}"${extra}><span class="dot"></span>${esc(c.nome)}</button>`;
  const tagCat = c => `<span class="cat-tag" style="${estiloCor(c.cor)}">${esc(c.nome)}</span>`;
  // a mesma etiqueta, para tocar (dentro do botão da linha, o toque nela vai para ela); sem categoria, Sem categoria
  const tagCatToque = (c, id) => `<span class="cat-tag toque${c ? '' : ' vazia'}" role="button" data-a="cat-rapida" data-id="${id}"${c ? ` style="${estiloCor(c.cor)}"` : ''}>${c ? esc(c.nome) : `${ic('plus', 'ic-s')}Categoria`}</span>`;
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
  const saiEm = iso => /^(hoje|amanhã)$/.test(dia(iso)) ? dia(iso) : 'em ' + new Date(iso + 'T12:00:00').toLocaleDateString('pt-BR');
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
  const ligados = () => Object.keys(NOMES).filter(k => S.e.ajustes.tipos[k]);
  // a fonte do tipo tem a conta posta (o TMDB nos filmes e nas séries, o IGDB nos jogos)? sem tipo: alguma dos ligados
  function temFonte(tipo) {
    const tv = S.e.tmdb.chave, jg = S.e.igdb.chave, l = ligados();
    if (tipo === 'livro') return true;  // os livros vêm da Open Library, sem conta
    if (tipo === 'jogo') return jg;
    if (tipo) return tv;
    return (tv && l.some(ehTV)) || (jg && l.includes('jogo')) || l.includes('livro');
  }
  // «Nome do filme, da série ou do jogo», com os tipos ligados (ou o escolhido)
  function oQue(tipo) {
    const n = { filme: 'do filme', serie: 'da série', jogo: 'do jogo', livro: 'do livro' }, l = (tipo ? [tipo] : ligados()).map(k => n[k]);
    if (l.length === 1 && l[0] === n.livro) return 'Nome do livro, autor ou ISBN';
    return 'Nome ' + (l.length > 1 ? l.slice(0, -1).join(', ') + ' ou ' + l[l.length - 1] : l[0]);
  }
  const podeProximo = t => { const s = t.tipo === 'serie' && seguinte(t); return s && jaSaiu(t, s) ? s : null; };

  /* ---------- pedaços da tela */
  const fechadas = () => new Set(lerJSON('odisseia-fechadas', []));
  // toda seção (cartão) contrai e expande num toque no cabeçalho; o aparelho lembra as fechadas
  const cab = (icone, titulo, chave, extra = '') => `<div class="rot" role="button" tabindex="0" data-dobra="${esc(chave || titulo)}" aria-expanded="${!fechadas().has(chave || titulo)}"><span class="rot-ic">${ic(icone)}</span><h2>${titulo}</h2>${extra}<span class="dobra-ic" aria-hidden="true">${ic('chev', 'ic-s')}</span></div>`;
  const card = (id, icone, titulo, corpo, chave) => `<section class="card${fechadas().has(chave || titulo) ? ' fechada' : ''}" id="${id}">${cab(icone, titulo, chave)}${corpo}</section>`;
  const lbl = (icone, titulo, para) => para ? `<label for="${para}">${ic(icone, 'ic-s')}${titulo}</label>` : `<span class="lbl">${ic(icone, 'ic-s')}${titulo}</span>`;
  const ICONE_TELA = { Agora: 'clock', Buscar: 'search', 'Concluídos': 'visto', Mais: 'mais', Categorias: 'tag', 'Configurações': 'gear', Sobre: 'info' };
  // 0.7.0: no alto de toda tela, como nos outros apps: a marca e o olá, a Conversa e o Falar (com a IA ligada e pronta)
  function barraTopo() {
    const eu = S.e && pessoa(S.e.eu);
    return `<div class="mh-row"><p class="eyebrow"><span class="brand">Odisse<span>IA</span></span>${eu ? `<span class="ola"><span class="sep"> · </span>olá, ${esc(eu.nome.split(' ')[0])}</span>` : ''}</p>
      ${iaOn() ? `<button class="chat-top" data-a="conversa" aria-label="Conversar com a IA" title="Conversar">${ic('chat')}</button>` : ''}
      ${falaOn() ? `<button class="mic-top" data-a="falar-top" aria-label="Falar com a IA" title="Falar">${ic('mic')}</button>` : ''}</div>`;
  }
  const topo = (titulo, volta) => `<header class="cab-tela">${barraTopo()}${volta ? `<button class="voltar" data-a="voltar">${ic('back', 'ic-s')}${volta}</button>` : ''}<h1><span class="rot-ic tela-ic" aria-hidden="true">${ic(ICONE_TELA[titulo])}</span>${titulo}</h1></header>`;
  const capa = (t, g) => t.capa ? `<img class="capa${g ? ' g' : ''}" src="api/capa/${esc(t.capa)}" alt="" loading="lazy">` : `<span class="capa${g ? ' g' : ''}">${ic(TIPO[t.tipo][1])}</span>`;
  const avs = ids => ids && ids.length && S.e.ajustes.quem ? `<span class="pessoas-mini">${ids.map(i => `<span class="av" title="${esc((pessoa(i) || {}).nome || i)}">${esc(inicial(i))}</span>`).join('')}</span>` : '';

  const emAndamento = t => t.tipo === 'serie' && t.situacao === 'quero' && !!t.temp;
  const catDe = t => (S.e.categorias[t.tipo] || []).find(c => c.id === t.categoria);
  function meta(t) {
    const p = [];
    if (emAndamento(t)) {
      p.push(`parou em ${ep(t.temp, t.ep)}`);
      const f = faltam(t);
      if (f) p.push(`faltam ${f}`);
    } else if (t.tipo === 'serie') {
      p.push('Série' + (t.temporadas && t.temporadas.length ? ' · ' + plural(t.temporadas.length, 'temporada', 'temporadas') : ''));
      if (t.ano) p.push(t.ano);
    } else if (t.tipo === 'livro') {
      p.push('Livro');
      if ((t.autores || []).length) p.push(t.autores[0]);
      if (t.ano) p.push(t.ano);
    } else if (t.tipo === 'jogo') {
      p.push('Jogo');
      if (t.ano) p.push(t.ano);
      if ((t.plataformas || []).length) p.push(t.plataformas.slice(0, 2).join(', '));
    } else {
      p.push('Filme');
      if (t.duracao) p.push(duracao(t.duracao));
      if (t.ano) p.push(t.ano);
    }
    return p.join(' · ');
  }
  // 0.4.0 (o dono: "o nome ali, D ou T, deixar no final, na direita, na mesma linha de cima, para ganhar uma linha, e
  // adicionar a categoria"): o nome e quem na linha de cima; embaixo, o tipo, a duração, o ano e a categoria na cor dela.
  // sel: o Selecionar (um toque marca); lado: o tipo do que já foi marcado (os outros ficam de fora)
  function linhaTit(t, opts = {}) {
    const sel = opts.sel, marcado = sel && sel.has(t.id), fora = sel && opts.lado && t.tipo !== opts.lado, c = catDe(t);
    const tag = opts.catToque && !sel ? tagCatToque(c, t.id) : c ? tagCat(c) : '';
    const s = !sel && opts.mais1 && podeProximo(t);
    const marca = sel ? `<span class="marca${marcado ? ' on' : ''}">${ic('check', 'ic-s')}</span>` : '';
    const acao = `data-a="${sel ? 'sel-marcar' : 'abrir'}" data-id="${t.id}"${fora ? ' disabled' : ''}${sel ? ` aria-pressed="${!!marcado}"` : ''}`;
    const mais = s ? `<button class="mais1" data-a="proximo" data-id="${t.id}" aria-label="Vi o ${ep(s[0], s[1])}">${ic('check', 'ic-s')}${ep(s[0], s[1])}</button>` : '';
    if (opts.curta) {
      return `<li class="linha-tit curta${fora ? ' fora' : ''}"><button class="tit" ${acao}>${marca}<span class="t-txt"><span class="t-l1"><b>${esc(t.nome)}</b>${tag}${t.ano ? `<small class="ano">${t.ano}</small>` : ''}${avs(t.quem)}</span></span></button>${mais}</li>`;
    }
    return `<li class="linha-tit${fora ? ' fora' : ''}"><button class="tit" ${acao}>${marca}${capa(t)}<span class="t-txt"><span class="t-l1"><b>${esc(t.nome)}</b>${avs(t.quem)}</span>
      <small class="${opts.dest ? 'dest' : ''}">${opts.sub != null ? opts.sub : esc(meta(t))}${opts.sub == null ? tag : ''}</small></span></button>${mais}</li>`;
  }
  // 0.4.0 (o dono: "permitir visualizar modo lista menor, ter opção de alteração em massa de categorias"; "e também o
  // quem, igual a alteração em massa de outros apps"): em cima da lista, Capas ou Lista (o aparelho lembra) e o
  // Selecionar, como no InventarIA (marcar vários e Alterar, com o Desfazer). Uma seleção é de um tipo só.
  // 0.5.0 (o dono: "ter opção de agrupar por categoria do filme, e pelo gênero"): os grupos na ordem das categorias (Sem
  // categoria no fim) ou dos gêneros (o primeiro de cada título, em ordem alfabética; Sem gênero no fim)
  function grupos(ts, ag) {
    const m = new Map();
    for (const t of ts) {
      const c = ag === 'categoria' ? catDe(t) : null, k = ag === 'categoria' ? (c ? c.id : '') : ((t.generos || [])[0] || '');
      if (!m.has(k)) m.set(k, { k, c, nome: k ? (c ? c.nome : k) : ag === 'categoria' ? 'Sem categoria' : 'Sem gênero', ts: [] });
      m.get(k).ts.push(t);
    }
    const ordem = ag === 'categoria' ? Object.values(S.e.categorias).flat().map(c => c.id) : [];
    return [...m.values()].sort((a, b) => (!a.k) - (!b.k) || (ag === 'categoria' ? ordem.indexOf(a.k) - ordem.indexOf(b.k) : a.nome.localeCompare(b.nome, 'pt-BR')));
  }
  function listaSel(ts, opts = {}) {
    const modo = guardada('odisseia-modo') === 'lista' ? 'lista' : 'capas', sel = S.sel;
    if (sel) { const vis = new Set(ts.map(t => t.id)); for (const id of [...sel]) if (!vis.has(id)) sel.delete(id); }
    const lado = sel && sel.size ? (S.e.titulos.find(t => sel.has(t.id)) || {}).tipo : '';
    const podem = ts.filter(t => t.tipo === (lado || (ts[0] || {}).tipo));
    S.podem = podem.map(t => t.id);
    const n = sel ? sel.size : 0, todos = n > 0 && n === podem.length;
    const barra = sel ? `<div class="ssum sel"><button class="fechar" data-a="sel-fim" aria-label="Cancelar seleção">${ic('x', 'ic-s')}</button><span class="sel-n">${n ? plural(n, 'selecionado', 'selecionados') : 'Selecionar'}</span>
        <button class="btn fino" data-a="sel-todos">${ic('list-checks', 'ic-s')}${todos ? 'Nenhum' : 'Todos'}</button></div>`
      : `<div class="ssum"><div class="modo" role="group" aria-label="Ver como">${[['capas', 'Capas', 'image'], ['lista', 'Lista', 'list']].map(([k, nome, i]) => `<button class="${modo === k ? 'on' : ''}" data-a="modo" data-v="${k}" aria-pressed="${modo === k}" aria-label="${nome}">${ic(i, 'ic-s')}<span>${nome}</span></button>`).join('')}</div>
        <button class="btn fino" data-a="sel-comecar">${ic('list-checks', 'ic-s')}Selecionar</button></div>`;
    const o = { mais1: opts.mais1, sel, lado, curta: modo === 'lista', catToque: true };
    const ag = guardada('odisseia-agrupar') || '', ul = l => `<ul class="titulos${modo === 'lista' ? ' curtas' : ''}">${l.map(t => linhaTit(t, o)).join('')}</ul>`;
    return barra + (ag ? grupos(ts, ag).map(g => {
      const k = ag + ':' + g.k, F = new Set(lerJSON('odisseia-grupos', [])), fechado = F.has(k);
      return `<div class="grupo${fechado ? ' fechado' : ''}"><button class="grupo-h" data-a="grupo" data-v="${esc(k)}" aria-expanded="${!fechado}"><span class="grupo-ic${g.c ? ' cor' : ''}"${g.c ? ` style="${estiloCor(g.c.cor)}"` : ''}>${ic(ag === 'genero' ? 'texto' : 'tag', 'ic-s')}</span><b>${esc(g.nome)}</b><span class="cont">${plural(g.ts.length, 'título', 'títulos')}</span>${ic('chev', 'ic-s seta')}</button>${fechado ? '' : ul(g.ts)}</div>`;
    }).join('') : ul(ts))
      // 0.10.0 (o padrão da família): o Apagar ao lado do Alterar, com o Desfazer
      + (sel ? `<div class="selbar dois"><button class="btn perigo" data-a="sel-apagar"${n ? '' : ' disabled'}>${ic('trash', 'ic-s')}Apagar</button><button class="btn pri" data-a="sel-alterar"${n ? '' : ' disabled'}>${ic('nota', 'ic-s')}${n ? 'Alterar ' + plural(n, 'título', 'títulos') : 'Alterar'}</button></div>` : '');
  }
  // 0.11.0 (o dono: "deixa tudo bem bonito nesse padrão", o dos Consumíveis do InventarIA): o título fecha o bloco (fechado,
  // o escolhido ao lado), as escolhas numa barra só, do mesmo tamanho, e cada grupo com o ícone, o nome, quantos e a seta.
  // 0.12.0 (PADROES.md, "O alto das listas"): fora do cartão, logo embaixo do Filtros; o Nenhum por último
  const AG = [['categoria', 'Categoria', 'tag'], ['genero', 'Gênero', 'texto'], ['', 'Nenhum', 'list']];
  function agruparBloco() {
    if (S.sel) return '';
    const ag = guardada('odisseia-agrupar') || '', agF = guardada('odisseia-agrupar-fechado') === '1';
    return `<div class="agrupar${agF ? ' fechado' : ''}"><button class="agrupar-l" id="agrupar-l" data-a="agrupar-dobra" aria-expanded="${!agF}">${ic('layers', 'ic-s')}<span>Agrupar por</span>${agF ? `<span class="agrupar-val">· ${(AG.find(([k]) => k === ag) || AG[2])[1]}</span>` : ''}${ic('chev', 'ic-s seta')}</button>
      <div class="modo agrupar-seg" role="group" aria-labelledby="agrupar-l"${agF ? ' hidden' : ''}>${AG.map(([k, n, i]) => `<button class="${ag === k ? 'on' : ''}" data-a="agrupar" data-v="${k}" aria-pressed="${ag === k}">${ic(i, 'ic-s')}<span>${n}</span></button>`).join('')}</div></div>`;
  }
  const lista = (ts, opts) => `<ul class="titulos">${ts.map(t => linhaTit(t, opts)).join('')}</ul>`;
  const ordem = ts => ts.slice().sort((a, b) => String(b.atualizado).localeCompare(String(a.atualizado)));

  /* ---------- Agora */
  function telaAgora() {
    const e = S.e, ts = e.titulos, eu = pessoa(e.eu);
    let h = topo('Agora');
    const l = ligados(), faltaTV = !e.tmdb.chave && l.some(ehTV), faltaJG = !e.igdb.chave && l.includes('jogo');
    if (faltaTV || faltaJG) {
      const txt = faltaTV && faltaJG ? `Para procurar, o app usa o ${site('https://www.themoviedb.org/settings/api', 'TMDB')} (filmes e séries) e o ${site('https://dev.twitch.tv/console', 'IGDB')} (jogos), os dois de graça. Ponha as contas em Configurações.`
        : faltaTV ? `Para procurar os filmes e as séries, o app usa o TMDB, de graça. Crie a sua chave no ${site('https://www.themoviedb.org/settings/api', 'TMDB')} e cole em Configurações.`
          : `Para procurar os jogos, o app usa o IGDB, de graça: crie um app no ${site('https://dev.twitch.tv/console', 'Twitch Developers')} e cole o Client ID e o Client Secret em Configurações.`;
      h += card('comeco', 'key', 'Comece aqui', `<p class="lead">${txt}</p>
        <div class="acoes"><button class="btn pri" data-a="ir-config" data-v="integracoes">${ic('key', 'ic-s')}${faltaTV && faltaJG ? 'Pôr as contas' : faltaTV ? 'Pôr a chave' : 'Pôr a conta'}</button></div>`);
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
    const saem = ts.filter(t => t.tipo === 'jogo' && t.situacao === 'quero' && t.data && t.data > hojeISO()).sort((a, b) => a.data.localeCompare(b.data));
    if (saem.length) {
      h += card('saem', 'calendar', 'Jogos que vão sair', `<ul class="titulos">${saem.slice(0, 6).map(t => linhaTit(t, { dest: true, sub: 'sai ' + esc(saiEm(t.data)) })).join('')}</ul>`);
    }
    for (const [k, nome, icone, so, vt] of [['quero', 'Quero ver', 'bookmark', t => ehTV(t.tipo), ''], ['quero-jogar', 'Quero jogar', 'gamepad', t => t.tipo === 'jogo', 'jogo'], ['quero-ler', 'Quero ler', 'book-open', t => t.tipo === 'livro', 'livro']]) {
      const quero = ordem(ts.filter(t => t.situacao === 'quero' && !emAndamento(t) && so(t)));
      if (quero.length) {
        h += card(k, icone, `${nome} <span class="cont">${quero.length}</span>`, lista(quero.slice(0, 6)) +
          (quero.length > 6 ? `<div class="acoes ver-todos"><button class="btn out" data-a="ver-quero" data-v="${vt}">${ic('list', 'ic-s')}Ver todos</button></div>` : ''), nome);
      }
    }
    return h;
  }

  /* ---------- Buscar */
  function filtrados() {
    const b = S.busca, alvo = semAcento(b.texto.trim()), cat = catDaBusca();
    return ordem(S.e.titulos.filter(t => (!alvo || semAcento(t.nome).includes(alvo) || semAcento(t.original).includes(alvo))
      && (!b.tipo || t.tipo === b.tipo || !ligados().includes(b.tipo)) && (!b.quem || t.quem.includes(b.quem))
      && (!b.situacao || t.situacao === b.situacao) && (!cat || (cat === 'sem' ? !catDe(t) : t.categoria === cat))));
  }
  // a categoria só vale com um tipo escolhido (ou um tipo só ligado)
  function catDaBusca() {
    const l = ligados();
    return l.length === 1 || l.includes(S.busca.tipo) ? S.busca.categoria : '';
  }
  // 0.3.0 (o dono: "a parte de filtros deixa no mesmo padrão dos outros apps"): a busca, o Filtros que fecha e abre (o
  // aparelho lembra) e as caixas de seleção lado a lado, como no InventarIA e no ResolvIA
  // 0.12.0 (PADROES.md): o Filtros fechado diz o que está escolhido em cada caixa (fora o «todos» do começo)
  function filtrosVal(caixas) {
    const sel = h => /<option value="([^"]*)" selected>([^<]*)</.exec(h) || /<option value="([^"]*)">([^<]*)</.exec(h);
    const v = caixas.map(h => { const m = sel(h); return m && m[1] && !/^__/.test(m[1]) ? m[2] : ''; }).filter(Boolean);
    // sem nada escolhido, o que vale na primeira caixa («Filmes, séries e jogos», «Todas as situações»)
    const m0 = caixas.length ? sel(caixas[0]) : null;
    const t = v.length ? v.join(', ') : m0 ? m0[2] : '';
    return t ? `<span class="filtros-val"> · ${t}</span>` : '';
  }
  function telaBuscar() {
    const b = S.busca, e = S.e, tipos = ligados(), aberto = guardada('odisseia-filtros') !== 'fechado';
    const caixa = (id, ic_, rot, opcoes, atual) => `<select class="inp select" id="${id}" data-ic="${ic_}" aria-label="${rot}">${opcoes}</select>`;
    const opt = (v, n, atual) => `<option value="${esc(v)}"${v === atual ? ' selected' : ''}>${esc(n)}</option>`;
    // 0.5.0 (o dono: "só deve habilitar o filtro de categorias se eu selecionar só filmes, séries ou jogos"): as categorias
    // são de cada tipo; com todos os tipos, a caixa fica inativa
    const tipoUm = tipos.length === 1 ? tipos[0] : tipos.includes(b.tipo) ? b.tipo : '';
    const cats = tipoUm ? e.categorias[tipoUm] || [] : [];
    const sel = [];
    const todos = tipos.map((k, i) => i ? NOMES[k].toLowerCase() : NOMES[k]), tipo = tipos.includes(b.tipo) ? b.tipo : '';
    if (tipos.length > 1) sel.push(caixa('f-tipo', 'film', 'Tipo', opt('', todos.slice(0, -1).join(', ') + ' e ' + todos[todos.length - 1], b.tipo) + tipos.map(k => opt(k, NOMES[k], b.tipo)).join('')));
    const um = tipo || (tipos.length === 1 ? tipos[0] : ''), comJogo = !um && tipos.includes('jogo'), comLivro = !um && tipos.includes('livro');
    const soJogo = um === 'jogo', soLivro = um === 'livro';
    sel.push(caixa('f-sit', 'layers', 'Situação', opt('', 'Todas as situações', b.situacao) + opt('quero', soLivro ? 'Quero ler' : soJogo ? 'Quero jogar' : comLivro ? 'Quero' : comJogo ? 'Quero ver ou jogar' : 'Quero ver', b.situacao)
      + opt('visto', soLivro ? 'Lidos' : soJogo ? 'Jogados' : comLivro ? 'Concluídos' : comJogo ? 'Vistos e jogados' : 'Vistos', b.situacao)));
    // 0.4.0 (o dono: "filtro por categoria aqui"): a caixa está sempre; sem nenhuma categoria, leva a criar
    sel.push(tipoUm ? caixa('f-cat', 'tag', 'Categoria', opt('', 'Todas as categorias', b.categoria) + cats.map(c => opt(c.id, c.nome, b.categoria)).join('')
      + opt('sem', 'Sem categoria', b.categoria) + (cats.length ? '' : opt('__criar', 'Criar categorias…', '')))
      : `<select class="inp select" id="f-cat" data-ic="tag" aria-label="Categoria: escolha o tipo antes" disabled><option>Categoria</option></select>`);
    if (e.ajustes.quem && e.pessoas.length > 1) sel.push(caixa('f-quem', 'users', 'Quem', opt('', 'Todas as pessoas', b.quem) + e.pessoas.map(p => opt(p.id, p.nome.split(' ')[0], b.quem)).join('')));
    const ts = filtrados();
    let h = topo('Buscar') + `<section class="sbar"><label class="busca">${ic('search')}<input id="b-texto" type="search" placeholder="${oQue()}" value="${esc(b.texto)}" enterkeyhint="search" autocomplete="off">${b.texto ? `<button class="limpar" data-a="b-limpar" aria-label="Limpar">${ic('x', 'ic-s')}</button>` : ''}</label>
      <button class="filtros-h" data-a="filtros" aria-expanded="${aberto}">${ic('sliders', 'ic-s')}<span>Filtros${aberto ? '' : filtrosVal(sel)}</span>${ic('chev', 'ic-s seta')}</button>
      <div class="sfiltros n${sel.length}"${aberto ? '' : ' hidden'}>${sel.join('')}</div>${ts.length ? agruparBloco() : ''}</section>`;
    const corpo = ts.length ? listaSel(ts, { mais1: true }) : `<p class="vazio">${e.titulos.length ? 'Nenhum título com esses filtros.' : 'A lista está vazia.'}</p>`;
    return h + card('resultado', 'list', `Títulos <span class="cont">${ts.length}</span>`, corpo, 'Títulos');
  }

  /* ---------- Vistos: o que está salvo como visto (jogado), numa aba para cada tipo (0.4.0, o dono: "não precisa ser
     histórico essa aba, pode ser aqui o que está salvo como visto"), com o filtro da categoria; o mais recente primeiro */
  const VISTOS = [['serie', 'Séries', 'tv', 'Séries vistas', 'Nenhuma série vista'], ['filme', 'Filmes', 'film', 'Filmes vistos', 'Nenhum filme visto'], ['jogo', 'Jogos', 'gamepad', 'Jogos jogados', 'Nenhum jogo jogado'], ['livro', 'Livros', 'book-open', 'Livros lidos', 'Nenhum livro lido']];
  function telaVistos() {
    const abas = VISTOS.filter(([k]) => ligados().includes(k));
    const [aba, , icone, titulo, vazio] = abas.find(([k]) => k === S.hist) || abas[0];
    const cats = S.e.categorias[aba] || [], todos = S.e.titulos.filter(t => t.situacao === 'visto' && t.tipo === aba);
    const semCat = todos.some(t => !catDe(t)), fc = S.vcat[aba] || '';
    const f = fc === 'sem' ? (semCat ? 'sem' : '') : cats.some(c => c.id === fc) ? fc : '';
    const ts = todos.filter(t => !f || (f === 'sem' ? !catDe(t) : t.categoria === f))
      .sort((a, b) => String(b.visto_em || '').localeCompare(String(a.visto_em || '')) || a.nome.localeCompare(b.nome, 'pt-BR'));
    let h = topo('Concluídos') + (abas.length < 2 ? '' : `<div class="abas" role="tablist">${abas.map(([k, n, i]) => `<button role="tab" aria-selected="${aba === k}" class="${aba === k ? 'on' : ''}" data-a="hist" data-v="${k}">${ic(i, 'ic-s')}${n}</button>`).join('')}</div>`);
    if (!todos.length) return h + card('nada-visto', icone, vazio, `<p class="lead">O que a casa ${aba === 'jogo' ? 'jogou' : aba === 'livro' ? 'leu' : 'viu'} aparece aqui.</p>`, 'nada-visto');
    const chip = (v, nome, icone_) => `<button class="chip${f === v ? ' on' : ''}" data-a="v-cat" data-v="${v}" aria-pressed="${f === v}">${icone_}${esc(nome)}</button>`;
    const chipCat = c => `<button class="chip cor${f === c.id ? ' on' : ''}" style="${estiloCor(c.cor)}" data-a="v-cat" data-v="${c.id}" aria-pressed="${f === c.id}"><span class="dot"></span>${esc(c.nome)}</button>`;
    // 0.12.0 (PADROES.md, "O alto das listas"): a categoria dentro do Filtros, que fecha (o aparelho lembra; fechado, a escolhida
    // ao lado), e o Agrupar por logo embaixo
    const vf = guardada('odisseia-vistos-filtros') === 'fechado';
    const fNome = f === 'sem' ? 'Sem categoria' : f ? (cats.find(c => c.id === f) || {}).nome : 'Todas';
    h += `<section class="sbar"><button class="filtros-h" id="vistos-filtros" data-a="vistos-filtros" aria-expanded="${!vf}">${ic('sliders', 'ic-s')}<span>Filtros${vf ? `<span class="filtros-val"> · ${esc(fNome)}</span>` : ''}</span>${ic('chev', 'ic-s seta')}</button>
      <div class="chips filtro-cat" role="group" aria-label="Categoria"${vf ? ' hidden' : ''}>${chip('', 'Todas', ic('layers', 'ic-s'))}${cats.map(chipCat).join('')}${cats.length && semCat ? chip('sem', 'Sem categoria', ic('x', 'ic-s')) : ''}
      ${cats.length ? '' : `<button class="chip" data-a="ir-categorias">${ic('plus', 'ic-s')}Criar categorias</button>`}</div>${ts.length ? agruparBloco() : ''}</section>`;
    return h + card('vistos', icone, `${titulo} <span class="cont">${ts.length}</span>`, ts.length ? listaSel(ts) : '<p class="vazio">Nenhum com essa categoria.</p>', 'vistos-' + aba);
  }

  /* ---------- Mais, Configurações e Sobre */
  function telaMais() {
    const linha = (a, icone, titulo, txt) => `<button class="linha" data-a="${a}"><span class="rot-ic">${ic(icone)}</span><span class="linha-t"><b>${titulo}</b><small>${txt}</small></span>${ic('chev', 'ic-s chev')}</button>`;
    return topo('Mais') + `<section class="card linha-card">${linha('ir-categorias', 'tag', 'Categorias', 'As categorias de cada tipo.')}${linha('ir-config', 'gear', 'Configurações', 'Integrações, dados, aparência e opções.')}${linha('sobre', 'info', 'Sobre', 'CorrerIA Code, os apps e o GitHub.')}</section>`;
  }
  // 0.3.0 (o dono: "tirar a opção de nota e colocar um campo de categoria... vou poder definir categorias para filme, outra
  // para séries e outra para jogos"); 0.4.0 (o dono: "colocar cor, fazer no mesmo padrão dos outros apps"): uma lista por
  // tipo ligado, como no MemorIA: cada categoria com o ícone na cor dela; o toque abre o nome e a cor
  const EXEMPLO_CAT = { filme: 'Ex.: Para ver em família', serie: 'Ex.: Para ver a dois', jogo: 'Ex.: Para jogar junto', livro: 'Ex.: Para ler nas férias' };
  function telaCategorias() {
    let h = topo('Categorias', 'Mais');
    for (const [k, nome, icone] of [['serie', 'Séries', 'tv'], ['filme', 'Filmes', 'film'], ['jogo', 'Jogos', 'gamepad'], ['livro', 'Livros', 'book-open']].filter(([k]) => ligados().includes(k))) {
      const cs = S.e.categorias[k] || [];
      const linhas = cs.map(c => {
        const n = S.e.titulos.filter(t => t.tipo === k && t.categoria === c.id).length;
        return `<button class="linha cat-linha" data-a="cat-abrir" data-k="${k}" data-id="${c.id}"><span class="rot-ic cat-tile" style="${estiloCor(c.cor)}">${ic('tag')}</span>
          <span class="linha-t"><b>${esc(c.nome)}</b><small>${n ? plural(n, 'título', 'títulos') : 'Nenhum título'}</small></span>${ic('chev', 'ic-s chev')}</button>`;
      }).join('');
      h += card('cat-' + k, icone, `${nome} <span class="cont">${cs.length}</span>`, `<div class="cats-lista">${linhas}
        <button class="linha cat-linha nova" data-a="cat-abrir" data-k="${k}"><span class="rot-ic">${ic('plus')}</span><span class="linha-t"><b>Nova categoria</b></span></button></div>`, 'Categorias de ' + nome);
    }
    return h;
  }
  function folhaCategoria(f) {
    const c = f.id ? (S.e.categorias[f.k] || []).find(x => x.id === f.id) : null, F = S.catf;
    const n = c ? S.e.titulos.filter(t => t.categoria === c.id).length : 0;
    const corpo = `<div class="campo">${lbl('nota', 'Nome', 'cat-nome')}<textarea class="inp umalinha" rows="1" id="cat-nome" maxlength="40" placeholder="${EXEMPLO_CAT[f.k]}" enterkeyhint="done">${esc(F.nome)}</textarea></div>
      <div class="campo">${lbl('palette', 'Cor')}<div class="cores" role="radiogroup" aria-label="Cor da categoria">${PALETA.map(x => `<button class="tsw${x.id === F.cor ? ' on' : ''}" role="radio" aria-checked="${x.id === F.cor}" style="--a:${x.fill}" data-a="cat-cor" data-v="${x.id}">
        <svg viewBox="-5 -5 40 30" aria-hidden="true"><path class="sw-ring" d="${TAG}"/><path class="sw-gap" d="${TAG}"/><path class="sw-fill" d="${TAG + FURO}"/><path class="sw-check" d="m14.6 10.3 3.2 3.2 6.5-6.9"/></svg><span>${x.nome}</span></button>`).join('')}</div></div>`;
    const pe = c && S.conf === 'cat:' + c.id ? `<p class="conf">Apagar «${esc(c.nome)}»?${n ? ` ${n === 1 ? 'O título dela fica' : `Os ${n} títulos dela ficam`} sem categoria.` : ''}</p><button class="btn out" data-a="conf-nao">${ic('x', 'ic-s')}Cancelar</button><button class="btn perigo" data-a="cat-apagar" data-id="${c.id}">${ic('trash', 'ic-s')}Apagar</button>`
      : c ? `<button class="btn out" data-a="conf" data-v="cat:${c.id}">${ic('trash', 'ic-s')}Apagar</button><button class="btn pri" data-a="cat-salvar">${ic('check', 'ic-s')}Salvar</button>`
        : `<button class="btn out" data-a="fechar">${ic('x', 'ic-s')}Cancelar</button><button class="btn pri" data-a="cat-salvar">${ic('plus', 'ic-s')}Criar categoria</button>`;
    return { titulo: c ? 'Categoria' : 'Nova categoria', icone: 'tag', corpo, pe };
  }
  // Alterar N títulos (o Selecionar): cada campo começa em Manter, como no InventarIA e no ResolvIA
  const MANTER = '__manter__';
  function folhaLote() {
    const ts = S.e.titulos.filter(t => S.sel && S.sel.has(t.id)), L = S.lote, e = S.e;
    if (!ts.length || !L) return null;
    const cats = e.categorias[ts[0].tipo] || [];
    const esc_ = (a, v, nome, icone, on) => `<button class="escolha${on ? ' on' : ''}" data-a="${a}" data-v="${esc(v)}">${on ? ic('check', 'ic-s') : icone}${esc(nome)}</button>`;
    let h = `<div class="campo">${lbl('tag', 'Categoria')}<div class="escolhas">${esc_('lote-cat', MANTER, 'Manter', ic('igual', 'ic-s'), L.cat === MANTER)}
      ${cats.map(c => pickCat('lote-cat', c, L.cat === c.id)).join('')}${esc_('lote-cat', '', 'Sem categoria', ic('x', 'ic-s'), L.cat === '')}</div></div>`;
    if (e.ajustes.quem && e.pessoas.length) {
      const q = L.quem, todos = q && e.pessoas.every(p => q.includes(p.id));
      h += `<div class="campo">${lbl('users', 'Quem')}<div class="escolhas">${esc_('lote-quem', MANTER, 'Manter', ic('igual', 'ic-s'), !q)}${esc_('lote-quem', '__ninguem__', 'Ninguém', ic('x', 'ic-s'), !!q && !q.length)}
        ${e.pessoas.length > 1 ? esc_('lote-quem', '__todos__', 'Todos', ic('users', 'ic-s'), todos) : ''}${e.pessoas.map(p => esc_('lote-quem', p.id, p.nome.split(' ')[0], ic('user', 'ic-s'), !!q && q.includes(p.id))).join('')}</div></div>`;
    }
    const muda = L.cat !== MANTER || L.quem;
    const pe = `<button class="btn out" data-a="fechar">${ic('x', 'ic-s')}Cancelar</button><button class="btn pri" data-a="lote-aplicar"${muda ? '' : ' disabled'}>${ic('check', 'ic-s')}Aplicar</button>`;
    return { titulo: 'Alterar ' + plural(ts.length, 'título', 'títulos'), icone: 'nota', corpo: h, pe };
  }
  async function categorias(corpo) {
    try { const r = await api.post('categorias', corpo); S.e.categorias = r.categorias; S.e.rev = r.rev; S.conf = ''; render(); return true; } catch (err) { toast(err.message); return false; }
  }
  function cardTMDB() {
    const t = S.e.tmdb, mostrar = !t.chave || S.trocarChave;
    return card('tmdb', 'film', 'Filmes e séries (TMDB)', `<p class="lead">De onde vêm os filmes, as séries, as capas e onde assistir. A conta do ${site('https://www.themoviedb.org/signup', 'TMDB')} é grátis; a chave fica em ${site('https://www.themoviedb.org/settings/api', 'Configurações › API')} (uso pessoal).</p>
      <p class="credito">Este app usa a API do TMDB, mas não é endossado nem certificado pelo TMDB. Onde assistir: dados da ${site('https://www.justwatch.com/br', 'JustWatch')}.</p>
      ${t.chave ? `<p class="status${t.erro ? ' erro' : ''}">${t.erro ? esc(t.erro) : `Chave ${esc(t.fim)} · funcionando`}</p>` : ''}
      ${mostrar ? `<div class="campo">${lbl('key', 'Chave da API ou token de leitura', 'f-chave')}<input class="inp" id="f-chave" type="password" autocomplete="off" spellcheck="false" placeholder="Cole aqui"></div>
        <div class="acoes${t.chave ? ' dois' : ''}">${t.chave ? `<button class="btn out" data-a="chave-cancelar">${ic('x', 'ic-s')}Cancelar</button>` : ''}<button class="btn pri" data-a="chave-salvar">${ic('check', 'ic-s')}Salvar e testar</button></div>`
        : `<div class="acoes dois"><button class="btn out" data-a="chave-apagar">${ic('trash', 'ic-s')}Apagar</button><button class="btn pri" data-a="chave-trocar">${ic('key', 'ic-s')}Trocar</button></div>`}`);
  }
  // 0.4.0: os jogos vêm do IGDB (da Twitch), com o Client ID e o Client Secret de um app grátis no Twitch Developers
  function cardIGDB() {
    const t = S.e.igdb, mostrar = !t.chave || S.trocarIGDB;
    return card('igdb', 'gamepad', 'Jogos (IGDB)', `<p class="lead">De onde vêm os jogos e as capas deles. Crie um app grátis no ${site('https://dev.twitch.tv/console/apps/create', 'Twitch Developers')} (a conta da Twitch precisa da verificação em duas etapas), com o endereço <code>http://localhost</code> e a categoria Application Integration, e cole aqui o Client ID e um Client Secret novo.</p>
      ${t.chave ? `<p class="status${t.erro ? ' erro' : ''}">${t.erro ? esc(t.erro) : `Client ID ${esc(t.fim)} · funcionando`}</p>` : ''}
      ${mostrar ? `<div class="campo">${lbl('key', 'Client ID', 'f-igdb-id')}<input class="inp" id="f-igdb-id" type="text" autocomplete="off" spellcheck="false" autocapitalize="off" placeholder="Cole aqui"></div>
        <div class="campo">${lbl('key', 'Client Secret', 'f-igdb-segredo')}<input class="inp" id="f-igdb-segredo" type="password" autocomplete="off" spellcheck="false" placeholder="Cole aqui"></div>
        <div class="acoes${t.chave ? ' dois' : ''}">${t.chave ? `<button class="btn out" data-a="igdb-cancelar">${ic('x', 'ic-s')}Cancelar</button>` : ''}<button class="btn pri" data-a="igdb-salvar">${ic('check', 'ic-s')}Salvar e testar</button></div>`
        : `<div class="acoes dois"><button class="btn out" data-a="igdb-apagar">${ic('trash', 'ic-s')}Apagar</button><button class="btn pri" data-a="igdb-trocar">${ic('key', 'ic-s')}Trocar</button></div>`}`);
  }
  function cardCorrerIA() {
    const c = S.e.correria, u = c.ultimo;
    return card('correria', 'chat', 'CorrerIA', `<div class="linha-sw"><div><b>${ic('zap', 'ic-s')}Usar pelo CorrerIA</b><span>Pergunte e marque o que viu pelo WhatsApp, pelo Claude ou pelo Gemini, com o CorrerIA.</span></div>
      <button class="sw${c.ligado ? ' on' : ''}" data-a="aj" data-k="correria" role="switch" aria-checked="${c.ligado}" aria-label="Usar pelo CorrerIA"></button></div>
      ${c.ligado && u ? `<p class="lead" style="margin:12px 0 0">Último uso: ${esc(u.app)}, ${esc(dia(u.em.slice(0, 10)))} às ${esc(u.em.slice(11, 16))}.</p>` : ''}`);
  }
  // 0.9.0 (o dono: "no OdisseIA criar também sensores do Home Assistant"): o cartão dos outros apps
  function cardSensores() {
    const on = !!S.e.ajustes.sensores, l = ligados();
    const lista = [
      ['sensor.odisseia_quero_ver', 'quantos em Quero ver, por tipo'],
      l.includes('serie') && ['sensor.odisseia_em_andamento', 'as séries em andamento e onde cada uma parou'],
      l.includes('serie') && ['sensor.odisseia_proximo_episodio', 'a data do próximo episódio, com a série'],
      l.includes('jogo') && ['sensor.odisseia_proximo_jogo', 'a data do próximo jogo que vai sair'],
      ['sensor.odisseia_concluidos_no_mes', 'quantos foram vistos ou jogados neste mês'],
    ].filter(Boolean);
    return card('sensores', 'gauge', 'Sensores no Home Assistant', `<p class="lead">Para usar em painéis e automações do Home Assistant.</p>
      <div class="linha-sw"><div><b>${ic('gauge', 'ic-s')}Criar sensores</b><span>${on ? 'Ligado.' : 'Desligado: nenhum sensor no Home Assistant.'}</span></div>
        <button class="sw${on ? ' on' : ''}" data-a="aj" data-k="sensores" role="switch" aria-checked="${on}" aria-label="Criar sensores"></button></div>
      ${on ? `<div class="sub-box sensor-list">${lista.map(([id, o]) => `<div class="sensor-row"><code>${id}</code><span>${o}</span></div>`).join('')}</div>` : ''}`);
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
    return card('exportar', 'baixar', 'Exportar', `<p class="lead">Um arquivo com a lista e as capas. As chaves do TMDB e do IGDB não vão junto.</p>
        <div class="acoes"><a class="btn" href="api/dados/exportar" download>${ic('baixar', 'ic-s')}Baixar</a></div>`)
      + card('backup', 'arquivo', 'Backup na pasta share', `<p class="lead">Em <code>share/odisseia/backups</code>, os 10 últimos.</p>
        <div class="acoes"><button class="btn" data-a="backup">${ic('arquivo', 'ic-s')}Fazer backup agora</button></div>${d.backups.length ? zips('backup', d.backups) : ''}`)
      + card('importar', 'subir', 'Importar', `<p class="lead">O arquivo de um Exportar ou de um backup. Troca tudo o que há agora.</p>
        ${S.importar ? confirma(`Trocar tudo pelo arquivo ${S.importar.nome}?`, 'importar', 'subir', 'Importar') : `<div class="acoes"><button class="btn" data-a="escolher">${ic('subir', 'ic-s')}Escolher arquivo</button></div>`}`)
      + (d.versoes.length ? card('versoes', 'clock', `Versões anteriores (${d.versoes.length})`, zips('versao', d.versoes), 'Versões anteriores') : '')
      + card('onde', 'database', 'Onde ficam os dados', '<p class="lead">Na pasta <code>/data</code> do app, que entra no backup do Home Assistant: <code>odisseia.json</code> (a lista), <code>capas</code>, <code>segredos.json</code> (as chaves do TMDB e do IGDB), <code>conversa.json</code> (a Conversa) e <code>uso_ia.json</code> (o Uso da IA). A Memória da IA, de todos os apps, fica em <code>share/familia</code>.</p>')
      + card('zerar', 'trash', 'Começar do zero', `<p class="lead">Apaga a lista e as capas. As chaves e as configurações ficam.</p>
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
      ${tipo('serie', 'tv', 'Séries', 'O episódio em que cada um parou e os que vão sair.')}${tipo('filme', 'film', 'Filmes', 'Os filmes e as coleções (as sagas).')}${tipo('jogo', 'gamepad', 'Jogos', 'Os jogos e as coleções, pelo IGDB.')}${tipo('livro', 'book-open', 'Livros', 'Os livros, pelo nome ou pelo código de barras.')}`) + card('quem-ve', 'users', 'Quem vê', `<div class="linha-sw"><div><b>${ic('users', 'ic-s')}Marcar quem vê</b><span>Cada título diz quem da casa está vendo ou já viu.</span></div>
      <button class="sw${a.quem ? ' on' : ''}" data-a="aj" data-k="quem" role="switch" aria-checked="${a.quem}" aria-label="Marcar quem vê"></button></div>`);
  }
  function telaConfig() {
    const abas = `<div class="abas" role="tablist">${ABAS.map(([k, n, i]) => `<button role="tab" aria-selected="${S.aba === k}" class="${S.aba === k ? 'on' : ''}" data-a="aba" data-v="${k}">${ic(i, 'ic-s')}${n}</button>`).join('')}</div>`;
    const l = ligados();
    const corpo = S.aba === 'dados' ? abaDados() : S.aba === 'aparencia' ? abaAparencia() : S.aba === 'opcoes' ? abaOpcoes()
      : (l.some(ehTV) ? cardTMDB() : '') + (l.includes('jogo') ? cardIGDB() : '') + cardCorrerIA() + cardIA()
        + (S.e.ajustes.ia ? cardMemoria() + cardFalar() + cardUso() : '') + cardSensores();
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
    ['OdisseIA', 'OdisseIA', 'play', 'Os filmes, as séries e os jogos da casa.'],
    ['CorrerIA', 'CorrerIA-ha', 'chat', 'Pergunte e peça a qualquer app, no chat ou no WhatsApp.'],
  ];
  const marcaNome = n => `<span class="sb-wm">${n.slice(0, -2)}<span>${n.slice(-2)}</span></span>`;
  function telaSobre() {
    return topo('Sobre', 'Mais') + `<div class="sobre-topo"><span class="sb-raio" aria-hidden="true">${ic('zap')}</span>
        <h2 class="sb-nome">Correr<span>IA</span> Code</h2><p class="sb-oque">desenvolvimento de softwares</p><p class="sb-lema">Feito na correria, rodado pela IA.</p></div>
      ${card('porque', 'hourglass', 'Por que CorrerIA?', '<p class="sb-txt">Porque eu sou um programador sem tempo: vivo na correria. Então eu uso a IA para rodar tudo isso aqui. Ela escreve, testa e publica; eu dou as ideias e reclamo dos botões tortos.</p>')}
      ${card('apps', 'layers', 'Os apps', `<ul class="sb-apps" aria-label="Os apps">${PRODUTOS.map(([n, repo, i, txt]) => `<li><a class="sb-app" href="${GITHUB}/${repo}" target="_blank" rel="noopener">
        <span class="rot-ic" aria-hidden="true">${ic(i)}</span><span class="mb"><b>${marcaNome(n)}${repo === 'OdisseIA' ? `<em class="sb-aqui">Este app · v${esc(S.e.versao)}</em>` : ''}</b><span>${txt}</span></span>${ic('external-link', 'sb-ext')}</a></li>`).join('')}</ul>`)}
      <a class="btn pri sb-github" href="${GITHUB}" target="_blank" rel="noopener">${ic('external-link', 'ic-s')}Meu GitHub</a>`;
  }

  /* ---------- as janelas: Adicionar e o título aberto */
  // 0.2.0 (o dono: "pensa num processo bem legal para ficar bonito e prático"): o Adicionar abre nas listas prontas do
  // TMDB (Em alta, Mais populares, Mais bem avaliados, Estreias) e mostra as capas em grade; em cada capa, Quero ver (o
  // marcador) e Já vi (o visto, que numa série marca até o último episódio que saiu), sem sair da janela. Tocar na capa
  // abre o título (e, fora da lista, põe como Quero ver); uma coleção abre os filmes dela.
  const LISTAS = [['alta', 'Em alta', 'zap'], ['populares', 'Mais populares', 'users'], ['avaliados', 'Mais bem avaliados', 'star'], ['colecoes', 'Coleções', 'layers'], ['estreias', 'Estreias', 'calendar']];
  const LISTAS_JOGO = { populares: 'Mais jogados', estreias: 'Lançamentos' };
  // as Coleções com os filmes (fora de Séries e de Jogos) ou com os jogos (em Tudo e em Jogos)
  const listas = () => {
    const t = S.add.tipo, l = ligados();
    return LISTAS.filter(([k]) => k !== 'colecoes' || (l.includes('filme') && (t === '' || t === 'filme')) || (l.includes('jogo') && (t === '' || t === 'jogo')))
      .map(([k, n, i]) => [k, t === 'jogo' && LISTAS_JOGO[k] || n, i]);
  };
  function cartaz(r, i, o) {
    // o que ainda não saiu (um filme da coleção, uma estreia futura) não tem o Já vi
    const col = r.tipo === 'colecao' || r.tipo === 'colecao_jogos', sit = r.situacao && [sitN(r.tipo, r.situacao), SIT[r.situacao][1]], saiu = r.saiu !== false && !(r.data && r.data > hojeISO());
    const jg = ehJogo(r), lv = r.tipo === 'livro', quer = lv ? 'Quero ler' : jg ? 'Quero jogar' : 'Quero ver', vi = lv ? 'Já li' : jg ? 'Já joguei' : 'Já vi';
    const img = r.capa ? `<img src="api/img/${lv ? `ol_M/${esc(r.capa)}.jpg` : jg ? `t_cover_big/${esc(r.capa)}.jpg` : 'w185' + esc(r.capa)}" alt="" loading="lazy">` : `<span class="cz-sem">${ic(TIPO[r.tipo][1])}</span>`;
    const meta = [r.ano, col ? 'Coleção' : lv && (r.autores || []).length ? r.autores[0] : TIPO[r.tipo][0], saiu ? '' : (r.data ? 'sai em ' + new Date(r.data + 'T12:00:00').toLocaleDateString('pt-BR') : 'sem data')].filter(Boolean).join(' · ');
    return `<li class="cz${r.situacao === 'visto' ? ' feito' : ''}"><div class="cz-quadro"><button class="cz-capa" data-a="cz-abrir" data-o="${o}" data-i="${i}" aria-label="${esc(r.nome)}">${img}
        ${sit ? `<span class="cz-sit">${ic(sit[1], 'ic-s')}${sit[0]}</span>` : col ? `<span class="cz-sit">${ic('layers', 'ic-s')}Coleção</span>` : ''}</button>
      ${col ? `<span class="cz-acoes">${r.situacao ? '' : `<button class="cz-bt" data-a="cz-col-todos" data-v="quero" data-o="${o}" data-i="${i}" aria-label="${quer} todos de ${esc(r.nome)}">${ic('bookmark', 'ic-s')}</button>`}
        ${r.situacao === 'visto' ? '' : `<button class="cz-bt vi" data-a="cz-col-todos" data-v="visto" data-o="${o}" data-i="${i}" aria-label="${vi} todos de ${esc(r.nome)}">${ic('check', 'ic-s')}</button>`}</span>`
      : `<span class="cz-acoes">${r.ja ? '' : `<button class="cz-bt" data-a="cz-quero" data-o="${o}" data-i="${i}" aria-label="${quer} ${esc(r.nome)}">${ic('bookmark', 'ic-s')}</button>`}
        ${r.situacao === 'visto' || !saiu ? '' : `<button class="cz-bt vi" data-a="cz-visto" data-o="${o}" data-i="${i}" aria-label="${vi} ${esc(r.nome)}">${ic('check', 'ic-s')}</button>`}</span>`}</div>
      <b class="cz-nome">${esc(r.nome)}</b><small>${esc(meta)}</small>
      ${(r.tipo === 'filme' || r.tipo === 'jogo') && r.colecao && o !== 'col' ? `<button class="cz-col" data-a="cz-colecao" data-id="${r.colecao.id}"${jg ? ' data-j="1"' : ''}>${ic('layers', 'ic-s')}Coleção</button>` : ''}
      ${o === 'col' && r.ja && S.e.titulos.some(t => t.id === r.ja) ? tagCatToque(catDe(S.e.titulos.find(t => t.id === r.ja)), r.ja) : ''}</li>`;
  }
  const grade = (rs, o) => `<ul class="cartazes">${rs.map((r, i) => cartaz(r, i, o)).join('')}</ul>`;
  function folhaAdicionar() {
    const a = S.add, l = ligados();
    if (a.tipo && !l.includes(a.tipo)) a.tipo = '';
    const semChave = !temFonte(a.tipo), busca = a.q.trim().length >= 2;
    const seg = l.length > 1 ? `<div class="seg n${l.length + 1}">${[['', 'Tudo'], ...l.map(k => [k, NOMES[k]])].map(([v, n]) => `<button class="${a.tipo === v ? 'on' : ''}" data-a="add-tipo" data-v="${v}">${n}</button>`).join('')}</div>` : '';
    let res = '';
    const faltaJogo = a.tipo === 'jogo' || (!a.tipo && !l.some(ehTV));
    const soLivro = a.tipo === 'livro' || (l.length === 1 && l[0] === 'livro');
    if (semChave) res = `<p class="lead" style="margin-top:14px">${faltaJogo ? 'Falta a conta do IGDB.' : 'Falta a chave do TMDB.'}</p><div class="acoes"><button class="btn pri" data-a="ir-config" data-v="integracoes">${ic('key', 'ic-s')}${faltaJogo ? 'Pôr a conta' : 'Pôr a chave'}</button></div>`;
    else if (busca) {
      if (a.erro) res = `<p class="status erro" style="margin-top:14px">${esc(a.erro)}</p>`;
      else if (!a.res) res = '<p class="vazio" style="margin-top:14px">Procurando…</p>';
      else if (!a.res.length) res = `<p class="vazio" style="margin-top:14px">Nada com esse nome${soLivro ? ' na Open Library' : a.tipo === 'jogo' ? ' no IGDB' : a.tipo ? ' no TMDB' : ''}.</p>`;
      else res = grade(a.res, 'busca');
    } else if (soLivro) {
      // os livros não têm listas prontas: o nome, o autor ou o código de barras (o ISBN)
      res = `<div class="acoes" style="margin-top:14px"><button class="btn pri" data-a="add-codigo">${ic('camera', 'ic-s')}Ler código de barras</button></div>
        <p class="credito">Dados da ${site('https://openlibrary.org', 'Open Library')}.</p>`;
    } else {
      const L = a.listas[a.lista + ':' + a.tipo];
      if (!listas().some(([k]) => k === a.lista)) a.lista = 'alta';
      res = `<div class="chips" role="tablist" aria-label="Listas prontas">${listas().map(([k, n, i]) => `<button class="chip${a.lista === k ? ' on' : ''}" role="tab" aria-selected="${a.lista === k}" data-a="add-lista" data-v="${k}">${ic(i, 'ic-s')}${n}</button>`).join('')}</div>`;
      if (!L || (!L.itens.length && L.carregando)) res += '<p class="vazio" style="margin-top:14px">Abrindo…</p>';
      else if (L.erro && !L.itens.length) res += `<p class="status erro" style="margin-top:14px">${esc(L.erro)}</p>`;
      else res += grade(L.itens, 'lista') + (L.mais ? `<div class="acoes" style="margin-top:16px"><button class="btn out" data-a="add-mais"${L.carregando ? ' disabled' : ''}>${ic('plus', 'ic-s')}Mostrar mais</button></div>` : '');
      if (!L) carregarLista();
    }
    return { titulo: 'Adicionar', icone: 'plus', alta: true, corpo: `<label class="busca" style="margin-bottom:12px">${ic('search')}<input id="add-q" type="search" placeholder="${oQue(a.tipo)}" value="${esc(a.q)}" enterkeyhint="search" autocomplete="off"${semChave ? ' disabled' : ''}>${a.q ? `<button class="limpar" data-a="add-limpar" aria-label="Limpar">${ic('x', 'ic-s')}</button>` : ''}</label>
      ${seg}${res}` };
  }
  // Sem categoria, as da casa e a Nova (o nome aparece embaixo; a categoria nasce com uma cor livre), como no MemorIA
  function campoCategoria(t) {
    const cats = S.e.categorias[t.tipo] || [], semC = !(t.categoria && cats.some(c => c.id === t.categoria));
    return `<div class="campo">${lbl('tag', 'Categoria')}<div class="escolhas"><button class="escolha${semC && S.novaCat == null ? ' on' : ''}" data-a="cat" data-v="">${ic('x', 'ic-s')}Sem categoria</button>
      ${cats.map(c => pickCat('cat', c, t.categoria === c.id && S.novaCat == null)).join('')}<button class="escolha${S.novaCat != null ? ' on' : ''}" data-a="cat-nova-t">${ic('plus', 'ic-s')}Nova</button></div>
      ${S.novaCat != null ? `<div class="nova-cat"><textarea class="inp umalinha" rows="1" id="cat-nova-t" maxlength="40" placeholder="Nome da nova categoria" aria-label="Nome da nova categoria" enterkeyhint="done">${esc(S.novaCat)}</textarea>
        <button class="btn pri" data-a="cat-nova-criar">${ic('check', 'ic-s')}Criar</button></div>` : ''}</div>`;
  }
  // 0.5.0 (o dono: "colocar a categoria em cada linha ali"): o toque na categoria de uma linha (ou no Sem categoria) abre só a
  // escolha dela; escolhida, a janela fecha
  function folhaCatTitulo(t) {
    return { titulo: t.nome, icone: 'tag', corpo: campoCategoria(t) };
  }
  function folhaTitulo(t) {
    const e = S.e, pode = podeProximo(t);
    const jg = t.tipo === 'jogo', lv = t.tipo === 'livro';
    const info = [t.ano, TIPO[t.tipo][0], lv && t.paginas ? plural(t.paginas, 'página', 'páginas') : t.tipo === 'filme' ? duracao(t.duracao) : t.tipo === 'serie' ? (t.temporadas.length ? plural(t.temporadas.length, 'temporada', 'temporadas') : '') : '',
      t.tipo === 'serie' && t.fim ? 'terminou' : '', jg && t.data && t.data > hojeISO() ? 'sai ' + saiEm(t.data) : ''].filter(Boolean).join(' · ');
    let h = `<div class="topo-tit">${capa(t, true)}<div class="info">${t.original && t.original !== t.nome ? `<span class="orig">${esc(t.original)}</span>` : ''}<span class="meta">${esc(info)}</span>
      ${t.generos.length ? `<span class="gens">${t.generos.map(g => `<span class="tag">${esc(g)}</span>`).join('')}</span>` : ''}</div></div>`;
    h += `<div class="campo">${lbl('layers', 'Situação')}<div class="escolhas">${Object.entries(SIT).map(([k, [, i]]) => `<button class="escolha${t.situacao === k ? ' on' : ''}" data-a="sit" data-v="${k}">${ic(i, 'ic-s')}${sitN(t.tipo, k)}</button>`).join('')}</div></div>`;
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
    if ((t.tipo === 'filme' || jg) && t.colecao) {
      h += `<div class="campo">${lbl('layers', 'Coleção')}<div class="acoes"><button class="btn out" data-a="abrir-colecao" data-id="${t.colecao.id}"${jg ? ' data-j="1"' : ''}>${ic('layers', 'ic-s')}${esc(t.colecao.nome)}</button></div></div>`;
    }
    h += campoCategoria(t);
    if (e.ajustes.quem && e.pessoas.length) {
      const todos = e.pessoas.every(p => t.quem.includes(p.id));
      h += `<div class="campo">${lbl('users', 'Quem')}<div class="escolhas">${e.pessoas.length > 1 ? `<button class="escolha${todos ? ' on' : ''}" data-a="quem-todos">${ic(todos ? 'check' : 'users', 'ic-s')}Todos</button>` : ''}${e.pessoas.map(p => `<button class="escolha${t.quem.includes(p.id) ? ' on' : ''}" data-a="quem" data-v="${esc(p.id)}">${ic(t.quem.includes(p.id) ? 'check' : 'user', 'ic-s')}${esc(p.nome.split(' ')[0])}</button>`).join('')}</div></div>`;
    }
    if (lv) {
      h += `<div class="campo">${lbl('user', (t.autores || []).length > 1 ? 'Autores' : 'Autor')}${(t.autores || []).length ? `<p class="sinopse">${esc(t.autores.join(', '))}</p>` : '<p class="vazio">A Open Library não diz o autor.</p>'}
        <p class="credito">${t.isbn ? `ISBN ${esc(t.isbn)} · ` : ''}Dados da ${t.link ? site(esc(t.link), 'Open Library') : 'Open Library'}${t.ol_em ? `, de ${esc(dia(t.ol_em.slice(0, 10)))}` : ''}.</p></div>`;
    } else if (jg) {
      h += `<div class="campo">${lbl('gamepad', 'Onde jogar')}${(t.plataformas || []).length ? `<dl class="onde"><div><dt>Plataformas</dt><dd>${esc(t.plataformas.join(', '))}</dd></div></dl>` : '<p class="vazio">O IGDB não diz as plataformas.</p>'}
        <p class="credito">Dados do ${t.link ? site(esc(t.link), 'IGDB') : 'IGDB'}${t.igdb_em ? `, de ${esc(dia(t.igdb_em.slice(0, 10)))}` : ''}.</p></div>`;
    } else {
      const o = t.onde || {}, partes = [['assinatura', 'Assinatura'], ['gratis', 'Grátis'], ['alugar', 'Alugar'], ['comprar', 'Comprar']].filter(([k]) => (o[k] || []).length);
      h += `<div class="campo">${lbl('tv', 'Onde assistir')}${partes.length ? `<dl class="onde">${partes.map(([k, n]) => `<div><dt>${n}</dt><dd>${esc(o[k].join(', '))}</dd></div>`).join('')}</dl>` : '<p class="vazio">Nada no Brasil, pelo que a JustWatch sabe.</p>'}
        <p class="credito">Dados da ${o.link ? site(esc(o.link), 'JustWatch') : 'JustWatch'}${t.tmdb_em ? `, de ${esc(dia(t.tmdb_em.slice(0, 10)))}` : ''}.</p></div>`;
    }
    if (t.sinopse) h += `<div class="campo">${lbl('texto', 'Sinopse')}<p class="sinopse">${esc(t.sinopse)}</p></div>`;
    h += `<div class="campo">${lbl('nota', 'Notas', 'f-notas')}<textarea class="inp" id="f-notas" rows="3" placeholder="${jg || lv ? 'Onde parou, o que achou…' : 'O que a casa achou, quem indicou…'}">${esc(t.notas)}</textarea></div>`;
    const pe = S.conf === 'apagar:' + t.id ? `<p class="conf">Apagar «${esc(t.nome)}» da lista?</p><button class="btn out" data-a="conf-nao">${ic('x', 'ic-s')}Cancelar</button><button class="btn perigo" data-a="apagar" data-id="${t.id}">${ic('trash', 'ic-s')}Apagar</button>`
      : `<button class="btn out" data-a="conf" data-v="apagar:${t.id}">${ic('trash', 'ic-s')}Apagar</button><button class="btn out" data-a="atualizar" data-id="${t.id}"${ref(t) ? '' : ' disabled'}>${ic('refresh', 'ic-s')}Atualizar</button>`;
    return { titulo: t.nome, icone: TIPO[t.tipo][1], corpo: h, pe };
  }
  function folhaColecao(f) {
    const jg = !!f.jogo, nome = jg ? 'Coleção de jogos' : 'Coleção de filmes';
    const c = S.col && S.col.id === f.id && S.col.jogo === jg ? S.col : null;
    if (!c) {
      S.col = { id: f.id, jogo: jg, dados: null, erro: '' };
      api.get(`colecao?id=${f.id}${jg ? '&tipo=jogo' : ''}`).then(r => { if (S.col && S.col.id === f.id) { S.col.dados = r.colecao; render(); } })
        .catch(err => { if (S.col && S.col.id === f.id) { S.col.erro = err.message; render(); } });
      return { titulo: nome, icone: 'layers', corpo: '<p class="vazio">Abrindo…</p>' };
    }
    if (c.erro) return { titulo: nome, icone: 'layers', corpo: `<p class="status erro">${esc(c.erro)}</p>` };
    if (!c.dados) return { titulo: nome, icone: 'layers', corpo: '<p class="vazio">Abrindo…</p>' };
    const d = c.dados, saiu = d.itens.filter(x => x.saiu), cats = S.e.categorias[jg ? 'jogo' : 'filme'] || [];
    // 0.5.0 (o dono: "antes do já vi todos, as opções de categorias para selecionar a categoria de todos ou individual"): a
    // categoria de todos vale no Quero ver todos e no Já vi todos; a de cada um, na etiqueta embaixo da capa
    const cc = S.colCat || MANTER;
    const campoCat = cats.length ? `<div class="campo">${lbl('tag', jg ? 'Categoria de todos os jogos' : 'Categoria de todos os filmes')}<div class="escolhas">
      <button class="escolha${cc === MANTER ? ' on' : ''}" data-a="col-cat" data-v="${MANTER}">${ic(cc === MANTER ? 'check' : 'igual', 'ic-s')}Manter</button>${cats.map(x => pickCat('col-cat', x, cc === x.id)).join('')}</div></div>` : '';
    const pe = `<button class="btn out" data-a="col-todos" data-v="quero"${d.itens.every(x => x.ja) ? ' disabled' : ''}>${ic('bookmark', 'ic-s')}${jg ? 'Quero jogar todos' : 'Quero ver todos'}</button>
      <button class="btn pri" data-a="col-todos" data-v="visto"${saiu.every(x => x.situacao === 'visto') ? ' disabled' : ''}>${ic('visto', 'ic-s')}${jg ? 'Já joguei todos' : 'Já vi todos'}</button>`;
    return { titulo: d.nome, icone: 'layers', alta: true, pe, corpo: `${d.sinopse ? `<p class="sinopse">${esc(d.sinopse)}</p>` : ''}
      <div class="campo" style="margin-top:14px">${lbl(jg ? 'gamepad' : 'film', jg ? plural(d.itens.length, 'jogo', 'jogos') : plural(d.itens.length, 'filme', 'filmes'))}${grade(d.itens, 'col')}</div>${campoCat}` };
  }
  /* O que um campo de janela tem escolhido ou escrito (para o campo fechado): os botões marcados, senão a caixa de
     seleção, senão o texto */
  const SUB_CAMPO = 'small, .sub, .badge, .n, .cont';
  const textoBotao = b => [...b.childNodes].filter(n => n.nodeType === 3 || (n.nodeType === 1 && !n.matches(SUB_CAMPO) && n.tagName !== 'svg'))
    .map(n => n.textContent).join(' ').replace(/\s+/g, ' ').trim();
  // sem nada escolhido nem escrito: «Sem categoria», «Ninguém» (Quem…), «Nenhuma» (uma palavra feminina) ou «Nenhum»
  function vazioDe(titulo) {
    const t = String(titulo || '').trim();
    if (/^categoria/i.test(t)) return 'Sem categoria';
    if (/^quem\b/i.test(t)) return 'Ninguém';
    return /^(notas?|observaç|lista|cor\b|fotos?|descriç|data|hora|temporada|plataforma|situaç|coleç)/i.test(t) ? 'Nenhuma' : 'Nenhum';
  }
  function valorCampo(c) {
    const meu = el => el.closest('.campo') === c && !el.closest('.lbl, .dobra-campo');
    const v = [...c.querySelectorAll('.on, .sel, [aria-pressed="true"], [aria-checked="true"]')]
      .filter(b => meu(b) && b.matches('button, .chip, .escolha, [role="radio"], [role="checkbox"]'))
      .map(b => textoBotao(b) || b.getAttribute('title') || b.getAttribute('aria-label') || '').filter(Boolean);
    let t = v.length ? [...new Set(v)].join(', ') : [...c.querySelectorAll('select, textarea, input:not([type=checkbox]):not([type=radio]):not([type=file]):not([type=hidden])')]
      .filter(meu)
      .map(x => (x.tagName === 'SELECT' ? (x.value !== '' ? (x.selectedOptions[0] || {}).textContent || '' : '') : (x.value || '').split('\n')[0]).replace(/\s+/g, ' ').trim())
      .filter(Boolean).join(' · ');
    if (t.length > 48) t = t.slice(0, 47) + '…';
    return t;
  }

  function pintarJanela() {
    const el = $('#janela');
    const f = S.folha;
    const t = f && (f.tipo === 'titulo' || f.tipo === 'cat-titulo') ? S.e.titulos.find(x => x.id === f.id) : null;
    const j = !f || ((f.tipo === 'titulo' || f.tipo === 'cat-titulo') && !t) || (f.tipo === 'conversa' && !iaOn()) ? null : f.tipo === 'conversa' ? folhaConversa() : f.tipo === 'adicionar' ? folhaAdicionar() : f.tipo === 'colecao' ? folhaColecao(f)
      : f.tipo === 'categoria' ? folhaCategoria(f) : f.tipo === 'lote' ? folhaLote() : f.tipo === 'cat-titulo' ? folhaCatTitulo(t) : folhaTitulo(t);
    if (!j) {
      if (el.innerHTML) el.innerHTML = '';
      document.body.classList.remove('com-folha');
      return;
    }
    const corpoAntes = el.querySelector('.folha-corpo'), rolou = corpoAntes && corpoAntes.dataset.k === (f.tipo + (f.id || '')) ? corpoAntes.scrollTop : 0;
    const foco = document.activeElement && el.contains(document.activeElement) ? document.activeElement.id : '';
    const sel = foco && document.activeElement.selectionStart;
    // a mesma janela pintada de novo (um toque, a lista que chegou) não sobe outra vez
    const fixa = corpoAntes && corpoAntes.dataset.k === (f.tipo + (f.id || ''));
    el.innerHTML = `<div class="veu" data-a="fechar"></div><div class="folha${j.alta ? ' alta' : ''}${j.conversa ? ' conversa' : ''}${fixa ? ' fixa' : ''}" role="dialog" aria-modal="true" aria-label="${esc(j.titulo)}">
      <div class="folha-cab"><h2><span class="folha-ic">${ic(j.icone)}</span><span class="folha-tt">${esc(j.titulo)}</span></h2><button class="fechar" data-a="fechar" aria-label="Fechar">${ic('x')}</button></div>
      <div class="folha-corpo" data-k="${f.tipo + (f.id || '')}">${j.corpo}</div>${j.pe ? `<div class="folha-pe">${j.pe}</div>` : ''}</div>`;
    document.body.classList.add('com-folha');
    const corpo = el.querySelector('.folha-corpo');
    // 0.5.0 (o dono: "falta de opções de retrair, igual os outros apps"): cada campo da janela fecha e abre pelo título, com a
    // seta no canto; o aparelho lembra (pelo título)
    const F = new Set(lerJSON('odisseia-campos', []));
    corpo.querySelectorAll(':scope > .campo').forEach(c => {
      const r = c.querySelector(':scope > .lbl, :scope > label');
      if (!r || !c.children[1]) return;
      const k = r.textContent.trim().replace(/^\d+ /, '');
      r.classList.add('dobra-campo');
      r.dataset.campo = k;
      r.setAttribute('role', 'button');
      r.setAttribute('aria-expanded', String(!F.has(k)));
      // 0.8.0 (o dono: "tem que mostrar o que foi selecionado do ladinho, quando eu retraio"): fechado, o escolhido ou o
      // escrito ao lado do título, como nos outros apps
      // 0.12.2 (o dono: "quando retraído sem selecionar nada deve estar como nenhum… em todos os apps")
      const v = valorCampo(c) || vazioDe(k);
      r.insertAdjacentHTML('beforeend', `<span class="fl-val">· ${esc(v)}</span>` + ic('chev', 'ic-s seta'));
      c.classList.toggle('fechado', F.has(k));
    });
    if (rolou) corpo.scrollTop = rolou;
    if (j.conversa && S.ch.rolar) { corpo.scrollTop = corpo.scrollHeight; S.ch.rolar = false; }  // a mensagem nova à vista
    if (foco && $('#' + foco)) { const x = $('#' + foco); x.focus({ preventScroll: true }); try { if (sel != null) x.setSelectionRange(sel, sel); } catch (e) { /* sem seleção */ } }
  }

  /* ---------- a barra de baixo e a lateral (o padrão da família) */
  const NAV = [['agora', 'Agora', 'clock'], ['buscar', 'Buscar', 'search'], ['+', 'Adicionar', 'plus'], ['vistos', 'Concluídos', 'visto'], ['mais', 'Mais', 'mais']];
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
    const h = S.tela === 'buscar' ? telaBuscar() : S.tela === 'vistos' ? telaVistos() : S.tela === 'mais' ? telaMais() : S.tela === 'categorias' ? telaCategorias() : S.tela === 'config' ? telaConfig() : S.tela === 'sobre' ? telaSobre() : telaAgora();
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
    S.sel = null; // o Selecionar acaba ao sair da tela
    if (tela === 'config') { S.uso = null; S.usoPedido = false; S.memPedida = false; }  // o Uso e a Memória de agora
    if (!sem) history.pushState({ t: tela }, '');
    render();
    window.scrollTo(0, 0);
  }
  // sobre: a janela abre por cima da de agora (uma coleção a partir da busca, um filme a partir da coleção) e o Voltar
  // do celular, o X e o Esc voltam para a de baixo; sem sobre, troca a de agora
  function abrirFolha(f, sobre) {
    S.conf = '';
    S.novaCat = null;
    const est = n => Object.assign({ t: S.tela, folha: n }, S.sel ? { sel: 1 } : {});
    if (S.folhas.length && sobre) { S.folhas.push(f); history.pushState(est(S.folhas.length), ''); }
    else if (S.folhas.length) { S.folhas[S.folhas.length - 1] = f; history.replaceState(est(S.folhas.length), ''); }
    else { S.folhas = [f]; history.pushState(est(1), ''); }
    S.folha = f;
    render();
  }
  function fecharFolha() {
    // o X da Conversa com as perguntas prontas abertas fecha as duas (a entrada delas e a da janela)
    if (history.state && history.state.painel && history.state.folha) { S.ch.rapidas = false; S.ch.editando = null; history.go(-2); }
    else if (history.state && history.state.folha) history.back();
    else { S.folhas = []; S.folha = null; render(); }
  }
  window.addEventListener('popstate', ev => {
    const st = ev.state || { t: 'agora' };
    if (window.__selectSheet && window.__selectSheet.isOpen()) return;
    S.folhas = S.folhas.slice(0, st.folha || 0);
    S.folha = S.folhas[S.folhas.length - 1] || null;
    if (S.ch.fala && !(S.folha && S.folha.tipo === 'conversa')) pararFala();  // o Voltar fechou a Conversa: o microfone para
    S.conf = '';
    S.novaCat = null;
    if (COD.aberto && !st.cod) fecharCodigo();  // e fecha a câmera do código de barras
    if (S.sel && !st.sel) S.sel = null; // o Voltar do celular sai do Selecionar
    if (!st.painel) { S.ch.rapidas = false; S.ch.editando = null; }  // e fecha as perguntas prontas
    if (st.t && st.t !== S.tela) { S.tela = st.t; window.scrollTo(0, 0); }
    render();
  });

  /* ---------- 0.16.0: o código de barras de um livro (o ISBN), pela câmera do app: o número vai para a busca */
  const COD = { aberto: false, fluxo: null, el: null, t: 0 };
  function fecharCodigo() {
    clearTimeout(COD.t);
    if (COD.fluxo) COD.fluxo.getTracks().forEach(x => x.stop());
    if (COD.el) COD.el.remove();
    Object.assign(COD, { aberto: false, fluxo: null, el: null });
  }
  function achouCodigo(n) {
    S.add.q = n;
    S.add.res = null;
    history.back();  // fecha a câmera (o popstate) e a busca começa
    setTimeout(buscarTMDB, 60);
  }
  async function lerCodigo() {
    const md = navigator.mediaDevices;
    if (!md || !md.getUserMedia || !('BarcodeDetector' in window)) {
      toast(window.isSecureContext === false ? 'Sem https não há câmera: escreva o número que fica embaixo do código de barras.' : 'Aqui não dá para ler o código: escreva o número que fica embaixo dele.');
      return;
    }
    try { COD.fluxo = await md.getUserMedia({ video: { facingMode: 'environment' }, audio: false }); } catch (err) {
      toast('Sem a câmera: escreva o número que fica embaixo do código de barras.');
      return;
    }
    const el = document.createElement('div');
    el.className = 'cod-cam';
    el.innerHTML = `<video playsinline muted></video><div class="cod-guia"></div><p>Aponte para o código de barras do livro</p><button class="btn out" data-a="cod-fechar">${ic('x', 'ic-s')}Fechar</button>`;
    document.body.appendChild(el);
    Object.assign(COD, { aberto: true, el });
    history.pushState(Object.assign({}, history.state, { cod: 1 }), '');
    const v = el.querySelector('video');
    v.srcObject = COD.fluxo;
    const toca = v.play();  // sem esperar: o vídeo começa quando der
    if (toca && toca.catch) toca.catch(() => {});
    const det = new window.BarcodeDetector({ formats: ['ean_13'] });
    const olhar = async () => {
      if (!COD.aberto) return;
      try {
        const cs = await det.detect(v);
        const c = cs.map(x => String(x.rawValue || '')).find(x => /^97[89]\d{10}$/.test(x));
        if (c) { achouCodigo(c); return; }
      } catch (err) { /* um quadro que não deu: o próximo */ }
      COD.t = setTimeout(olhar, 250);
    };
    olhar();
  }

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
    const primeira = !S.e;
    S.e = e;
    aplicarCor();
    render();
    if (primeira) carregarIA();
  }
  function carregarLista(mais) {
    const a = S.add, k = a.lista + ':' + a.tipo, L = a.listas[k] || (a.listas[k] = { itens: [], pagina: 0, mais: false, carregando: false, erro: '' });
    if (L.carregando || !temFonte(a.tipo)) return;
    L.carregando = true;
    api.get(`lista?nome=${a.lista}&tipo=${a.tipo}&pagina=${L.pagina + 1}`).then(r => {
      const vistos = new Set(L.itens.map(x => x.tipo + ref(x)));
      L.itens.push(...r.resultados.filter(x => !vistos.has(x.tipo + ref(x))));
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
    return o === 'col' ? S.col.dados.itens[i] : o === 'busca' ? S.add.res[i] : S.add.listas[S.add.lista + ':' + S.add.tipo].itens[i];
  }
  async function adicionarUm(r, situacao) {
    const tipo = r.tipo || (S.col && S.col.jogo ? 'jogo' : 'filme');
    const x = await api.post('titulo', { acao: 'adicionar', tipo, [tipo === 'jogo' ? 'igdb' : tipo === 'livro' ? 'ol' : 'tmdb']: ref(Object.assign({ tipo }, r)), situacao });
    trocar(x.titulo);
    r.ja = x.titulo.id;
    r.situacao = x.titulo.situacao;
    if (!x.novo) toast('Já estava na lista.');
    return x;
  }
  // o mesmo texto do ferramentas.texto_colecao (o CorrerIA)
  function textoColecao(r, situacao) {
    const jg = r.tipo === 'jogo', p = [];
    if (r.novos) p.push(`${r.novos} ${r.novos === 1 ? (jg ? 'jogo posto' : 'filme posto') : (jg ? 'jogos postos' : 'filmes postos')} na lista como ${sitN(r.tipo, situacao)}`);
    if (r.marcados) p.push(`${r.marcados} ${r.marcados === 1 ? 'marcado' : 'marcados'} como ${sitN(r.tipo, 'visto')}`);
    if (r.ja) p.push(`${r.ja} já ${r.ja === 1 ? 'estava' : 'estavam'} na lista`);
    if (r.fora) p.push(`${r.fora} ainda não ${r.fora === 1 ? 'saiu' : 'saíram'}`);
    return `${r.nome}: ${p.length ? p.join(', ') : 'nada a mudar'}.` + ('categoria' in r ? ` Categoria de todos: ${r.categoria || 'nenhuma'}.` : '');
  }
  const salvarBusca = () => guardar('odisseia-busca', JSON.stringify({ tipo: S.busca.tipo, situacao: S.busca.situacao, quem: S.busca.quem, categoria: S.busca.categoria }));

  /* ---------- a IA (0.7.0; o dono: "no topo das telas opções de chat e de falar igual os outros apps"; "toda a sorte de IA
     deve estar no OdisseIA"). A Conversa (a IA do Home Assistant com as ferramentas daqui: lê na hora, muda depois do Sim),
     o Falar (o microfone vira texto e vai para a Conversa), Escolher fotos (a IA vê a foto), a Memória da IA (a mesma de
     todos os apps) e o Uso da IA. Tudo só com Usar IA ligado e uma IA no Home Assistant. */
  const iaOn = () => !!(S.e && S.e.ajustes.ia && S.ia && S.ia.pronta);
  const falaOn = () => iaOn() && !!(S.ia.fala && S.ia.fala.pronta);
  const noCelular = () => { try { return matchMedia('(hover: none) and (pointer: coarse)').matches; } catch (e) { return false; } };
  function carregarIA(novo) {
    return api.get('ia' + (novo ? '?novo=1' : '')).then(r => { S.ia = r; render(); }).catch(() => { S.ia = { ligada: S.e && S.e.ajustes.ia, pronta: false, motivo: 'Não consegui ver a IA do Home Assistant.', entidades: [], fala: {} }; render(); });
  }
  // a Conversa: o texto da IA com *negrito* e as listas com "- "
  function md(t) {
    const linhas = String(t || '').split('\n');
    let h = '', lista = false;
    const neg = s => esc(s).replace(/\*([^*\n]+)\*/g, '<b>$1</b>');
    for (const l of linhas) {
      const m = /^\s*[-•]\s+(.*)$/.exec(l);
      if (m) { if (!lista) { h += '<ul>'; lista = true; } h += `<li>${neg(m[1])}</li>`; continue; }
      if (lista) { h += '</ul>'; lista = false; }
      if (l.trim()) h += `<p>${neg(l)}</p>`;
    }
    return h + (lista ? '</ul>' : '');
  }
  /* 0.10.0 (o padrão da família): as perguntas prontas: 6 à vista e, em Editar perguntas, as Mais perguntas (20 modelos; um
     toque põe), guardadas no aparelho (odisseia-perguntas). Todas gerais, que valem em qualquer casa: nada de títulos,
     pessoas ou categorias inventadas (o pedido com o detalhe é o que a pessoa escreve). */
  const PERGUNTAS = ['O que tem de novo para ver?', 'Em que episódio paramos?', 'O que sai esta semana?', 'Me sugere um filme da nossa lista',
    'Quais jogos vão sair?', 'O que está em alta para ver?',
    'O que a casa viu este mês?', 'Quais séries estão em andamento?', 'O que tem em Quero ver?', 'Quais jogos estão em Quero jogar?',
    'Onde assistir o que está na lista?', 'Me sugere uma série para começar', 'Me sugere um jogo da nossa lista', 'Quais coleções estão pela metade?',
    'Qual série está mais perto do fim?', 'O que a casa viu por último?', 'Quantos títulos tem cada categoria?', 'Quais estreias valem a pena?',
    'Quais séries vão ter episódio novo?', 'O que está nos cinemas agora?', 'Quais são os mais bem avaliados para ver?', 'Me sugere algo para ver em família',
    'Quantos títulos a casa já concluiu?', 'Quais títulos estão sem categoria?', 'O que cada pessoa está vendo?', 'O que da lista está em algum streaming?'];
  const PERG = 'odisseia-perguntas';
  function perguntas() {
    const pad = PERGUNTAS.slice(0, 6), modelos = PERGUNTAS.slice(6, 26), v = lerJSON(PERG, null);
    return { lista: Array.isArray(v) ? v.filter(x => typeof x === 'string' && x.trim()) : pad, pad, modelos };
  }
  // em Editar perguntas, as Perguntas prontas e as Mais perguntas fecham num toque no título (o aparelho lembra)
  const edCab = (k, icone, titulo, fechada) => `<button type="button" class="perg-h" data-a="perg-dobra" data-v="${k}" aria-expanded="${!fechada}">${ic(icone, 'ic-s')}<span>${esc(titulo)}</span>${ic('chev', 'ic-s seta')}</button>`;
  function blocoPerguntas() {
    const ed = S.ch.editando, F = lerJSON('odisseia-perguntas-fechadas', {});
    if (ed) {
      const mais = perguntas().modelos.filter(q => !ed.lista.includes(q));
      return `<div class="perg-ed">${edCab('prontas', 'nota', `Perguntas prontas (${ed.lista.length})`, F.prontas)}
        ${F.prontas ? '' : `${ed.lista.map((q, i) => `<div class="perg-lin"><textarea class="perg-txt" data-ed-i="${i}" rows="1" maxlength="120" data-size="off" aria-label="Mudar “${esc(q)}”">${esc(q)}</textarea><button class="perg-x" data-a="perg-tirar" data-v="${i}" aria-label="Tirar “${esc(q)}”" title="Tirar">${ic('x', 'ic-s')}</button></div>`).join('')}
        <div class="perg-nova"><textarea id="perg-nova" class="inp umalinha" rows="1" maxlength="120" placeholder="Nova pergunta" aria-label="Nova pergunta">${esc(ed.rascunho || '')}</textarea><button class="btn out" data-a="perg-add">${ic('plus', 'ic-s')}Adicionar</button></div>`}
        ${mais.length ? `${edCab('mais', 'sparkles', `Mais perguntas (${mais.length})`, F.mais)}
          ${F.mais ? '' : mais.map(q => `<button class="perg-lin perg-modelo" data-a="perg-por" data-v="${esc(q)}" aria-label="Pôr “${esc(q)}”"><span>${esc(q)}</span>${ic('plus', 'ic-s')}</button>`).join('')}` : ''}
        <div class="acoes dois"><button class="btn out" data-a="perg-padrao">${ic('refresh', 'ic-s')}Padrão</button><button class="btn pri" data-a="perg-pronto">${ic('check', 'ic-s')}Pronto</button></div></div>`;
    }
    const { lista } = perguntas();
    return `${lista.length ? `<div class="conv-ideias">${lista.map(t => `<button class="btn" data-a="conv-ideia" data-v="${esc(t)}">${ic('sparkles', 'ic-s')}${esc(t)}</button>`).join('')}</div>` : ''}
      <button class="perg-abrir" data-a="perg-editar">${ic('nota', 'ic-s')}Editar perguntas</button>`;
  }
  // as perguntas prontas por cima da caixa (o ✨) e o Editar perguntas ocupam uma entrada no histórico: o Voltar fecha
  function abrirPerguntas(o) {
    const ja = S.ch.rapidas || S.ch.editando;
    Object.assign(S.ch, o);
    if (!ja && (S.ch.rapidas || S.ch.editando)) history.pushState(Object.assign({}, history.state, { painel: 1 }), '');
    pintarJanela();
  }
  function fecharPerguntas() {
    if (!(S.ch.rapidas || S.ch.editando)) return;
    if (history.state && history.state.painel) history.back();
    else { S.ch.rapidas = false; S.ch.editando = null; pintarJanela(); }
  }
  function folhaConversa() {
    const c = S.conv || { mensagens: [], pendente: null }, ch = S.ch, msgs = c.mensagens;
    const bolha = (m, i) => {
      const ult = i === msgs.length - 1;
      if (m.papel === 'eu') return `<div class="msg eu">${m.mini ? `<img class="msg-mini" src="${esc(m.mini)}" alt="Foto">` : m.foto ? `<span class="msg-foto">${ic('image', 'ic-s')}Foto</span>` : ''}${m.texto ? `<div class="msg-t">${esc(m.texto).replace(/\n/g, '<br>')}</div>` : ''}</div>`;
      return `<div class="msg ia${m.erro ? ' erro' : ''}"><div class="msg-t">${md(m.texto)}</div>${m.sim && ult && c.pendente ? `<div class="acoes dois msg-sim">
          <button class="btn out" data-a="conv-sim" data-v="0">${ic('x', 'ic-s')}Não</button><button class="btn pri" data-a="conv-sim" data-v="1">${ic('check', 'ic-s')}Sim</button></div>`
        : m.decidido ? `<p class="msg-dec">${m.decidido === 'sim' ? 'Você confirmou.' : 'Você disse não.'}</p>` : ''}</div>`;
    };
    const corpo = !msgs.length && !ch.enviando
      ? `<div class="conv-vazia"><p class="lead">Pergunte sobre a lista da casa, peça para pôr ou marcar um título, ou mande a foto de um pôster.</p>
          ${blocoPerguntas()}</div>`
      : `<div class="conv-topo"><button class="btn fino" data-a="conv-nova"${ch.enviando ? ' disabled' : ''}>${ic('refresh', 'ic-s')}Nova conversa</button></div>
        <div class="msgs" aria-live="polite">${msgs.map(bolha).join('')}${ch.enviando ? `<div class="msg ia pensando"><span class="pontos"><i></i><i></i><i></i></span>Pensando…</div>` : ''}</div>`;
    const f = ch.fala, ouvindo = f === 'ouvindo' || f === 'abrindo';
    const vazio = !ch.texto.trim() && !ch.anexo;
    const pri = f === 'entendendo' ? `<button class="conv-bt pri" disabled aria-label="Entendendo">${ic('hourglass')}</button>`
      : ouvindo ? `<button class="conv-bt pri gravando" id="conv-pri" data-a="conv-falar" aria-label="Pronto: enviar o que falei"${f === 'abrindo' ? ' disabled' : ''}>${ic('check')}</button>`
      : vazio && falaOn() ? `<button class="conv-bt pri" id="conv-pri" data-a="conv-falar" aria-label="Falar"${ch.enviando ? ' disabled' : ''}>${ic('mic')}</button>`
      : `<button class="conv-bt pri" id="conv-pri" data-a="conv-enviar" aria-label="Enviar"${ch.enviando || vazio ? ' disabled' : ''}>${ic('send')}</button>`;
    const rap = msgs.length && (ch.rapidas || ch.editando);
    const pe = `<div class="conv-pe">${rap ? `<div class="conv-rapidas">${blocoPerguntas()}</div>` : ''}${ch.anexo ? `<div class="conv-anexo"><img src="${esc(ch.anexo.mini)}" alt=""><span>${esc(ch.anexo.nome || 'Foto')}</span><button class="conv-bt" data-a="conv-tirar-foto" aria-label="Tirar a foto">${ic('x')}</button></div>` : ''}
      <div class="conv-linha">${ouvindo ? `<button class="conv-bt" data-a="conv-falar-x" aria-label="Cancelar">${ic('x')}</button>`
        : `<button class="conv-bt" data-a="conv-foto" aria-label="Escolher fotos"${ch.enviando ? ' disabled' : ''}>${ic('image')}</button>`}
        <textarea id="conv-texto" class="inp" rows="1" data-size="off" maxlength="2000" enterkeyhint="${noCelular() ? 'enter' : 'send'}" placeholder="${ouvindo ? 'Ouvindo… toque em ✓ quando terminar' : f === 'entendendo' ? 'Entendendo…' : 'Pergunte ou peça'}" aria-label="Mensagem"${ouvindo || f ? ' disabled' : ''}>${esc(ch.texto)}</textarea>${msgs.length && !ouvindo ? `<button class="conv-bt${rap ? ' on' : ''}" data-a="perg-rapidas" aria-label="Perguntas prontas" title="Perguntas prontas" aria-expanded="${rap ? 'true' : 'false'}">${ic('sparkles')}</button>` : ''}${pri}</div></div>`;
    return { titulo: 'Conversa', icone: 'chat', alta: true, corpo, pe, conversa: true };
  }
  function abrirConversa(falar) {
    if (!iaOn()) return;
    Object.assign(S.ch, { rapidas: false, editando: null });  // a Conversa abre sempre no chat (o padrão da família)
    if (!(S.folha && S.folha.tipo === 'conversa')) abrirFolha({ tipo: 'conversa' });
    S.ch.rolar = true;
    if (!S.conv) api.get('conversa').then(r => { S.conv = r; S.ch.rolar = true; render(); }).catch(err => toast(err.message));
    render();
    if (falar) setTimeout(falarConversa, 120);
  }
  async function enviarConversa(texto) {
    const ch = S.ch, t = String(texto != null ? texto : ch.texto).trim(), anexo = ch.anexo;
    if (ch.enviando || (!t && !anexo)) return;
    S.conv = S.conv || { mensagens: [], pendente: null };
    S.conv.mensagens = S.conv.mensagens.map(m => Object.assign({}, m, { sim: false }));
    S.conv.mensagens.push(Object.assign({ papel: 'eu', texto: t }, anexo ? { foto: true, mini: anexo.mini } : {}));
    S.conv.pendente = null;
    ch.texto = ''; ch.anexo = null; ch.enviando = true; ch.rolar = true;
    render();
    try {
      S.conv = await api.post('conversa', Object.assign({ texto: t }, anexo ? { anexo: { tipo: anexo.tipo, b64: anexo.b64, mini: anexo.mini } } : {}));
    } catch (err) {
      S.conv.mensagens.pop();
      ch.texto = t; ch.anexo = anexo;
      toast(err.message);
    }
    ch.enviando = false; ch.rolar = true;
    render();
    // uma mudança feita pela Conversa: a lista da tela vem de novo
    try { const r = await api.get('rev'); if (r.rev !== S.e.rev) await carregar(); } catch (e) { /* depois, pela revisão */ }
  }
  // a foto: diminuída para 1600 px em JPEG (o que a IA lê bem), e a miniatura de 96 px para a conversa
  function encolher(img, max, q) {
    const k = Math.min(1, max / Math.max(img.naturalWidth || img.width, img.naturalHeight || img.height));
    const cv = document.createElement('canvas');
    cv.width = Math.max(1, Math.round((img.naturalWidth || img.width) * k)); cv.height = Math.max(1, Math.round((img.naturalHeight || img.height) * k));
    cv.getContext('2d').drawImage(img, 0, 0, cv.width, cv.height);
    return cv.toDataURL('image/jpeg', q);
  }
  function lerFoto(arquivo) {
    if (!/^image\//.test(arquivo.type)) return toast('Escolha uma foto.');
    const url = URL.createObjectURL(arquivo), img = new Image();
    img.onload = () => {
      const grande = encolher(img, 1600, 0.85), mini = encolher(img, 96, 0.7);
      URL.revokeObjectURL(url);
      S.ch.anexo = { tipo: 'image/jpeg', b64: grande.split(',')[1], mini, nome: arquivo.name };
      render();
    };
    img.onerror = () => { URL.revokeObjectURL(url); toast('Não consegui abrir a foto.'); };
    img.src = url;
  }
  /* o Falar: o microfone em PCM de 16 kHz, 16 bits, mono (o que a fala para texto do Home Assistant recebe, como o Assist;
     o mesmo dos outros apps). Pronto: vira texto no servidor (/api/fala) e vai como a pergunta. Até 2 minutos. */
  const TAXA = 16000, MAX_FALA = 120;
  function Gravador(nivel) {
    let pedacos = [], total = 0, taxa = TAXA, fluxo = null, ctx = null, fonte = null, no = null;
    const fechar = () => {
      try { if (no) no.onaudioprocess = null; if (fonte) fonte.disconnect(); if (no) no.disconnect(); } catch (e) { /* já fechado */ }
      if (fluxo) fluxo.getTracks().forEach(t => t.stop());
      if (ctx && ctx.state !== 'closed') ctx.close().catch(() => {});
      fluxo = ctx = fonte = no = null;
    };
    this.iniciar = async () => {
      const md = navigator.mediaDevices;
      if (!md || !md.getUserMedia) throw Object.assign(new Error('sem_api'), { name: 'NoApi' });
      fluxo = await md.getUserMedia({ audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true, autoGainControl: true } });
      const AC = window.AudioContext || window.webkitAudioContext;
      try { ctx = new AC({ sampleRate: TAXA }); } catch (e) { ctx = new AC(); }
      if (ctx.state === 'suspended') await ctx.resume().catch(() => {});
      taxa = ctx.sampleRate;
      fonte = ctx.createMediaStreamSource(fluxo);
      no = ctx.createScriptProcessor(4096, 1, 1);
      no.onaudioprocess = ev => {
        const d = ev.inputBuffer.getChannelData(0);
        pedacos.push(new Float32Array(d)); total += d.length;
        let soma = 0;
        for (let i = 0; i < d.length; i += 4) soma += d[i] * d[i];
        if (nivel) nivel(Math.min(1, Math.sqrt(soma / (d.length / 4)) * 5));
      };
      fonte.connect(no); no.connect(ctx.destination);
    };
    this.parar = () => {
      fechar();
      const tudo = new Float32Array(total);
      let o = 0;
      for (const p of pedacos) { tudo.set(p, o); o += p.length; }
      pedacos = [];
      const r = taxa / TAXA, n = Math.floor(tudo.length / r), out = new Int16Array(n);
      for (let i = 0; i < n; i++) {
        const a = Math.floor(i * r), b = Math.max(a + 1, Math.min(tudo.length, Math.floor((i + 1) * r)));
        let s2 = 0;
        for (let j = a; j < b; j++) s2 += tudo[j];
        const v = Math.max(-1, Math.min(1, s2 / (b - a)));
        out[i] = v < 0 ? v * 0x8000 : v * 0x7fff;
      }
      return out;
    };
    this.cancelar = () => { fechar(); pedacos = []; total = 0; };
  }
  function erroMicrofone(err) {
    const n = (err && err.name) || '';
    if (n === 'NotAllowedError' || n === 'SecurityError') return 'O microfone está bloqueado. Permita o microfone para o Home Assistant (no navegador, no cadeado ao lado do endereço; no app do celular, nas permissões do app Home Assistant) e tente de novo.';
    if (n === 'NotFoundError' || n === 'OverconstrainedError') return 'Não achei um microfone neste aparelho.';
    if (n === 'NotReadableError') return 'O microfone está sendo usado por outro app. Feche o outro e tente de novo.';
    if (n === 'NoApi') return window.isSecureContext === false
      ? 'O microfone só funciona com o Home Assistant aberto por um endereço seguro (https). Neste endereço (http), o celular e o navegador não deixam usar o microfone.'
      : 'Este navegador não deixa usar o microfone aqui.';
    return `Não consegui abrir o microfone (${(err && err.message) || n || 'erro'}).`;
  }
  let GRAV = null;
  async function falarConversa() {
    const ch = S.ch;
    if (ch.fala === 'ouvindo') {  // Pronto: o que falou vira texto e vai
      const g = GRAV;
      GRAV = null; clearTimeout(falarConversa.t);
      if (!g) { ch.fala = ''; return render(); }
      const pcm = g.parar();
      if (pcm.length < TAXA * 0.4) { ch.fala = ''; render(); return toast('Não ouvi nada. Toque no microfone e fale.'); }
      ch.fala = 'entendendo'; render();
      try {
        const r = await fetch('api/fala', { method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: pcm.buffer }).then(ok);
        if (ch.fala !== 'entendendo') return;
        ch.fala = '';
        if (r && r.texto) return enviarConversa(r.texto);
        render();
      } catch (err) {
        if (ch.fala === 'entendendo') { ch.fala = ''; render(); }
        toast(err.message);
      }
      return;
    }
    if (ch.fala || ch.enviando) return;
    const g = new Gravador(nv => { const b = $('#conv-pri'); if (b) b.style.setProperty('--nivel', nv.toFixed(2)); });
    GRAV = g; ch.fala = 'abrindo'; render();
    try {
      await g.iniciar();
    } catch (err) {
      g.cancelar();
      if (GRAV === g) { GRAV = null; ch.fala = ''; render(); toast(erroMicrofone(err)); }
      return;
    }
    if (GRAV !== g) return g.cancelar();
    ch.fala = 'ouvindo'; render();
    falarConversa.t = setTimeout(() => S.ch.fala === 'ouvindo' && falarConversa(), MAX_FALA * 1000);
  }
  function pararFala() {  // Cancelar, fechar a Conversa ou sair do app: o que estava ouvindo some
    clearTimeout(falarConversa.t);
    if (GRAV) GRAV.cancelar();
    GRAV = null;
    if (S.ch.fala) S.ch.fala = '';
  }
  document.addEventListener('visibilitychange', () => { if (document.hidden && S.ch.fala) { pararFala(); render(); } });

  /* Configurações › Integrações: IA, Memória da IA, Falar e Uso da IA (os textos dos outros apps) */
  const nomeIA = id => { const e = ((S.ia && S.ia.entidades) || []).find(x => x.id === id); return e ? e.nome : id || 'a padrão do Home Assistant'; };
  function cardIA() {
    const a = S.e.ajustes, i = S.ia, on = a.ia;
    const chave = `<div class="linha-sw"><div><b>${ic('zap', 'ic-s')}Usar IA</b><span>${on ? 'Ligado: a Conversa, o Falar e as fotos na Conversa.' : 'Desligado: a Conversa e o Falar somem em todos os aparelhos.'}</span></div>
      <button class="sw${on ? ' on' : ''}" data-a="aj" data-k="ia" role="switch" aria-checked="${on}" aria-label="Usar IA"></button></div>`;
    if (!on) return card('ia', 'zap', 'IA', `<p class="lead">Usa a IA configurada no Home Assistant. O app não guarda chave.</p>${chave}`);
    const st = !i ? ['manual', 'Verificando a IA do Home Assistant…'] : i.pronta ? ['', `Pronta. Usando ${esc(nomeIA(i.conversa))}.`] : ['erro', esc(i.motivo || 'A IA não está pronta.')];
    const ents = (i && i.entidades) || [];
    const op = (k, primeira, soImagem) => `<option value="">${primeira}</option>${ents.map(e => `<option value="${esc(e.id)}"${e.id === (a[k] || '') ? ' selected' : ''}${soImagem && !e.imagens ? ' disabled' : ''}>${esc(e.nome)}${soImagem && !e.imagens ? ' (só texto)' : ''}</option>`).join('')}`;
    return card('ia', 'zap', 'IA', `<p class="lead">Usa a IA configurada no Home Assistant. O app não guarda chave.</p>${chave}
      <div class="sub-box"><p class="status ${st[0]}">${st[1]}</p>
        <div class="campo">${lbl('chat', 'Para conversar', 'ia-conversa')}<select id="ia-conversa" class="inp select" data-aj-sel="ia_conversa">${op('ia_conversa', 'Padrão do Home Assistant')}</select></div>
        <div class="campo">${lbl('image', 'Para ler fotos', 'ia-fotos')}<select id="ia-fotos" class="inp select" data-aj-sel="ia_fotos">${op('ia_fotos', 'Igual à de conversar', true)}</select></div>
        <div class="campo">${lbl('search', 'Para pesquisar na internet', 'ia-pesquisa')}<select id="ia-pesquisa" class="inp select" data-aj-sel="ia_pesquisa">${op('ia_pesquisa', 'Igual à de conversar')}</select></div>
        <div class="acoes"><button class="btn out" data-a="ia-verificar">${ic('refresh', 'ic-s')}Verificar de novo</button></div>
        <p class="nota">Para pesquisar, a IA precisa da busca na web ligada no Home Assistant.</p></div>`);
  }
  function cardMemoria() {
    if (!S.mem && !S.memPedida) { S.memPedida = true; api.get('memoria-ia').then(r => { S.mem = r; render(); }).catch(() => { S.mem = { lista: [] }; render(); }); }
    const lista = (S.mem && S.mem.lista) || [];
    const quando = x => { const t = /^(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d)/.exec(x.em || ''); return [t ? `${t[3]}/${t[2]}/${t[1]} ${t[4]}:${t[5]}` : '', x.app, x.quem].filter(Boolean).join(' · '); };
    return card('memoria-ia', 'nota', 'Memória da IA', `<p class="lead">Uma memória só, da casa, compartilhada por todos os apps: o que você escreve aqui a IA lembra em toda conversa, em qualquer um deles.</p>
      <div class="campo">${lbl('texto', 'O que lembrar', 'mem-texto')}<textarea id="mem-texto" class="inp umalinha" rows="1" maxlength="240" placeholder="A Ana não gosta de filme de terror"></textarea></div>
      <div class="acoes"><button class="btn pri" data-a="mem-add">${ic('check', 'ic-s')}Salvar</button></div>
      ${!S.mem ? '<p class="lead mem-vazio">Carregando…</p>' : lista.length ? `<ul class="mem-lista">${lista.map(x => `<li><span><b>${esc(x.texto)}</b><small>${esc(quando(x))}</small></span>
        <button class="icbtn" data-a="mem-del" data-v="${esc(x.id)}" aria-label="Apagar">${ic('trash')}</button></li>`).join('')}</ul>` : ''}`);
  }
  function cardFalar() {
    // 0.9.0 (o dono: "cadê a opção para alterar o falar igual os outros apps?"): a Fala para texto, Automático ou um motor
    const f = (S.ia && S.ia.fala) || null, escolha = S.e.ajustes.fala || '', ops = (f && f.opcoes) || [];
    const st = !f ? ['manual', 'Verificando…', ''] : f.pronta && !S.ia.pronta ? ['manual', 'Sem fala para texto', 'Só com a IA pronta.']
      : f.pronta ? ['', 'Pronto para ouvir', `Transcreve com ${esc(f.nome || 'a fala para texto do Home Assistant')}.${f.escolha_sumiu ? ' O escolhido não foi encontrado: usando o automático.' : ''}`]
      : ['erro', 'Sem fala para texto', esc(f.motivo || '')];
    const auto = f && f.automatico ? `: ${esc(f.automatico)}` : '';
    return card('falar', 'mic', 'Falar', `<p class="lead">Quem transforma a fala em texto. Não muda o assistente de voz do Home Assistant.</p>
      <p class="status ${st[0]}"><span><b>${st[1]}</b>${st[2] ? ` · ${st[2]}` : ''}</span></p>
      ${ops.length ? `<div class="campo">${lbl('mic', 'Fala para texto', 'fala-motor')}<select id="fala-motor" class="inp select" data-aj-sel="fala" aria-label="Fala para texto">
        <option value="">Automático${auto}</option>${ops.map(o => `<option value="${esc(o.id)}"${o.id === escolha ? ' selected' : ''}>${esc(o.nome)}</option>`).join('')}</select></div>` : ''}
      <div class="acoes"><button class="btn out" data-a="ia-verificar">${ic('refresh', 'ic-s')}Verificar de novo</button></div>
      ${f && !f.pronta ? `<div class="passos-box"><b>Como configurar</b><ol class="passos">
        <li>Com o ${site('https://www.nabucasa.com/', 'Home Assistant Cloud')}, a fala para texto já vem pronta.</li>
        <li>Sem ele, instale um motor de fala: o app Whisper (local, de graça) com a integração Wyoming, ou a fala para texto de uma IA como Google Gemini ou OpenAI.</li>
        <li>Volte aqui, toque em Verificar de novo e escolha o motor na lista.</li></ol></div>` : ''}`);
  }
  const USO_TIPO = { conversa: 'Conversa', foto: 'Conversa com foto', pesquisa: 'Pesquisar na internet' };
  const USO_RES = { ok: '', cota: 'Sem cota', formato: 'Fora do formato', erro: 'Com erro' };
  const DIA_SEM = ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sáb'];
  const milTokens = n => n >= 1000 ? `${(n / 1000).toFixed(n >= 10000 ? 0 : 1).replace('.', ',')} mil` : String(Math.round(n || 0));
  // 0.10.0 (o padrão da família): onde ver o consumo e o saldo de cada IA em uso, uma linha por provedor, com o site
  const PROVEDORES_IA = [
    [/google|gemini/, () => `Gemini: consumo e cota no ${site('https://aistudio.google.com/', 'Google AI Studio')}, em Dashboard › Usage; o saldo dos créditos, em Billing.`],
    [/openai|chatgpt|gpt/, () => `OpenAI: consumo e custo em ${site('https://platform.openai.com/usage', 'platform.openai.com/usage')}.`],
    [/anthropic|claude/, () => `Claude: consumo e custo no ${site('https://platform.claude.com/usage', 'Claude Console')}; o saldo dos créditos, em ${site('https://platform.claude.com/settings/billing', 'Billing')}.`],
  ];
  function provedoresIA(u) {
    const ents = (S.ia && S.ia.entidades) || [], aj = S.e.ajustes, de = id => { const e = ents.find(x => x.id === id); return e ? `${e.id} ${e.nome}` : (id || ''); };
    const acha = t => PROVEDORES_IA.filter(([re]) => re.test(String(t).toLowerCase()));
    let achados = acha([aj.ia_conversa, aj.ia_fotos, aj.ia_pesquisa, ...((u && u.ultimas) || []).map(c => c.ia)].map(de).join(' '));
    if (!achados.length) {  // na padrão do Home Assistant: o provedor das IAs de lá, se for um só
      const todos = new Set(ents.flatMap(e => acha(`${e.id} ${e.nome}`)));
      if (todos.size === 1) achados = [...todos];
    }
    return achados.length ? achados.map(([, nota]) => `<p class="nota">${nota()}</p>`).join('') : '<p class="nota">O consumo exato fica no painel do provedor da IA.</p>';
  }
  function cardUso() {
    if (!S.uso && !S.usoPedido) { S.usoPedido = true; api.get('uso').then(r => { S.uso = r; render(); }).catch(() => { S.uso = {}; render(); }); }
    const u = S.uso;
    let corpo;
    if (!u) corpo = '<p class="status manual">Carregando…</p>';
    else if (!u.hoje || !(u.dias || []).length || !u.dias.some(x => x.chamadas) && !(u.ultimas || []).length) corpo = '<p class="status manual">Sem dados de uso ainda.</p>';
    else {
      const sub = t => t.cota ? `<span class="s alerta">${t.cota} sem cota</span>` : t.erros ? `<span class="s alerta">${t.erros} com erro</span>` : `<span class="s">≈ ${milTokens(t.tokens)} tokens</span>`;
      const tile = (k, t) => `<div class="uso-tile"><span class="uk">${k}</span><span class="v">${t.chamadas || 0}</span>${sub(t)}</div>`;
      const max = Math.max(1, ...u.dias.map(x => x.chamadas || 0));
      const barras = u.dias.map(x => `<span class="uso-bar" title="${esc(`${x.dia.slice(8, 10)}/${x.dia.slice(5, 7)}: ${plural(x.chamadas || 0, 'chamada', 'chamadas')}`)}"><i style="height:${x.chamadas ? Math.max(4, Math.round(x.chamadas / max * 100)) : 0}%"></i></span>`).join('');
      const ult = (u.ultimas || []).map(c => `<li><b>${esc(USO_TIPO[c.tipo] || c.tipo)}</b><span>${esc(nomeIA(c.ia))}</span>${USO_RES[c.resultado] ? `<span class="r-erro">${esc(USO_RES[c.resultado])}</span>` : ''}
        <span class="t">${esc(String(c.segundos).replace('.', ','))} s · ≈ ${milTokens(c.tokens)} tokens · ${esc((c.quando || '').slice(8, 10))}/${esc((c.quando || '').slice(5, 7))} ${esc((c.quando || '').slice(11, 16))}</span>${c.erro ? `<span class="uso-motivo">${esc(c.erro)}</span>` : ''}</li>`).join('');
      corpo = `<div class="uso-tiles">${tile('Hoje', u.hoje)}${tile('7 dias', u.semana)}${tile('Este mês', u.mes)}</div>
        <div class="uso-chart" aria-hidden="true">${barras}</div><div class="uso-dias" aria-hidden="true">${u.dias.map((x, k) => `<span>${k === u.dias.length - 1 ? 'hoje' : DIA_SEM[new Date(x.dia + 'T12:00:00').getDay()]}</span>`).join('')}</div>
        <details class="uso-ult"><summary>${ic('chev', 'ic-s seta')}${ic('clock', 'ic-s')}Últimas chamadas (${(u.ultimas || []).length})</summary><ul>${ult || '<li>Nenhuma chamada ainda.</li>'}</ul></details>
        ${provedoresIA(u)}`;
    }
    return card('uso-ia', 'chart', 'Uso da IA', `<p class="lead">As chamadas do app para a IA. Os tokens são estimados.</p>${corpo}`);
  }

  const ACOES = {
    // 0.7.0: a IA
    conversa: () => abrirConversa(),
    'falar-top': () => abrirConversa(true),
    'conv-ideia': el => { const t = el.dataset.v; if (S.ch.rapidas || S.ch.editando) fecharPerguntas(); enviarConversa(t); },
    'perg-rapidas': () => (S.ch.rapidas || S.ch.editando ? fecharPerguntas() : abrirPerguntas({ rapidas: true })),
    'perg-editar': () => abrirPerguntas({ editando: { lista: perguntas().lista.slice(), rascunho: '' } }),
    'perg-dobra': el => { const F = lerJSON('odisseia-perguntas-fechadas', {}); F[el.dataset.v] = !F[el.dataset.v]; guardar('odisseia-perguntas-fechadas', JSON.stringify(F)); pintarJanela(); },
    'perg-por': el => { if (!S.ch.editando.lista.includes(el.dataset.v)) S.ch.editando.lista.push(el.dataset.v); pintarJanela(); },
    'perg-tirar': el => { S.ch.editando.lista.splice(Number(el.dataset.v), 1); pintarJanela(); },
    'perg-add': () => {
      const ed = S.ch.editando, t = (ed.rascunho || '').trim();
      if (!t) { const x = $('#perg-nova'); if (x) x.focus(); return; }
      ed.lista.push(t); ed.rascunho = ''; pintarJanela();
    },
    'perg-padrao': () => { guardar(PERG, 'null'); S.ch.editando = { lista: perguntas().pad.slice(), rascunho: '' }; pintarJanela(); },
    'perg-pronto': () => {
      // uma pergunta mudada vale como ficou; uma apagada até ficar vazia sai; as do app (as 6 de início) seguem o app
      const ed = S.ch.editando, t = (ed.rascunho || '').trim(), lista = ed.lista.map(q => String(q || '').trim()).filter(Boolean).concat(t ? [t] : []);
      guardar(PERG, lista.join('\n') === perguntas().pad.join('\n') ? 'null' : JSON.stringify(lista));
      fecharPerguntas();
    },
    'conv-enviar': () => enviarConversa(),
    'conv-falar': () => falarConversa(),
    'conv-falar-x': () => { pararFala(); render(); },
    'conv-foto': () => $('#conv-foto-arquivo').click(),
    'conv-tirar-foto': () => { S.ch.anexo = null; render(); },
    'conv-nova': async () => { try { S.conv = await api.post('conversa/nova', {}); S.ch.texto = ''; S.ch.anexo = null; render(); } catch (err) { toast(err.message); } },
    'conv-sim': async el => {
      try { S.conv = await api.post('conversa/sim', { sim: el.dataset.v === '1' }); S.ch.rolar = true; render(); } catch (err) { toast(err.message); return; }
      if (el.dataset.v === '1') { try { const r = await api.get('rev'); if (r.rev !== S.e.rev) await carregar(); } catch (e) { /* depois */ } }
    },
    'ia-verificar': () => { S.ia = null; render(); carregarIA(true); },
    'mem-add': async () => {
      const t = ($('#mem-texto') || {}).value || '';
      if (!t.trim()) { const x = $('#mem-texto'); if (x) x.focus(); return; }
      try { S.mem = await api.post('memoria-ia', { acao: 'nova', texto: t }); $('#mem-texto').value = ''; render(); toast('Guardado na Memória da IA'); } catch (err) { toast(err.message); }
    },
    'mem-del': async el => { try { S.mem = await api.post('memoria-ia', { acao: 'apagar', id: el.dataset.v }); render(); } catch (err) { toast(err.message); } },
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
    'add-codigo': () => lerCodigo(),
    'cod-fechar': () => history.back(),
    'cz-abrir': async el => {
      const r = itemDe(el);
      if (r.tipo === 'colecao' || r.tipo === 'colecao_jogos') { S.col = null; S.colCat = null; abrirFolha({ tipo: 'colecao', id: ref(r), jogo: r.tipo === 'colecao_jogos' }, true); return; }
      if (r.ja) { abrirFolha({ tipo: 'titulo', id: r.ja }, true); return; }
      el.disabled = true;
      try { const x = await adicionarUm(r, 'quero'); abrirFolha({ tipo: 'titulo', id: x.titulo.id }, true); } catch (err) { el.disabled = false; toast(err.message); }
    },
    'cz-quero': async el => {
      const r = itemDe(el);
      el.disabled = true;
      try { const x = await adicionarUm(r, 'quero'); toast(`${x.titulo.nome}: ${sitN(x.titulo.tipo, 'quero')}.`); render(); } catch (err) { el.disabled = false; toast(err.message); }
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
        toast(`${t.nome}: ${sitN(t.tipo, 'visto')}` + (t.tipo === 'serie' && t.temp ? `, até ${ep(t.temp, t.ep)}.` : '.'));
        render();
      } catch (err) { el.disabled = false; toast(err.message); }
    },
    'abrir-colecao': el => { S.col = null; S.colCat = null; abrirFolha({ tipo: 'colecao', id: +el.dataset.id, jogo: !!el.dataset.j }, true); },
    'cz-colecao': el => { S.col = null; S.colCat = null; abrirFolha({ tipo: 'colecao', id: +el.dataset.id, jogo: !!el.dataset.j }, true); },
    // a coleção inteira de uma vez, sem abrir: Já vi todos (os que já saíram) ou Quero ver todos
    'cz-col-todos': async el => {
      const r = itemDe(el), sit = el.dataset.v;
      el.disabled = true;
      try {
        const x = await api.post('titulo', { acao: 'adicionar_colecao', colecao: ref(r), tipo: r.tipo === 'colecao_jogos' ? 'jogo' : 'filme', situacao: sit });
        r.situacao = sit;
        toast(textoColecao(x, sit));
        await carregar();
      } catch (err) { el.disabled = false; toast(err.message); }
    },
    'col-todos': async el => {
      el.disabled = true;
      try {
        const r = await api.post('titulo', Object.assign({ acao: 'adicionar_colecao', colecao: S.col.id, tipo: S.col.jogo ? 'jogo' : 'filme', situacao: el.dataset.v },
          S.colCat && S.colCat !== MANTER ? { categoria: S.colCat } : {}));
        toast(textoColecao(r, el.dataset.v));
        S.col = null;
        await carregar();
      } catch (err) { el.disabled = false; toast(err.message); }
    },
    sit: el => mudar(S.folha.id, { situacao: el.dataset.v }),
    cat: async el => { S.novaCat = null; await mudar(S.folha.id, { categoria: el.dataset.v }); if (S.folha && S.folha.tipo === 'cat-titulo') fecharFolha(); },
    'cat-rapida': el => abrirFolha({ tipo: 'cat-titulo', id: el.dataset.id }, true),
    'col-cat': el => { S.colCat = el.dataset.v; render(); },
    agrupar: el => { guardar('odisseia-agrupar', el.dataset.v); render(); },
    'agrupar-dobra': () => { guardar('odisseia-agrupar-fechado', guardada('odisseia-agrupar-fechado') === '1' ? '' : '1'); render(); },
    grupo: el => { const F = new Set(lerJSON('odisseia-grupos', [])), k = el.dataset.v; if (F.has(k)) F.delete(k); else F.add(k); guardar('odisseia-grupos', JSON.stringify([...F])); render(); },
    'cat-nova-t': () => { S.novaCat = S.novaCat == null ? '' : null; render(); if (S.novaCat != null) { const c = $('#cat-nova-t'); if (c) c.focus(); } },
    'cat-nova-criar': async el => {
      const t = S.e.titulos.find(x => x.id === S.folha.id), nome = (S.novaCat || '').trim();
      if (!nome) { toast('Escreva o nome da categoria.'); const c = $('#cat-nova-t'); if (c) c.focus(); return; }
      el.disabled = true;
      try {
        const r = await api.post('categorias', { acao: 'nova', tipo: t.tipo, nome });
        S.e.categorias = r.categorias;
        const c = r.categorias[t.tipo].find(x => x.nome === nome) || r.categorias[t.tipo][r.categorias[t.tipo].length - 1];
        S.novaCat = null;
        await mudar(t.id, { categoria: c.id });
        if (S.folha && S.folha.tipo === 'cat-titulo') fecharFolha();
      } catch (err) { el.disabled = false; toast(err.message); }
    },
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
      try { const r = await api.post('titulo', { acao: 'atualizar', id: el.dataset.id }); trocar(r.titulo); toast(r.titulo.tipo === 'livro' ? 'Atualizado pela Open Library.' : `Atualizado pelo ${r.titulo.tipo === 'jogo' ? 'IGDB' : 'TMDB'}.`); render(); } catch (err) { el.disabled = false; toast(err.message); }
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
    'vistos-filtros': () => { guardar('odisseia-vistos-filtros', guardada('odisseia-vistos-filtros') === 'fechado' ? 'aberto' : 'fechado'); render(); },
    'b-limpar': () => { S.busca.texto = ''; render(); },
    'ver-quero': el => { S.busca.situacao = 'quero'; S.busca.texto = ''; S.busca.tipo = el.dataset.v || ''; salvarBusca(); ir('buscar'); },
    'lado-sit': el => { S.busca.texto = ''; S.busca.situacao = el.dataset.v; salvarBusca(); S.tela === 'buscar' ? render() : ir('buscar'); },
    'ir-config': el => { if (el.dataset.v) { S.aba = el.dataset.v; guardar('odisseia-aba', S.aba); } if (S.folha) { S.folha = null; S.folhas = []; history.replaceState({ t: S.tela }, ''); } ir('config'); },
    sobre: () => ir('sobre'),
    hist: el => { S.hist = el.dataset.v; guardar('odisseia-vistos', S.hist); S.sel = null; if (history.state && history.state.sel) history.replaceState({ t: S.tela }, ''); render(); },
    'v-cat': el => { S.vcat[S.hist] = el.dataset.v; const ab = VISTOS.find(([k]) => k === S.hist && ligados().includes(k)); if (!ab) S.vcat[(VISTOS.find(([k]) => ligados().includes(k)) || [''])[0]] = el.dataset.v; guardar('odisseia-vistos-cat', JSON.stringify(S.vcat)); render(); },
    modo: el => { guardar('odisseia-modo', el.dataset.v); render(); },
    'sel-comecar': () => { S.sel = new Set(); history.pushState({ t: S.tela, sel: 1 }, ''); render(); },
    'sel-fim': () => { if (history.state && history.state.sel) history.back(); else { S.sel = null; render(); } },
    'sel-marcar': el => { const id = el.dataset.id; if (S.sel.has(id)) S.sel.delete(id); else S.sel.add(id); render(); },
    'sel-todos': () => { const todos = S.podem.length && S.podem.every(id => S.sel.has(id)); S.sel = new Set(todos ? [] : S.podem); render(); },
    'sel-alterar': () => { S.lote = { cat: MANTER, quem: null }; abrirFolha({ tipo: 'lote' }); },
    'sel-apagar': async el => {
      const ids = [...S.sel];
      if (!ids.length) return;
      el.disabled = true;
      try {
        const r = await api.post('titulo', { acao: 'apagar_varios', ids });
        S.e.titulos = S.e.titulos.filter(t => !ids.includes(t.id));
        S.e.rev = r.rev;
        if (history.state && history.state.sel) history.back(); else { S.sel = null; render(); }
        toast(plural(r.apagados.length, 'título apagado', 'títulos apagados'), { rotulo: 'Desfazer', fazer: async () => {
          try { const v = await api.post('titulo', { acao: 'restaurar', titulos: r.apagados }); v.titulos.forEach(trocar); S.e.rev = v.rev; render(); toast('Desfeito.'); } catch (err) { toast(err.message); }
        } });
      } catch (err) { el.disabled = false; toast(err.message); }
    },
    'lote-cat': el => { S.lote.cat = el.dataset.v; render(); },
    'lote-quem': el => {
      const v = el.dataset.v, L = S.lote, todos = S.e.pessoas.map(p => p.id);
      if (v === MANTER) L.quem = null;
      else if (v === '__ninguem__') L.quem = [];
      else if (v === '__todos__') L.quem = L.quem && todos.every(p => L.quem.includes(p)) ? [] : todos;
      else { const q = L.quem || []; L.quem = q.includes(v) ? q.filter(x => x !== v) : [...q, v]; }
      render();
    },
    'lote-aplicar': async el => {
      const L = S.lote, itens = [], antes = [];
      for (const t of S.e.titulos.filter(x => S.sel.has(x.id))) {
        const c = {}, b = {};
        if (L.cat !== MANTER && L.cat !== (t.categoria || '')) { c.categoria = L.cat; b.categoria = t.categoria || ''; }
        if (L.quem && (L.quem.length !== t.quem.length || L.quem.some(p => !t.quem.includes(p)))) { c.quem = L.quem; b.quem = t.quem; }
        if (Object.keys(c).length) { itens.push({ id: t.id, campos: c }); antes.push({ id: t.id, campos: b }); }
      }
      if (!itens.length) { fecharFolha(); toast('Nada mudou.'); return; }
      el.disabled = true;
      try {
        const r = await api.post('titulo', { acao: 'lote', itens });
        r.titulos.forEach(trocar);
        S.e.rev = r.rev;
        S.sel = new Set();
        fecharFolha();
        toast(plural(r.titulos.length, 'título alterado', 'títulos alterados'), { rotulo: 'Desfazer', fazer: async () => {
          try { const v = await api.post('titulo', { acao: 'lote', itens: antes }); v.titulos.forEach(trocar); S.e.rev = v.rev; render(); toast('Desfeito.'); } catch (err) { toast(err.message); }
        } });
      } catch (err) { el.disabled = false; toast(err.message); }
    },
    aba: el => { S.aba = el.dataset.v; S.conf = ''; guardar('odisseia-aba', S.aba); render(); },
    tema: el => { S.tema = el.dataset.v; guardar('odisseia-tema', S.tema); aplicarTema(); render(); },
    cor: async el => { try { S.e.ajustes = (await api.post('ajustes', { cor: el.dataset.v })).ajustes; aplicarCor(); render(); } catch (err) { toast(err.message); } },
    aj: async el => {
      const k = el.dataset.k;
      try {
        S.e.ajustes = (await api.post('ajustes', { [k]: !S.e.ajustes[k] })).ajustes;
        if (k === 'correria') S.e.correria.ligado = S.e.ajustes.correria;
        if (k === 'ia') { if (!S.e.ajustes.ia && S.folha && S.folha.tipo === 'conversa') { pararFala(); fecharFolha(); } carregarIA(); }
        aplicarCor();
        render();
      } catch (err) { toast(err.message); }
    },
    'aj-tipo': async el => {
      try { S.e.ajustes = (await api.post('ajustes', { tipos: { [el.dataset.k]: !S.e.ajustes.tipos[el.dataset.k] } })).ajustes; S.add.listas = {}; await carregar(); } catch (err) { toast(err.message); }
    },
    'cat-abrir': el => {
      const k = el.dataset.k, c = el.dataset.id && (S.e.categorias[k] || []).find(x => x.id === el.dataset.id);
      S.catf = { nome: c ? c.nome : '', cor: c ? c.cor : corLivre(S.e.categorias[k] || []) };
      abrirFolha({ tipo: 'categoria', k, id: c ? c.id : '' });
    },
    'cat-cor': el => { S.catf.cor = el.dataset.v; render(); },
    'cat-salvar': async el => {
      const f = S.folha, nome = (S.catf.nome || '').trim();
      if (!nome) { toast('Escreva o nome da categoria.'); const c = $('#cat-nome'); if (c) c.focus(); return; }
      el.disabled = true;
      if (await categorias(f.id ? { acao: 'editar', id: f.id, nome, cor: S.catf.cor } : { acao: 'nova', tipo: f.k, nome, cor: S.catf.cor })) { toast(f.id ? 'Categoria salva.' : 'Categoria criada.'); fecharFolha(); } else el.disabled = false;
    },
    'cat-apagar': async el => { if (await categorias({ acao: 'apagar', id: el.dataset.id })) { toast('Categoria apagada.'); fecharFolha(); } },
    'chave-salvar': async el => {
      const v = ($('#f-chave') || {}).value || '';
      if (!v.trim()) { toast('Cole a chave do TMDB.'); return; }
      el.disabled = true;
      try { S.e.tmdb = (await api.post('tmdb', { chave: v })).tmdb; S.trocarChave = false; toast('Chave do TMDB funcionando.'); render(); } catch (err) { el.disabled = false; toast(err.message); }
    },
    'igdb-salvar': async el => {
      const cid = (($('#f-igdb-id') || {}).value || '').trim(), seg = (($('#f-igdb-segredo') || {}).value || '').trim();
      if (!cid || !seg) { toast('Cole o Client ID e o Client Secret.'); return; }
      el.disabled = true;
      try { S.e.igdb = (await api.post('igdb', { cliente: cid, segredo: seg })).igdb; S.trocarIGDB = false; S.add.listas = {}; toast('Conta do IGDB funcionando.'); render(); } catch (err) { el.disabled = false; toast(err.message); }
    },
    'igdb-trocar': () => { S.trocarIGDB = true; render(); },
    'igdb-cancelar': () => { S.trocarIGDB = false; render(); },
    'igdb-apagar': async () => { try { S.e.igdb = (await api.post('igdb', {})).igdb; S.add.listas = {}; render(); } catch (err) { toast(err.message); } },
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
    const campo = ev.target.closest('[data-campo]');
    if (campo) {
      ev.preventDefault();
      const F = new Set(lerJSON('odisseia-campos', [])), k = campo.dataset.campo;
      if (F.has(k)) F.delete(k); else F.add(k);
      guardar('odisseia-campos', JSON.stringify([...F]));
      render();
      return;
    }
    const dobra = ev.target.closest('[data-dobra]');
    if (dobra) {
      const F = fechadas(), k = dobra.dataset.dobra;
      if (F.has(k)) F.delete(k); else F.add(k);
      guardar('odisseia-fechadas', JSON.stringify([...F]));
      render();
    }
  });
  document.addEventListener('contextmenu', ev => {
    const b = ev.target.closest && ev.target.closest('#app .linha-tit .tit[data-a="abrir"]');
    if (!b || S.sel || !b.closest('.card').querySelector('[data-a="sel-comecar"]')) return;
    ev.preventDefault();
    try { navigator.vibrate && navigator.vibrate(12); } catch (e) { /* sem vibração */ }
    S.sel = new Set([b.dataset.id]);
    history.pushState({ t: S.tela, sel: 1 }, '');
    render();
  });
  document.addEventListener('keydown', ev => {
    if ((ev.key === 'Enter' || ev.key === ' ') && ev.target.matches('[data-dobra]')) { ev.preventDefault(); ev.target.click(); }
    if (ev.key === 'Escape' && S.folha && !(window.__selectSheet && window.__selectSheet.isOpen())) fecharFolha();
    // a Conversa: com teclado de verdade, o Enter envia; no celular, é uma linha nova (o botão envia), como nos outros apps
    if (ev.key === 'Enter' && !ev.shiftKey && ev.target.id === 'conv-texto' && !noCelular() && !ev.isComposing) { ev.preventDefault(); enviarConversa(); }
    if (ev.key === 'Enter' && !ev.shiftKey && ev.target.id === 'mem-texto') { ev.preventDefault(); ACOES['mem-add'](); }
    if (ev.key === 'Enter' && !ev.shiftKey && ev.target.id === 'perg-nova') { ev.preventDefault(); ACOES['perg-add'](); }
    if (ev.key === 'Enter' && !ev.shiftKey && ev.target.classList && ev.target.classList.contains('perg-txt')) { ev.preventDefault(); ev.target.blur(); }
    if (ev.key === 'Enter' && ev.target.id === 'f-chave') { ev.preventDefault(); ACOES['chave-salvar']($('[data-a="chave-salvar"]')); }
    if (ev.key === 'Enter' && ev.target.id === 'f-igdb-segredo') { ev.preventDefault(); ACOES['igdb-salvar']($('[data-a="igdb-salvar"]')); }
    // o nome da categoria: um campo de uma linha só, o Enter salva
    if (ev.key === 'Enter' && !ev.shiftKey && ev.target.id === 'cat-nome') { ev.preventDefault(); ACOES['cat-salvar']($('[data-a="cat-salvar"]')); }
    if (ev.key === 'Enter' && !ev.shiftKey && ev.target.id === 'cat-nova-t') { ev.preventDefault(); ACOES['cat-nova-criar']($('[data-a="cat-nova-criar"]')); }
  });
  document.addEventListener('input', ev => {
    const id = ev.target.id;
    if (id === 'b-texto') { S.busca.texto = ev.target.value; render(); }
    if (id === 'add-q') { S.add.q = ev.target.value; buscarTMDB(); }
    if (id === 'cat-nome' && S.catf) S.catf.nome = ev.target.value;
    if (id === 'cat-nova-t') S.novaCat = ev.target.value;
    if (id === 'perg-nova' && S.ch.editando) S.ch.editando.rascunho = ev.target.value;
    if (ev.target.dataset && ev.target.dataset.edI != null && S.ch.editando) S.ch.editando.lista[Number(ev.target.dataset.edI)] = ev.target.value;
    if (id === 'conv-texto') {  // o botão troca entre o Falar e o Enviar quando o campo fica vazio ou não
      const antes = !S.ch.texto.trim();
      S.ch.texto = ev.target.value;
      if (antes !== !S.ch.texto.trim()) pintarJanela();
    }
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
    const filtro = { 'f-tipo': 'tipo', 'f-sit': 'situacao', 'f-cat': 'categoria', 'f-quem': 'quem' }[id];
    if (id === 'f-cat' && ev.target.value === '__criar') { ev.target.value = S.busca.categoria; ir('categorias'); return; }
    if (filtro) {
      S.busca[filtro] = ev.target.value;
      if (filtro === 'tipo') S.busca.categoria = ''; // as categorias são de cada tipo
      salvarBusca();
      render();
    }
    const k = ev.target.dataset && ev.target.dataset.ajSel;  // 0.7.0: a IA de cada uso
    if (k) {
      api.post('ajustes', { [k]: ev.target.value }).then(r => {
        S.e.ajustes = r.ajustes;
        if (k === 'fala') carregarIA(); else S.ia = Object.assign({}, S.ia, { [k.slice(3)]: ev.target.value });  // o Falar diz com qual vai transcrever
        render();
      }).catch(err => toast(err.message));
    }
    if (id === 'conv-foto-arquivo' && ev.target.files[0]) { lerFoto(ev.target.files[0]); ev.target.value = ''; }
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
