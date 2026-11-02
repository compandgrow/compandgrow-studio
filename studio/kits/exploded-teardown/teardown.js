// Exploded Teardown kit for @compandgrow (1080×1920 vertical).
// Adapted from Lemo-Opuscar styles/teardown/demo (src/main.js + src/overlay.js): three.js PBR object on a graphite seamless,
// anchored labels (accent index · name · one spec line), perspective dimension lines, monotone camera keys, one-line subtitles.
// Changes for this account and for a 2-core software-GL render budget (SwiftShader, ~0.5 s/frame):
//   W/H = 1080×1920; Latin fonts only (Archivo for names/captions, IBM Plex Mono for specs/numbers);
//   English one-line subtitles centred at y 1500 (above the Reels bottom UI), auto-fit to 960 px, *stars* = accent words;
//   no GTAO / depth of field / bloom / 2× supersampling: MSAA at 1×, an additive "glow" material for emitters, a 2D vignette;
//   RoomEnvironment PMREM instead of the studio HDRI (no download); one 2048 shadow map that follows the camera target;
//   window.MBCAP caps motion-blur sub-frames (accumulated only while the camera moves fast); window.SFX = sound cues for the mix.
// A film: import * as K from './kit/teardown.js'; await K.boot({ dur, build, update }) where update(t) poses the scene and draws overlay marks.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { clamp, lerp, seg, ss, eio, eo, track } from '/core/lib.js';
export { THREE, clamp, lerp, seg, ss, eio, eo };

export const W = 1080, H = 1920;
export const INK = '#f1efe9', DIM = 'rgba(241,239,233,.64)', ACC = '#ff6b3d', LINE = 'rgba(241,239,233,.78)';
export const SANS = '"Archivo", sans-serif', MONO = '"PlexMono", monospace';
export const SAFE = { x0: 60, x1: 1020, y0: 230, y1: 1420, subY: 1500 };
const KITURL = new URL('.', import.meta.url).href;
const CSS = `
@font-face{font-family:"Archivo";src:url(${KITURL}fonts/Archivo-VF.ttf) format("truetype");font-weight:100 900;font-stretch:62% 125%}
@font-face{font-family:"PlexMono";src:url(${KITURL}fonts/IBMPlexMono-Medium.ttf) format("truetype");font-weight:500}
@font-face{font-family:"PlexMono";src:url(${KITURL}fonts/IBMPlexMono-SemiBold.ttf) format("truetype");font-weight:600}
html,body{margin:0;background:#0d0e10;overflow:hidden;width:${W}px;height:${H}px}
#gl,#ov{position:absolute;left:0;top:0;width:${W}px;height:${H}px}`;

// ---------------------------------------------------------------- stage
export let renderer, scene, camera, key, rim, fill, floor, ov, g;
let glCanvas, accCanvas, accCtx;
export async function stage({ fov = 30, ground = ['#383a3f', '#25272b', '#0c0d0f'], centre = [540, 900] } = {}) {
  const st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);
  renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1); renderer.setSize(W, H, false);
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = .95;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  glCanvas = renderer.domElement; glCanvas.id = 'gl'; document.body.appendChild(glCanvas);
  ov = document.createElement('canvas'); ov.id = 'ov'; ov.width = W; ov.height = H; document.body.appendChild(ov); g = ov.getContext('2d');
  scene = new THREE.Scene();
  { // dark graphite seamless: screen-space radial gradient
    const c = document.createElement('canvas'); c.width = W / 4; c.height = H / 4; const x = c.getContext('2d');
    const gr = x.createRadialGradient(centre[0] / 4, centre[1] / 4, 20, centre[0] / 4, centre[1] / 4 + 40, 560);
    gr.addColorStop(0, ground[0]); gr.addColorStop(.45, ground[1]); gr.addColorStop(1, ground[2]);
    x.fillStyle = gr; x.fillRect(0, 0, c.width, c.height);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; scene.background = t;
  }
  const pm = new THREE.PMREMGenerator(renderer);
  scene.environment = pm.fromScene(new RoomEnvironment(), .04).texture; scene.environmentIntensity = .42;
  camera = new THREE.PerspectiveCamera(fov, W / H, 2, 400000);
  key = new THREE.DirectionalLight('#fff1e2', 2.1);
  key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
  key.shadow.bias = -.0004; key.shadow.normalBias = .6; key.shadow.radius = 4;
  scene.add(key, key.target);
  rim = new THREE.DirectionalLight('#dfe9ff', 1.6); scene.add(rim, rim.target);
  fill = new THREE.HemisphereLight('#c9d3e0', '#1a1712', .22); scene.add(fill);
  floor = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.ShadowMaterial({ color: '#000000', opacity: .42 }));
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; floor.scale.set(400000, 400000, 1); scene.add(floor);
  accCanvas = document.createElement('canvas'); accCanvas.width = W; accCanvas.height = H; accCtx = accCanvas.getContext('2d');
  return { renderer, scene, camera };
}

