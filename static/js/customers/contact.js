document.addEventListener("DOMContentLoaded", function () {

  function showToast(message, type = 'info') {
      const toast = document.createElement('div');
      toast.className = `toast ${type}`;
      toast.textContent = message;

      const container = document.getElementById('toastContainer');
      container.appendChild(toast);

      setTimeout(() => {
          toast.remove();
      }, 10000);
  }

  const form = document.getElementById("forms-contact");
  const mensaje = document.getElementById("mensaje-flotante");
  const submitBtn = document.getElementById("submit-btn");
  const submitText = document.getElementById("submit-text");
  const spinner = document.getElementById("spinner");
  
  form.addEventListener("submit", function (e) {
    e.preventDefault();
  
    submitBtn.disabled = true;
    submitText.style.display = "none";
    spinner.style.display = "inline-block";
  
    const name = document.getElementById("name").value.trim();
    const lastName = document.getElementById("last_name").value.trim();
    const telefono = document.getElementById("telefono").value.trim();
    const email = document.getElementById("email").value.trim();
    const mensajeTexto = document.getElementById("mensaje").value.trim();
  
    if (!name || !lastName || !telefono || !email || !mensajeTexto) {
      showToast("Todos los campos son obligatorios.", "error");
      restoreSubmitButton();
      return;
    }
  
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
      showToast("Por favor, ingresa un correo electrónico válido.", "error");
      restoreSubmitButton();
      return;
    }
  
    const formData = new FormData(form);
    const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]").value;
  
    fetch("/core/enviar-correo-contacto/", {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken,
        "X-Requested-With": "XMLHttpRequest"
      },
      body: formData,
    })
    .then(response => {
      if (!response.ok) throw new Error("Error al enviar");
      return response.text();
    })
    .then(() => {
      showToast("Formulario enviado correctamente.", "success");
      form.reset();
    })
    .catch(error => {
      console.error(error);
      showToast("Hubo un error al enviar el formulario.", "error");
    })
    .finally(() => {
      restoreSubmitButton();
    });
  });
  
  function restoreSubmitButton() {
    submitBtn.disabled = false;
    submitText.style.display = "inline";
    spinner.style.display = "none";
  }
  
});