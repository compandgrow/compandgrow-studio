// Halftone Dossier engine, adapted for @compandgrow: 1080×1920 vertical, Latin fonts, narrated,
// one-line-or-two English caption bar driven by the film's timeline, SFX cue list exported for the mix.
// Adapted from Lemo-Opuscar styles/halftone-dossier/demo/index.html (helpers, halftone, stamp, paper, wipes, HUD).
// Contract with core/render/*.mjs: window.READY, window.DUR, window.render(t).
export const W = 1080, H = 1920;
export const NS = 'http://www.w3.org/2000/svg';
export const C = {
  paper: '#F4ECDD', navy: '#1D2340', blue: '#2E55D6', pink: '#FF5A87', yellow: '#FFC628',
  cream: '#FFF4E2', red: '#E8384F', night: '#18203F', night2: '#2A3568', steel: '#8E9BB5',
};
export const F = {
  slab: "'Alfa Slab One'", bagel: "'Bagel Fat One'", mono: "'JetBrains Mono'", sans: "'Archivo'", cute: "'Chewy'",
};
export const FAMS = ['400 50px "Alfa Slab One"', '400 50px "Bagel Fat One"', '800 50px "JetBrains Mono"', '900 50px "Archivo"', '700 50px "Archivo"', '400 50px "Chewy"'];

export function el(tag, attrs = {}, parent) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}
export function txt(parent, str, attrs) { const e = el('text', attrs, parent); e.textContent = str; return e; }
export function tf(e, x = 0, y = 0, s = 1, r = 0, sy) {
  e.setAttribute('transform', `translate(${x.toFixed(2)} ${y.toFixed(2)}) rotate(${r.toFixed(2)}) scale(${s.toFixed(4)} ${(sy ?? s).toFixed(4)})`);
}
export function op(e, o) { e.setAttribute('opacity', Math.max(0, Math.min(1, o)).toFixed(3)); }
export function show(e, v) { e.style.display = v ? '' : 'none'; }
export const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const seg = (t, a, b) => clamp((t - a) / (b - a));
export const lerp = (a, b, p) => a + (b - a) * p;
export const E = {
  out: p => 1 - Math.pow(1 - p, 3),
  in: p => p * p * p,
  io: p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2,
  back: p => { const c = 1.9; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); },
};
export const pop = (t, t0, d = 0.35) => t < t0 ? 0 : E.back(seg(t, t0, t0 + d));
export function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const mctx = document.createElement('canvas').getContext('2d');
export function measure(str, size, family, weight = 900) { mctx.font = `${weight} ${size}px ${family}`; return mctx.measureText(str).width; }

// ---------- sound cues: the picture registers them, the mix reads window.SFX ----------
export const SFX = [];
export function sfx(t, kind, gain = 1, extra = {}) { SFX.push({ t: +t.toFixed(3), kind, gain, ...extra }); return t; }

// ---------- per-character text ----------
export function chars(parent, str, o) {
  const { x, y, size, family, weight = 400, fill = C.navy, anchor = 'start', ls = 0, shadow, stroke, sw = 0 } = o;
  const g = el('g', {}, parent);
  const arr = [...str];
  const widths = arr.map(c => measure(c, size, family, weight));
  const total = widths.reduce((a, b) => a + b, 0) + ls * (arr.length - 1);
  let cx = anchor === 'middle' ? x - total / 2 : anchor === 'end' ? x - total : x;
  const items = arr.map((ch, i) => {
    const cg = el('g', {}, g);
    const base = { x: 0, y: 0, 'font-size': size, 'font-family': family, 'font-weight': weight, 'text-anchor': 'middle' };
    if (shadow) txt(cg, ch, { ...base, x: shadow.dx, y: shadow.dy, fill: shadow.fill, class: 'mul' });
    const st = stroke ? { stroke, 'stroke-width': sw, 'paint-order': 'stroke', 'stroke-linejoin': 'round' } : {};
    txt(cg, ch, { ...base, fill, ...st });
    const it = { g: cg, x: cx + widths[i] / 2, y, w: widths[i], size };
    cx += widths[i] + ls;
    tf(cg, it.x, it.y);
    return it;
  });
  return { g, items, total };
}
export function charsPop(c, t, t0, stagger = 0.03, d = 0.34, from = 50) {
  c.items.forEach((it, i) => {
    const s = t0 + i * stagger;
    const p = seg(t, s, s + d);
    const h = it.size * 0.35;
    if (t < s) { op(it.g, 0); return; }
    op(it.g, 1);
    const sc = E.back(p);
    const sq = 1 + 0.25 * Math.sin(p * Math.PI) * (1 - p);
    it.g.setAttribute('transform', `translate(${it.x} ${it.y + from * (1 - E.out(p))}) translate(0 ${-h}) scale(${(sc / sq).toFixed(3)} ${(sc * sq).toFixed(3)}) translate(0 ${h})`);
  });
}

