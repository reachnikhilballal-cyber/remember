#!/usr/bin/env python3
"""Remember - build the three standalone variant HTMLs from one ticket set.

Run:  python3 scripts/build.py
Emits: variant-a-shelf.html, variant-b-cinema.html, variant-c-editorial.html, index.html
Each output is fully self-contained (inline CSS + JS, fonts via Google Fonts link).
"""
import io, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# One ticket set, shared by all three variants so the design is what differs.
TICKETS = [
    {"cat": "Concerts", "kind": "CONCERT", "title": "Coldplay", "sub": "Music of the Spheres",
     "venue": "Narendra Modi Stadium, Ahmedabad", "date": "26 Jan 2025", "serial": "CP-7741-C14",
     "seat": "Section C14", "note": "Seventy-thousand wristbands turned the stands into a slow galaxy. Fix You at full voice, nobody sat down."},
    {"cat": "Concerts", "kind": "CONCERT", "title": "Diljit Dosanjh", "sub": "Dil-Luminati Tour",
     "venue": "Bengaluru", "date": "08 Dec 2024", "serial": "DL-2210-GA", "seat": "General",
     "note": "The whole ground did bhangra at the same beat. First Punjabi gig that felt like a festival."},
    {"cat": "Concerts", "kind": "CONCERT", "title": "A.R. Rahman", "sub": "Marakkuma Nenjam",
     "venue": "YMCA Grounds, Chennai", "date": "10 Sep 2023", "serial": "ARR-0096-B", "seat": "Block B",
     "note": "Roja melting into Kun Faya Kun. Thirty thousand people, one collective shiver."},
    {"cat": "Movies", "kind": "IMAX 70MM", "title": "Oppenheimer", "sub": "Christopher Nolan",
     "venue": "PVR Orion, Bengaluru", "date": "21 Jul 2023", "serial": "OPP-H7-IMAX", "seat": "Seat H7",
     "note": "Three hours, no break, no popcorn. The silence after the Trinity test was deafening."},
    {"cat": "Movies", "kind": "IMAX", "title": "Dune: Part Two", "sub": "Denis Villeneuve",
     "venue": "PVR, Bengaluru", "date": "01 Mar 2024", "serial": "DUN-F12-X", "seat": "Seat F12",
     "note": "Saw it twice in one week. The Fremen war cry still lives somewhere in my chest."},
    {"cat": "Movies", "kind": "70MM RE-RELEASE", "title": "Interstellar", "sub": "10th Anniversary",
     "venue": "Bengaluru", "date": "16 Nov 2024", "serial": "INT-J9-10Y", "seat": "Seat J9",
     "note": "Cried at the docking scene, again. Hans Zimmer in 70mm is basically a religion."},
    {"cat": "Events", "kind": "IPL", "title": "RCB vs CSK", "sub": "Indian Premier League",
     "venue": "M. Chinnaswamy Stadium, Bengaluru", "date": "18 May 2024", "serial": "RCB-UT-441", "seat": "Upper Tier",
     "note": "Kohli at the boundary rope, forty thousand in red. Lost the game, kept the roar."},
    {"cat": "Events", "kind": "WORLD CUP FINAL", "title": "India vs Australia", "sub": "ICC Cricket World Cup",
     "venue": "Narendra Modi Stadium, Ahmedabad", "date": "19 Nov 2023", "serial": "WC-FIN-2023", "seat": "Lower Block",
     "note": "1.3 lakh people went silent at the same moment. Heartbreak, but what a night to be in the room."},
    {"cat": "One-off", "kind": "STAND-UP", "title": "Zakir Khan", "sub": "Tathastu",
     "venue": "Bengaluru", "date": "04 Mar 2023", "serial": "ZK-M-018", "seat": "Row M",
     "note": "Sakht launda, softened. Laughed till it hurt, then he made the whole hall go quiet."},
    {"cat": "One-off", "kind": "FESTIVAL", "title": "NH7 Weekender", "sub": "The Happiest Music Festival",
     "venue": "Pune", "date": "26 Nov 2022", "serial": "NH7-3DAY-22", "seat": "3-day pass",
     "note": "Found four bands I now love. Mud, filter coffee, and the best sunset set of my life."},
]

ORDER = ["Concerts", "Movies", "Events", "One-off"]
DATA = json.dumps(TICKETS, ensure_ascii=False)

