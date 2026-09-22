/* rendercheck.js — MV Maker Signal Scan
   Fails the run rather than shipping a broken page.
   Usage: node rendercheck.js [path-to-index.html] [expected-signal-count]  */
const { chromium } = require('playwright');
const path = require('path');
const file = path.resolve(process.argv[2] || 'index.html');
const expected = process.argv[3] ? parseInt(process.argv[3], 10) : null;

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1360, height: 1400 } });
  const errs = [];
  p.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));
  p.on('console', m => { if (m.type() === 'error') errs.push('CONSOLE: ' + m.text()); });
  await p.goto('file://' + file);
  await p.waitForTimeout(800);

  // Broken-interpolation sweep. EXACT match on leaf elements only — never substring:
  // a legitimate signal may contain the word "null" or "undefined" in its prose.
  const bad = await p.evaluate(() => {
    const BAD = new Set(['undefined', 'null', '[object Object]', 'NaN']);
    const out = [];
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
    let n;
    while ((n = w.nextNode())) {
      if (n.tagName === 'SCRIPT' || n.tagName === 'STYLE') continue;
      if (n.children.length) continue;
      const t = (n.textContent || '').trim();
      if (t && BAD.has(t)) out.push(n.tagName + ' :: ' + t);
    }
    return out;
  });

  const a = await p.evaluate(() => ({
    opps: document.querySelectorAll('.ot.op').length,
    threats: document.querySelectorAll('.ot.th').length,
    cus: document.querySelectorAll('.cu').length,
    cards: document.querySelectorAll('.card').length,
    epiChips: document.querySelectorAll('#epichips .chip').length,
    likChips: document.querySelectorAll('#likchips .chip').length,
    matrixCells: document.querySelectorAll('#matrix .cell').length,
    secBars: document.querySelectorAll('#secbars .barrow').length,
    epiBars: document.querySelectorAll('#epibars .barrow').length,
    evButtons: document.querySelectorAll('[data-goto]').length,
    poles: document.querySelectorAll('.pole').length,
    emptyEpis: [...document.querySelectorAll('.epis')].filter(e => !e.children.length).length,
    stamp: (document.getElementById('stamp').textContent || '').length,
    footLen: (document.getElementById('foot').textContent || '').length,
  }));

  const fails = [];
  if (bad.length) fails.push('broken text nodes: ' + JSON.stringify(bad.slice(0, 8)));
  if (a.opps !== 3) fails.push('opportunities ' + a.opps);
  if (a.threats !== 3) fails.push('threats ' + a.threats);
  if (a.cus < 2) fails.push('critical uncertainties ' + a.cus);
  if (expected && a.cards !== expected) fails.push(`cards ${a.cards} != expected ${expected}`);
  if (a.epiChips !== 8) fails.push('episteme chips ' + a.epiChips);
  if (a.likChips !== 5) fails.push('likelihood chips ' + a.likChips);
  if (a.matrixCells !== 9) fails.push('matrix cells ' + a.matrixCells);
  if (a.secBars !== 8) fails.push('sector bars ' + a.secBars);
  if (a.epiBars !== 8) fails.push('episteme bars ' + a.epiBars);
  if (a.poles !== a.cus * 2) fails.push('poles ' + a.poles);
  if (a.emptyEpis) fails.push('cards with no episteme tags: ' + a.emptyEpis);
  if (a.stamp < 40) fails.push('stamp too short');
  if (a.footLen < 400) fails.push('footer too short');
  if (a.evButtons < 20) fails.push('evidence buttons ' + a.evButtons);

  // interaction smoke tests
  await p.click('#epichips .chip'); await p.waitForTimeout(220);
  await p.click('#reset');          await p.waitForTimeout(180);
  await p.click('#matrix .cell');   await p.waitForTimeout(220);
  await p.click('#reset');          await p.waitForTimeout(180);
  await p.click('#viewbtn');        await p.waitForTimeout(280);
  const rows = await p.evaluate(() => document.querySelectorAll('table.data tbody tr').length);
  if (expected && rows !== expected) fails.push(`table rows ${rows} != expected ${expected}`);
  await p.click('#viewbtn');        await p.waitForTimeout(180);
  await p.click('#tbtn');           await p.waitForTimeout(350);
  await p.screenshot({ path: 'shot-dark.png' });
  await p.click('#tbtn');           await p.waitForTimeout(250);
  await p.screenshot({ path: 'shot-top.png' });

  console.log('assertions:', JSON.stringify(a), '| table rows:', rows);
  if (errs.length) { fails.push('js errors'); console.log('JS errors:', errs); }

  await b.close();
  if (fails.length) { console.log('\nRENDER CHECK FAILED:'); fails.forEach(f => console.log('  -', f)); process.exit(1); }
  console.log('\nRENDER CHECK PASSED');
})();
