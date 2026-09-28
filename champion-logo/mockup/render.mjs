import { chromium } from 'playwright-core';
const [,, shot, w, h, out] = process.argv;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: +w, height: +h } });
p.on('console', m => console.log('console:', m.text()));
p.on('pageerror', e => console.log('pageerror:', e.message));
await p.goto(`http://localhost:8765/scene.html?shot=${shot}&w=${w}&h=${h}`);
await p.waitForFunction('window.__done === true', null, { timeout: 180000 });
await p.screenshot({ path: out });
await b.close();
console.log('saved', out);