# Shared interaction: tap a ticket -> it glows and expands its one-liner.
# Accessible (button semantics, keyboard, aria-expanded), reduced-motion safe.
TOGGLE_JS = """
  function wire(){
    document.querySelectorAll('.tk').forEach(function(el){
      function toggle(){
        var open = el.classList.toggle('is-open');
        el.setAttribute('aria-expanded', String(open));
      }
      el.addEventListener('click', toggle);
      el.addEventListener('keydown', function(e){
        if(e.key === 'Enter' || e.key === ' '){ e.preventDefault(); toggle(); }
      });
    });
  }
"""

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<meta name="theme-color" content="__THEME__" />
<title>Remember __VTITLE__</title>
<meta name="description" content="Remember, a nostalgic shelf for the ticket stubs you kept. Concerts, movies, events, one-offs. Tap a stub to light it up and read the memory." />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="stylesheet" href="__FONTS__" />
<style>
__CSS__
</style>
</head>
<body>
<a class="skip" href="#shelf">Skip to the shelf</a>
__BODY__
<a class="badge" href="index.html">Remember __VLABEL__</a>
<script>
'use strict';
var TICKETS = __DATA__;
var ORDER = __ORDER__;
__RENDER__
__TOGGLE__
(function(){
  render();
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var io = new IntersectionObserver(function(es){
      es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('seen'); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    document.querySelectorAll('.tk').forEach(function(el){ io.observe(el); });
  } else {
    document.querySelectorAll('.tk').forEach(function(el){ el.classList.add('seen'); });
  }
  wire();
})();
</script>
</body>
</html>
"""

def page(vtitle, vlabel, theme, fonts, css, body, render):
    return (HEAD
        .replace("__VTITLE__", vtitle).replace("__VLABEL__", vlabel)
        .replace("__THEME__", theme).replace("__FONTS__", fonts)
        .replace("__CSS__", css).replace("__BODY__", body)
        .replace("__RENDER__", render).replace("__TOGGLE__", TOGGLE_JS)
        .replace("__DATA__", DATA).replace("__ORDER__", json.dumps(ORDER)))


# =====================================================================
# VARIANT A - THE VINTAGE SHELF  (light, kraft paper, warm amber glow)
# =====================================================================
A_FONTS = "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap"
A_CSS = r"""
:root{
  --paper:#efe7d6; --paper-2:#e7dcc6; --card:#f7f1e3; --ink:#211c15; --ink-2:rgba(33,28,21,.62);
  --ink-3:rgba(33,28,21,.40); --line:rgba(33,28,21,.16); --line-2:rgba(33,28,21,.10);
  --glow:#cf7a2c; --glow-soft:rgba(207,122,44,.30); --stamp:#b23a2e;
  --sans:'Space Grotesk',system-ui,sans-serif; --mono:'Space Mono',ui-monospace,monospace;
  --ease:cubic-bezier(.16,1,.3,1);
}
*{box-sizing:border-box;margin:0;padding:0;}
html{-webkit-text-size-adjust:100%;}
body{
  background:var(--paper);color:var(--ink);font-family:var(--sans);-webkit-font-smoothing:antialiased;line-height:1.5;
  background-image:
    radial-gradient(circle at 18% 12%, rgba(255,255,255,.45), transparent 38%),
    radial-gradient(circle at 86% 84%, rgba(150,120,70,.10), transparent 46%),
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='120' height='120' filter='url(%23n)' opacity='.05'/%3E%3C/svg%3E");
  min-height:100dvh;
}
.skip{position:absolute;left:-999px;}.skip:focus{left:16px;top:16px;background:var(--ink);color:var(--paper);padding:8px 14px;border-radius:8px;z-index:99;}
.wrap{max-width:1080px;margin:0 auto;padding:0 28px;}

/* masthead */
.mast{padding:72px 0 30px;text-align:center;}
.mast .eye{font-family:var(--mono);font-size:11px;letter-spacing:.34em;text-transform:uppercase;color:var(--stamp);}
.mast h1{font-size:clamp(56px,11vw,104px);font-weight:700;letter-spacing:-.04em;line-height:.9;margin-top:10px;}
.mast h1 .dot{color:var(--stamp);}
.mast .sub{margin-top:16px;font-size:clamp(15px,1.7vw,18px);color:var(--ink-2);max-width:46ch;margin-inline:auto;}
.mast .meta{margin-top:18px;font-family:var(--mono);font-size:11px;letter-spacing:.14em;color:var(--ink-3);}
.rule{height:1px;background:repeating-linear-gradient(90deg,var(--line) 0 8px,transparent 8px 16px);margin:8px 0 0;}

/* category section */
.cat{padding:40px 0 8px;}
.cat-h{display:flex;align-items:baseline;gap:14px;margin-bottom:26px;}
.cat-h .n{font-family:var(--mono);font-size:12px;color:var(--stamp);letter-spacing:.1em;}
.cat-h h2{font-size:26px;font-weight:600;letter-spacing:-.01em;}
.cat-h .c{font-family:var(--mono);font-size:12px;color:var(--ink-3);margin-left:auto;}
.shelf{display:grid;grid-template-columns:repeat(2,1fr);gap:26px 28px;}
@media(max-width:720px){.shelf{grid-template-columns:1fr;}}

/* the ticket stub */
.tk{
  position:relative;display:block;width:100%;text-align:left;cursor:pointer;font:inherit;color:inherit;
  background:transparent;border:0;padding:0;
  opacity:0;transform:translateY(16px) rotate(var(--tilt,0deg));
  transition:opacity .7s var(--ease),transform .7s var(--ease),filter .45s var(--ease);
  -webkit-tap-highlight-color:transparent;
}
.tk.seen{opacity:1;transform:translateY(0) rotate(var(--tilt,0deg));}
.tk:nth-child(odd){--tilt:-1.1deg;}.tk:nth-child(even){--tilt:1deg;}
.tk-top{
  position:relative;display:flex;background:var(--card);
  border-radius:10px;overflow:hidden;
  box-shadow:0 1px 0 rgba(255,255,255,.6) inset, 0 14px 30px -18px rgba(33,28,21,.5), 0 1px 2px rgba(33,28,21,.12);
  border:1px solid var(--line-2);
}
.tk:hover{transform:translateY(-2px) rotate(0deg);}
.tk:focus-visible{outline:0;}
.tk:focus-visible .tk-top{outline:2px solid var(--glow);outline-offset:3px;}
/* glow + straighten on open */
.tk.is-open{transform:translateY(0) rotate(0deg) scale(1.012);z-index:2;}
.tk.is-open .tk-top{
  box-shadow:0 0 0 1px var(--glow-soft), 0 0 34px var(--glow-soft), 0 22px 40px -20px rgba(33,28,21,.55);
  border-color:var(--glow);
}
.tk-body{flex:1;min-width:0;padding:20px 22px;}
.tk-cat{font-family:var(--mono);font-size:9.5px;letter-spacing:.2em;color:var(--stamp);text-transform:uppercase;}
.tk-title{font-size:22px;font-weight:700;letter-spacing:-.02em;margin-top:8px;line-height:1.05;}
.tk-sub{font-size:13px;color:var(--ink-2);margin-top:3px;}
.tk-venue{font-size:12.5px;color:var(--ink-3);margin-top:14px;line-height:1.4;}
.tk-date{font-family:var(--mono);font-size:12px;color:var(--ink);margin-top:6px;letter-spacing:.02em;}
/* perforation */
.tk-perf{position:relative;width:0;border-left:2px dashed var(--line);}
.tk-perf::before,.tk-perf::after{content:"";position:absolute;left:-9px;width:18px;height:18px;border-radius:50%;background:var(--paper);box-shadow:inset 0 0 0 1px var(--line-2);}
.tk-perf::before{top:-9px;}.tk-perf::after{bottom:-9px;}
/* stub end */
.tk-stub{width:120px;flex-shrink:0;padding:18px 16px;display:flex;flex-direction:column;align-items:center;justify-content:space-between;background:linear-gradient(180deg,rgba(33,28,21,.03),rgba(33,28,21,.06));text-align:center;}
.tk-admit{font-family:var(--mono);font-size:8.5px;letter-spacing:.2em;color:var(--ink-3);writing-mode:vertical-rl;transform:rotate(180deg);}
.tk-barcode{flex:1;width:40px;margin:8px 0;align-self:center;background:repeating-linear-gradient(90deg,var(--ink) 0 2px,transparent 2px 3px,var(--ink) 3px 4px,transparent 4px 7px);opacity:.78;border-radius:1px;}
.tk-serial{font-family:var(--mono);font-size:9px;color:var(--ink-2);letter-spacing:.04em;}
/* the memory, revealed on open */
.tk-note{display:grid;grid-template-rows:0fr;transition:grid-template-rows .5s var(--ease);}
.tk.is-open .tk-note{grid-template-rows:1fr;}
.tk-note > div{overflow:hidden;}
.tk-note p{padding:16px 6px 4px;font-size:14.5px;line-height:1.55;color:var(--ink);max-width:54ch;}
.tk-note .seatline{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--stamp);margin-top:2px;padding:0 6px 2px;}