// ---------------------------------------------------------------- materials
export function mats() {
  return {
    foil: new THREE.MeshPhysicalMaterial({ color: '#dfe1e6', metalness: 1, roughness: .34, side: THREE.DoubleSide }),
    balsa: new THREE.MeshStandardMaterial({ color: '#d8b98a', roughness: .82 }),
    wire: new THREE.MeshStandardMaterial({ color: '#b9a99a', metalness: .9, roughness: .35, emissive: ACC, emissiveIntensity: 0 }),
    glow: new THREE.MeshBasicMaterial({ color: '#9c7bff', transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }),
    ghost: new THREE.MeshBasicMaterial({ color: '#cfe3ff', transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide }),
    ghostEdge: new THREE.LineBasicMaterial({ color: '#cfe3ff', transparent: true, opacity: 0 }),
    matte: new THREE.MeshStandardMaterial({ color: '#8d9096', roughness: .7 }),
    dark: new THREE.MeshStandardMaterial({ color: '#3a3d43', roughness: .55, metalness: .3 }),
    glass: new THREE.MeshPhysicalMaterial({ color: '#dfe9f2', metalness: 0, roughness: .04, transparent: true, opacity: .16, side: THREE.DoubleSide, depthWrite: false, clearcoat: 1 }),
    ion: new THREE.MeshBasicMaterial({ color: '#59b4ff' }),
    air: new THREE.MeshStandardMaterial({ color: '#8f949c', roughness: .6 }),
    arrowInk: new THREE.MeshBasicMaterial({ color: '#d9d6cf', transparent: true, opacity: 1 }),
    arrowAcc: new THREE.MeshBasicMaterial({ color: ACC, transparent: true, opacity: 1 }),
  };
}
export const shadowy = (m, cast = true, recv = true) => { m.castShadow = cast; m.receiveShadow = recv; return m; };

