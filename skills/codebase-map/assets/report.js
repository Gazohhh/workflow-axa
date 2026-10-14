'use strict';
// Native radio inputs and scrolling work without this progressive enhancement.
function revealAnchor() {
  const id = location.hash.slice(1);
  const target = document.getElementById(id);
  if (!target) return;
  let parent = target.parentElement;
  while (parent) {
    if (parent.tagName === 'DETAILS') parent.open = true;
    parent = parent.parentElement;
  }
  target.scrollIntoView({block:target.closest('.canvas') ? 'nearest' : 'start', inline:'center'});
}
for (const anchor of document.querySelectorAll('a[href^="#"]')) {
  anchor.addEventListener('click', () => {
    const target = document.getElementById(anchor.getAttribute('href').slice(1));
    let parent = target;
    while (parent) {
      if (parent.tagName === 'DETAILS') parent.open = true;
      parent = parent.parentElement;
    }
  });
}
window.addEventListener('hashchange', revealAnchor);
if (location.hash) revealAnchor();
function centerEntry(canvas) {
  if (!canvas.clientWidth) return;
  const node = document.getElementById(canvas.dataset.startId);
  if (!node) return;
  const bounds = node.getBoundingClientRect();
  const viewport = canvas.getBoundingClientRect();
  canvas.scrollLeft += bounds.x + bounds.width/2 - viewport.x - viewport.width/2;
}
function centerVisibleEntries() {
  for (const canvas of document.querySelectorAll('.canvas')) centerEntry(canvas);
}
for (const input of document.querySelectorAll('.review input[type="radio"]')) {
  input.addEventListener('change', centerVisibleEntries);
}
const resizeObserver = typeof ResizeObserver === 'function' ? new ResizeObserver(entries => {
  for (const entry of entries) centerEntry(entry.target);
}) : null;
for (const canvas of document.querySelectorAll('.canvas')) {
  // On narrow screens show the entry node, not the diagram's empty left margin.
  resizeObserver?.observe(canvas);
  let drag = null;
  canvas.addEventListener('keydown', event => {
    const choices = ['100', '125', '150'];
    const selected = document.querySelector('input[name="diagram-zoom"]:checked');
    let index = choices.indexOf(selected.id.slice(5));
    let next = null;
    if (event.key === '+' || event.key === '=') next = choices[Math.min(2, index+1)];
    else if (event.key === '-') next = choices[Math.max(0, index-1)];
    else if (event.key.toLowerCase() === 'f') next = 'fit';
    else if (event.key === '0') next = '100';
    if (next) {
      event.preventDefault();
      const input = document.getElementById('zoom-'+next);
      input.checked = true;
      input.dispatchEvent(new Event('change'));
    }
  });
  canvas.addEventListener('pointerdown', event => {
    if (event.pointerType !== 'mouse' || event.button !== 0) return;
    drag = {x:event.clientX, scroll:canvas.scrollLeft};
    canvas.setPointerCapture(event.pointerId);
    canvas.classList.add('dragging');
  });
  canvas.addEventListener('pointermove', event => {
    if (drag) canvas.scrollLeft = drag.scroll + drag.x-event.clientX;
  });
  const stop = () => { drag = null; canvas.classList.remove('dragging'); };
  canvas.addEventListener('pointerup', stop);
  canvas.addEventListener('pointercancel', stop);
  canvas.addEventListener('lostpointercapture', stop);
}

centerVisibleEntries();