footer{padding:60px 0 80px;text-align:center;font-family:var(--mono);font-size:11px;letter-spacing:.12em;color:var(--ink-3);}
footer .hint{margin-bottom:18px;color:var(--ink-2);}
.badge{position:fixed;left:16px;bottom:16px;z-index:40;font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-2);background:var(--card);border:1px solid var(--line);padding:8px 13px;border-radius:999px;text-decoration:none;box-shadow:0 6px 18px -8px rgba(33,28,21,.4);}
.badge:hover{color:var(--stamp);border-color:var(--glow);}
"""
A_RENDER = r"""
  function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');}
  function ticket(t){
    return '<article class="tk" tabindex="0" role="button" aria-expanded="false" aria-label="'+esc(t.title)+', tap to read the memory">'
      + '<div class="tk-top">'
      +   '<div class="tk-body">'
      +     '<div class="tk-cat">'+esc(t.kind)+'</div>'
      +     '<div class="tk-title">'+esc(t.title)+'</div>'
      +     '<div class="tk-sub">'+esc(t.sub)+'</div>'
      +     '<div class="tk-venue">'+esc(t.venue)+'</div>'
      +     '<div class="tk-date">'+esc(t.date)+'</div>'
      +   '</div>'
      +   '<div class="tk-perf" aria-hidden="true"></div>'
      +   '<div class="tk-stub"><div class="tk-admit">Admit One</div><div class="tk-barcode"></div><div class="tk-serial">'+esc(t.serial)+'</div></div>'
      + '</div>'
      + '<div class="tk-note"><div><div class="seatline">'+esc(t.seat)+'</div><p>'+esc(t.note)+'</p></div></div>'
      + '</article>';
  }
  function render(){
    var root = document.getElementById('shelf'); var html='';
    ORDER.forEach(function(cat,i){
      var items = TICKETS.filter(function(t){return t.cat===cat;});
      if(!items.length) return;
      html += '<section class="cat"><div class="wrap"><div class="cat-h"><span class="n">0'+(i+1)+'</span><h2>'+cat+'</h2><span class="c">'+items.length+' kept</span></div><div class="shelf">'+items.map(ticket).join('')+'</div></div></section>';
    });
    root.innerHTML = html;
  }
