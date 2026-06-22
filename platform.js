const $ = (selector, scope = document) => scope.querySelector(selector);
const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];

$('#year').textContent = new Date().getFullYear();

const header = $('.site-header');
const menuToggle = $('.menu-toggle');
menuToggle.addEventListener('click', () => {
  const open = header.classList.toggle('menu-open');
  menuToggle.setAttribute('aria-expanded', String(open));
});
$$('.main-nav a').forEach(link => link.addEventListener('click', () => {
  header.classList.remove('menu-open');
  menuToggle.setAttribute('aria-expanded', 'false');
}));

const trackingModal = $('#tracking-modal');
$$('[data-open-tracking]').forEach(button => button.addEventListener('click', () => trackingModal.showModal()));
$('.modal-close', trackingModal).addEventListener('click', () => trackingModal.close());
trackingModal.addEventListener('click', event => { if (event.target === trackingModal) trackingModal.close(); });
$('#track-order').addEventListener('click', () => {
  const code = $('#tracking-code').value.trim().toUpperCase();
  if (!code) {
    $('#tracking-code').focus();
    $('#tracking-code').setCustomValidity('Introduza o código do pedido.');
    $('#tracking-code').reportValidity();
    return;
  }
  $('#tracking-code').setCustomValidity('');
  const message = encodeURIComponent(`Olá Scolor Print, quero consultar o estado do pedido ${code}.`);
  window.open(`https://wa.me/258849900402?text=${message}`, '_blank', 'noopener');
});
$('#tracking-code').addEventListener('input', event => event.target.setCustomValidity(''));

$$('.file-field input[type="file"]').forEach(input => input.addEventListener('change', () => {
  const file = input.files[0];
  const title = $('b', input.nextElementSibling);
  const note = $('small', input.nextElementSibling);
  if (!file) return;
  if (file.size > 8 * 1024 * 1024) {
    input.value = '';
    title.textContent = 'Ficheiro demasiado grande';
    note.textContent = 'Escolha um ficheiro até 8 MB';
    return;
  }
  title.textContent = file.name;
  note.textContent = `${Math.max(1, Math.round(file.size / 1024))} KB · pronto para enviar`;
}));

async function submitForm(form) {
  const button = $('button[type="submit"]', form);
  const status = $('.form-status', form);
  const original = button.innerHTML;
  button.disabled = true;
  button.textContent = 'A enviar...';
  status.className = 'form-status';
  status.textContent = '';
  const data = new FormData(form);
  data.append('_captcha', 'false');
  data.append('_template', 'table');
  data.append('_url', location.href);
  try {
    const response = await fetch(form.action, { method: 'POST', body: data, headers: { Accept: 'application/json' } });
    if (!response.ok) throw new Error('Falha no envio');
    status.className = 'form-status success';
    status.textContent = form.id === 'partner-form' ? 'Obrigado pela candidatura. A equipa Scolor Print irá analisar os seus dados e entrar em contacto pelo WhatsApp.' : 'Pedido enviado. Vamos responder pelo WhatsApp com orientação, preço e prazo.';
    button.innerHTML = 'Enviado com sucesso ✓';
    form.reset();
    $$('.file-field span b', form).forEach(item => item.textContent = '↑ Escolher ficheiro');
  } catch {
    status.className = 'form-status error';
    status.innerHTML = 'Não foi possível enviar agora. <a href="https://wa.me/258849900402" target="_blank" rel="noopener">Envie pelo WhatsApp</a> ou contacte info@scolorprint.com.';
    button.disabled = false;
    button.innerHTML = original;
  }
}

$$('.smart-form').forEach(form => form.addEventListener('submit', event => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  submitForm(form);
}));
