/**
 * Remember — link reader (Cloudflare Worker)
 *
 * The browser app can't fetch a BookMyShow / PVR / Insider page directly (CORS),
 * so this tiny Worker does it server-side and returns the page's Open Graph data
 * plus a stripped text blob the app parses for date / venue / etc.
 *
 * Two modes:
 *   GET ?url=<page>  -> { title, description, image, text }
 *   GET ?img=<image> -> the image bytes (proxied with CORS, so it can become the stub photo)
 *
 * Deploy (free):  cd worker && npx wrangler deploy
 * Then put the resulting https://...workers.dev URL into LINK_READER in index.html.
 */
const ALLOW_ORIGIN = '*'; // tighten to your Pages origin if you prefer

export default {
  async fetch(req) {
    const cors = {
      'Access-Control-Allow-Origin': ALLOW_ORIGIN,
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    if (req.method === 'OPTIONS') return new Response(null, { headers: cors });

    const sp = new URL(req.url).searchParams;
    const target = sp.get('url') || sp.get('img');
    if (!target || !/^https?:\/\//i.test(target)) return json({ error: 'bad url' }, 400, cors);

    let t;
    try { t = new URL(target); } catch { return json({ error: 'bad url' }, 400, cors); }
    // SSRF guard: no localhost / private ranges
    if (/^(localhost|127\.|10\.|0\.|169\.254\.|192\.168\.|\[?::1)/i.test(t.hostname) ||
        /^172\.(1[6-9]|2\d|3[01])\./.test(t.hostname)) return json({ error: 'blocked host' }, 400, cors);

    // image proxy mode
    if (sp.get('img')) {
      try {
        const r = await fetch(t.href, { headers: { 'User-Agent': UA }, redirect: 'follow', cf: { cacheTtl: 3600 } });
        const ct = r.headers.get('content-type') || '';
        if (!r.ok || !/^image\//.test(ct)) return new Response('', { status: 415, headers: cors });
        const buf = await r.arrayBuffer();
        if (buf.byteLength > 8_000_000) return new Response('', { status: 413, headers: cors });
        return new Response(buf, { headers: { ...cors, 'Content-Type': ct, 'Cache-Control': 'public, max-age=3600' } });
      } catch { return new Response('', { status: 502, headers: cors }); }
    }

    // page-read mode
    let html;
    try {
      const r = await fetch(t.href, { headers: { 'User-Agent': UA, Accept: 'text/html,*/*' }, redirect: 'follow', cf: { cacheTtl: 600 } });
      if (!r.ok) return json({ error: 'fetch ' + r.status }, 502, cors);
      html = (await r.text()).slice(0, 600_000);
    } catch { return json({ error: 'fetch failed' }, 502, cors); }

    const meta = (p) => {
      const a = html.match(new RegExp('<meta[^>]+(?:property|name)=["\\\']' + p + '["\\\'][^>]+content=["\\\']([^"\\\']*)', 'i'));
      if (a) return decode(a[1]);
      const b = html.match(new RegExp('<meta[^>]+content=["\\\']([^"\\\']*)["\\\'][^>]+(?:property|name)=["\\\']' + p + '["\\\']', 'i'));
      return b ? decode(b[1]) : '';
    };
    const title = meta('og:title') || decode((html.match(/<title[^>]*>([^<]*)<\/title>/i) || [, ''])[1]).trim();
    const description = meta('og:description') || meta('description');
    const image = meta('og:image') || meta('og:image:secure_url') || meta('twitter:image');
    const text = html
      .replace(/<script[\s\S]*?<\/script>/gi, ' ')
      .replace(/<style[\s\S]*?<\/style>/gi, ' ')
      .replace(/<[^>]+>/g, '\n')
      .replace(/&nbsp;/g, ' ')
      .split('\n').map((s) => s.trim()).filter(Boolean).slice(0, 400).join('\n').slice(0, 8000);

    return json({ title, description, image, text }, 200, cors);
  },
};

const UA = 'Mozilla/5.0 (compatible; RememberBot/1.0; +https://reachnikhilballal-cyber.github.io/remember/)';
function json(o, status, cors) {
  return new Response(JSON.stringify(o), { status: status || 200, headers: { 'Content-Type': 'application/json', ...cors } });
}
function decode(s) {
  return String(s || '')
    .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"').replace(/&#0?39;|&#x27;/gi, "'").replace(/&#x2f;/gi, '/');
}