"""
A_BODY = """
<header class="mast"><div class="wrap">
  <div class="eye">A shelf for the ones you kept</div>
  <h1>Remember<span class="dot">.</span></h1>
  <p class="sub">The ticket stubs we used to keep in a drawer. The concert, the film, the match, the night. Tap a stub to light it up and read what it was.</p>
  <div class="meta">__N__ stubs &middot; 4 shelves &middot; est. 2026</div>
  <div class="rule"></div>
</div></header>
<main id="shelf"></main>
<footer><div class="wrap"><div class="hint">Tap any stub to remember it.</div>Remember &middot; The Vintage Shelf</div></footer>
""".replace("__N__", str(len(TICKETS)))


# =====================================================================
# VARIANT B - DARK CINEMA  (near-black, tungsten/marquee gold glow)
# =====================================================================
B_FONTS = "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
B_CSS = r"""
:root{
  --bg:#0b0b0f; --bg-2:#121218; --card:#15151c; --ink:#f2efe9; --ink-2:rgba(242,239,233,.62);
  --ink-3:rgba(242,239,233,.40); --line:rgba(255,255,255,.10); --line-2:rgba(255,255,255,.06);
  --glow:#ffc864; --glow-2:#ff9d3c; --glow-soft:rgba(255,200,100,.30);
  --sans:'Space Grotesk',system-ui,sans-serif; --mono:'JetBrains Mono',ui-monospace,monospace;
  --ease:cubic-bezier(.16,1,.3,1);
}
*{box-sizing:border-box;margin:0;padding:0;}
body{
  background:var(--bg);color:var(--ink);font-family:var(--sans);-webkit-font-smoothing:antialiased;line-height:1.5;min-height:100dvh;
  background-image:radial-gradient(ellipse 70% 50% at 50% -8%, rgba(255,200,100,.06), transparent 60%),radial-gradient(ellipse 90% 60% at 50% 120%, rgba(255,157,60,.05), transparent 60%);
}
.skip{position:absolute;left:-999px;}.skip:focus{left:16px;top:16px;background:var(--glow);color:#000;padding:8px 14px;border-radius:8px;z-index:99;}
.wrap{max-width:1120px;margin:0 auto;padding:0 28px;}
.mast{padding:84px 0 28px;}
.mast .eye{font-family:var(--mono);font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:var(--glow);}
.mast h1{font-size:clamp(54px,10vw,98px);font-weight:700;letter-spacing:-.04em;line-height:.92;margin-top:12px;}
.mast h1 .dot{color:var(--glow);text-shadow:0 0 24px var(--glow-soft);}
.mast .sub{margin-top:16px;font-size:clamp(15px,1.7vw,18px);color:var(--ink-2);max-width:48ch;}
.mast .meta{margin-top:18px;font-family:var(--mono);font-size:11px;letter-spacing:.14em;color:var(--ink-3);}

.cat{padding:44px 0 6px;}
.cat-h{display:flex;align-items:baseline;gap:14px;margin-bottom:24px;border-top:1px solid var(--line-2);padding-top:22px;}
.cat-h .n{font-family:var(--mono);font-size:12px;color:var(--glow);}
.cat-h h2{font-size:24px;font-weight:600;letter-spacing:-.01em;}
.cat-h .c{font-family:var(--mono);font-size:12px;color:var(--ink-3);margin-left:auto;}
.shelf{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;}
@media(max-width:900px){.shelf{grid-template-columns:repeat(2,1fr);}}
@media(max-width:620px){.shelf{grid-template-columns:1fr;}}

.tk{
  position:relative;display:block;width:100%;text-align:left;cursor:pointer;font:inherit;color:inherit;background:transparent;border:0;padding:0;
  opacity:0;transform:translateY(18px);transition:opacity .7s var(--ease),transform .7s var(--ease);-webkit-tap-highlight-color:transparent;
}
.tk.seen{opacity:1;transform:none;}
.tk-top{
  position:relative;display:flex;flex-direction:column;background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;
  transition:border-color .4s var(--ease),box-shadow .4s var(--ease),transform .4s var(--ease);
}
.tk:hover .tk-top{transform:translateY(-3px);border-color:rgba(255,200,100,.35);}
.tk:focus-visible{outline:0;}.tk:focus-visible .tk-top{outline:2px solid var(--glow);outline-offset:3px;}
/* the signature: a dark stub ignites with marquee gold */
.tk.is-open .tk-top{
  border-color:var(--glow);
  box-shadow:0 0 0 1px var(--glow-soft),0 0 40px -2px var(--glow-soft),0 0 90px -10px rgba(255,200,100,.25),inset 0 1px 0 rgba(255,220,150,.18);
  transform:translateY(-3px);
}
.tk-body{padding:18px 18px 16px;}
.tk-row{display:flex;align-items:center;justify-content:space-between;}
.tk-cat{font-family:var(--mono);font-size:9px;letter-spacing:.18em;color:var(--glow);text-transform:uppercase;}
.tk-bulb{width:7px;height:7px;border-radius:50%;background:var(--ink-3);transition:background .4s,box-shadow .4s;}
.tk.is-open .tk-bulb{background:var(--glow);box-shadow:0 0 10px var(--glow);}
.tk-title{font-size:21px;font-weight:700;letter-spacing:-.02em;margin-top:12px;line-height:1.05;}
.tk-sub{font-size:12.5px;color:var(--ink-2);margin-top:3px;}
.tk-venue{font-size:12px;color:var(--ink-3);margin-top:14px;line-height:1.4;}
/* perforated divider with marquee notches */
.tk-tear{position:relative;height:0;border-top:1px dashed var(--line);margin:2px 14px 0;}
.tk-tear::before,.tk-tear::after{content:"";position:absolute;top:-8px;width:16px;height:16px;border-radius:50%;background:var(--bg);}
.tk-tear::before{left:-22px;}.tk-tear::after{right:-22px;}
.tk-foot{display:flex;align-items:center;justify-content:space-between;padding:12px 18px 16px;}
.tk-date{font-family:var(--mono);font-size:11px;color:var(--ink-2);letter-spacing:.02em;}
.tk-serial{font-family:var(--mono);font-size:9.5px;color:var(--ink-3);}
.tk-barcode{height:22px;margin:0 18px;background:repeating-linear-gradient(90deg,var(--ink) 0 2px,transparent 2px 3px,var(--ink) 3px 4px,transparent 4px 6px);opacity:.18;transition:opacity .4s;}
.tk.is-open .tk-barcode{opacity:.5;}
.tk-note{display:grid;grid-template-rows:0fr;transition:grid-template-rows .5s var(--ease);padding:0 18px;}
.tk.is-open .tk-note{grid-template-rows:1fr;padding-bottom:16px;}
.tk-note > div{overflow:hidden;}
.tk-note .seatline{font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--glow);padding-top:14px;}
.tk-note p{padding-top:6px;font-size:14px;line-height:1.55;color:var(--ink);}

