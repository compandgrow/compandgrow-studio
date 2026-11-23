// node render.mjs probe t1 t2 ...  -> out/probe.jpg ;  node render.mjs full -> out/frames + out/video.mp4
import { createRequire } from 'module'; const { chromium } = createRequire(import.meta.url)(process.env.PW || 'playwright');
import http from 'http'; import fs from 'fs'; import path from 'path'; import { execSync } from 'child_process';
const dir = path.dirname(new URL(import.meta.url).pathname), out = path.join(dir, 'out');
fs.mkdirSync(out, { recursive: true });
const types = { '.html': 'text/html', '.woff2': 'font/woff2', '.ttf': 'font/ttf' };
const srv = http.createServer((q, r) => { const f = path.join(dir, decodeURIComponent(q.url.split('?')[0])); if (!fs.existsSync(f)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r); }).listen(0);
const port = srv.address().port, FPS = 30, mode = process.argv[2];
const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
pg.on('pageerror', e => console.log('PAGEERR', e.message));
await pg.goto(`http://127.0.0.1:${port}/index.html`); await pg.waitForFunction('window.ready === true');
const stage = await pg.$('#stage'); const shot = async (t, f) => { await pg.evaluate(t => seek(t), t); await stage.screenshot({ path: f, type: 'jpeg', quality: 92 }); };
if (mode === 'probe') {
  const ts = process.argv.slice(3).map(Number); fs.mkdirSync(path.join(out, 'probe'), { recursive: true });
  for (const [i, t] of ts.entries()) await shot(t, path.join(out, 'probe', `p_${String(i).padStart(2, '0')}.jpg`));
  execSync(`ffmpeg -v error -y -pattern_type glob -i '${out}/probe/p_*.jpg' -vf scale=270:-1,tile=${Math.min(ts.length, 6)}x${Math.ceil(ts.length / 6)} -frames:v 1 ${out}/probe.jpg`);
} else {
  const dur = await pg.evaluate('DUR'), n = Math.round(dur * FPS); fs.mkdirSync(path.join(out, 'frames'), { recursive: true });
  for (let i = 0; i < n; i++) await shot(i / FPS, path.join(out, 'frames', `f_${String(i).padStart(5, '0')}.jpg`));
  fs.writeFileSync(path.join(out, 'stamps.json'), JSON.stringify(await pg.evaluate('STAMPS')));
  execSync(`ffmpeg -v error -y -framerate ${FPS} -i ${out}/frames/f_%05d.jpg -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p ${out}/video.mp4`);
}
await b.close(); srv.close(); console.log('done', mode);
