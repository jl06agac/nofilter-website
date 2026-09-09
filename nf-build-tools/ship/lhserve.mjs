// serves a SHIP bundle on :9000 with the shared CDN mapped to local staged copies
import http from 'node:http'; import { gzipSync, brotliCompressSync } from 'node:zlib'; import { readFileSync, existsSync, statSync } from 'node:fs'; import { join } from 'node:path';
const ROOT = '/home/claude/ship/' + (process.argv[2] || 'SHIP-2026-09-02d');
const CDN = '/mnt/user-data/uploads/Desktop/NoFilter/_CDN-UPLOAD-SAFE';
const PORT = +(process.argv[3] || 9000);
const types = { html: 'text/html; charset=utf-8', js: 'text/javascript', css: 'text/css', woff2: 'font/woff2', mp4: 'video/mp4', jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', webp: 'image/webp', svg: 'image/svg+xml', ico: 'image/x-icon', xml: 'application/xml', txt: 'text/plain' };
http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (req.method === 'POST') { res.writeHead(200); return res.end('ok'); }
  let f;
  if (p.startsWith('/cdn/')) {
    f = join(CDN, p.slice(5));
    if (!existsSync(f)) {
      // stand-ins so the page behaves: any missing video → the toru banner, any missing image → the hero poster
      if (/\.mp4$/.test(p)) f = join(CDN, 'batang-toru-banner-lite.mp4');
      else if (/\.(jpg|jpeg|png|webp)$/.test(p)) f = join(CDN, 'hero-poster.jpg');
      else { res.writeHead(404); return res.end(); }
    }
  } else {
    f = join(ROOT, p);
    if (existsSync(f) && statSync(f).isDirectory()) f = join(f, 'index.html');
    if (!existsSync(f)) { res.writeHead(404); return res.end('nf'); }
  }
  const ext = f.split('.').pop();
  let body = readFileSync(f);
  const hdr = { 'Content-Type': types[ext] || 'application/octet-stream', 'Cache-Control': ext === 'html' ? 'no-cache' : 'public, max-age=31536000' };
  if (ext === 'html') body = Buffer.from(body.toString('utf8').split('https://nofilter-shared.netlify.app/').join(`http://localhost:${PORT}/cdn/`));
  const SLOW = +(process.env.SLOW_MBPS || 0);   // pace media at N Mbps to mimic a real CDN
  const paced = (buf, status, h) => { if (!SLOW) { res.writeHead(status, h); return res.end(buf); }
    res.writeHead(status, h); const chunk = 64 * 1024; const delay = chunk * 8 / (SLOW * 1e6) * 1000; let i = 0;
    const tick = () => { if (i >= buf.length) return res.end(); res.write(buf.subarray(i, i + chunk)); i += chunk; setTimeout(tick, delay); }; tick(); };
  if (ext === 'mp4' && req.headers.range) {
    const m = /bytes=(\d+)-(\d*)/.exec(req.headers.range); const a = +m[1], b = m[2] ? +m[2] : body.length - 1;
    return paced(body.subarray(a, b + 1), 206, { ...hdr, 'Content-Range': `bytes ${a}-${b}/${body.length}`, 'Accept-Ranges': 'bytes', 'Content-Length': b - a + 1 });
  }
  if (ext === 'mp4') return paced(body, 200, { ...hdr, 'Content-Length': body.length, 'Accept-Ranges': 'bytes' });
  const ae = req.headers['accept-encoding'] || '';
  if (/^(html|js|css|svg|xml|txt|json)$/.test(ext) && /br|gzip/.test(ae)) {
    const br = /br/.test(ae); const enc = br ? brotliCompressSync(body) : gzipSync(body);
    res.writeHead(200, { ...hdr, 'Content-Encoding': br ? 'br' : 'gzip', 'Content-Length': enc.length, 'Vary': 'Accept-Encoding' }); return res.end(enc);
  }
  res.writeHead(200, { ...hdr, 'Content-Length': body.length, 'Accept-Ranges': 'bytes' }); res.end(body);
}).listen(PORT, () => console.log('serving', ROOT, 'on', PORT));
