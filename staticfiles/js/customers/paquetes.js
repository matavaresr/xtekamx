document.getElementById('filtros-form').addEventListener('change', function(e) {
    e.preventDefault();
    const form = this;
    const params = new URLSearchParams(new FormData(form));
  
    fetch(window.location.pathname + '?' + params.toString(), {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(res => res.text())
    .then(html => {
      document.getElementById('paquetes-container').innerHTML = html;
    });
  });