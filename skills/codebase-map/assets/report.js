'use strict';
// The viewer changes only SVG viewBoxes; it never submits or records approval.
for (const card of document.querySelectorAll('.graph-card')) {
  const svg = card.querySelector('svg');
  const original = svg.dataset.original.split(' ').map(Number);
  let box = [...original];
  let drag = null;
  const draw = () => svg.setAttribute('viewBox', box.join(' '));
  const zoom = factor => {
    const width = Math.min(original[2] * 4, Math.max(original[2] / 8, box[2] * factor));
    const scale = width / box[2];
    const height = box[3] * scale;
    box = [box[0] + (box[2] - width) / 2, box[1] + (box[3] - height) / 2, width, height];
    draw();
  };
  const fit = () => { box = [...original]; draw(); };
  card.querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
    if (button.dataset.action === 'fit') fit();
    else zoom(button.dataset.action === 'in' ? 0.8 : 1.25);
  }));
  svg.addEventListener('wheel', event => {
    // Ordinary scrolling still moves the document; Ctrl/Command-wheel zooms the board.
    if (!event.ctrlKey && !event.metaKey) return;
    event.preventDefault();
    zoom(event.deltaY < 0 ? 0.9 : 1.1);
  }, {passive: false});
  svg.addEventListener('keydown', event => {
    if (['+', '=', '-', 'f', 'F', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) {
      event.preventDefault();
      if (event.key === '+' || event.key === '=') zoom(0.8);
      else if (event.key === '-') zoom(1.25);
      else if (event.key.toLowerCase() === 'f') fit();
      else {
        if (event.key === 'ArrowLeft') box[0] -= box[2] / 12;
        if (event.key === 'ArrowRight') box[0] += box[2] / 12;
        if (event.key === 'ArrowUp') box[1] -= box[3] / 12;
        if (event.key === 'ArrowDown') box[1] += box[3] / 12;
        draw();
      }
    }
  });
  svg.addEventListener('pointerdown', event => {
    if (event.button !== 0) return;
    const matrix = svg.getScreenCTM();
    if (!matrix) return;
    drag = {x:event.clientX, y:event.clientY, box:[...box], scale:1 / matrix.a};
    svg.setPointerCapture(event.pointerId);
    svg.classList.add('dragging');
  });
  svg.addEventListener('pointermove', event => {
    if (!drag) return;
    box[0] = drag.box[0] - (event.clientX - drag.x) * drag.scale;
    box[1] = drag.box[1] - (event.clientY - drag.y) * drag.scale;
    draw();
  });
  const stop = () => { drag = null; svg.classList.remove('dragging'); };
  svg.addEventListener('pointerup', stop);
  svg.addEventListener('pointercancel', stop);
  svg.addEventListener('lostpointercapture', stop);
}
// Evidence anchors reveal their containing details when navigating from a diagram.
for (const anchor of document.querySelectorAll('a[href^="#"]')) {
  anchor.addEventListener('click', () => {
    const target = document.getElementById(anchor.getAttribute('href').slice(1));
    if (!target) return;
    let parent = target.parentElement;
    while (parent) {
      if (parent.tagName === 'DETAILS') parent.open = true;
      parent = parent.parentElement;
    }
  });
}