// ---------------------------------------------------------------- generic geometry
// a crinkled vertical band along a closed polyline (foil skirt): pts [[x,z],..], heights y0..y1, n segments per edge, rows
export function bandGeometry(pts, y0, y1, n = 16, rows = 3, crinkle = .9, seed = 1) {
  const pos = [], idx = []; let v = 0;
  const h = (a) => { const s = Math.sin(a * 12.9898 + seed * 78.233) * 43758.5453; return s - Math.floor(s) - .5; };
  for (let e = 0; e < pts.length; e++) {
    const [ax, az] = pts[e], [bx, bz] = pts[(e + 1) % pts.length];
    const nx = -(bz - az), nz = bx - ax, L = Math.hypot(nx, nz);
    for (let i = 0; i <= n; i++) for (let r = 0; r <= rows; r++) {
      const u = i / n, w = (i === 0 || i === n) ? 0 : h(e * 1000 + i * 31 + r * 7) * crinkle;
      pos.push(ax + (bx - ax) * u + nx / L * w, y0 + (y1 - y0) * r / rows + (r > 0 && r < rows ? h(i * 13 + r) * crinkle * .6 : 0), az + (bz - az) * u + nz / L * w);
    }
    for (let i = 0; i < n; i++) for (let r = 0; r < rows; r++) {
      const a = v + i * (rows + 1) + r, b = a + rows + 1;
      idx.push(a, b, a + 1, b, b + 1, a + 1);
    }
    v += (n + 1) * (rows + 1);
  }
  const gm = new THREE.BufferGeometry(); gm.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); gm.setIndex(idx); gm.computeVertexNormals();
  return gm;
}
// a cylinder from point a to point b (Vector3), radius r
export function rod(a, b, r, seg = 6) {
  const d = new THREE.Vector3().subVectors(b, a), L = d.length();
  const gm = new THREE.CylinderGeometry(r, r, L, seg, 1, false); gm.translate(0, L / 2, 0);
  const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.normalize());
  gm.applyQuaternion(q); gm.translate(a.x, a.y, a.z); return gm;
}
export function merge(list) {   // merge non-indexed-compatible geometries (positions + normals)
  const gs = list.map(x => x.index ? x.toNonIndexed() : x);
  let n = 0; for (const x of gs) n += x.attributes.position.count;
  const P = new Float32Array(n * 3), N = new Float32Array(n * 3); let o = 0;
  for (const x of gs) { if (!x.attributes.normal) x.computeVertexNormals(); P.set(x.attributes.position.array, o * 3); N.set(x.attributes.normal.array, o * 3); o += x.attributes.position.count; }
  const out = new THREE.BufferGeometry(); out.setAttribute('position', new THREE.BufferAttribute(P, 3)); out.setAttribute('normal', new THREE.BufferAttribute(N, 3)); return out;
}
// arrow along +y of length L (shaft radius r), base at origin
export function arrowGeometry(L, r) {
  const head = Math.min(L * .4, r * 7);
  const sh = new THREE.CylinderGeometry(r, r, L - head, 8); sh.translate(0, (L - head) / 2, 0);
  const hd = new THREE.ConeGeometry(r * 3, head, 12); hd.translate(0, L - head / 2, 0);
  return merge([sh, hd]);
}

// ---------------------------------------------------------------- camera: monotone keys, no overshoot
// keys: [t, [ex,ey,ez], [tx,ty,tz], fov, shiftX, shiftY] (px; + shiftX moves the subject left, + shiftY moves it up)
export function camTrack(keys) {
  const tr = track(keys.map(([t, e, c, f, sx, sy]) => [t, [...e, ...c, f, sx || 0, sy || 0]]));
  return t => { const v = tr(t); return { eye: v.slice(0, 3), tgt: v.slice(3, 6), fov: v[6], sx: v[7], sy: v[8] }; };
}
export function setCam(c) {
  camera.position.set(...c.eye); camera.fov = c.fov; camera.lookAt(...c.tgt);
  const dist = Math.hypot(c.eye[0] - c.tgt[0], c.eye[1] - c.tgt[1], c.eye[2] - c.tgt[2]);
  camera.near = Math.max(1, dist / 400); camera.far = dist * 60 + 2000;
  camera.setViewOffset(W, H, c.sx || 0, c.sy || 0, W, H); camera.updateProjectionMatrix();
  // light rig keeps its relation to the camera: warm key above front-left, cool rim behind
  const A = Math.atan2(c.eye[0] - c.tgt[0], c.eye[2] - c.tgt[2]);
  const R = Math.max(600, dist * .9), [tx, ty, tz] = c.tgt;
  key.position.set(tx + R * Math.sin(A - .9), ty + R * 1.6, tz + R * Math.cos(A - .9)); key.target.position.set(tx, ty, tz);
  rim.position.set(tx + R * Math.sin(A + 2.7), ty + R * .7, tz + R * Math.cos(A + 2.7)); rim.target.position.set(tx, ty, tz);
  const S = Math.max(320, dist * .75); Object.assign(key.shadow.camera, { left: -S, right: S, top: S, bottom: -S, near: 10, far: R * 4 });
  key.shadow.camera.updateProjectionMatrix();
  return dist;
}

