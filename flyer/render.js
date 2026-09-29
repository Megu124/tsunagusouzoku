// 入稿データ書き出し: node render.js  (要 playwright)
// 出力: nyuko/ に塗り足し込みPDF・350dpi PNG、プレビューはカット後サイズ
const { chromium } = require('playwright');
const path = require('path');
const MM = 96 / 25.4;
(async () => {
  const b = await chromium.launch();
  for (const side of ['omote', 'ura']) {
    const p = await b.newPage({ viewport: { width: Math.round(216 * MM), height: Math.round(154 * MM) }, deviceScaleFactor: 350 / 96 });
    await p.goto('file://' + path.join(__dirname, `a5-${side}.html`), { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    await p.pdf({ path: `nyuko/a5-${side}.pdf`, width: '216mm', height: '154mm', printBackground: true });
    await p.locator('.sheet').screenshot({ path: `nyuko/a5-${side}-350dpi.png` });
    await p.close();
    const v = await b.newPage({ viewport: { width: Math.round(216 * MM), height: Math.round(154 * MM) }, deviceScaleFactor: 2 });
    await v.goto('file://' + path.join(__dirname, `a5-${side}.html`), { waitUntil: 'networkidle' });
    await v.evaluate(() => document.fonts.ready);
    await v.screenshot({ path: `preview-${side}.png`, clip: { x: 3 * MM, y: 3 * MM, width: 210 * MM, height: 148 * MM } });
    await v.close();
  }
  await b.close();
})();
