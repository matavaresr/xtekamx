const elements = document.querySelectorAll('.fade-in-on-scroll');

function checkVisibility() {
  elements.forEach(el => {
    const rect = el.getBoundingClientRect();
    if (rect.top < window.innerHeight) {
      el.classList.add('visible');
    }
  });
}

window.addEventListener('load', function() {
    checkVisibility();
});

window.addEventListener('scroll', checkVisibility);