// ---------- halftone ----------
export function halftone(parent, { x0 = 0, y0 = 0, w = W, h = H, step = 22, angle = 15, color, f, maxK = 0.62 }) {
  const a = angle * Math.PI / 180, ca = Math.cos(a), sa = Math.sin(a);
  const n = Math.ceil(Math.hypot(w, h) / step / 2) + 2;
  let d = '';
  for (let i = -n; i <= n; i++) for (let j = -n; j <= n; j++) {
    const u = i * step, v = j * step;
    const x = x0 + w / 2 + u * ca - v * sa, y = y0 + h / 2 + u * sa + v * ca;
    if (x < x0 - step || x > x0 + w + step || y < y0 - step || y > y0 + h + step) continue;
    const s = clamp(f(x, y)); if (s < 0.05) continue;
    const r = s * step * maxK;
    d += `M${(x - r).toFixed(1)} ${y.toFixed(1)}a${r.toFixed(1)} ${r.toFixed(1)} 0 1 0 ${(2 * r).toFixed(1)} 0a${r.toFixed(1)} ${r.toFixed(1)} 0 1 0 ${(-2 * r).toFixed(1)} 0`;
  }
  return el('path', { d, fill: color }, parent);
}
export const radial = (cx, cy, R, pw = 1.2) => (x, y) => Math.pow(clamp(1 - Math.hypot(x - cx, y - cy) / R), pw);
export const edge = (R = 1100, pw = 1.6) => (x, y) => Math.pow(clamp(Math.hypot((x - W / 2) * 1.5, y - H / 2) / R - 0.35), pw) * 1.3;
export const ramp = (y0, y1, a = .2, b = 1) => (x, y) => a + (b - a) * clamp((y - y0) / (y1 - y0));
export function bg(parent, color) { return el('rect', { x: -200, y: -200, width: W + 400, height: H + 400, fill: color }, parent); }
export function mul(e) { e.setAttribute('class', 'mul'); return e; }

// giant numeral filled flat and overprinted with a halftone clipped to the glyph
let clipN = 0;
export function bigNum(parent, str, { x, y, size = 640, fill = C.yellow, dots = C.pink, anchor = 'end', angle = 25 }) {
  const g = el('g', {}, parent);
  const id = 'numclip' + (clipN++);
  const clip = el('clipPath', { id }, g);
  txt(clip, str, { x, y, 'font-size': size, 'font-family': F.bagel, 'text-anchor': anchor });
  txt(g, str, { x, y, 'font-size': size, 'font-family': F.bagel, fill, 'text-anchor': anchor });
  const hg = el('g', { 'clip-path': `url(#${id})` }, g);
  mul(halftone(hg, { color: dots, step: 20, angle, f: ramp(y - size * .75, y, .2, .95), maxK: .7 }));
  return g;
}

