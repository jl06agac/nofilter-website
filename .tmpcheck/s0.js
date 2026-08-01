
(function(){
  var slot   = document.getElementById('slot');
  var slotc  = document.getElementById('slotc');
  var head   = document.getElementById('maniHead');
  var words  = [' workplace ', ' hotel ', ' cafe '];   // the inserted adjectives, in order
  var HOLD   = 780;   // ms the word stays open, long enough to read
  var MOVE   = 460;   // ms > the .42s grid transition, so each squeeze fully finishes
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion:reduce)').matches;
  var running = false;

  function wait(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
  function openSlot(){ slot.classList.add('open');    return wait(MOVE); }
  function closeSlot(){ slot.classList.remove('open'); return wait(MOVE); }

  async function run(){
    if(running) return;
    running = true;
    // reduced motion: no cycling — settle straight to "Most coffee"
    if(reduce){ slotc.textContent = ' '; slot.classList.add('open'); running = false; return; }

    await closeSlot();                 // squeeze the resting word-gap shut
    for(var i=0;i<words.length;i++){
      slotc.textContent = words[i];    // swap text while collapsed + faded out
      await openSlot();                // squeeze IN
      await wait(HOLD);                // hold to read
      await closeSlot();               // squeeze OUT
    }
    slotc.textContent = ' ';           // settle to a normal single-space gap -> "Most coffee"
    await openSlot();
    running = false;
  }

  // fire once when the headline scrolls into view
  if('IntersectionObserver' in window){
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if(e.isIntersecting){ io.disconnect(); if(document.fonts&&document.fonts.ready){ document.fonts.ready.then(run); } else { run(); } }
      });
    }, { threshold: 0.6 });
    io.observe(head);
  } else {
    run();
  }

  // replay button (test harness)
  document.getElementById('replay').addEventListener('click', function(){
    if(running) return;
    slotc.textContent = ' '; slot.classList.add('open');
    run();
  });

  document.getElementById('rmNote').textContent = reduce ? 'reduced-motion ON — settles, no cycle' : '';
})();