// ---------------------------------------------------------------- overlay marks
const v3 = new THREE.Vector3();
export const proj = v => { v3.copy(v).project(camera); return [(v3.x + 1) / 2 * W, (1 - v3.y) / 2 * H, v3.z]; };
export const P = (x, y, z) => new THREE.Vector3(x, y, z);
const fade = (t, a, d = .3) => ss(seg(t, a, a + d));
export let TEXTS = [];
const note = (id, text, x0, y0, x1, y1) => TEXTS.push({ id, text, x0, y0, x1, y1 });

// label: anchor dot + leader (diagonal, then horizontal) + accent index / name / spec. lx,ly = text origin; align left|right
export function label(t, o) {
  const { t0, t1, a, lx, ly, idx, name, spec, id = name, align = 'left', strike = null } = o;
  const dl = eo(seg(t, t0, t0 + .38)), tx = fade(t, t0 + .18, .32), out = 1 - fade(t, t1 - .3, .3);
  if (dl <= 0 || out <= 0 || !a || a[2] > 1) return;
  const [ax, ay] = a, dir = align === 'left' ? 1 : -1, ex = lx - dir * 30;
  g.save(); g.globalAlpha = out;
  g.fillStyle = INK; g.beginPath(); g.arc(ax, ay, 4.5, 0, 7); g.fill();
  g.strokeStyle = 'rgba(241,239,233,.38)'; g.lineWidth = 1.4; g.beginPath(); g.arc(ax, ay, 4.5 + 8 * dl, 0, 7); g.stroke();
  const s1 = Math.hypot(ex - ax, ly - ay), s2 = Math.abs(lx - dir * 12 - ex), len = (s1 + s2) * dl;
  g.strokeStyle = LINE; g.lineWidth = 2; g.beginPath(); g.moveTo(ax, ay);
  if (len <= s1) g.lineTo(ax + (ex - ax) * len / s1, ay + (ly - ay) * len / s1);
  else { g.lineTo(ex, ly); g.lineTo(ex + dir * (len - s1), ly); }
  g.stroke();
  if (tx > 0) {
    g.globalAlpha = out * tx; const dx = (1 - tx) * 10 * dir;
    g.textBaseline = 'alphabetic'; g.shadowColor = 'rgba(0,0,0,.6)'; g.shadowBlur = 10;
    g.font = `600 26px ${MONO}`; const iw = idx ? g.measureText(idx).width + 14 : 0;
    g.font = `600 46px ${SANS}`; const nw = g.measureText(name).width;
    g.font = `500 29px ${MONO}`; const sw = spec ? g.measureText(spec).width : 0;
    const wTot = Math.max(iw + nw, sw);
    const x0 = align === 'left' ? lx : lx - wTot;
    if (o.plate !== false) { g.shadowBlur = 0; g.fillStyle = `rgba(13,14,16,${.55 * tx})`; g.fillRect(x0 - 14 + dx, ly - 30, wTot + 28, spec ? 98 : 60); g.shadowBlur = 10; }
    if (idx) { g.fillStyle = ACC; g.font = `600 26px ${MONO}`; g.textAlign = 'left'; g.fillText(idx, x0 + dx, ly + 5); }
    g.fillStyle = INK; g.font = `600 46px ${SANS}`; g.textAlign = 'left'; g.fillText(name, x0 + iw + dx, ly + 15);
    if (spec) { g.fillStyle = DIM; g.font = `500 29px ${MONO}`; g.fillText(spec, x0 + dx, ly + 56); }
    g.shadowBlur = 0;
    if (strike !== null) {   // a struck-out label (hook: WINGS 0 · ROTOR 0 · FUEL 0)
      const k = eo(seg(t, strike, strike + .25));
      if (k > 0) { g.strokeStyle = ACC; g.lineWidth = 5; g.beginPath(); g.moveTo(x0 - 6, ly + 0); g.lineTo(x0 - 6 + (iw + nw + 12) * k, ly + 0); g.stroke(); }
    }
    if (tx > .99 && out > .99) note(id, name + (spec ? ' ' + spec : ''), x0, ly - 30, x0 + wTot, ly + (spec ? 58 : 20));
  }
  g.restore();
}
// dimension line between world points A,B with extension lines ext [[p,q]..]; text on a dark plate, never upside down
export function dimension(t, o) {
  const { t0, t1, A, B, ext = [], text, sub, id = text, side = -1 } = o;
  const k = eo(seg(t, t0, t0 + .55)), out = 1 - fade(t, t1 - .3, .3);
  if (k <= 0 || out <= 0) return;
  const a = proj(A), b = proj(B); if (a[2] > 1 || b[2] > 1) return;
  const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
  g.save(); g.globalAlpha = out; g.strokeStyle = ACC; g.lineWidth = 2.4; g.lineCap = 'round';
  for (const [p, q] of ext) { const p1 = proj(p), q1 = proj(q); g.beginPath(); g.moveTo(p1[0], p1[1]); g.lineTo(p1[0] + (q1[0] - p1[0]) * k, p1[1] + (q1[1] - p1[1]) * k); g.stroke(); }
  g.beginPath(); g.moveTo(mx + (a[0] - mx) * k, my + (a[1] - my) * k); g.lineTo(mx + (b[0] - mx) * k, my + (b[1] - my) * k); g.stroke();
  const ang = Math.atan2(b[1] - a[1], b[0] - a[0]);
  for (const p of [a, b]) { g.save(); g.translate(p[0], p[1]); g.rotate(ang - Math.PI / 4); g.beginPath(); g.moveTo(-9 * k, 0); g.lineTo(9 * k, 0); g.stroke(); g.restore(); }
  const tA = fade(t, t0 + .35, .3);
  if (tA > 0) {
    let ra = ang; if (ra > Math.PI / 2) ra -= Math.PI; if (ra < -Math.PI / 2) ra += Math.PI;
    g.translate(mx, my); g.rotate(ra); g.globalAlpha = out * tA; g.textAlign = 'center';
    g.font = `600 34px ${MONO}`; const w = g.measureText(text).width;
    const oy = side < 0 ? -52 : 10;
    g.fillStyle = 'rgba(14,15,17,.78)'; g.fillRect(-w / 2 - 12, oy, w + 24, 44);
    g.fillStyle = INK; g.fillText(text, 0, oy + 33);
    if (sub) { g.font = `500 24px ${MONO}`; g.fillStyle = DIM; g.fillText(sub, 0, side < 0 ? oy - 12 : oy + 74); }
    if (tA > .99 && out > .99) note(id, (sub ? sub + ' ' : '') + text, mx - w / 2, my - 60, mx + w / 2, my + 60);
  }
  g.restore();
}
// fit a string to a width: returns the font px
export function fit(text, weight, family, max, px) { g.font = `${weight} ${px}px ${family}`; const w = g.measureText(text).width; return w > max ? Math.floor(px * max / w) : px; }
// screen-space title / big text lines: lines [{text, px, weight, col, y, d}] ; centred
export function textBlock(t, t0, t1, lines, { x = W / 2, align = 'center', id = 'title', immediate = false, family = SANS } = {}) {
  const out = 1 - fade(t, t1 - .35, .35); if (t < t0 - (immediate ? 1e9 : 0) || out <= 0 || t > t1) return;
  g.save(); g.textAlign = align; g.textBaseline = 'alphabetic'; g.shadowColor = 'rgba(0,0,0,.7)'; g.shadowBlur = 18;
  for (const L of lines) {
    const a = immediate ? 1 : fade(t, t0 + (L.d || 0), .4); if (a <= 0) continue;
    const px = fit(L.text, L.weight || 800, L.family || family, L.max || 960, L.px);
    g.globalAlpha = a * out; g.font = `${L.weight || 800} ${px}px ${L.family || family}`; g.fillStyle = L.col || INK;
    g.fillText(L.text, x, L.y + (1 - a) * 14);
    if (L.rule) { g.fillStyle = ACC; const rw = L.rule * eo(seg(t, t0 + (L.d || 0), t0 + (L.d || 0) + .5)); g.fillRect(align === 'center' ? x - rw / 2 : x, L.y + 18, rw, 5); }
    if (a > .99 && out > .99) { const w = g.measureText(L.text).width; note(id + ':' + L.text, L.text, x - (align === 'center' ? w / 2 : 0), L.y - px, x + (align === 'center' ? w / 2 : w), L.y + 10); }
  }
  g.restore();
}
// a stamp that lands with a thud: lines of text in a double accent frame, rotated. tStrike draws a bar through it
export function stamp(t, o) {
  const { t0, t1, x, y, lines, px = 78, rot = -4, col = INK, frame = ACC, tStrike = null, id = lines.join(' '), stagger = null } = o;
  if (t < t0 || t > t1) return;
  const k = seg(t, t0, t0 + .16), out = 1 - fade(t, t1 - .3, .3), sc = 1 + .35 * (1 - eo(k));
  g.save(); g.translate(x, y); g.rotate(rot * Math.PI / 180); g.scale(sc, sc); g.globalAlpha = Math.min(1, k * 2.5) * out;
  g.textAlign = 'center'; g.textBaseline = 'middle';
  const shown = lines.filter((_, i) => !stagger || t >= stagger[i]);
  const fonts = shown.map((s, i) => fit(s, 900, SANS, 900, i === 0 ? px : px * .5));
  let wMax = 0; shown.forEach((s, i) => { g.font = `900 ${fonts[i]}px ${SANS}`; wMax = Math.max(wMax, g.measureText(s).width); });
  const lh = fonts.map(f => f * 1.12), hT = lh.reduce((a, b) => a + b, 0);
  g.fillStyle = 'rgba(12,13,15,.72)'; g.fillRect(-wMax / 2 - 34, -hT / 2 - 24, wMax + 68, hT + 48);
  g.strokeStyle = frame; g.lineWidth = 7; g.strokeRect(-wMax / 2 - 34, -hT / 2 - 24, wMax + 68, hT + 48);
  g.lineWidth = 2.5; g.strokeRect(-wMax / 2 - 22, -hT / 2 - 12, wMax + 44, hT + 24);
  let yy = -hT / 2;
  shown.forEach((s, i) => {
    g.font = `900 ${fonts[i]}px ${SANS}`; g.fillStyle = i === 0 ? col : INK;
    g.fillText(s, 0, yy + lh[i] / 2 + 2);
    yy += lh[i];
  });
  if (tStrike !== null && t > tStrike) { const ks = eo(seg(t, tStrike, tStrike + .22)); g.globalAlpha = out; g.strokeStyle = ACC; g.lineWidth = 12; g.beginPath(); g.moveTo(-wMax / 2 - 50, 6); g.lineTo(-wMax / 2 - 50 + (wMax + 100) * ks, -6); g.stroke(); }
  if (k >= 1 && out > .99) note(id, lines.join(' '), x - wMax / 2 - 34, y - hT / 2 - 24, x + wMax / 2 + 34, y + hT / 2 + 24);
  g.restore();
}
export function vignette(amt = .5) {
  const gr = g.createRadialGradient(W / 2, H * .46, H * .28, W / 2, H * .5, H * .75);
  gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, `rgba(0,0,0,${amt})`);
  g.fillStyle = gr; g.fillRect(0, 0, W, H);
}

