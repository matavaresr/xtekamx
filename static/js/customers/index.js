const video_movil = window.matchMedia('(max-width: 800px)');
const video = document.getElementById("background-video");
const container_video = document.getElementById("video-container");

const controlar_video = () => {
    if (window.innerWidth > 800) {
        video.pause();                 // Detiene el video
        container_video.style.display = 'none';  // Asegura que esté visible
    }else{
        video.play();                
        container_video.style.display = 'block';
    }
}
video_movil.addEventListener('change', () => {
    controlar_video();
});  

video.addEventListener('timeupdate', function() {
    localStorage.setItem('videoTime', video.currentTime);
});

window.addEventListener('load', function() {
    controlar_video();

    const savedTime = localStorage.getItem('videoTime');
        if (savedTime) {
            video.currentTime = savedTime;
        }

        setTimeout(function() {
            document.getElementById('loader').classList.add('hidden');
        }, 500);
});


const textos = ["HUASTECA POTOSINA", "CASCADA EL MECO", "CASCADA DE TAMUL", "ASOMBROSA XILITLA"];
let indexTexto = 0;
let indexLetra = 0;
let actualTexto = "";
let letra = "";
let escribiendo = true;

function escribir() {
  actualTexto = textos[indexTexto];

  if (escribiendo) {
    letra = actualTexto.slice(0, ++indexLetra);
    document.getElementById('text-change-title').textContent = letra;

    if (letra.length === actualTexto.length) {
      escribiendo = false;
      setTimeout(escribir, 1500); // Espera antes de empezar a borrar
    } else {
      setTimeout(escribir, 100); // Velocidad escribiendo
    }
  } else {
    letra = actualTexto.slice(0, --indexLetra);
    document.getElementById('text-change-title').textContent = letra;

    if (indexLetra === 0) {
      escribiendo = true;
      indexTexto = (indexTexto + 1) % textos.length;
      setTimeout(escribir, 500); // Espera un poco antes de empezar a escribir otra vez
    } else {
      setTimeout(escribir, 50); // Velocidad borrando (puedes hacer que borre más rápido si quieres)
    }
  }
}

escribir();