// Check the page against the numbers in the brief rather than against my
// impression of it. Every line prints PASS/FAIL and the measurement.
import { chromium } from 'playwright';
import { serve } from '/home/claude/nfsplit/serve.mjs';

const ROOT = process.argv[2], PORT = 8881;
const PNG = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=', 'base64');
const srv = await serve(ROOT, PORT);
const b = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--no-sandbox', '--disable-dev-shm-usage'],
});
const out = [];
const say = (ok, label, detail) => out.push(`${ok ? 'PASS' : 'FAIL'}  ${label.padEnd(48)} ${detail}`);

async function ctxFor(w, h) {
  const ctx = await b.newContext({ viewport: { width: w, height: h }, reducedMotion: 'reduce' });
  await ctx.route('**/*', async r => {
    if (r.request().url().startsWith('http://127.0.0.1')) return r.continue();
    const t = r.request().resourceType();
    if (t === 'image') return r.fulfill({ status: 200, contentType: 'image/png', body: PNG });
    return r.fulfill({ status: 200, contentType: 'text/plain', body: '' });
  });
  return ctx;
}

const ctx = await ctxFor(1440, 1100);
const p = await ctx.newPage();
const errs = [];
p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
p.on('console', m => { if (m.type() === 'error') errs.push(m.text().slice(0, 120)); });
await p.goto(`http://127.0.0.1:${PORT}/faqs`, { waitUntil: 'load' });
await p.waitForTimeout(1600);
await p.evaluate(() => document.querySelectorAll('.nf-faq-group').forEach(g => g.open = false));
await p.waitForTimeout(400);

// ── 1 · no photography in the index ─────────────────────────────────────
const idx = await p.evaluate(() => {
  const panel = document.querySelector('.faq-panel');
  const heads = [...document.querySelectorAll('.nf-faq-group>summary')];
  return {
    imgsInHeads: heads.reduce((n, h) => n + h.querySelectorAll('img,picture,video').length, 0),
    plates: document.querySelectorAll('.grp-plate').length,
    ghosts: document.querySelectorAll('.grp-ghost,.grp-plot,.grp-vtx').length,
    heroImgs: document.querySelectorAll('.faq-hero img').length,
    evidence: [...document.querySelectorAll('.faq-ev')].map(f => ({
      q: f.closest('.nf-faq-item').id,
      src: f.querySelector('img').getAttribute('src').split('/').pop(),
    })),
    panelBg: getComputedStyle(panel).backgroundColor,
  };
});
say(idx.imgsInHeads === 0, 'no image in any closed category header', idx.imgsInHeads + ' found');
say(idx.plates === 0, 'category plate elements gone', idx.plates + ' found');
say(idx.ghosts === 0, 'ghost numerals / plot / vertex gone', idx.ghosts + ' found');
say(idx.heroImgs === 1, 'hero keeps exactly one photograph', idx.heroImgs + '');
say(idx.evidence.length === 3, 'three evidence images, inside answers',
    idx.evidence.map(e => e.q + ':' + e.src).join(' '));

// ── 2 · one warm paper, no dark panel ───────────────────────────────────
const tone = await p.evaluate(() => {
  const grps = [...document.querySelectorAll('.nf-faq-group')];
  const closed = grps.map(g => getComputedStyle(g).backgroundColor);
  const borders = grps.map(g => getComputedStyle(g).borderLeftWidth + ' ' + getComputedStyle(g).borderLeftColor);
  grps[1].open = true;
  const openBg = getComputedStyle(grps[1]).backgroundColor;
  const openBorder = getComputedStyle(grps[1]).borderLeftWidth + ' ' + getComputedStyle(grps[1]).borderLeftColor;
  grps[1].open = false;
  return { closed: [...new Set(closed)], borders: [...new Set(borders)], openBg, openBorder,
           page: getComputedStyle(document.getElementById('faq')).backgroundColor,
           hero: getComputedStyle(document.querySelector('.faq-hero')).backgroundColor,
           rules: [...new Set(grps.slice(0, 3).map(g => getComputedStyle(g).borderBottomColor))],
           zoneRule: (() => { const c = getComputedStyle(document.querySelector('.faq-zone'));
             return c.borderTopWidth + ' ' + c.borderTopColor; })(),
           zonePad: (() => { const c = getComputedStyle(document.querySelector('.faq-body'));
             return c.paddingTop + '/' + c.paddingBottom; })(),
           /* the three grounds must be a real descent, not a printing accident:
              measure the luminance gap between them */
           steps: (() => {
             const lum = c => { const [r, g2, b2] = c.match(/\d+/g).map(Number);
               return .2126 * r + .7152 * g2 + .0722 * b2; };
             const hero = lum(getComputedStyle(document.querySelector('.faq-hero')).backgroundColor);
             const zone = lum(getComputedStyle(document.getElementById('faq')).backgroundColor);
             const sheet = lum(getComputedStyle(document.querySelector('.faq-panel')).backgroundColor);
             return { heroToZone: +(hero - zone).toFixed(1), zoneToSheet: +(sheet - zone).toFixed(1),
                      sheetVsHero: +(sheet - hero).toFixed(1) }; })() };
});
say(tone.closed.length === 1 && tone.closed[0] === 'rgba(0, 0, 0, 0)',
    'every closed category on the same sheet', tone.closed.join(','));