// ---------------------------------------------------------------- subtitles: one line, centred at SAFE.subY, *stars* in accent
let SUBS = [];
export function buildCaptions(subs) { SUBS = subs; }
export function subMax() {   // widest caption in px at its fitted size (for the check)
  return SUBS.map(s => { const px = capPx(s.text); g.font = `600 ${px}px ${SANS}`; return { id: s.id, px, w: Math.round(g.measureText(s.text.replace(/\*/g, '')).width) }; });
}
const capPx = text => fit(text.replace(/\*/g, ''), 600, SANS, 960, 50);
function drawSubs(t) {
  if (new URLSearchParams(location.search).has('nosub')) return;
  for (const c of SUBS) {
    if (t < c.t0 || t > c.t1) continue;
    const k = Math.min(fade(t, c.t0, .12), 1 - fade(t, c.t1 - .12, .12));
    const px = capPx(c.text), parts = c.text.split('*');
    g.save(); g.font = `600 ${px}px ${SANS}`; g.textBaseline = 'alphabetic'; g.textAlign = 'left';
    const total = g.measureText(c.text.replace(/\*/g, '')).width; let x = W / 2 - total / 2;
    g.globalAlpha = k; g.shadowColor = 'rgba(0,0,0,.85)'; g.shadowBlur = 16;
    parts.forEach((p, i) => { g.fillStyle = i % 2 ? ACC : INK; g.fillText(p, x, SAFE.subY); x += g.measureText(p).width; });
    g.restore();
    if (k > .99) note('sub:' + c.id, c.text.replace(/\*/g, ''), W / 2 - total / 2, SAFE.subY - px, W / 2 + total / 2, SAFE.subY + 12);
  }
}

