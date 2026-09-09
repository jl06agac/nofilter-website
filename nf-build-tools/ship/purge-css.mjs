// purge-css.mjs — drop CSS rules that cannot match anything in this document.
// A selector is kept unless it names a class or id that appears NOWHERE in the
// page outside its style blocks — not in the markup, not in any script (as a
// whole token, or as a hyphen-ended string prefix such as 'deck-' that a script
// completes at run time). Element selectors, attribute selectors, pseudo-classes
// and anything inside :not()/:is()/:where() never cause removal. Keyframes are
// kept while any surviving declaration or script names them.
import postcss from 'postcss';
import selectorParser from 'postcss-selector-parser';

export function purgeDocument(html, opts = {}) {
  const styles = [...html.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/g)];
  const ref = html.replace(/<style\b[^>]*>[\s\S]*?<\/style>/g, ' ');
  const tokens = new Set(ref.match(/[A-Za-z_][A-Za-z0-9_-]*/g) || []);
  // hyphen-ended string prefixes a script completes at run time: 'cx-', "deck-"
  const prefixes = new Set([...ref.matchAll(/['"]([A-Za-z][A-Za-z0-9_-]*-)['"]/g)].map(m => m[1]));
  const alive = (name) => {
    if (tokens.has(name)) return true;
    for (const p of prefixes) if (name.startsWith(p)) return true;
    return false;
  };
  const stats = { rules: 0, removedRules: 0, selectors: 0, removedSelectors: 0, keyframesRemoved: 0, dead: new Map() };
  const testSelector = (sel) => {
    let ok = true;
    try {
      selectorParser(root => {
        root.walk(node => {
          if (!ok) return;
          // inside :not/:is/:where/:has the class is a condition, not a requirement
          let p = node.parent; let inFn = false;
          while (p) { if (p.type === 'pseudo' && /^::?(not|is|where|has|host|host-context|slotted)$/i.test(p.value)) { inFn = true; break; } p = p.parent; }
          if (inFn) return;
          if (node.type === 'class' && !alive(node.value)) { ok = false; stats.dead.set('.' + node.value, (stats.dead.get('.' + node.value) || 0) + 1); }
          if (node.type === 'id' && !alive(node.value)) { ok = false; stats.dead.set('#' + node.value, (stats.dead.get('#' + node.value) || 0) + 1); }
        });
      }).processSync(sel);
    } catch (e) { ok = true; }   // unparseable → keep
    return ok;
  };
  const walk = (container) => {
    container.each(node => {
      if (node.type === 'rule') {
        if (node.parent && node.parent.type === 'atrule' && /keyframes$/i.test(node.parent.name)) return;
        stats.rules++;
        const sels = node.selectors; stats.selectors += sels.length;
        const keep = sels.filter(testSelector);
        stats.removedSelectors += sels.length - keep.length;
        if (!keep.length) { node.remove(); stats.removedRules++; }
        else if (keep.length !== sels.length) node.selectors = keep;
      } else if (node.type === 'atrule') {
        if (/^(media|supports|layer|container)$/i.test(node.name)) { walk(node); if (node.nodes && !node.nodes.length) node.remove(); }
      }
    });
  };
  const roots = styles.map(m => postcss.parse(m[1]));
  roots.forEach(walk);
  // keyframes: names still referenced by surviving CSS or by scripts
  const cssText = roots.map(r => r.toString()).join('\n');
  const animNames = new Set();
  for (const m of cssText.matchAll(/animation(?:-name)?\s*:\s*([^;}]+)/g)) for (const t of m[1].split(/[\s,]+/)) if (/^[A-Za-z_][\w-]*$/.test(t)) animNames.add(t);
  roots.forEach(root => root.walkAtRules(/keyframes$/i, at => {
    if (!animNames.has(at.params) && !tokens.has(at.params)) { at.remove(); stats.keyframesRemoved++; }
  }));
  let i = 0;
  const out = html.replace(/(<style\b[^>]*>)([\s\S]*?)(<\/style>)/g, (m, a, b, c) => a + roots[i++].toString() + c);
  stats.before = styles.reduce((s, m) => s + m[1].length, 0);
  stats.after = roots.reduce((s, r) => s + r.toString().length, 0);
  return { html: out, stats };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const { readFileSync, writeFileSync } = await import('node:fs');
  const [,, inFile, outFile] = process.argv;
  const { html, stats } = purgeDocument(readFileSync(inFile, 'utf8'));
  if (outFile) writeFileSync(outFile, html);
  const { dead, ...rest } = stats; console.log(rest);
  console.log('top dead tokens:', [...dead.entries()].sort((a, b) => b[1] - a[1]).slice(0, 40).map(([k, v]) => k + '×' + v).join('  '));
}