say(idx.panelBg === 'rgb(246, 239, 229)', 'file panel #F6EFE5', idx.panelBg);
say(tone.page === 'rgb(221, 209, 193)', 'zone #DDD1C1', tone.page);
say(tone.hero === 'rgb(241, 232, 219)', 'hero #F1E8DB', tone.hero);
say(tone.openBg === 'rgb(239, 231, 217)', 'open category #EFE7D9', tone.openBg);
say(tone.openBorder === '2px rgb(238, 77, 23)', 'open category 2px orange rule', tone.openBorder);
say(tone.borders.length === 1 && /rgba\(0, 0, 0, 0\)/.test(tone.borders[0]),
    'closed categories carry no left rule', tone.borders.join(','));
say(tone.rules.length === 1 && tone.rules[0] === 'rgb(201, 189, 174)',
    'sections separated by #C9BDAE rules', tone.rules.join(','));

say(tone.zoneRule === '1px rgba(238, 77, 23, 0.55)', 'zone opens on a 1px orange hairline', tone.zoneRule);
say(tone.zonePad === '42px/80px', 'zone padding 42/80', tone.zonePad);
say(tone.steps.heroToZone >= 14 && tone.steps.zoneToSheet >= 14 && tone.steps.sheetVsHero > 0,
    'three real steps: hero > zone < sheet, sheet lightest', JSON.stringify(tone.steps));