// ---------------------------------------------------------------- sound cues for the mix
export const SFX = [];
export const sfx = (t, kind, o = {}) => { SFX.push({ t: +t.toFixed(3), kind, gain: 1, ...o }); return t; };

// ---------------------------------------------------------------- frame + boot
// update(t) poses the 3D scene and returns the camera state { eye, tgt, fov, sy }; marks(t) draws overlay marks.
// Motion blur: when the camera moves more than ~6 px per shutter, up to window.MBCAP (default 8, film may lower) sub-frames are averaged.
let UPDATE, MARKS, CAMF, MBMAX = 3, MBAT = null;
function camSpeed(t) {
  const sh = 1 / 48, a = CAMF(t - sh / 2), b = CAMF(t + sh / 2);
  const d = Math.hypot(a.eye[0] - b.eye[0], a.eye[1] - b.eye[1], a.eye[2] - b.eye[2]) + Math.hypot(a.tgt[0] - b.tgt[0], a.tgt[1] - b.tgt[1], a.tgt[2] - b.tgt[2]) * .5;
  const dist = Math.hypot(a.eye[0] - a.tgt[0], a.eye[1] - a.tgt[1], a.eye[2] - a.tgt[2]);
  return d / dist * H / (2 * Math.tan(a.fov * Math.PI / 360));   // ≈ px of screen motion per shutter
}
function render(t) {
  const sp = camSpeed(t), n = Math.max(1, Math.min(window.MBCAP || 8, MBAT ? MBAT(t) : MBMAX, sp > 6 ? Math.ceil(sp / 6) : 1));
  if (n > 1) {
    accCtx.globalAlpha = 1; accCtx.clearRect(0, 0, W, H);
    for (let i = 0; i < n; i++) { const tt = t + (i / (n - 1) - .5) / 48; setCam(UPDATE(tt)); renderer.render(scene, camera); accCtx.globalAlpha = 1 / (i + 1); accCtx.drawImage(glCanvas, 0, 0); }
    setCam(UPDATE(t));
    g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, W, H); g.globalAlpha = 1; g.drawImage(accCanvas, 0, 0);
  } else {
    setCam(UPDATE(t)); renderer.render(scene, camera);
    g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, W, H);
  }
  TEXTS = [];
  vignette(.55);
  { const gr = g.createLinearGradient(0, SAFE.subY - 140, 0, SAFE.subY + 70);   // soft dark strip under the subtitles
    gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(.6, 'rgba(0,0,0,.38)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(0, SAFE.subY - 140, W, 210); }
  MARKS(t);
  drawSubs(t);
  g.globalAlpha = 1;
}
export async function boot({ dur, build, update, marks, cam, mbMax = 3, mbAt = null }) {
  UPDATE = update; MARKS = marks; CAMF = cam; MBMAX = mbMax; MBAT = mbAt;
  const sample = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,:;!?\'"-–—·×%()/+=≈@';
  await Promise.all([`600 40px Archivo`, `800 40px Archivo`, `900 40px Archivo`, `500 20px PlexMono`, `600 20px PlexMono`].map(f => document.fonts.load(f, sample)));
  await document.fonts.ready;
  if (build) await build();
  window.DUR = dur; window.SFX = SFX; window.render = render; window.TEXTS = () => TEXTS; window.SUBCHECK = () => subMax();
  render(parseFloat(new URLSearchParams(location.search).get('t') || '0'));
  window.READY = true;
}
