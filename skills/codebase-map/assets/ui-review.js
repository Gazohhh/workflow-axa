
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

// Kit screens: one copy of each saved kit's styles, expanded into sandboxed srcdoc frames.
// The frames run no scripts; only the kit's inlined fonts and Typekit may load (report policy).
(function buildKitFrames(){
  const node=document.getElementById('ui-kit-data');
  if(!node) return;
  let data;
  try { data=JSON.parse(node.textContent); } catch { return; }
  const frameCsp="default-src 'none'; script-src 'none'; style-src 'unsafe-inline' https://use.typekit.net https://p.typekit.net; "+
    "font-src data: https://use.typekit.net; img-src data:; connect-src 'none'; form-action 'none'; base-uri 'none'";
  const docs={};
  function build(id){
    if(docs[id]) return docs[id];
    const screen=data.screens[id]; const kit=screen && data.kits[screen.kit];
    if(!kit) return '';
    const markup=screen.markup.replace(/<style data-kit-shadow-ref="(k\d+)"><\/style>/g,(m,key)=>'<style>'+(kit.shadow[key]||'')+'</style>');
    const assets=text=>text.replace(/__KIT_ASSET_\d+__/g,key=>kit.assets[key]||'data:,');
    const links=kit.typekit.map(href=>'<link rel="stylesheet" href="'+href+'">').join('');
    docs[id]='<!doctype html><html'+kit.html_attrs+'><head><meta charset="utf-8">'+
      '<meta http-equiv="Content-Security-Policy" content="'+frameCsp+'">'+links+'<style>'+assets(kit.css)+'</style></head>'+
      '<body'+kit.body_attrs+'>'+assets(markup)+'</body></html>';
    return docs[id];
  }
  for(const frame of document.querySelectorAll('iframe[data-kit-screen]')) frame.srcdoc=build(frame.dataset.kitScreen);
  // Full-size views show the whole 1280px page scaled to the report column, never cut off.
  function fitKitDetails(){
    for(const box of document.querySelectorAll('.ui-kit-detail')){
      const frame=box.querySelector('iframe');
      if(!frame || !box.clientWidth) continue;
      const scale=Math.min(1,box.clientWidth/frame.width);
      frame.style.transform='scale('+scale+')';
      box.style.height=Math.ceil(frame.height*scale)+'px';
    }
  }
  fitKitDetails();
  for(const d of document.querySelectorAll('details')) d.addEventListener('toggle',fitKitDetails);
  window.addEventListener('resize',fitKitDetails);
})();
