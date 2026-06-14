# Remember — link reader (optional)

A ~70-line Cloudflare Worker that powers the **"paste a link"** option in the Add
sheet. The browser can't fetch a BookMyShow / PVR / Insider page directly (CORS),
so this reads the page server-side and returns its Open Graph data (title, date,
venue, poster) for the app to pre-fill. Free tier is plenty (100k requests/day).

It's **optional** — the app works fully without it; the link field just stays hidden
until you point it at a deployed Worker.

## Deploy (one command)

```bash
cd worker
npx wrangler login      # first time only
npx wrangler deploy
```

You'll get a URL like `https://remember-link.<your-subdomain>.workers.dev`.

## Turn it on in the app

Open [`../index.html`](../index.html), find:

```js
var LINK_READER = '';
```

and set it to your Worker URL:

```js
var LINK_READER = 'https://remember-link.your-subdomain.workers.dev';
```

Commit and push. The Add sheet now shows **"Or paste a ticket or event link"**.

## What it does / doesn't do

- **Does**: pull the title, date, venue and poster from a public **event** page and
  pre-fill the form (poster becomes the stub photo).
- **Doesn't**: read your private booking details (seats, booking ID) — those live in
  your ticket, not on the public page. Use a screenshot for those.
- SSRF-guarded (no localhost / private ranges), caps page and image size, and caches
  responses for a few minutes.
