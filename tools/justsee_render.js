// Render a Just See job in local headless Chromium (software WebGPU) and save the MP4 locally.
// node jsrender.js <render_url> <out.mp4> [shot.png]
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [url, out, shot] = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--disable-http2', '--autoplay-policy=no-user-gesture-required', '--enable-unsafe-webgpu',
    '--enable-features=Vulkan,WebGPU', '--use-vulkan=swiftshader', '--use-webgpu-adapter=swiftshader', '--use-angle=swiftshader',
    '--disable-vulkan-surface', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1000, height: 900 } });
  await p.addInitScript(() => {
    const F = window.File;
    window.File = class extends F {
      constructor(parts, name, opts) { super(parts, name, opts); if (opts && opts.type === 'video/mp4') { window.__files = window.__files || []; window.__files.push(this); } }
    };
  });
  await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  const t0 = Date.now(); let last = '';
  while (Date.now() - t0 < 1500000) {
    await p.waitForTimeout(5000);
    
    const txt = (await p.innerText('body').catch(() => '')).replace(/\s+/g, ' ').slice(0, 160);
    if (txt !== last) { console.log(Math.round((Date.now() - t0) / 1000) + 's', txt); last = txt; }
    if (/Uploading|Download|Open in the editor/.test(txt)) { await p.evaluate(() => { const f = window.__files || []; window.__mp4 = f[f.length - 1]; }); break; }
    if (/Failed|error/i.test(txt) && !/Making your video (Loading|Captions|Render)/.test(txt)) { console.log('PAGE ERROR'); break; }
  }
  const size = await p.evaluate(() => window.__mp4 ? window.__mp4.size : 0);
  if (size) {
    const CH = 1 << 20; const bufs = [];
    for (let i = 0; i < size; i += CH) {
      const b64 = await p.evaluate(async ([i, CH]) => {
        const ab = new Uint8Array(await window.__mp4.slice(i, i + CH).arrayBuffer()); let s = '';
        for (let j = 0; j < ab.length; j += 8192) s += String.fromCharCode.apply(null, ab.subarray(j, j + 8192));
        return btoa(s);
      }, [i, CH]);
      bufs.push(Buffer.from(b64, 'base64'));
    }
    fs.writeFileSync(out, Buffer.concat(bufs)); console.log('SAVED', out, size, 'bytes');
  } else console.log('NO MP4');
  if (shot) await p.screenshot({ path: shot });
  await b.close();
})();
