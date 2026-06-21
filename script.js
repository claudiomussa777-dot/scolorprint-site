const $ = (selector, scope = document) => scope.querySelector(selector);
const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];

const API_BASE = (() => {
  const host = location.hostname;
  if (host === 'localhost' || host === '127.0.0.1' || host === '') return 'http://localhost:8765';
  return 'https://scolor-api.onrender.com';
})();

$('#year').textContent = new Date().getFullYear();
$('.menu-button').addEventListener('click', () => $('.site-header').classList.toggle('open'));

const PRODUCTS = {
  tshirt:   { name:'Camiseta',                 price:650,  front:'assets/mockup-tshirt-real-v2.jpg',    back:'assets/tshirt-designer-back-white-v1.png', zone:{l:'35%',t:'33%',w:'30%',h:'30%'}, colorable:false, hasBack:false, printLabel:'ÁREA DE IMPRESSÃO · FRENTE 30×40cm' },
  hoodie:   { name:'Hoodie',                   price:1500, front:'assets/mockup-hoodie-real-v2.jpg',    back:null,                                        zone:{l:'39%',t:'46%',w:'22%',h:'22%'}, colorable:false, hasBack:false, printLabel:'IMPRESSÃO · PEITO 25×25cm · DTG' },
  mug:      { name:'Mug',                      price:380,  front:'assets/mockup-mug-real-v2.jpg',       back:null,                                        zone:{l:'44%',t:'38%',w:'22%',h:'22%'}, colorable:false, hasBack:false, printLabel:'SUBLIMAÇÃO 360° · 330ml' },
  cap:      { name:'Boné',                     price:450,  front:'assets/mockup-cap-real-v2.jpg',       back:null,                                        zone:{l:'42%',t:'13%',w:'16%',h:'16%'}, colorable:false, hasBack:false, printLabel:'ÁREA FRONTAL · BORDADO/DTG · 8×4cm' },
  tote:     { name:'Tote bag',                 price:550,  front:'assets/mockup-tote-real-v2.jpg',      back:null,                                        zone:{l:'38%',t:'60%',w:'24%',h:'24%'}, colorable:false, hasBack:false, printLabel:'IMPRESSÃO CENTRAL · DTG 25×25cm' },
  bottle:   { name:'Garrafa térmica',          price:950,  front:'assets/mockup-bottle-real-v2.jpg',    back:null,                                        zone:{l:'43%',t:'42%',w:'14%',h:'14%'}, colorable:false, hasBack:false, printLabel:'GRAVAÇÃO LASER · ÁREA 7×12cm' },
  pillow:   { name:'Almofada',                 price:720,  front:'assets/mockup-pillow-real-v2.jpg',    back:null,                                        zone:{l:'34%',t:'34%',w:'32%',h:'32%'}, colorable:false, hasBack:false, printLabel:'SUBLIMAÇÃO TOTAL · 40×40cm' },
  frame:    { name:'Quadro personalizado',     price:1200, front:'assets/mockup-frame-real-v2.jpg',     back:null,                                        zone:{l:'37%',t:'34%',w:'26%',h:'26%'}, colorable:false, hasBack:false, printLabel:'IMPRESSÃO ALTA RES · 30×40cm' },
  keychain: { name:'Chaveiro',                 price:180,  front:'assets/mockup-keychain-real-v2.jpg',  back:null,                                        zone:{l:'39%',t:'44%',w:'22%',h:'22%'}, colorable:false, hasBack:false, printLabel:'ACRÍLICO · 6×6cm · UV' },
  giftkit:  { name:'Kit corporativo',          price:2500, front:'assets/mockup-giftkit-real-v2.jpg',   back:null,                                        zone:{l:'18%',t:'18%',w:'26%',h:'26%'}, colorable:false, hasBack:false, printLabel:'BUNDLE: t-shirt + mug + boné + caderno' }
};

const state = { productId: 'tshirt', product: 'Camiseta', basePrice: 650, color: 'Branco', side: 'Frente', zoom: 1, dx: 0, dy: 0 };
const shirtImage = $('#shirt-image');
const shirtWrap = $('#shirt-wrap');
const designContent = $('#design-content');
const uploadedArt = $('#uploaded-art');
const printZone = $('#print-zone');
const colorSection = $('#color-section');
const sideToggle = $('.side-toggle');
const printGuide = $('.print-guide');

