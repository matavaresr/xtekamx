const submitBtn = document.getElementById("submit-btn");
const submitText = document.getElementById("submit-text");
const spinner = document.getElementById("spinner");
const form = document.getElementById("formReservacion");

function mostrarConfirmModal(onAceptar, onCancelar) {
    const modal = document.getElementById("confirmModal");
    modal.classList.remove("hidden");

    const btnAceptar = document.getElementById("btnConfirmarUso");
    const btnCancelar = document.getElementById("btnCancelarUso");

    btnAceptar.onclick = () => {
        modal.classList.add("hidden");
        if (typeof onAceptar === 'function') onAceptar();
    };

    btnCancelar.onclick = () => {
        modal.classList.add("hidden");
        if (typeof onCancelar === 'function') onCancelar();
    };
}

function cerrarConfirmModal() {
    document.getElementById("confirmModal").classList.add("hidden");
}

function closeModal() {
    const modal = document.getElementById("modalReservacion");
    if (modal) {
        modal.classList.add("hidden");
    }
}

document.addEventListener("DOMContentLoaded", () => {
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

    const input = document.getElementById('fecha_inicio');
    if (!input) return;

    let bloqueadas = [];
    try {
        bloqueadas = JSON.parse(document.getElementById("rango-reservas").textContent);
        if (!Array.isArray(bloqueadas)) {
            console.error("La variable bloqueadas no es un array:", bloqueadas);
            bloqueadas = [];
        }
    } catch (e) {
        console.warn("No se pudieron leer las fechas bloqueadas o el JSON estaba vacío");
        bloqueadas = [];
    }

    const hoy = new Date();

    flatpickr(input, {
        dateFormat: "Y-m-d",
        minDate: new Date(hoy.setDate(hoy.getDate() + 10)),
        disable: bloqueadas,
        maxDate: new Date(hoy.setDate(hoy.getDate() + 365))
    });

    const btnReservar = document.getElementById("btn-reservar");
    if (btnReservar) {
        btnReservar.addEventListener("click", () => {
            const modal = document.getElementById("modalReservacion");
            if (modal) {
                modal.classList.remove("hidden");
            }
        });
    }

    function showSpinner(bool){
        if (bool)
        {
            submitBtn.disabled = true;
            submitText.style.display = "none";
            spinner.style.display = "inline-block";
        }else{
            submitBtn.disabled = false;
            submitText.style.display = "inline";
            spinner.style.display = "none";
        }
    }

    form.addEventListener('submit', function (event) {
        showSpinner(true);
        event.preventDefault();
    
        const form = event.target;
        const formData = new FormData(form);
    
        fetch('/ajax/reservar/', {
            method: "POST",
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(async response => {
            const data = await response.json();
    
            if (response.ok) {
                showToast(data.message || "Reservación exitosa", 'success');
                showSpinner(false);
                form.reset();
                closeModal();
            } else {
                // Mostrar errores del formulario Cliente
                if (data.cliente_errors) {
                    for (let field in data.cliente_errors) {
                        data.cliente_errors[field].forEach(errorObj => {
                            showToast(`${errorObj.message}`, 'error');
                        });
                    }
                }
    
                // Mostrar errores del formulario Reservacion
                if (data.reservacion_errors) {
                    for (let field in data.reservacion_errors) {
                        data.reservacion_errors[field].forEach(errorObj => {
                            showToast(`${errorObj.message}`, 'error');
                        });
                    }
                }
    
                // Mensaje genérico si no hay errores específicos
                if (!data.cliente_errors && !data.reservacion_errors && data.message) {
                    showToast(data.message, 'error');
                }
                showSpinner(false);
            }

            const paqueteId = formData.get('paquete_id');
            fetch(`/ajax/fechas-bloqueadas/${paqueteId}/`)
                .then(resp => resp.json())
                .then(result => {
                    if (result.bloqueadas) {
                        bloqueadas = result.bloqueadas;  // variable global actualizada

                        // Destruir y reinicializar el flatpickr con nuevas fechas
                        if (input._flatpickr) {
                            input._flatpickr.destroy();
                        }

                        flatpickr(input, {
                            dateFormat: "Y-m-d",
                            minDate: new Date(new Date().setDate(new Date().getDate() + 10)),
                            disable: bloqueadas,
                            maxDate: new Date(new Date().setDate(new Date().getDate() + 365))
                        });
                    }
                });
        })
        .catch(error => {
            console.error("Error en la solicitud AJAX:", error);
            showToast("Ocurrió un error al enviar el formulario.", 'error');
            showSpinner(false);
        });
    });    
});

