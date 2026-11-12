const header = document.querySelector('[data-header]');
const menuButton = document.querySelector('[data-menu-toggle]');
const navigation = document.querySelector('[data-nav]');

const updateHeader = () => header.classList.toggle('scrolled', window.scrollY > 20);
updateHeader();
window.addEventListener('scroll', updateHeader, { passive: true });

const closeMenu = () => {
  navigation.classList.remove('open');
  menuButton.setAttribute('aria-expanded', 'false');
  menuButton.setAttribute('aria-label', 'Открыть меню');
  document.body.classList.remove('menu-open');
};

menuButton.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  navigation.classList.toggle('open', open);
  menuButton.setAttribute('aria-expanded', String(open));
  menuButton.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
  document.body.classList.toggle('menu-open', open);
});

navigation.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
window.addEventListener('resize', () => {
  if (window.innerWidth > 760) closeMenu();
});

document.querySelectorAll('[data-year]').forEach(node => {
  node.textContent = new Date().getFullYear();
});

const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const revealItems = document.querySelectorAll('.reveal');
if (reducedMotion || !('IntersectionObserver' in window)) {
  revealItems.forEach(item => item.classList.add('visible'));
} else {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -35px' });
  revealItems.forEach(item => observer.observe(item));
}

const lightbox = document.querySelector('[data-lightbox]');
const lightboxImage = document.querySelector('[data-lightbox-image]');
const lightboxCaption = document.querySelector('[data-lightbox-caption]');
const closeLightboxButton = document.querySelector('[data-lightbox-close]');
let lastGalleryButton = null;

document.querySelectorAll('[data-gallery]').forEach(button => {
  button.addEventListener('click', () => {
    lastGalleryButton = button;
    lightboxImage.src = button.dataset.gallery;
    lightboxImage.alt = button.dataset.alt;
    lightboxCaption.textContent = button.dataset.alt;
    lightbox.showModal();
  });
});

const closeLightbox = () => lightbox.close();
closeLightboxButton.addEventListener('click', closeLightbox);
lightbox.addEventListener('click', event => {
  if (event.target === lightbox) closeLightbox();
});
lightbox.addEventListener('close', () => {
  if (lastGalleryButton) lastGalleryButton.focus();
});