footer{padding:64px 0 90px;text-align:center;font-family:var(--mono);font-size:11px;letter-spacing:.12em;color:var(--ink-3);}
footer .hint{margin-bottom:16px;color:var(--ink-2);}
.badge{position:fixed;left:16px;bottom:16px;z-index:40;font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-2);background:var(--card);border:1px solid var(--line);padding:8px 13px;border-radius:999px;text-decoration:none;}
.badge:hover{color:var(--glow);border-color:var(--glow);}
"""
B_RENDER = r"""
  function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');}
  function ticket(t){
    return '<article class="tk" tabindex="0" role="button" aria-expanded="false" aria-label="'+esc(t.title)+', tap to light it up">'
      + '<div class="tk-top">'
      +   '<div class="tk-body"><div class="tk-row"><span class="tk-cat">'+esc(t.kind)+'</span><span class="tk-bulb"></span></div>'
      +     '<div class="tk-title">'+esc(t.title)+'</div><div class="tk-sub">'+esc(t.sub)+'</div>'
      +     '<div class="tk-venue">'+esc(t.venue)+'</div></div>'
      +   '<div class="tk-tear" aria-hidden="true"></div>'
      +   '<div class="tk-barcode" aria-hidden="true"></div>'
      +   '<div class="tk-foot"><span class="tk-date">'+esc(t.date)+'</span><span class="tk-serial">'+esc(t.serial)+'</span></div>'
      +   '<div class="tk-note"><div><div class="seatline">'+esc(t.seat)+'</div><p>'+esc(t.note)+'</p></div></div>'
      + '</div></article>';
  }
  function render(){
    var root = document.getElementById('shelf'); var html='';
    ORDER.forEach(function(cat,i){
      var items = TICKETS.filter(function(t){return t.cat===cat;});
      if(!items.length) return;
      html += '<section class="cat"><div class="wrap"><div class="cat-h"><span class="n">0'+(i+1)+'</span><h2>'+cat+'</h2><span class="c">'+items.length+'</span></div><div class="shelf">'+items.map(ticket).join('')+'</div></div></section>';
    });
    root.innerHTML = html;
  }
