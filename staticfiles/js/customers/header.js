const media_movil = window.matchMedia('(max-width: 1150px)');
const menu = document.getElementById('menu-expanded');
const btn_nav = document.getElementById('btn-nav-vertical');
const logo_nav = document.getElementById('nav-logo');
const nav_urls = document.getElementById('nav-urls');

const menu_expanded = (changes_window) => {
    if(btn_nav.classList.contains("open") || changes_window){
        menu.classList.remove('visible');
        btn_nav.classList.remove('open');
        nav_urls.classList.remove('remove-shadow');
        document.body.style.overflow = 'visible';
    }else{
        menu.classList.add('visible');
        btn_nav.classList.add('open');
        nav_urls.classList.add('remove-shadow');
        document.body.style.overflow = 'hidden';
    }
}

document.getElementById('btn-nav-vertical').addEventListener('click', () => {
    menu_expanded(false);
});

media_movil.addEventListener('change', () => {
    menu_expanded(true);
});  

window.addEventListener('scroll', function() {
    if (window.scrollY >= 40) { 
        nav_urls.classList.add('scroll-down');
    }else{
        nav_urls.classList.remove('scroll-down');
    }
});
