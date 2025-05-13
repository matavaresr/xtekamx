document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab');
    const contents = document.querySelectorAll('.tab-content');
    const questions = document.querySelectorAll(".xteka-faq-question");
    const answers = document.querySelectorAll(".xteka-faq-answer");
    const arrows = document.querySelectorAll(".arrow");
    const toggle = document.getElementById("expandir-toggle");
    const detalles = document.querySelectorAll(".detalle-dia");
    const botones = document.querySelectorAll(".boton-colapsar");

    const toggleGrupos = document.querySelectorAll(".grupo-toggle");

    toggleGrupos.forEach(toggle => {
        const group = toggle.dataset.group;
        const detalles = document.querySelectorAll(`.detalle-dia[data-group="${group}"]`);
        const botones = document.querySelectorAll(`.boton-colapsar[data-group="${group}"]`);
        const flechas = document.querySelectorAll(`[data-group="${group}"] .arrow`);

        const expandir = (el, arrow) => {
            el.style.maxHeight = el.scrollHeight + "px";
            if (arrow) arrow.classList.add("rotate");
        };

        const colapsar = (el, arrow) => {
            el.style.maxHeight = "0px";
            if (arrow) arrow.classList.remove("rotate");
        };

        // Toggle global
        const aplicarEstadoGlobal = () => {
            detalles.forEach((d, i) => {
                if (toggle.checked) expandir(d, flechas[i]);
                else colapsar(d, flechas[i]);
            });
        };

        // Ejecutar al inicio (esperar render)
        setTimeout(aplicarEstadoGlobal, 10);
        toggle.addEventListener("change", aplicarEstadoGlobal);

        // Botón individual (abre solo uno)
        botones.forEach((btn, i) => {
            btn.addEventListener("click", () => {
                detalles.forEach((ans, j) => {
                    const arrow = flechas[j];
                    const isCurrent = i === j;
                    const isOpen = ans.style.maxHeight && ans.style.maxHeight !== "0px";

                    if (isCurrent) {
                        isOpen ? colapsar(ans, arrow) : expandir(ans, arrow);
                    } else {
                        colapsar(ans, arrow);
                    }
                });
            });
        });
    });

    tabs.forEach((tab, index) => {
        tab.addEventListener('click', () => {
            // Activar pestaña
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Mostrar contenido correspondiente
            contents.forEach(c => c.classList.remove('active'));
            contents[index].classList.add('active');
        });
    });

    // Modal abrir
    const btn = document.getElementById('btn-reservar');
    if (btn) {
        btn.addEventListener('click', () => {
            document.getElementById("modalReservacion").classList.remove("hidden");
        });
    }
});