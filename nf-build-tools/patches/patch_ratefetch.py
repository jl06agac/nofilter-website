import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

def fix(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor count %d (want %d) for %r" % (n, count, old[:70])
    src = src.replace(old, new)

# ══ 115 · THE LADDER ARRIVES WITH THE ACCESS ANSWER (7 Sep) ══════════════════
# Pair to patch_ratesplit (114). The shipped page carries no RATES; build-ship
# lifts them into netlify/functions/access-verify.js, which now answers a valid
# code with { ok:true, rates:{SG,AE,UK} }. The CRT's submit() used to reduce the
# answer to a boolean before anyone could read it; it now merges the rates into
# MARKETS (nfMergeRates re-runs applyMarket) BEFORE unlock() reveals the builder,
# so the console never paints a seeded placeholder ladder. From disk
# (__nfAccessLive false) nothing changes: the master is unsplit and RATES were
# merged inline at load.
fix("""      .then(function(j){ return !!(j && j.ok); })
      .catch(function(){ return false; })
      .then(function(ok){
        if(chk.parentNode) chk.remove();
        inputEnabled = true;
        if(ok){ unlock(); } else { deny(); }
      });""",
"""      .then(function(j){
        /* 115: the ladder rides on the answer; merge it before the builder shows */
        if(j && j.ok && j.rates && typeof window.__nfMergeRates === 'function'){
          try{ window.__nfMergeRates(j.rates); }catch(e){}
        }
        return !!(j && j.ok);
      })
      .catch(function(){ return false; })
      .then(function(ok){
        if(chk.parentNode) chk.remove();
        inputEnabled = true;
        if(ok){ unlock(); } else { deny(); }
      });""")

io.open(F, "w", encoding="utf-8").write(src)
print("patch_ratefetch OK")
