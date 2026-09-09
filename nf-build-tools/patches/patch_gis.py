import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d for %r" % (n, old[:70])
    src = src.replace(old, new)

# ══ 96 · THE EVIDENCE MAP LOADS WHEN IT IS ASKED FOR ══════════════════════
# Alex, 3 Sep: "what about the GIS Evidence map, is that behaving as there's
# a slight judder there too". Same cause as the counter: a live cross-origin
# page (nofilter-gis-map.netlify.app — d3 globe, then Google Maps) inside a
# frame, on the scroll path, with no still to fall back to. And this one
# pulled the Maps API for every reader of At Work whether or not they ever
# looked at it.
# The origins route already answers this the right way ([Layer 02]: the
# plate stands in for the map until it is asked for). The tablet now does
# the same: a poster of the map's own intro — the globe, HOLD THE LINE, the
# Enter map button, cut 3 Sep from the live app — is the screen until the
# reader taps it; then the live map loads in its place and the reader is on
# the app's intro, one tap from the map. Nothing on the scroll path, nothing
# downloaded for the reader who scrolls past.
# gis-map-poster.webp (1024×640, 16 KB) is new in _CDN-UPLOAD-SAFE.
fix("""          <iframe class="nw-gis" data-src="https://nofilter-gis-map.netlify.app/"
                  title="Interactive GIS evidence map — conservation boundaries and NoFilter plots"
                  loading="lazy" referrerpolicy="no-referrer"></iframe>""",
    """          <!-- block 96 — the map's intro as a poster until it is asked for -->
          <button type="button" class="nw-gis-facade" id="nwGisFacade" aria-label="Load the live evidence map">
            <img src="../../_CDN-UPLOAD-SAFE/gis-map-poster.webp" alt="" loading="lazy" decoding="async" width="1024" height="640">
            <span class="nw-gis-tag">Live map · tap to load</span>
          </button>
          <iframe class="nw-gis" data-gis-src="https://nofilter-gis-map.netlify.app/"
                  title="Interactive GIS evidence map — conservation boundaries and NoFilter plots"
                  loading="lazy" referrerpolicy="no-referrer" hidden></iframe>""")

CSS = r'''
/* ══ 96 · THE MAP FACADE ═══════════════════════════════════════════════ */
.nw-screen .nw-gis-facade{position:absolute;inset:0;width:100%;height:100%;margin:0;padding:0;border:0;
  background:#0b0c0e;cursor:pointer;display:block;overflow:hidden;border-radius:inherit}
.nw-screen .nw-gis-facade img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;
  transition:transform .6s cubic-bezier(.16,1,.3,1)}
.nw-screen .nw-gis-facade:hover img{transform:scale(1.015)}
.nw-screen .nw-gis-tag{position:absolute;left:12px;bottom:10px;font-family:var(--mono,ui-monospace,monospace);
  font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:rgba(244,242,238,.62);
  background:rgba(11,12,14,.72);padding:6px 9px;border-radius:99px;pointer-events:none}
.nw-screen .nw-gis-facade:focus-visible{outline:2px solid var(--signal,#EE4D17);outline-offset:-2px}
.nw-screen .nw-gis-facade.is-loading .nw-gis-tag{color:#F4F2EE}
.nw-screen .nw-gis[hidden]{display:none}
'''
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if '<style id="nf-es-cover">' in l)
end = next(i for i in range(start, len(lines)) if lines[i].strip() == "</style>")
lines.insert(end, CSS)
src = "\n".join(lines)

JS = r'''<script>
/* ── block 96 · the evidence map, on demand ────────────────────────────── */
(function(){
  var btn = document.getElementById('nwGisFacade'); if(!btn) return;
  var frame = btn.parentNode.querySelector('iframe[data-gis-src]'); if(!frame) return;
  var tag = btn.querySelector('.nw-gis-tag');
  btn.addEventListener('click', function(){
    if(frame.src) return;
    btn.classList.add('is-loading'); if(tag) tag.textContent = 'Loading the live map…';
    frame.addEventListener('load', function(){ btn.hidden = true; try{ frame.focus(); }catch(e){} }, { once:true });
    frame.hidden = false;
    frame.src = frame.getAttribute('data-gis-src');
    /* a frame that never reports load still replaces the poster after 6s */
    setTimeout(function(){ btn.hidden = true; }, 6000);
  });
})();
</script>
'''
fix("""<!-- block 89: keystroke-audio.js is loaded by the gate, on first open -->""",
    JS + """<!-- block 89: keystroke-audio.js is loaded by the gate, on first open -->""")

io.open(F, "w", encoding="utf-8").write(src)
print("evidence map behind a poster")