// ---------- caption bar (the spoken line; keyword in the highlight ink) ----------
// text may mark keywords with *stars*: "the *sticky point*".
export function caption(parent, text, { x = 520, y = 1450, size = 44, maxW = 860, dark = false } = {}) {
  const g = el('g', {}, parent);
  const inner = el('g', {}, g);
  // tokens with highlight flags
  const toks = []; let hi = false;
  let prevSpace = true;
  for (const part of text.split('*')) {
    part.split(' ').forEach((w, i) => { if (w) toks.push({ w, hi, glue: i === 0 && !prevSpace && toks.length > 0 }); });
    if (part.length) prevSpace = part.endsWith(' ');
    hi = !hi;
  }
  const join = l => l.map((z, j) => (j && !z.glue ? ' ' : '') + z.w).join('');
  const sp = measure(' ', size, F.sans, 900);
  const lines = [[]]; let lw = 0;
  for (const tk of toks) {
    const tw = measure(tk.w, size, F.sans, 900);
    if (lw > 0 && !tk.glue && lw + sp + tw > maxW) { lines.push([]); lw = 0; }
    lines[lines.length - 1].push(tk); lw += (lw > 0 && !tk.glue ? sp : 0) + tw;
  }
  // balance two lines
  if (lines.length === 2) {
    const all = [...lines[0], ...lines[1]]; let best = null;
    for (let k = 1; k < all.length; k++) {
      const a = all.slice(0, k), b = all.slice(k);
      if (b[0].glue) continue;
      const wa = measure(join(a), size, F.sans, 900), wb = measure(join(b), size, F.sans, 900);
      if (Math.max(wa, wb) <= maxW && (!best || Math.max(wa, wb) < best.m)) best = { m: Math.max(wa, wb), a, b };
    }
    if (best) { lines[0] = best.a; lines[1] = best.b; }
  }
  lines.forEach(l => { if (l[0]) l[0] = { ...l[0], glue: true }; });
  const widths = lines.map(l => measure(join(l), size, F.sans, 900));
  const w = Math.max(...widths), lh = size * 1.22, padX = 32, padY = size * .42;
  const hgt = lh * lines.length + padY * 2 - (lh - size);
  el('rect', { x: -w / 2 - padX + 8, y: -hgt / 2 + 8, width: w + padX * 2, height: hgt, rx: 16, fill: C.pink, class: 'mul' }, inner);
  el('rect', { x: -w / 2 - padX, y: -hgt / 2, width: w + padX * 2, height: hgt, rx: 16, fill: dark ? C.cream : C.navy }, inner);
  lines.forEach((l, i) => {
    const t = el('text', { x: -widths[i] / 2, y: -hgt / 2 + padY + size * .8 + i * lh, 'font-size': size, 'font-family': F.sans, 'font-weight': 900 }, inner);
    l.forEach((tk, j) => { const s = el('tspan', { fill: tk.hi ? (dark ? C.red : C.yellow) : (dark ? C.navy : C.cream) }, t); s.textContent = (j && !tk.glue ? ' ' : '') + tk.w; });
  });
  return { g, inner, x, y, hgt };
}
export function captionAnim(c, t, t0, t1) {
  if (t < t0 || t >= t1) { op(c.g, 0); return; }
  const p = seg(t, t0, t0 + 0.32);
  op(c.g, seg(t, t0, t0 + 0.1));
  tf(c.g, c.x, c.y + 30 * (1 - E.out(p)), lerp(0.85, 1, E.back(p)), -1.0 * (1 - p) - 0.5);
}

// ---------- stamp ----------
export function stampEl(parent, str, { size = 150, color = C.red, family = F.sans, padX = 40, padY = 20, border = 11 } = {}) {
  const g = el('g', {}, parent);
  const inner = el('g', { filter: 'url(#stampInk)' }, g);
  const w = measure(str, size, family, 900) + padX * 2, h = size * 1.0 + padY * 2;
  el('rect', { x: -w / 2, y: -h / 2, width: w, height: h, rx: 20, fill: 'none', stroke: color, 'stroke-width': border }, inner);
  el('rect', { x: -w / 2 + border * 1.8, y: -h / 2 + border * 1.8, width: w - border * 3.6, height: h - border * 3.6, rx: 11, fill: 'none', stroke: color, 'stroke-width': border * 0.35 }, inner);
  txt(inner, str, { x: 0, y: size * 0.355, 'font-size': size, 'font-family': family, 'font-weight': 900, fill: color, 'text-anchor': 'middle', 'letter-spacing': 2 });
  return { g, w, h };
}
export function stampAnim(s, t, t0, x, y, rot) {
  if (t < t0 - 0.09) { op(s.g, 0); return; }
  const p = seg(t, t0 - 0.09, t0);
  const after = Math.max(0, t - t0);
  const bounce = 1 + 0.05 * Math.sin(after * 30) * Math.exp(-after * 9);
  op(s.g, p < 1 ? 0.3 + 0.7 * p : 0.93);
  tf(s.g, x, y, lerp(2.6, 1, E.in(p)) * bounce, rot);
}

