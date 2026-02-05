(function(){
  // activar animaciones reveal
  document.querySelectorAll('.rp-reveal').forEach(el=>{
    requestAnimationFrame(()=>el.classList.add('in'));
  });
})();
