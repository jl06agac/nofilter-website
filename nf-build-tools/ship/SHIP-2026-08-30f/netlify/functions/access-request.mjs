/* Trade access, step 1: email a code. 163 (8 Nov, Codex): moved to Netlify's current function format
   so Netlify can rate-limit it per visitor; the logic is unchanged in _lib/access-request-core.js. With a custom
   path, Netlify no longer serves this at /.netlify/functions/access-request, so the limit cannot be stepped round.
   5 requests a minute per IP. */
import core from './_lib/access-request-core.js';

export default async (req) => {
  const r = await core.handler({ httpMethod: req.method, headers: Object.fromEntries(req.headers), body: await req.text() });
  return new Response(r.body, { status: r.statusCode, headers: r.headers || {} });
};

export const config = {
  path: '/api/access-request',
  rateLimit: { windowLimit: 5, windowSize: 60, aggregateBy: ['ip', 'domain'] },
};