// ---------- stage ----------
let world, hud, wipe, flash, fade, capL, boilT;
export const scenes = [];
export const SHAKES = [];   // [t0, amp px, dur]
export const FLASHES = [];  // [t0, peak, dur]
export const WIPES = [];    // [cut time, colour]
export const GROOVE = [];   // [a, b] windows with a beat pulse
export const DARK = [];     // [a, b] windows where the HUD inverts
export let FADE = [1e9, 1e9 + 1];
export function setFade(a, b) { FADE = [a, b]; }
export function scene(t0, t1, build) {
  const g = el('g', {}, world);
  const s = { g, t0, t1 };
  s.update = build(g, s) || (() => {});
  scenes.push(s);
  return s;
}
// boil filter only for drawn props
export const BOIL = 'url(#boil)';

export function stageSVG() {
  return `
<svg id="stage" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="boil" x="-10%" y="-10%" width="120%" height="120%">
      <feTurbulence id="boilT" type="fractalNoise" baseFrequency="0.022" numOctaves="2" seed="1" result="w"/>
      <feDisplacementMap in="SourceGraphic" in2="w" scale="5" xChannelSelector="R" yChannelSelector="G" result="d"/>
      <feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="2" seed="4" result="g"/>
      <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -22 15.2" result="gm"/>
      <feComposite in="d" in2="gm" operator="in"/>
    </filter>
    <filter id="stampInk" x="-10%" y="-10%" width="120%" height="120%">
      <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="3" seed="11" result="w"/>
      <feDisplacementMap in="SourceGraphic" in2="w" scale="7" xChannelSelector="R" yChannelSelector="G" result="d"/>
      <feTurbulence type="fractalNoise" baseFrequency="0.55" numOctaves="3" seed="21" result="g"/>
      <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -9 5.9" result="gm"/>
      <feComposite in="d" in2="gm" operator="in"/>
    </filter>
    <clipPath id="frameClip"><rect width="${W}" height="${H}"/></clipPath>
  </defs>
  <g clip-path="url(#frameClip)">
    <g id="cam"><g id="world"></g></g>
    <g id="caps"></g>
    <g id="hud"></g>
    <g id="wipe"></g>
    <rect id="flash" width="${W}" height="${H}" fill="#FFFFFF" opacity="0"/>
    <rect id="fade" width="${W}" height="${H}" fill="${C.navy}" opacity="0"/>
  </g>
</svg>
<canvas id="paper" width="${W}" height="${H}"></canvas>
<canvas id="fx" width="${W}" height="${H}"></canvas>`;
}
export const CSS = `
  @font-face { font-family: 'Alfa Slab One'; src: url('kit/fonts/AlfaSlabOne.woff2') format('woff2'); font-weight: 400; font-display: block; }
  @font-face { font-family: 'Bagel Fat One'; src: url('kit/fonts/BagelFatOne.woff2') format('woff2'); font-weight: 400; font-display: block; }
  @font-face { font-family: 'JetBrains Mono'; src: url('kit/fonts/JetBrainsMono-ExtraBold.woff2') format('woff2'); font-weight: 800; font-display: block; }
  @font-face { font-family: 'Archivo'; src: url('kit/fonts/Archivo-VF.ttf') format('truetype'); font-weight: 100 900; font-stretch: 62% 125%; font-display: block; }
  @font-face { font-family: 'Chewy'; src: url('kit/fonts/Chewy.woff2') format('woff2'); font-weight: 400; font-display: block; }
  html, body { margin: 0; width: ${W}px; height: ${H}px; overflow: hidden; background: #F4ECDD; }
  svg, canvas { position: absolute; left: 0; top: 0; width: ${W}px; height: ${H}px; }
  #paper { mix-blend-mode: multiply; pointer-events: none; }
  #fx { pointer-events: none; }
  .mul { mix-blend-mode: multiply; }`;