// ── 3 · one display voice ───────────────────────────────────────────────
const type = await p.evaluate(() => {
  const g = (el, k) => getComputedStyle(el)[k];
  const h1 = document.querySelector('.faq-h1'), t = document.querySelector('.grp-t');
  const q = document.querySelector('.q-t'), meta = document.querySelector('.beat-hd');
  const fam = s => s.split(',')[0].replace(/["']/g, '').trim();
  return {
    h1: { fam: fam(g(h1, 'fontFamily')), w: g(h1, 'fontWeight'), size: Math.round(parseFloat(g(h1, 'fontSize'))) },
    title: { fam: fam(g(t, 'fontFamily')), w: g(t, 'fontWeight'), size: Math.round(parseFloat(g(t, 'fontSize'))),
             ls: g(t, 'letterSpacing') },
    question: { fam: fam(g(q, 'fontFamily')), w: g(q, 'fontWeight'), size: g(q, 'fontSize') },
    meta: { fam: fam(g(meta, 'fontFamily')), size: g(meta, 'fontSize') },
    families: [...new Set([...document.querySelectorAll('#faq *')]
      .map(e => fam(getComputedStyle(e).fontFamily)).filter(Boolean))],
  };
});
say(type.title.fam === type.h1.fam && type.title.w === type.h1.w,
    'category title = hero face and weight', `${type.title.fam} ${type.title.w} vs ${type.h1.fam} ${type.h1.w}`);
say(type.title.size >= 42 && type.title.size <= 50, 'category title 42-50px', type.title.size + 'px');
say(type.h1.size > type.title.size, 'hero still outranks the category', `${type.h1.size} > ${type.title.size}`);
say(type.question.fam === 'Archivo' && type.meta.fam === 'IBM Plex Mono',
    'sans for questions, mono for meta', `${type.question.fam} / ${type.meta.fam}`);
say(type.families.length <= 3, 'three type voices at most', type.families.join(', '));

// ── 4 · question rows unchanged from the last cut ───────────────────────
await p.evaluate(() => { document.querySelector('.nf-faq-group').open = true; });
await p.waitForTimeout(400);
const q = await p.evaluate(() => {
  const rows = [...document.querySelectorAll('.nf-faq-group[open] .nf-faq-item>summary')];
  const c0 = getComputedStyle(rows[0]);
  return {
    radii: [...new Set(rows.map(r => getComputedStyle(r).borderTopLeftRadius))],
    minH: Math.min(...rows.map(r => Math.round(r.getBoundingClientRect().height))),
    cols: [...new Set(rows.map(r => getComputedStyle(r).gridTemplateColumns.split(' ')[0]))],
    rule: c0.borderTopWidth + ' ' + c0.borderTopColor,
    ans: (() => { const c = getComputedStyle(document.querySelector('.nf-faq-group[open] .faq-a'));
      return { max: c.maxWidth, margin: c.marginLeft + '/' + c.marginBottom,
               pad: c.paddingTop + '/' + c.paddingLeft, bl: c.borderLeftWidth + ' ' + c.borderLeftColor }; })(),
  };
});
say(q.radii.every(r => r === '0px'), 'question rows: no border-radius', q.radii.join(','));
say(q.minH >= 62, 'question row min-height 62', q.minH + 'px min');
say(q.cols.length === 1 && q.cols[0] === '52px', 'question grid first column 52px', q.cols.join(','));
say(q.rule === '1px rgba(20, 20, 18, 0.14)', 'question rule rgba(20,20,18,.14)', q.rule);
say(q.ans.max === '740px' && q.ans.margin === '52px/28px' && q.ans.pad === '6px/18px'
    && q.ans.bl === '2px rgb(238, 77, 23)', 'answer 740/52/28/6/18/2px orange', JSON.stringify(q.ans));

// the evidence figure must sit inside the answer column, not spill past it
await p.evaluate(() => { const e = document.getElementById('what-nofilter-does');
  e.closest('.nf-faq-group').open = true; e.open = true; });
await p.waitForTimeout(400);
const ev = await p.evaluate(() => {
  const f = document.querySelector('#what-nofilter-does .faq-ev');
  if (!f) return null;
  const a = f.closest('.faq-a').getBoundingClientRect(), r = f.getBoundingClientRect();
  const i = f.querySelector('img').getBoundingClientRect();
  return { w: Math.round(r.width), inside: r.left >= a.left - 1 && r.right <= a.right + 1,
           ratio: (i.width / i.height).toFixed(2) };
});
say(ev && ev.inside && ev.ratio === '1.78', 'evidence image inside the answer, 16/9', JSON.stringify(ev));

// closed index height: the whole stack should now be brisk
await p.evaluate(() => document.querySelectorAll('.nf-faq-group').forEach(g => g.open = false));
await p.waitForTimeout(300);
const heights = await p.evaluate(() =>
  [...document.querySelectorAll('.nf-faq-group')].map(g => Math.round(g.getBoundingClientRect().height)));
say(heights.every(h => h >= 130 && h <= 210), 'closed category rows 130-210', heights.join(', '));

// ── the two brand devices ──────────────────────────────────────────────
const dev = await p.evaluate(() => {
  const m = getComputedStyle(document.querySelector('.grp-mark'));
  const q = getComputedStyle(document.querySelector('.q-mark'));
  const t = document.querySelector('.faq-trail');
  const mask = x => (x.webkitMaskImage || x.maskImage || '');
  return {
    markIsWordmarkCross: /svg\+xml/.test(mask(m)) && /svg\+xml/.test(mask(q)),
    markColour: m.backgroundColor,
    markSizes: [m.width + 'x' + m.height, q.width + 'x' + q.height],
    trailHidden: t ? getComputedStyle(t).display : 'missing',
    trailAria: t ? t.getAttribute('aria-hidden') : null,
    trailInTabOrder: t ? t.querySelectorAll('a,button,input').length : 0,
  };
});
say(dev.markIsWordmarkCross && dev.markColour === 'rgb(238, 77, 23)',
    'mark is the wordmark cross, in orange', JSON.stringify([dev.markColour, dev.markSizes]));
say(dev.trailAria === 'true' && dev.trailInTabOrder === 0,
    'trail is decorative and out of the reading order', `aria-hidden=${dev.trailAria}`);

say(errs.length === 0, 'console errors', errs.length + (errs.length ? ' ' + errs[0] : ''));
await ctx.close();

// mobile
{
  const c2 = await ctxFor(390, 900);
  const p2 = await c2.newPage();
  await p2.goto(`http://127.0.0.1:${PORT}/faqs`, { waitUntil: 'load' });
  await p2.waitForTimeout(1400);
  const g = await p2.evaluate(() => {
    document.querySelector('.nf-faq-group').open = true;
    const rows = [...document.querySelectorAll('.nf-faq-group[open] .nf-faq-item>summary')];
    return {
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      countHidden: getComputedStyle(document.querySelector('.grp-count')).display === 'none',
      radii: [...new Set(rows.map(r => getComputedStyle(r).borderTopLeftRadius))],
      tap: Math.min(...rows.map(r => Math.round(r.getBoundingClientRect().height))),
      imgsInHeads: [...document.querySelectorAll('.nf-faq-group>summary')]
        .reduce((n, h) => n + h.querySelectorAll('img').length, 0),
    };
  });
  say(g.overflow === 0, 'mobile: no horizontal overflow', g.overflow + 'px');
  say(g.countHidden, 'mobile: question count hidden', String(g.countHidden));
  say(g.radii.every(r => r === '0px'), 'mobile: no pills', g.radii.join(','));
  say(g.tap >= 44, 'mobile: tap target >= 44px', g.tap + 'px');
  say(g.imgsInHeads === 0, 'mobile: no images in the index', g.imgsInHeads + '');
  await p2.screenshot({ path: '/tmp/faq-brief-390.png' });
  await c2.close();
}

console.log(out.join('\n'));
console.log('\n' + out.filter(l => l.startsWith('FAIL')).length + ' failing of ' + out.length);
await b.close(); srv.close();
