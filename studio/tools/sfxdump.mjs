// node studio/tools/sfxdump.mjs <film dir inside $LIB> <out.json>  (run from $LIB): writes window.SFX (the picture's sound cues)
import fs from 'fs';
const { openDemo, closeServer } = await import(process.cwd() + '/core/render/page.mjs');
const [dir, out] = process.argv.slice(2);
const { browser, page } = await openDemo(dir, { w: 1080, h: 1920 });
const sfx = await page.evaluate(() => ({ dur: window.DUR, sfx: window.SFX, cut: window.CUT }));
fs.writeFileSync(out, JSON.stringify(sfx, null, 1)); console.log(out, sfx.sfx.length, 'cues');
await browser.close(); closeServer();
