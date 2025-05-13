const submitBtn = document.getElementById("submit-btn");
const submitText = document.getElementById("submit-text");
const spinner = document.getElementById("spinner");

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
        }, 4000);
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

    console.log(bloqueadas);

    const duracion = parseInt(input.dataset.duracion || "1");
    const hoy = new Date();
    hoy.setDate(hoy.getDate() + 10);

    flatpickr(input, {
        minDate: hoy,
        disable: bloqueadas,
        onDayCreate: function (dObj, dStr, fp, dayElem) {
            if (!dayElem.dateObj) return;
            dayElem.addEventListener("mouseenter", () => {
                const start = new Date(dayElem.dateObj);
                for (let i = 0; i < duracion; i++) {
                    const target = new Date(start);
                    target.setDate(start.getDate() + i);
                    const label = target.toDateString();
                    const targetElem = fp.calendarContainer.querySelector(`.flatpickr-day[aria-label='${label}']`);
                    if (targetElem) targetElem.classList.add("in-range-hover");
                }
            });
            dayElem.addEventListener("mouseleave", () => {
                const elems = fp.calendarContainer.querySelectorAll(".in-range-hover");
                elems.forEach(el => el.classList.remove("in-range-hover"));
            });
        },
        onChange: function (selectedDates, dateStr, fp) {
            if (!selectedDates.length) return;
            const start = new Date(selectedDates[0]);
            fp.calendarContainer.querySelectorAll(".in-range-hover")
                .forEach(el => el.classList.remove("in-range-hover"));

            for (let i = 0; i < duracion; i++) {
                const target = new Date(start);
                target.setDate(start.getDate() + i);
                const label = target.toDateString();
                const targetElem = fp.calendarContainer.querySelector(`.flatpickr-day[aria-label='${label}']`);
                if (targetElem) targetElem.classList.add("in-range-hover");
            }
        }
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

    document.getElementById("formReservacion").addEventListener("submit", function (e) {
        e.preventDefault();
        submitBtn.disabled = true;
        submitText.style.display = "none";
        spinner.style.display = "inline-block";

        const form = e.target;

        const data = {
            nombre: form.nombre.value,
            apellido: form.apellido.value,
            email: form.email.value,
            telefono: form.telefono.value,
            fecha_inicio: form.fecha_inicio.value,
            cantidad_adultos: form.cantidad_adultos.value,
            cantidad_ninos: form.cantidad_ninos.value,
            paquete_id: PAQUETE_ID
        };

        fetch(URL_RESERVACION, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": form.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(data)
        })
            .then(res => res.json())
            .then(response => {
                if (response.match && response.cliente) {
                    // Mostrar modal de confirmación visual
                    mostrarConfirmModal(() => {
                        // Si acepta usar datos previos, los aplicamos
                        form.nombre.value = response.cliente.nombre;
                        form.apellido.value = response.cliente.apellido;
                        form.telefono.value = response.cliente.telefono;

                        fetch(URL_RESERVACION, {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                                "X-CSRFToken": form.querySelector('[name=csrfmiddlewaretoken]').value
                            },
                            body: JSON.stringify({
                                ...data,
                                usar_datos_previos: true
                            })
                        })
                            .then(res2 => res2.json())
                            .then(r2 => {
                                if (r2.success) {
                                    showToast(r2.success, 'success');
                                    form.reset();
                                    closeModal();
                                } else {
                                    showToast(r2.error || "Error al confirmar con los datos previos.", 'error');
                                }
                                submitBtn.disabled = false;
                                submitText.style.display = "inline";
                                spinner.style.display = "none";
                            })
                            .catch(() => {
                                showToast("Error al reenviar la solicitud.", 'error');
                                submitBtn.disabled = false;
                                submitText.style.display = "inline";
                                spinner.style.display = "none";
                            });
                    }, () => {
                        // Si elige NO usar datos previos, se avisa que debe usar otro correo
                        showToast("Este correo ya está registrado. Por favor, usa otro diferente.", 'info');
                        submitBtn.disabled = false;
                        submitText.style.display = "inline";
                        spinner.style.display = "none";
                    });

                } else if (response.success) {
                    showToast(response.success, 'success');
                    form.reset();
                    closeModal();
                    submitBtn.disabled = false;
                    submitText.style.display = "inline";
                    spinner.style.display = "none";
                } else {
                    showToast(response.error || "Ocurrió un error.", 'error');
                    submitBtn.disabled = false;
                    submitText.style.display = "inline";
                    spinner.style.display = "none";
                }
            })
            .catch(() => {
                showToast("Error al enviar la solicitud.", 'error');
                submitBtn.disabled = false;
                submitText.style.display = "inline";
                spinner.style.display = "none";
            });

            setTimeout(() => {
                location.reload();
            }, 5000);
    });
});