function setProduct(id) {
  const product = PRODUCTS[id];
  if (!product) return;
  state.productId = id;
  state.product = product.name;
  state.basePrice = product.price;
  state.side = 'Frente';
  state.dx = 0; state.dy = 0;
  printZone.style.transform = '';
  shirtImage.src = product.front;
  shirtImage.alt = `Pré-visualização de ${product.name}`;
  printZone.style.left = product.zone.l;
  printZone.style.top = product.zone.t;
  printZone.style.width = product.zone.w;
  printZone.style.height = product.zone.h;
  colorSection.style.display = product.colorable ? '' : 'none';
  sideToggle.style.display = product.hasBack ? '' : 'none';
  printGuide.textContent = product.printLabel;
  printZone.style.mixBlendMode = 'multiply';
  $('#summary-product').textContent = product.name;
  const meta = product.colorable ? `${state.color} · Frente personalizada` : 'Personalização total';
  $('.summary-meta').textContent = meta;
  $$('.side-toggle button').forEach(b => b.classList.toggle('active', b.dataset.side === 'front'));
  shirtWrap.classList.remove('back-view');
  updatePrice();
}

$$('.tool').forEach(button => button.addEventListener('click', () => {
  $$('.tool').forEach(item => item.classList.remove('active'));
  $$('.panel').forEach(panel => panel.classList.remove('active'));
  button.classList.add('active');
  $('#' + button.dataset.panel).classList.add('active');
}));

$$('.product-option').forEach(button => button.addEventListener('click', () => {
  $$('.product-option').forEach(item => item.classList.remove('selected'));
  button.classList.add('selected');
  setProduct(button.dataset.product);
}));

$$('.swatch').forEach(button => button.addEventListener('click', () => {
  $$('.swatch').forEach(item => item.classList.remove('selected'));
  button.classList.add('selected');
  state.color = button.dataset.color;
  const filters = { 'Azul-marinho': 'brightness(.25) sepia(1) hue-rotate(168deg) saturate(2)' };
  shirtImage.style.setProperty('--shirt-filter', filters[state.color] || button.dataset.filter);
  const darkShirt = ['Preto', 'Azul-marinho', 'Vermelho', 'Verde'].includes(state.color);
  printZone.style.mixBlendMode = darkShirt ? 'normal' : 'multiply';
  designContent.style.color = darkShirt ? '#ffffff' : '';
  $('#color-name').textContent = state.color;
  $('#summary-color').textContent = state.color;
}));

$$('.side-toggle button').forEach(button => button.addEventListener('click', () => {
  const product = PRODUCTS[state.productId];
  if (!product.hasBack) return;
  $$('.side-toggle button').forEach(item => item.classList.remove('active'));
  button.classList.add('active');
  const isBack = button.dataset.side === 'back';
  state.side = isBack ? 'Costas' : 'Frente';
  shirtImage.src = isBack ? product.back : product.front;
  shirtImage.alt = isBack ? 'Pré-visualização das costas' : 'Pré-visualização da frente';
  shirtWrap.classList.toggle('back-view', isBack);
  $('.summary-meta').textContent = `${state.color} · ${state.side} personalizada`;
  designContent.style.opacity = '1';
}));

$('#add-text').addEventListener('click', () => {
  const text = $('#custom-text').value.trim() || 'A SUA IDEIA';
  designContent.className = 'design-content style-brand';
  designContent.innerHTML = `<small>PERSONALIZADO</small><strong>${escapeHtml(text).replace(/\s+/g, '<br>')}</strong><i>✦</i>`;
  designContent.style.fontFamily = $('#font-select').value;
  designContent.style.color = $('#text-color').value;
  uploadedArt.style.display = 'none';
});

$('#art-upload').addEventListener('change', event => {
  const file = event.target.files[0];
  if (!file) return;
  if (file.size > 8 * 1024 * 1024) return alert('O ficheiro deve ter no máximo 8 MB.');
  const reader = new FileReader();
  reader.onload = () => {
    uploadedArt.src = reader.result;
    uploadedArt.style.display = 'block';
    designContent.style.opacity = '.12';
  };
  reader.readAsDataURL(file);
});

$$('.style-chips button').forEach(button => button.addEventListener('click', () => {
  $$('.style-chips button').forEach(item => item.classList.remove('selected'));
  button.classList.add('selected');
}));

const aiResults = $('#ai-results');
const aiCredits = $('#ai-credits');

async function refreshCredits() {
  try {
    const response = await fetch(`${API_BASE}/api/credits`);
    if (!response.ok) return;
    const data = await response.json();
    renderCredits(data.remaining, data.daily_limit);
  } catch {}
}
function renderCredits(remaining, limit) {
  aiCredits.textContent = remaining > 0
    ? `Restam ${remaining} de ${limit} gerações grátis hoje`
    : `Limite diário grátis atingido — adquira créditos para continuar`;
  aiCredits.classList.toggle('exhausted', remaining === 0);
}
function applyConceptToShirt(url, label) {
  uploadedArt.src = url;
  uploadedArt.alt = `Conceito IA — ${label}`;
  uploadedArt.style.display = 'block';
  designContent.style.opacity = '0';
  renderApplyToStrip();
}

