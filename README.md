# Remember

A nostalgic shelf for the ticket stubs you held on to.

People used to keep ticket stubs in a drawer: the concert, the film, the match, the
one-off night you never forgot. **Remember** is that drawer as a single, design-focused
web page. Stubs are filed by kind (Concerts, Movies, Events, One-off), and the
interaction is the one that matters: **tap a stub and it lights up, then expands to pull
out the original ticket** — poster, seats, booking ID and all — with the one line you
wrote about that night tucked underneath. A **Collected / Upcoming** tab keeps the nights
you've already had separate from the ones still ahead.

## The app

[`index.html`](index.html) is the **real, working app** — an installable PWA that runs
entirely in the browser:

- **Add a ticket** with the `+` button: drop a **photo or screenshot of the real ticket**,
  or type the details (title, shelf, date, venue, seats, booking ID, the memory). It's
  filed automatically — past events go to **Collected**, future ones to **Upcoming**.
- **Tap a stub** to light it up. If you added a photo, you see *that* photo; if you typed
  the details, you get a faithful recreation of the M-ticket (QR for upcoming, an
  "Attended" stamp for past).
- **Your stubs live on your device** (IndexedDB) — no account, no server, nothing leaves
  the browser. **Export / Import** a `.json` backup from the `⋯` menu to move between
  devices.
- **Light / dark** theme toggle, **installable** (Add to Home Screen), works offline.

First run is seeded with sample tickets so the shelf isn't empty — clear them anytime from
the banner or the menu.

## Design directions

[`directions.html`](directions.html) holds the three static explorations behind the app —
same memories, three feelings:

| | Direction | The feeling |
|---|---|---|
| **A** | [The Vintage Shelf, light](variant-a-shelf.html) | Warm paper, torn stubs on a slight tilt, a soft amber glow. The drawer itself. |
| **B** | [The Vintage Shelf, dark](variant-b-shelf-dark.html) | The same shelf after dark. Same stubs, same amber glow, on warm near-black. The app's default. |
| **C** | [The Editorial Wall](variant-c-editorial.html) | Oversized type, a filed grid, an electric accent. The stubs as a printed index. |

## Brand

The mark is an **R** with a hand-sketched brain (memory) and a terracotta fullstop —
`logo.png` / `logo-light.png` / `logo-mark.png` (transparent), with `icon.svg` and the
PWA icons generated from it. Regenerate any size with [`shot.html`](shot.html).

## How it works

- Each file is **fully self-contained**: inline CSS and JS, no build step or dependencies
  to view. Fonts load from Google Fonts ([Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk)
  for display, Space Mono for the serials and dates).
- On the shelf, each ticket is a skeuomorphic **stub**: a perforated tear edge, a barcode,
  a monospace serial. Tap it and it glows, then expands into a faithful recreation of the
  **original M-ticket** (poster, format, screen, seats, booking ID, amount).
- Because the event has already passed, the QR is replaced by an **"Attended"** rubber
  stamp. Tickets in the **Upcoming** tab are still valid, so they keep their QR and show a
  live countdown.
- The single per-stub interaction is `tap to glow + expand`. It is accessible (real button
  semantics, keyboard support, `aria-expanded`) and honours `prefers-reduced-motion`.
- The sample tickets are real, recognisable events so the shelf feels alive on first load.

## The product idea

The variants are the **library page** of a larger app. The full vision: you add a stub by
**uploading a photo, dropping a screenshot, or pasting a shareable link**, Remember pulls
out the event, the date and the venue, and files it on the right shelf. Lightweight,
straightforward, and built to be looked at.

## Editing the tickets

All three variants are generated from one shared ticket set so the content stays in sync.
Edit the `TICKETS` list at the top of [`scripts/build.py`](scripts/build.py) and run:

```bash
python3 scripts/build.py
```

That rewrites the three `variant-*.html` files. To preview locally:

```bash
python3 -m http.server 4730
# open http://localhost:4730/
```
