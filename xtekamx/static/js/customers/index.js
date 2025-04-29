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