function renderApplyToStrip() {
  let strip = $('#ai-apply-strip');
  if (!strip) {
    strip = document.createElement('div');
    strip.id = 'ai-apply-strip';
    strip.className = 'ai-apply-strip';
    aiResults.insertAdjacentElement('afterend', strip);
  }
  const others = Object.entries(PRODUCTS).filter(([id]) => id !== state.productId);
  strip.innerHTML = '<small>Aplicar esta arte a:</small><div class="apply-grid"></div>';
  const grid = strip.querySelector('.apply-grid');
  others.forEach(([id, product]) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'apply-chip';
    button.title = `${product.name} · ${product.price} MT`;
    button.innerHTML = `<img src="${product.front}" alt=""><span>${product.name.split(' ')[0]}</span>`;
    button.addEventListener('click', () => {
      $$('.product-option').forEach(b => b.classList.toggle('selected', b.dataset.product === id));
      setProduct(id);
      const editor = document.querySelector('.shirt-canvas');
      if (editor) editor.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    grid.appendChild(button);
  });
}
function renderConcepts(concepts) {
  aiResults.innerHTML = '';
  concepts.forEach(concept => {
    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'ai-concept';
    card.innerHTML = `<img src="${concept.preview_url}" alt="Conceito ${escapeHtml(concept.style_label)}"><span>${escapeHtml(concept.style_label)}</span>`;
    card.addEventListener('click', () => {
      $$('.ai-concept').forEach(item => item.classList.remove('selected'));
      card.classList.add('selected');
      applyConceptToShirt(concept.preview_url, concept.style_label);
    });
    aiResults.appendChild(card);
  });
}

$('#generate-ai').addEventListener('click', async () => {
  const button = $('#generate-ai');
  const idea = $('#ai-prompt').value.trim();
  if (idea.length < 3) {
    aiResults.innerHTML = '<p class="ai-error">Descreva a sua ideia (mínimo 3 caracteres).</p>';
    return;
  }
  const style = ($('.style-chips button.selected')?.dataset.style) || 'vibrante';
  button.innerHTML = '<span>✦</span> A gerar 4 conceitos...';
  button.disabled = true;
  aiResults.innerHTML = '<div class="ai-loading"><span></span><span></span><span></span><span></span></div>';
  try {
    const response = await fetch(`${API_BASE}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: idea, style })
    });
    if (response.status === 429) {
      const err = await response.json().catch(() => ({ detail: 'Limite atingido.' }));
      aiResults.innerHTML = `<p class="ai-error">${escapeHtml(err.detail)}</p>`;
      renderCredits(0, 3);
      return;
    }
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    renderConcepts(data.concepts);
    renderCredits(data.credits_remaining, 3);
    if (data.concepts[0]) applyConceptToShirt(data.concepts[0].preview_url, data.concepts[0].style_label);
    $$('.ai-concept')[0]?.classList.add('selected');
  } catch (error) {
    aiResults.innerHTML = `<p class="ai-error">Não foi possível gerar agora. Tente novamente em instantes.</p>`;
  } finally {
    button.innerHTML = '<span>✦</span> Gerar 4 conceitos';
    button.disabled = false;
  }
});

refreshCredits();

const queryProduct = new URLSearchParams(location.search).get('product');
const initialProduct = (queryProduct && PRODUCTS[queryProduct]) ? queryProduct : 'tshirt';
$$('.product-option').forEach(b => b.classList.toggle('selected', b.dataset.product === initialProduct));
setProduct(initialProduct);

const templates = {
  maputo: ['style-maputo', 'FEITO EM', 'MAPUTO', '✦'],
  team: ['style-team', 'A NOSSA', 'EQUIPA', '●'],
  event: ['style-event', 'VIVA', '2026', '✦'],
  brand: ['style-brand', 'A SUA', 'MARCA', '+']
};
$$('[data-template]').forEach(button => button.addEventListener('click', () => {
  const [style, small, strong, icon] = templates[button.dataset.template];
  designContent.className = `design-content ${style}`;
  designContent.innerHTML = `<small>${small}</small><strong>${strong}</strong><i>${icon}</i>`;
  designContent.style.color = ['Preto', 'Azul-marinho', 'Vermelho', 'Verde'].includes(state.color) ? '#ffffff' : '';
  uploadedArt.style.display = 'none';
  designContent.style.opacity = '1';
}));

const cartoonModels = [
  { name: 'Leão skater', src: 'assets/cartoon-leao-v1.png' },
  { name: 'Robô criativo', src: 'assets/cartoon-robo-v1.png' },
  { name: 'Dança urbana', src: 'assets/cartoon-danca-v1.png' },
  { name: 'Camaleão DJ', src: 'assets/cartoon-camaleao-v1.png' }
];
const templateGrid = $('.template-grid');
cartoonModels.forEach(model => {
  const button = document.createElement('button');
  button.className = 'cartoon-option';
  button.type = 'button';
  button.innerHTML = `<img class="cartoon-thumb" src="${model.src}" alt="${model.name}"><span>${model.name}</span>`;
  button.addEventListener('click', () => {
    uploadedArt.src = model.src;
    uploadedArt.alt = model.name;
    uploadedArt.style.display = 'block';
    designContent.style.opacity = '0';
  });
  templateGrid.appendChild(button);
});

$('#zoom-in').addEventListener('click', () => setZoom(Math.min(1.25, state.zoom + .05)));
$('#zoom-out').addEventListener('click', () => setZoom(Math.max(.75, state.zoom - .05)));
function setZoom(value) { state.zoom = value; shirtWrap.style.transform = `scale(${value})`; $('#zoom-value').textContent = `${Math.round(value * 100)}%`; }

let dragStart = null;
printZone.addEventListener('pointerdown', event => { dragStart = { x: event.clientX, y: event.clientY, dx: state.dx, dy: state.dy }; printZone.setPointerCapture(event.pointerId); });
printZone.addEventListener('pointermove', event => {
  if (!dragStart) return;
  state.dx = Math.max(-35, Math.min(35, dragStart.dx + event.clientX - dragStart.x));
  state.dy = Math.max(-45, Math.min(45, dragStart.dy + event.clientY - dragStart.y));
  printZone.style.transform = `translate(${state.dx}px,${state.dy}px)`;
});
printZone.addEventListener('pointerup', () => dragStart = null);

$$('.size-qty').forEach(input => input.addEventListener('input', updatePrice));
function getQuantity() { return $$('.size-qty').reduce((sum, input) => sum + Math.max(0, Number(input.value) || 0), 0); }
function updatePrice() {
  const quantity = Math.max(1, getQuantity());
  const discount = quantity >= 50 ? .15 : quantity >= 25 ? .10 : quantity >= 10 ? .05 : 0;
  const unit = Math.round(state.basePrice * (1 - discount));
  const total = unit * quantity;
  $('#total-units').textContent = quantity;
  $('#shirts-price').textContent = formatMzn(total);
  $('#order-total').textContent = formatMzn(total);
  $('#unit-price').textContent = `${formatMzn(unit)} por unidade${discount ? ` · ${Math.round(discount * 100)}% desconto` : ''}`;
  return { quantity, unit, total };
}
function formatMzn(value) { return `${new Intl.NumberFormat('pt-PT').format(value)} MT`; }

const modal = $('#order-modal');
$('#continue-order').addEventListener('click', () => {
  const price = updatePrice();
  const summary = `${price.quantity} × ${state.product}, cor ${state.color}, impressão nas ${state.side.toLowerCase()}, total estimado ${formatMzn(price.total)}`;
  $('#order-summary').value = summary;
  $('#modal-recap-text').textContent = `${price.quantity} × ${state.product} · ${state.color}`;
  $('#modal-recap-price').textContent = formatMzn(price.total);
  modal.showModal();
});
$('.modal-close').addEventListener('click', () => modal.close());
modal.addEventListener('click', event => { if (event.target === modal) modal.close(); });

$('#order-form').addEventListener('submit', async event => {
  event.preventDefault();
  const submit = $('button[type="submit"]', event.target);
  const status = $('#form-status');
  submit.disabled = true; submit.textContent = 'A enviar...'; status.textContent = '';
  try {
    const response = await fetch(event.target.action, { method: 'POST', body: new FormData(event.target), headers: { Accept: 'application/json' } });
    if (!response.ok) throw new Error();
    status.className = 'form-status success'; status.textContent = 'Pedido enviado. Vamos responder em breve.'; submit.textContent = 'Pedido enviado ✓';
  } catch {
    status.className = 'form-status error'; status.textContent = 'Não foi possível enviar. Contacte info@scolorprint.com ou +258 84 990 0402.'; submit.disabled = false; submit.textContent = 'Tentar novamente';
  }
});

$('#reset-design').addEventListener('click', () => location.reload());
$('#share-design').addEventListener('click', async () => {
  const share = { title: 'A minha camiseta — S Color Print', text: 'Veja a minha ideia de camiseta personalizada.', url: location.href };
  if (navigator.share) await navigator.share(share).catch(() => {}); else { await navigator.clipboard.writeText(location.href); $('#share-design').textContent = 'Link copiado ✓'; }
});

function escapeHtml(value) { const node = document.createElement('div'); node.textContent = value; return node.innerHTML; }
updatePrice();
