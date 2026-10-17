// Render frames from the end of the film backwards to JPEGs, until told to stop (a STOP file) or frame `lo`.
import fs from 'fs'; import path from 'path';
const LIB = '/tmp/ext-lemo/repo'; const { openDemo, closeServer } = await import(path.join(LIB, 'core/render/page.mjs'));
const dir = path.join(LIB, 'films/cloak-hull'), out = path.join(dir, 'out/parts/tail'), FPS = 24, TOTAL = 2611, lo = +process.argv[2] || 1306;
const { browser, page } = await openDemo(dir, { w: 1080, h: 1920 }); await page.evaluate(() => { window.MBCAP = 8; });
for (let f = TOTAL - 1; f >= lo; f--) {
  if (fs.existsSync(path.join(out, 'STOP'))) break;
  const fn = path.join(out, `f_${String(f).padStart(5, '0')}.jpg`); if (fs.existsSync(fn)) continue;
  await page.evaluate(t => window.render(t), f / FPS);
  fs.writeFileSync(fn + '.tmp', await page.screenshot({ type: 'jpeg', quality: 95 })); fs.renameSync(fn + '.tmp', fn);
}
await browser.close(); closeServer(); console.log('tail stopped');
