
// Highlight the contents entry for the section being read.
(function () {
  const links = [...document.querySelectorAll('.toc__link')];
  const targets = links.map(a => document.getElementById(a.getAttribute('href').slice(1))).filter(Boolean);
  if (!targets.length) return;
  function update() {
    const line = Math.min(window.innerHeight * 0.3, 240);
    let current = targets[0];
    for (const t of targets) { if (t.getBoundingClientRect().top - line <= 0) current = t; }
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) current = targets[targets.length - 1];
    for (const a of links) {
      const on = a.getAttribute('href') === '#' + current.id;
      a.setAttribute('aria-current', on ? 'true' : 'false');
      if (on && a.closest('.toc').scrollWidth > a.closest('.toc').clientWidth) {
        const nav = a.closest('.toc');
        const r = a.getBoundingClientRect(), n = nav.getBoundingClientRect();
        if (r.left < n.left || r.right > n.right) nav.scrollLeft += r.left - n.left - 24;
      }
    }
  }
  let queued = false;
  window.addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(() => { queued = false; update(); }); } }, {passive:true});
  window.addEventListener('resize', update);
  update();
})();

// Start diagrams on "Fit" when the whole board fits at a readable size.
(function () {
  const canvas = document.querySelector('.panel .canvas');
  const fit = document.getElementById('zoom-fit');
  if (!canvas || !fit || location.hash) return;
  const visible = [...document.querySelectorAll('.canvas')].find(c => c.clientWidth);
  if (!visible) return;
  const board = parseFloat(getComputedStyle(visible).getPropertyValue('--board-width')) || 0;
  if (board && visible.clientWidth < board && visible.clientWidth / board >= 0.6) {
    fit.checked = true;
    fit.dispatchEvent(new Event('change'));
  }
})();