"""
B_BODY = """
<header class="mast"><div class="wrap">
  <div class="eye">The stubs, in the dark</div>
  <h1>Remember<span class="dot">.</span></h1>
  <p class="sub">A dark room of the nights you held on to. Each stub sits unlit until you reach for it. Tap one and it lights up, like the marquee did.</p>
  <div class="meta">__N__ stubs &middot; 4 reels &middot; tap to light</div>
</div></header>
<main id="shelf"></main>
<footer><div class="wrap"><div class="hint">Tap a stub. Watch it light up.</div>Remember &middot; The Dark Cinema</div></footer>
""".replace("__N__", str(len(TICKETS)))


# =====================================================================
# VARIANT C - EDITORIAL WALL  (bold off-white, ink, electric accent)
# =====================================================================
C_FONTS = "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
C_CSS = r"""
:root{
  --bg:#f6f5f2; --card:#ffffff; --ink:#0e0e0f; --ink-2:rgba(14,14,15,.60); --ink-3:rgba(14,14,15,.38);
  --line:rgba(14,14,15,.12); --line-2:rgba(14,14,15,.07); --accent:#0a3df0; --accent-soft:rgba(10,61,240,.18);
  --sans:'Space Grotesk',system-ui,sans-serif; --mono:'JetBrains Mono',ui-monospace,monospace; --ease:cubic-bezier(.16,1,.3,1);
}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--ink);font-family:var(--sans);-webkit-font-smoothing:antialiased;line-height:1.5;min-height:100dvh;}
.skip{position:absolute;left:-999px;}.skip:focus{left:16px;top:16px;background:var(--ink);color:var(--bg);padding:8px 14px;border-radius:8px;z-index:99;}
.wrap{max-width:1180px;margin:0 auto;padding:0 32px;}
/* oversized editorial masthead */
.mast{padding:60px 0 24px;border-bottom:2px solid var(--ink);}
.mast .topline{display:flex;justify-content:space-between;font-family:var(--mono);font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--ink-2);}
.mast h1{font-size:clamp(72px,19vw,260px);font-weight:700;letter-spacing:-.05em;line-height:.82;margin:18px 0 0;}
.mast h1 .dot{color:var(--accent);}
.mast .sub{display:flex;flex-wrap:wrap;gap:14px 30px;justify-content:space-between;align-items:baseline;margin-top:22px;}
.mast .sub p{font-size:clamp(15px,1.6vw,18px);color:var(--ink-2);max-width:42ch;}
.mast .sub .tag{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);}

.cat{padding:48px 0 6px;}
.cat-h{display:flex;align-items:flex-end;gap:16px;margin-bottom:22px;}
.cat-h .n{font-family:var(--mono);font-size:13px;color:var(--accent);}
.cat-h h2{font-size:clamp(28px,4vw,44px);font-weight:700;letter-spacing:-.03em;text-transform:uppercase;}
.cat-h .c{font-family:var(--mono);font-size:12px;color:var(--ink-3);margin-left:auto;padding-bottom:8px;}
.shelf{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border-top:1px solid var(--ink);border-left:1px solid var(--line);}
@media(max-width:860px){.shelf{grid-template-columns:repeat(2,1fr);}}
@media(max-width:560px){.shelf{grid-template-columns:1fr;}}

