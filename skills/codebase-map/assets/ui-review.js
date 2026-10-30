
// Screen previews are inert; this only scales the report viewer, never an application.
function fitUiFlow() {
  const panel=document.getElementById('panel-ui-preview');
  if(!panel || !panel.offsetWidth) return;
  const canvas=panel.querySelector('.ui-canvas');
  const scaled=panel.querySelector('.ui-scaled');
  const width=parseFloat(scaled.style.getPropertyValue('--ui-width'));
  const selected=document.querySelector('input[name="diagram-zoom"]:checked');
  const value=selected?.id==='zoom-fit' ? Math.min(1,canvas.clientWidth/width) : ({'zoom-100':1,'zoom-125':1.25,'zoom-150':1.5}[selected?.id]||1);
  scaled.style.setProperty('--scale',value);
}
for(const input of document.querySelectorAll('.review input[type="radio"]')) input.addEventListener('change',fitUiFlow);
if(typeof ResizeObserver==='function') {
  const uiCanvas=document.querySelector('.ui-canvas');
  if(uiCanvas) new ResizeObserver(fitUiFlow).observe(uiCanvas);
}
fitUiFlow();

// Keep source/decision links clickable; report panning must not capture their pointer.
for(const link of document.querySelectorAll('.ui-canvas a')) {
  link.addEventListener('pointerdown',event=>event.stopPropagation());
}