// ---------- HUD: case number + chapter chip (top-left), REC + date (top-right) ----------
let hudUpdate = () => {};
export function buildHUD(caseNo, chips, dateStr) {
  const hudG = el('g', {}, hud);
  const Y = 168;   // below the Reels top bar
  const cn = txt(hudG, caseNo, { x: 64, y: Y, 'font-size': 26, 'font-family': F.mono, 'font-weight': 800, 'letter-spacing': 2 });
  const chip = el('g', {}, hudG);
  const chipBg = el('rect', { x: 64, y: Y + 16, height: 46, rx: 7 }, chip);
  const chipA = txt(chip, '', { x: 80, y: Y + 50, 'font-size': 28, 'font-family': F.sans, 'font-weight': 900, 'letter-spacing': 1 });
  const chipB = txt(chip, '', { y: Y + 50, 'font-size': 28, 'font-family': F.sans, 'font-weight': 900 });
  const date = el('g', {}, hudG);
  const dw = measure(dateStr, 30, F.mono, 800) + 62;
  const dateBg = el('rect', { x: W - 64 - dw, y: Y - 30, width: dw, height: 52, rx: 8, fill: 'none', 'stroke-width': 4 }, date);
  const rec = el('circle', { cx: W - 64 - dw + 26, cy: Y - 4, r: 9, fill: C.red }, date);
  const dateT = txt(date, dateStr, { x: W - 64 - dw + 46, y: Y + 7, 'font-size': 30, 'font-family': F.mono, 'font-weight': 800 });
  hudUpdate = (t) => {
    const c = chips.find(c => t >= c[0] && t < c[1]);
    show(hudG, !!c);
    if (!c) return;
    const dark = DARK.some(([a, b]) => t >= a && t < b);
    const ink = dark ? C.cream : C.navy;
    cn.setAttribute('fill', ink);
    chipBg.setAttribute('fill', dark ? C.cream : C.navy);
    chipA.textContent = c[2]; chipA.setAttribute('fill', dark ? C.red : C.yellow);
    chipB.textContent = c[3]; chipB.setAttribute('fill', dark ? C.navy : C.cream);
    const wa = measure(c[2], 28, F.sans), wb = measure(c[3], 28, F.sans);
    chipB.setAttribute('x', 80 + wa + 16);
    chipBg.setAttribute('width', wa + wb + 48);
    dateBg.setAttribute('stroke', ink); dateT.setAttribute('fill', ink);
    op(rec, Math.floor(t * 2) % 2 ? 0.25 : 1);
  };
}

// ---------- captions from the timeline ----------
let caps = [];
export function buildCaptions(subs, opts = {}) {
  caps = subs.map(s => ({ ...s, c: caption(capL, s.text, { ...opts, dark: DARK.some(([a, b]) => s.t0 >= a && s.t0 < b) }) }));
}

// ---------- dot wipe ----------
let wipeUpdate = () => {};
function buildWipe() {
  const dotsG = el('g', {}, wipe);
  const dots = [];
  for (let y = 0; y <= H + 80; y += 80) for (let x = 0; x <= W + 80; x += 80) dots.push({ el: el('circle', { cx: x, cy: y, r: 0 }, dotsG), x, y });
  wipeUpdate = (t) => {
    const w = WIPES.find(([b]) => Math.abs(t - b) < 0.22);
    show(dotsG, !!w);
    if (!w) return;
    dotsG.setAttribute('fill', w[1]);
    const u = (t - w[0] + 0.22) / 0.44;
    dots.forEach(d => {
      const delay = (d.x / W * 0.4 + d.y / H * 0.6) * 0.35;
      const p = clamp((u - delay) / 0.65);
      d.el.setAttribute('r', (Math.sin(p * Math.PI) * 62).toFixed(1));
    });
  };
}

