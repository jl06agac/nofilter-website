/* Built pages use document navigation. The master retains its standalone SPA. */
(function(){
  function market(){var p=document.querySelector('meta[name="nf-market"]');return p?p.content:'SG';}
  function destination(path,k){
    var clean=path.replace(/^\/(ae|uk)(?=\/|$)/,'')||'/';
    var live=/^(www\.)?nofilter\.(sg|ae)$/.test(location.hostname);
    if(live)return (k==='AE'?'https://nofilter.ae':'https://nofilter.sg')+(k==='UK'?'/uk':'')+clean;
    return (k==='AE'?'/ae':k==='UK'?'/uk':'')+clean;
  }
  document.addEventListener('click',function(e){
    if(e.button!==0||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;
    var b=e.target.closest('[data-mkt],[data-pbm],[data-deckmkt]');
    if(b){var k=b.getAttribute('data-mkt')||b.getAttribute('data-pbm')||b.getAttribute('data-deckmkt');if(/^(SG|AE|UK)$/.test(k)){
      e.preventDefault();e.stopImmediatePropagation();if(k!==market())location.assign(destination(location.pathname,k));return;
    }}
    var a=e.target.closest('a[href]');if(!a||a.hasAttribute('download')||(a.target&&a.target!=='_self'))return;
    var raw=a.getAttribute('href');if(!raw||raw.charAt(0)==='#')return;
    var u=new URL(raw,location.href);if(u.origin!==location.origin)return;
    if(!/^\/(?:ae\/|uk\/)?(?:origins(?:\/[^/]+)?|shop|wholesale-coffee|trade-pricing|faqs)?\/?$/.test(u.pathname))return;
    e.preventDefault();e.stopImmediatePropagation();
    var targetMarket=/^\/uk(?:\/|$)/.test(u.pathname)?'UK':/^\/ae(?:\/|$)/.test(u.pathname)?'AE':market();
    location.assign(destination(u.pathname,targetMarket)+u.search+u.hash);
  },true);
  // Explicit campaign market selections land on the matching content tree.
  var q=new URLSearchParams(location.search),k=(q.get('mkt')||'').toUpperCase();if(k==='GB')k='UK';
  if(/^(SG|AE|UK)$/.test(k)&&k!==market()){q.delete('mkt');location.replace(destination(location.pathname,k)+(q.toString()?'?'+q:'')+location.hash);}
})();
