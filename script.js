const menuButton = document.querySelector('.menu-toggle');
const nav = document.querySelector('.main-nav');
menuButton.addEventListener('click', () => {
  const open = nav.classList.toggle('open');
  menuButton.setAttribute('aria-expanded', String(open));
});
nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
  nav.classList.remove('open');
  menuButton.setAttribute('aria-expanded', 'false');
}));

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
document.getElementById('year').textContent = new Date().getFullYear();

document.getElementById('quote-form').addEventListener('submit', event => {
  event.preventDefault();
  const data = new FormData(event.currentTarget);
  const message = [
    'Olá S Color Print, gostaria de pedir um orçamento.',
    '',
    `Nome: ${data.get('nome')}`,
    `Contacto: ${data.get('contacto')}`,
    `Serviço: ${data.get('servico')}`,
    `Projecto: ${data.get('mensagem') || 'A combinar'}`
  ].join('\n');
  window.open(`https://wa.me/258849900402?text=${encodeURIComponent(message)}`, '_blank', 'noopener');
});
