import { readFileSync } from 'node:fs';
const f = process.argv[2] || 'SHIP-2026-09-02d/index.html';
const s = readFileSync(f, 'utf8');
const sum = (re) => { let t = 0, n = 0; for (const m of s.matchAll(re)) { t += m[0].length; n++; } return [n, t]; };
console.log('total bytes', s.length);
console.log('inline <script> blocks [n,bytes]', sum(/<script(?![^>]*\bsrc=)[^>]*>[\s\S]*?<\/script>/g));
console.log('<style> blocks', sum(/<style[^>]*>[\s\S]*?<\/style>/g));
console.log('data: URIs', sum(/data:[a-z\/+.-]+;base64,[A-Za-z0-9+\/=]+/g));
const d = [...s.matchAll(/data:([a-z\/+.-]+);base64,([A-Za-z0-9+\/=]+)/g)].map(m => [m[1], m[2].length]).sort((a, b) => b[1] - a[1]).slice(0, 8);
console.log('largest data URIs', d);
console.log('data:image/svg+xml (url-encoded)', sum(/data:image\/svg\+xml,[^"')]+/g));
console.log('inline svg', sum(/<svg[\s\S]*?<\/svg>/g));
console.log('external scripts', [...s.matchAll(/<script[^>]*\bsrc="([^"]+)"/g)].map(m => m[1]));
console.log('html comments', sum(/<!--[\s\S]*?-->/g));
// per-script sizes
const scripts = [...s.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map((m, i) => [i, m[1].length, m[1].slice(0, 70).replace(/\s+/g, ' ')]);
console.log('scripts:', scripts.length); scripts.sort((a, b) => b[1] - a[1]).slice(0, 12).forEach(x => console.log('  ', x[1], x[0], x[2]));
const styles = [...s.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g)].map((m, i) => [i, m[1].length]);
console.log('styles:', styles.length, styles.sort((a, b) => b[1] - a[1]).slice(0, 6));
// markup only
const markup = s.replace(/<script[\s\S]*?<\/script>/g, '').replace(/<style[\s\S]*?<\/style>/g, '');
console.log('markup only bytes', markup.length);
