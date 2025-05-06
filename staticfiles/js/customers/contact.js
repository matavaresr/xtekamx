document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("forms-contact");
  const mensaje = document.getElementById("mensaje-flotante");
  const submitBtn = document.getElementById("submit-btn");
  const submitText = document.getElementById("submit-text");
  const spinner = document.getElementById("spinner");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    // Ocultar texto y mostrar spinner
    submitBtn.disabled = true;
    submitText.style.display = "none";
    spinner.style.display = "inline-block";

    const formData = new FormData(form);
    const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]").value;

    fetch("/core/enviar-correo-contacto/", {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken,
        "X-Requested-With": "XMLHttpRequest"  // <- Esto es lo nuevo
      },
      body: formData,
    })
    .then(response => {
      if (!response.ok) throw new Error("Error");
      return response.text();
    })
    .then(() => {
      mensaje.style.display = "block";
      setTimeout(() => mensaje.style.display = "none", 3000);
      form.reset();
    })
    .catch(error => {
      alert("Hubo un error al enviar el correo.");
      console.error(error);
    })
    .finally(() => {
      // Restaurar texto y ocultar spinner
      submitBtn.disabled = false;
      submitText.style.display = "inline";
      spinner.style.display = "none";
    });
  });
});