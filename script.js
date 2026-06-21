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

document.getElementById('year').textContent = new Date().getFullYear();

const materialSelect = document.getElementById('material-select');
const sectorSelect = document.getElementById('sector-select');
const ideaInput = document.getElementById('idea-input');
const generateButton = document.getElementById('generate-button');
const mockupObject = document.getElementById('mockup-object');
const designFace = document.getElementById('design-face');
const mockupSector = document.getElementById('mockup-sector');
const mockupTitle = document.getElementById('mockup-title');
const quoteProduct = document.getElementById('quote-product');
const tones = document.querySelectorAll('.tone');
const proposals = document.querySelectorAll('.proposal');
const viewButtons = document.querySelectorAll('.view-switch button');
const workspaceStage = document.getElementById('workspace-stage');
let activeTone = 'Vibrante';
let activeStyle = 'one';

const productClasses = {
  'Cartão de visita': 'business-card', Flyer: 'flyer', Banner: 'banner',
  Menu: 'menu', Autocolante: 'sticker', 'T-shirt': 't-shirt'
};

const sectorNames = {
  Restaurante: ['SABORES', 'MESA', 'FRESCO'], Tecnologia: ['NEXO', 'FUTURO', 'LIGA'],
  Moda: ['LINHA', 'FORMA', 'MOVA'], Beleza: ['LUME', 'ESSÊNCIA', 'BRILHO'],
  Construção: ['BASE', 'FORTE', 'ERGUE'], Eventos: ['VIVA', 'MOMENTO', 'CELEBRA'],
  Educação: ['SABER', 'CRESCER', 'IDEIAS'], Outro: ['MARCA', 'NOVA', 'IMPACTO']
};

function applyProduct(product) {
  mockupObject.className = `mockup-object ${productClasses[product] || 'business-card'}`;
  quoteProduct.textContent = product;
  materialSelect.value = product;
  updateQuote();
}

document.querySelectorAll('.product-card').forEach(card => {
  card.addEventListener('click', () => {
    applyProduct(card.dataset.product);
    document.getElementById('studio').scrollIntoView({ behavior: 'smooth' });
  });
});

materialSelect.addEventListener('change', () => applyProduct(materialSelect.value));

tones.forEach(tone => tone.addEventListener('click', () => {
  tones.forEach(item => item.classList.remove('active'));
  tone.classList.add('active');
  activeTone = tone.dataset.tone;
}));

function applyProposal(style) {
  activeStyle = style;
  proposals.forEach(item => item.classList.toggle('selected', item.dataset.style === style));
  designFace.className = `design-face style-${style}`;
}

proposals.forEach(proposal => proposal.addEventListener('click', () => applyProposal(proposal.dataset.style)));

viewButtons.forEach(button => button.addEventListener('click', () => {
  viewButtons.forEach(item => item.classList.remove('active'));
  button.classList.add('active');
  workspaceStage.classList.toggle('flat', button.dataset.view === 'flat');
}));

generateButton.addEventListener('click', () => {
  const product = materialSelect.value;
  const sector = sectorSelect.value;
  const words = sectorNames[sector] || sectorNames.Outro;
  generateButton.classList.add('loading');
  generateButton.innerHTML = '<span>✦</span> A criar propostas...';
  applyProduct(product);

  setTimeout(() => {
    const detail = ideaInput.value.trim();
    const lead = detail ? detail.split(/\s+/).slice(0, 3).join(' ').toUpperCase() : words[0];
    mockupSector.textContent = `${sector.toUpperCase()} • ${activeTone.toUpperCase()}`;
    mockupTitle.innerHTML = `${lead}<br>${words[1]}`;
    document.querySelector('.mini-one b').textContent = words[0];
    document.querySelector('.mini-two b').textContent = words[1];
    document.querySelector('.mini-three b').textContent = words[2];
    applyProposal('one');
    generateButton.classList.remove('loading');
    generateButton.innerHTML = '<span>✓</span> 3 propostas criadas';
    setTimeout(() => generateButton.innerHTML = '<span>✦</span> Gerar novas propostas', 1800);
  }, 1200);
});

