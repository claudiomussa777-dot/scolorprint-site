const $ = (selector, scope = document) => scope.querySelector(selector);
const $$ = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));

const phone = '258849900402';
const form = $('#order-form');
const productInput = $('#selected-product');
const productSummary = $('#summary-product');
const previewImage = $('#preview-image');
const whatsappOrder = $('#whatsapp-order');
const status = $('.form-status', form);

function whatsappUrl(message) {
  return `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;
}

function buildMessage() {
  const data = new FormData(form);
  const product = data.get('Produto') || 'produto personalizado';
  const name = data.get('Nome') || '';
  const qty = data.get('Quantidade') || '';
  const city = data.get('Cidade') || '';
  const idea = data.get('Ideia') || '';

  return [
    'Olá Smart Color Print, quero receber orçamento em até 10 minutos.',
    `Produto: ${product}`,
    name && `Nome: ${name}`,
    qty && `Quantidade: ${qty}`,
    city && `Cidade: ${city}`,
    idea && `Ideia: ${idea}`
  ].filter(Boolean).join('\n');
}

function refreshWhatsAppLink() {
  whatsappOrder.href = whatsappUrl(buildMessage());
}

$$('[data-product]').forEach(card => {
  card.addEventListener('click', () => {
    const product = card.dataset.product;
    const image = card.dataset.img;

    $$('[data-product]').forEach(item => item.classList.remove('is-selected'));
    card.classList.add('is-selected');

    productInput.value = product;
    productSummary.textContent = product;
    previewImage.src = image;
    previewImage.alt = `Pré-visualização: ${product}`;
    refreshWhatsAppLink();
    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});

$$('input, textarea', form).forEach(field => {
  field.addEventListener('input', refreshWhatsAppLink);
  field.addEventListener('change', refreshWhatsAppLink);
});

$('.file-field input', form).addEventListener('change', event => {
  const file = event.target.files[0];
  const label = $('.file-field strong', form);
  const hint = $('.file-field small', form);

  if (!file) {
    label.textContent = 'Anexar imagem ou logotipo';
    hint.textContent = 'Opcional. Pode enviar referência, arte ou PDF.';
    return;
  }

  if (file.size > 8 * 1024 * 1024) {
    event.target.value = '';
    label.textContent = 'Ficheiro demasiado grande';
    hint.textContent = 'Escolha imagem ou PDF até 8 MB.';
    return;
  }

  label.textContent = file.name;
  hint.textContent = 'Ficheiro pronto para enviar.';
});

form.addEventListener('submit', async event => {
  event.preventDefault();
  if (!form.reportValidity()) return;

  const button = $('button[type="submit"]', form);
  const originalLabel = button.textContent;
  const data = new FormData(form);
  data.append('_url', location.href);

  button.disabled = true;
  button.textContent = 'A enviar...';
  status.className = 'form-status';
  status.textContent = '';

  try {
    const response = await fetch(form.action, {
      method: 'POST',
      body: data,
      headers: { Accept: 'application/json' }
    });

    if (!response.ok) throw new Error('Form submission failed');

    status.className = 'form-status success';
    status.textContent = 'Pedido enviado. Vamos responder pelo WhatsApp com preço e prazo em até 10 minutos.';
    button.textContent = 'Pedido enviado ✓';
    form.reset();
    productInput.value = productSummary.textContent;
    $('.file-field strong', form).textContent = 'Anexar imagem ou logotipo';
    $('.file-field small', form).textContent = 'Opcional. Pode enviar referência, arte ou PDF.';
    refreshWhatsAppLink();
  } catch {
    status.className = 'form-status error';
    status.textContent = 'Não foi possível enviar por email. Use o botão de WhatsApp abaixo.';
    whatsappOrder.href = whatsappUrl(buildMessage());
    whatsappOrder.focus();
    button.disabled = false;
    button.textContent = originalLabel;
  }
});

refreshWhatsAppLink();
