import { chromium } from 'playwright';
import { serve } from '/home/claude/nfsplit/serve.mjs';

const ROOT = process.argv[2], PORT = 8863;
const PNG = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=', 'base64');

const srv = await serve(ROOT, PORT);
const b = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--no-sandbox', '--disable-dev-shm-usage'],
});

async function page(width, height) {
  const ctx = await b.newContext({ viewport: { width, height } });
  await ctx.route('**/*', async r => {
    const u = r.request().url();
    if (u.startsWith('http://127.0.0.1')) return r.continue();
    const t = r.request().resourceType();
    if (t === 'image') return r.fulfill({ status: 200, contentType: 'image/png', body: PNG });
    if (t === 'media') return r.fulfill({ status: 200, contentType: 'video/mp4', body: Buffer.alloc(0) });
    return r.fulfill({ status: 200, contentType: 'text/plain', body: '' });
  });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e).slice(0, 140)));
  p.on('console', m => { if (m.type() === 'error') errs.push(m.text().slice(0, 140)); });
  return { ctx, p, errs };
}

// 1 · deep link straight to a question
{
  const { ctx, p, errs } = await page(1440, 1150);
  await p.goto(`http://127.0.0.1:${PORT}/faqs#certification`, { waitUntil: 'load' });
  await p.waitForTimeout(2200);
  const g = await p.evaluate(() => ({
    openItems: [...document.querySelectorAll('.nf-faq-item[open]')].map(i => i.id),
    openGroups: [...document.querySelectorAll('.nf-faq-group[open]')].map(i => i.id),
    y: Math.round(document.getElementById('certification').getBoundingClientRect().top),
  }));
  console.log('deep link /faqs#certification ->', JSON.stringify(g), 'errors', errs.length);
  await p.screenshot({ path: '/tmp/faq-ra.png' });
  await ctx.close();
}

// 2 · mutual exclusion of the six categories
{
  const { ctx, p, errs } = await page(1440, 1000);
  await p.goto(`http://127.0.0.1:${PORT}/faqs`, { waitUntil: 'load' });
  await p.waitForTimeout(1200);
  const before = await p.$$eval('.nf-faq-group[open]', n => n.length);
  await p.evaluate(() => { document.getElementById('grp-buying').open = true; });
  await p.waitForTimeout(400);
  const after = await p.evaluate(() => [...document.querySelectorAll('.nf-faq-group[open]')].map(n => n.id));
  console.log('categories open at load', before, '| after opening 03 ->', JSON.stringify(after), 'errors', errs.length);
  await ctx.close();
}

// 3 · mobile
{
  const { ctx, p, errs } = await page(390, 900);
  await p.goto(`http://127.0.0.1:${PORT}/faqs`, { waitUntil: 'load' });
  await p.waitForTimeout(1400);
  const g = await p.evaluate(() => ({
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    smallestTap: Math.min(...[...document.querySelectorAll('.nf-faq-item>summary')]
      .map(s => Math.round(s.getBoundingClientRect().height))),
  }));
  console.log('mobile 390px ->', JSON.stringify(g), 'errors', errs.length);
  await p.screenshot({ path: '/tmp/faq-mobile.png', fullPage: false });
  await ctx.close();
}

// 4 · every answer present with JavaScript disabled
{
  const ctx = await b.newContext({ viewport: { width: 1200, height: 900 }, javaScriptEnabled: false });
  const p = await ctx.newPage();
  await p.goto(`http://127.0.0.1:${PORT}/faqs`, { waitUntil: 'domcontentloaded' });
  const g = await p.evaluate(() => 0).catch(() => null);
  const txt = await p.content();
  const has = ['sets standards for how certified farms are managed',
               'Where demand lands matters',
               'no separate office, café, hotel or zoo tariff',
               'Service on schedule, not on complaint'].map(s => txt.includes(s));
  console.log('with JS OFF, answers present in the HTML ->', JSON.stringify(has));
  await ctx.close();
}

await b.close(); srv.close();
