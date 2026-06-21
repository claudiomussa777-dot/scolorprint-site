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

const quoteForm = document.getElementById('quote-form');
const formStatus = document.getElementById('form-status');
quoteForm.addEventListener('submit', async event => {
  event.preventDefault();
  const submitButton = quoteForm.querySelector('button[type="submit"]');
  const originalLabel = submitButton.innerHTML;
  submitButton.disabled = true;
  submitButton.textContent = 'A enviar...';
  formStatus.className = 'form-status';
  formStatus.textContent = '';

  try {
    const formData = Object.fromEntries(new FormData(quoteForm).entries());
    const response = await fetch('https://formsubmit.co/ajax/info@scolorprint.com', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(formData)
    });
    if (!response.ok) throw new Error('Falha no envio');
    quoteForm.reset();
    formStatus.className = 'form-status success';
    formStatus.textContent = 'Pedido enviado com sucesso! Responderemos para o seu email.';
  } catch (error) {
    formStatus.className = 'form-status error';
    formStatus.innerHTML = 'Não foi possível enviar agora. Escreva para <a href="mailto:info@scolorprint.com">info@scolorprint.com</a>.';
  } finally {
    submitButton.disabled = false;
    submitButton.innerHTML = originalLabel;
  }
});
