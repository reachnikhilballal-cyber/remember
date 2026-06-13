# Remember

A nostalgic shelf for the ticket stubs you held on to.

People used to keep ticket stubs in a drawer: the concert, the film, the match, the
one-off night you never forgot. **Remember** is that drawer as a single, design-focused
web page. Stubs are filed by kind (Concerts, Movies, Events, One-off), and the only
interaction is the one that matters: **tap a stub and it lights up, then expands to show
the one line you wrote about that night.**

## Three directions

This repo ships three complete design directions of the same shelf. Same memories in each,
three different feelings. Open [`index.html`](index.html) to choose, or jump straight in:

| | Direction | The feeling |
|---|---|---|
| **A** | [The Vintage Shelf](variant-a-shelf.html) | Warm paper, torn stubs on a slight tilt, a soft amber glow. The drawer itself. |
| **B** | [The Dark Cinema](variant-b-cinema.html) | A near-black room. Each stub sits unlit until you tap it, then it ignites like a marquee. |
| **C** | [The Editorial Wall](variant-c-editorial.html) | Oversized type, a filed grid, an electric accent. The stubs as a printed index. |

## How it works

- Each file is **fully self-contained**: inline CSS and JS, no build step or dependencies
  to view. Fonts load from Google Fonts ([Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk)
  for display, Space Mono / JetBrains Mono for the serials and dates).
- Tickets are skeuomorphic stubs: a perforated tear edge, a barcode, a monospace serial.
- The single interaction is `tap to glow + expand`. It is accessible (real button
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