const quantityInput = document.getElementById('quantity-input');
const paperSelect = document.getElementById('paper-select');
const finishSelect = document.getElementById('finish-select');
const deliverySelect = document.getElementById('delivery-select');
const productionPrice = document.getElementById('production-price');
const deliveryPrice = document.getElementById('delivery-price');
const totalPrice = document.getElementById('total-price');

const pricing = {
  'Cartão de visita': { setup: 400, unit: 3.5 }, Flyer: { setup: 500, unit: 7 },
  Banner: { setup: 850, unit: 600 }, Menu: { setup: 550, unit: 55 },
  Autocolante: { setup: 350, unit: 5 }, 'T-shirt': { setup: 300, unit: 650 }
};
const materialFactor = { standard: 1, premium: 1.28, eco: 1.18 };
const finishFactor = { none: 1, matte: 1.2, gloss: 1.15 };
const deliveryFees = { pickup: 0, maputo: 250, matola: 350, province: 650 };
let latestTotal = 750;

function money(value) {
  return `${Math.round(value).toLocaleString('pt-PT')} MT`;
}

function updateQuote() {
  const product = materialSelect.value;
  const qty = Math.max(1, Number(quantityInput.value) || 1);
  const config = pricing[product] || pricing['Cartão de visita'];
  const volumeDiscount = qty >= 1000 ? .78 : qty >= 500 ? .84 : qty >= 250 ? .91 : 1;
  const production = (config.setup + config.unit * qty) * materialFactor[paperSelect.value] * finishFactor[finishSelect.value] * volumeDiscount;
  const delivery = deliveryFees[deliverySelect.value];
  latestTotal = production + delivery;
  productionPrice.textContent = money(production);
  deliveryPrice.textContent = delivery ? money(delivery) : 'Grátis';
  totalPrice.textContent = money(latestTotal);
}

[quantityInput, paperSelect, finishSelect, deliverySelect].forEach(field => field.addEventListener('input', updateQuote));
updateQuote();

const checkoutModal = document.getElementById('checkout-modal');
const checkoutButton = document.getElementById('checkout-button');
const modalClose = document.getElementById('modal-close');
const modalProduct = document.getElementById('modal-product');
const modalTotal = document.getElementById('modal-total');
const orderSummary = document.getElementById('order-summary');

checkoutButton.addEventListener('click', () => {
  const summary = `${materialSelect.value} • ${quantityInput.value} unidades • ${paperSelect.options[paperSelect.selectedIndex].text} • ${finishSelect.options[finishSelect.selectedIndex].text} • ${deliverySelect.options[deliverySelect.selectedIndex].text}`;
  modalProduct.textContent = summary;
  modalTotal.textContent = money(latestTotal);
  orderSummary.value = `${summary} • Total estimado: ${money(latestTotal)} • Direção visual: ${activeStyle}`;
  checkoutModal.showModal();
});
modalClose.addEventListener('click', () => checkoutModal.close());
checkoutModal.addEventListener('click', event => {
  if (event.target === checkoutModal) checkoutModal.close();
});

const orderForm = document.getElementById('order-form');
const modalStatus = document.getElementById('modal-status');
orderForm.addEventListener('submit', async event => {
  event.preventDefault();
  const button = orderForm.querySelector('button[type="submit"]');
  const original = button.innerHTML;
  button.disabled = true;
  button.textContent = 'A enviar...';
  modalStatus.textContent = '';
  modalStatus.className = 'modal-status';
  try {
    const data = Object.fromEntries(new FormData(orderForm).entries());
    const response = await fetch('https://formsubmit.co/ajax/info@scolorprint.com', {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Falha no envio');
    modalStatus.className = 'modal-status success';
    modalStatus.textContent = 'Pedido enviado! Entraremos em contacto para confirmar.';
    orderForm.reset();
  } catch (error) {
    modalStatus.className = 'modal-status error';
    modalStatus.textContent = 'Não foi possível enviar. Contacte info@scolorprint.com.';
  } finally {
    button.disabled = false;
    button.innerHTML = original;
  }
});