/* editorial flat stub cells */
.tk{
  position:relative;display:block;width:100%;text-align:left;cursor:pointer;font:inherit;color:inherit;
  background:var(--card);border-right:1px solid var(--line);border-bottom:1px solid var(--ink);padding:0;
  opacity:0;transform:translateY(14px);transition:opacity .6s var(--ease),transform .6s var(--ease),background-color .35s,box-shadow .35s;-webkit-tap-highlight-color:transparent;
}
.tk.seen{opacity:1;transform:none;}
.tk:hover{background:#fff;}
.tk:focus-visible{outline:2px solid var(--accent);outline-offset:-2px;}
.tk.is-open{background:#fff;box-shadow:inset 4px 0 0 var(--accent),0 0 0 1px var(--accent),0 18px 40px -22px var(--accent-soft);z-index:2;}
.tk-top{padding:20px 20px 16px;}
.tk-row{display:flex;justify-content:space-between;align-items:baseline;}
.tk-cat{font-family:var(--mono);font-size:9.5px;letter-spacing:.18em;text-transform:uppercase;color:var(--accent);}
.tk-serial{font-family:var(--mono);font-size:9.5px;color:var(--ink-3);}
.tk-title{font-size:clamp(22px,2.5vw,30px);font-weight:700;letter-spacing:-.03em;line-height:1;margin-top:16px;}
.tk-sub{font-size:13px;color:var(--ink-2);margin-top:6px;}
.tk-foot{display:flex;justify-content:space-between;align-items:baseline;gap:12px;margin-top:18px;padding-top:12px;border-top:1px dashed var(--line);}
.tk-venue{font-size:12px;color:var(--ink-3);line-height:1.35;}
.tk-date{font-family:var(--mono);font-size:11.5px;color:var(--ink);white-space:nowrap;}
.tk-note{display:grid;grid-template-rows:0fr;transition:grid-template-rows .45s var(--ease);}
.tk.is-open .tk-note{grid-template-rows:1fr;}
.tk-note > div{overflow:hidden;}
.tk-note .inner{padding:14px 20px 20px;border-top:1px solid var(--ink);background:linear-gradient(180deg,var(--accent-soft),transparent 70%);}
.tk-note .seatline{font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);}
.tk-note p{font-size:14.5px;line-height:1.55;color:var(--ink);margin-top:6px;}

footer{padding:60px 0 90px;border-top:2px solid var(--ink);margin-top:50px;}
footer .in{display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;font-family:var(--mono);font-size:11px;letter-spacing:.12em;color:var(--ink-3);}
footer .hint{color:var(--ink);}
.badge{position:fixed;left:16px;bottom:16px;z-index:40;font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--bg);background:var(--ink);padding:9px 14px;border-radius:999px;text-decoration:none;}
.badge:hover{background:var(--accent);}
"""
C_RENDER = r"""
  function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');}
  function ticket(t){
    return '<article class="tk" tabindex="0" role="button" aria-expanded="false" aria-label="'+esc(t.title)+', tap to read the memory">'
      + '<div class="tk-top"><div class="tk-row"><span class="tk-cat">'+esc(t.kind)+'</span><span class="tk-serial">'+esc(t.serial)+'</span></div>'
      +   '<div class="tk-title">'+esc(t.title)+'</div><div class="tk-sub">'+esc(t.sub)+'</div>'
      +   '<div class="tk-foot"><span class="tk-venue">'+esc(t.venue)+'</span><span class="tk-date">'+esc(t.date)+'</span></div></div>'
      + '<div class="tk-note"><div><div class="inner"><div class="seatline">'+esc(t.seat)+'</div><p>'+esc(t.note)+'</p></div></div></div>'
      + '</article>';
  }
  function render(){
    var root = document.getElementById('shelf'); var html='';
    ORDER.forEach(function(cat,i){
      var items = TICKETS.filter(function(t){return t.cat===cat;});
      if(!items.length) return;
      html += '<section class="cat"><div class="wrap"><div class="cat-h"><span class="n">0'+(i+1)+'</span><h2>'+cat+'</h2><span class="c">'+items.length+' stubs</span></div><div class="shelf">'+items.map(ticket).join('')+'</div></div></section>';
    });
    root.innerHTML = html;
  }
"""
C_BODY = """
<header class="mast"><div class="wrap">
  <div class="topline"><span>The keepsake index</span><span>Bengaluru &middot; MMXXVI</span></div>
  <h1>Remember<span class="dot">.</span></h1>
  <div class="sub"><p>A wall of the stubs you never threw away. Set in type, filed by kind. Tap any one to pull the memory out of it.</p><span class="tag">__N__ stubs &middot; tap to expand</span></div>