// ---------- paper & grain ----------
function buildPaper() {
  const cv = document.getElementById('paper'), ctx = cv.getContext('2d');
  const r = rng(3);
  const small = document.createElement('canvas'); small.width = 54; small.height = 96;
  const sctx = small.getContext('2d'); const sim = sctx.createImageData(54, 96);
  for (let i = 0; i < sim.data.length; i += 4) { const v = 242 + r() * 13; sim.data[i] = sim.data[i + 1] = sim.data[i + 2] = v; sim.data[i + 3] = 255; }
  sctx.putImageData(sim, 0, 0);
  ctx.imageSmoothingEnabled = true; ctx.drawImage(small, 0, 0, W, H);
  const base = ctx.getImageData(0, 0, W, H);
  for (let i = 0; i < base.data.length; i += 4) {
    const n = (r() - 0.5) * 26;
    base.data[i] = clamp(base.data[i] + n, 0, 255);
    base.data[i + 1] = clamp(base.data[i + 1] + n, 0, 255);
    base.data[i + 2] = clamp(base.data[i + 2] + n - 4, 0, 255);
  }
  ctx.putImageData(base, 0, 0);
  const gr = ctx.createRadialGradient(W / 2, H / 2, 500, W / 2, H / 2, 1150);
  gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(1, 'rgba(120,100,80,0.35)');
  ctx.fillStyle = gr; ctx.fillRect(0, 0, W, H);
  ctx.strokeStyle = 'rgba(140,120,100,0.18)'; ctx.lineWidth = 3;   // horizontal fold of a letter-size file
  ctx.beginPath(); ctx.moveTo(0, H * .52); ctx.lineTo(W, H * .52 + 2); ctx.stroke();
}
function drawFx(frame) {
  const cv = document.getElementById('fx'), ctx = cv.getContext('2d');
  ctx.clearRect(0, 0, W, H);
  const r = rng(1000 + Math.floor(frame / 2));
  ctx.fillStyle = 'rgba(255,248,235,0.75)';
  for (let i = 0; i < 520; i++) { const x = r() * W, y = r() * H, s = 0.6 + r() * 1.8; ctx.beginPath(); ctx.arc(x, y, s, 0, 7); ctx.fill(); }
  ctx.fillStyle = 'rgba(29,35,64,0.25)';
  for (let i = 0; i < 90; i++) { ctx.beginPath(); ctx.arc(r() * W, r() * H, 0.6 + r() * 1.3, 0, 7); ctx.fill(); }
}

// ---------- render ----------
let FPSr = 24, BEATs = 0.5;
export function render(t) {
  const frame = Math.round(t * FPSr);
  boilT.setAttribute('seed', 1 + (Math.floor(t * 10) % 40));
  for (const s of scenes) { const on = t >= s.t0 && t < s.t1; show(s.g, on); if (on) s.update(t); }
  for (const c of caps) captionAnim(c.c, t, c.t0, c.t1);
  let dx = 0, dy = 0;
  for (const [t0, a, d] of SHAKES) if (t >= t0 && t < t0 + d) { const k = 1 - (t - t0) / d; dx += a * k * k * Math.sin(t * 91 + t0); dy += a * k * k * Math.cos(t * 77 + t0 * 3); }
  const inGroove = GROOVE.some(([a, b]) => t >= a && t < b);
  const pulse = inGroove ? 1 + 0.006 * Math.exp(-((t % BEATs) / 0.07)) : 1;
  document.getElementById('cam').setAttribute('transform', `translate(${(dx + W / 2 * (1 - pulse)).toFixed(2)} ${(dy + H / 2 * (1 - pulse)).toFixed(2)}) scale(${pulse.toFixed(4)})`);
  let fl = 0;
  for (const [f, pk, d] of FLASHES) if (t >= f && t < f + d) fl = Math.max(fl, pk * Math.pow(1 - (t - f) / d, 2));
  op(flash, Math.min(fl, .5));
  op(fade, seg(t, FADE[0], FADE[1]));
  hudUpdate(t);
  wipeUpdate(t);
  drawFx(frame);
}

// boot: mount the stage, load fonts, build the film, expose the contract
export async function boot(buildFilm, { dur, fps = 24, beat = 0.5 } = {}) {
  FPSr = fps; BEATs = beat;
  const st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);
  document.body.insertAdjacentHTML('afterbegin', stageSVG());
  world = document.getElementById('world'); hud = document.getElementById('hud'); wipe = document.getElementById('wipe');
  flash = document.getElementById('flash'); fade = document.getElementById('fade'); capL = document.getElementById('caps');
  boilT = document.getElementById('boilT');
  const sample = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,:;!?\'"-–—·×%()/+=';
  await Promise.all(FAMS.map(f => document.fonts.load(f, sample)));
  await document.fonts.ready;
  buildPaper();
  await buildFilm();
  buildWipe();
  window.DUR = dur; window.SFX = SFX; window.render = render;
  const q = new URLSearchParams(location.search);
  render(parseFloat(q.get('t') || '0'));
  window.READY = true;
}