</div></header>
<main id="shelf"></main>
<footer><div class="wrap in"><span class="hint">Tap a stub to read it.</span><span>Remember &middot; The Editorial Wall</span></div></footer>
""".replace("__N__", str(len(TICKETS)))


# =====================================================================
# CHOOSER
# =====================================================================
CHOOSER = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Remember - three directions</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Space+Mono&display=swap"/>
<style>
:root{--bg:#101014;--ink:#f3f1ec;--ink-2:rgba(243,241,236,.6);--ink-3:rgba(243,241,236,.4);--line:rgba(255,255,255,.1);--accent:#ffc864;--ease:cubic-bezier(.16,1,.3,1);--sans:'Space Grotesk',sans-serif;--mono:'Space Mono',monospace;}
*{box-sizing:border-box;margin:0;}body{background:var(--bg);color:var(--ink);font-family:var(--sans);min-height:100dvh;display:grid;place-items:center;padding:56px 24px;-webkit-font-smoothing:antialiased;}
.lab{width:100%;max-width:760px;}
.k{font-family:var(--mono);font-size:11px;letter-spacing:.24em;text-transform:uppercase;color:var(--ink-3);}
h1{font-size:clamp(36px,7vw,60px);font-weight:700;letter-spacing:-.03em;line-height:.95;margin:14px 0 0;}
h1 .d{color:var(--accent);}
.lead{color:var(--ink-2);margin-top:14px;max-width:54ch;line-height:1.6;}
.opts{display:grid;gap:13px;margin-top:34px;}
.o{display:grid;grid-template-columns:30px 1fr auto;gap:18px;align-items:center;padding:22px 24px;border:1px solid var(--line);border-radius:16px;text-decoration:none;color:inherit;background:rgba(255,255,255,.02);transition:border-color .25s var(--ease),background .25s var(--ease),transform .25s var(--ease);}
.o:hover{border-color:var(--accent);background:rgba(255,200,100,.06);transform:translateY(-2px);}
.o .l{font-family:var(--mono);font-size:22px;color:var(--accent);}
.o .nm{display:block;font-weight:600;font-size:17px;}
.o .ds{display:block;color:var(--ink-2);font-size:13.5px;margin-top:4px;line-height:1.5;}
.o .go{font-family:var(--mono);font-size:13px;color:var(--ink-3);}
.o:hover .go{color:var(--accent);}
@media(max-width:560px){.o{grid-template-columns:24px 1fr;}.o .go{display:none;}}
.foot{margin-top:30px;font-family:var(--mono);font-size:11px;color:var(--ink-3);letter-spacing:.06em;}
</style></head><body>
<main class="lab">
  <div class="k">Remember &middot; design directions</div>
  <h1>Three ways to keep a stub<span class="d">.</span></h1>
  <p class="lead">A one-page shelf for the ticket stubs you held on to, segregated by kind. Same memories in each, three different feelings. Open one, tap a stub to light it up, and pick the one that feels like Remember.</p>
  <nav class="opts">
    <a class="o" href="variant-a-shelf.html"><span class="l">A</span><span><span class="nm">The Vintage Shelf</span><span class="ds">Warm paper, torn stubs on a tilt, a soft amber glow. The drawer you kept them in.</span></span><span class="go">open -&gt;</span></a>
    <a class="o" href="variant-b-cinema.html"><span class="l">B</span><span><span class="nm">The Dark Cinema</span><span class="ds">Near-black room, each stub unlit until you tap it, then it ignites like a marquee.</span></span><span class="go">open -&gt;</span></a>
    <a class="o" href="variant-c-editorial.html"><span class="l">C</span><span><span class="nm">The Editorial Wall</span><span class="ds">Oversized type, a filed grid, electric accent. The stubs as a printed index.</span></span><span class="go">open -&gt;</span></a>
  </nav>
  <p class="foot">Built with Space Grotesk &middot; tap-to-glow is the only interaction</p>
</main></body></html>
"""

def main():
    io.open(os.path.join(ROOT, "variant-a-shelf.html"), "w", encoding="utf-8").write(
        page("- The Vintage Shelf", "A", "#efe7d6", A_FONTS, A_CSS, A_BODY, A_RENDER))
    io.open(os.path.join(ROOT, "variant-b-cinema.html"), "w", encoding="utf-8").write(
        page("- The Dark Cinema", "B", "#0b0b0f", B_FONTS, B_CSS, B_BODY, B_RENDER))
    io.open(os.path.join(ROOT, "variant-c-editorial.html"), "w", encoding="utf-8").write(
        page("- The Editorial Wall", "C", "#f6f5f2", C_FONTS, C_CSS, C_BODY, C_RENDER))
    io.open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(CHOOSER)
    print("built: variant-a-shelf.html, variant-b-cinema.html, variant-c-editorial.html, index.html")

if __name__ == "__main__":
    main()
