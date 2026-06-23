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
  tshirt:   { name:'Camiseta', price:650,  zone:{l:'35%',t:'33%',w:'30%',h:'30%'}, hasBack:false, printLabel:'ÁREA DE IMPRESSÃO · FRENTE 30×40cm',
              sizes:['S','M','L','XL','2XL'],
              colors:[{name:'Branco',hex:'#f4f2ec',img:'assets/mockup-tshirt-real-v2.jpg'},{name:'Preto',hex:'#18191d',img:'assets/mockup-tshirt-black-v2.jpg'},{name:'Azul-marinho',hex:'#17304f',img:'assets/mockup-tshirt-navy-v2.jpg'},{name:'Vermelho',hex:'#a62d38',img:'assets/mockup-tshirt-red-v2.jpg'}] },
  hoodie:   { name:'Hoodie', price:1500, zone:{l:'39%',t:'46%',w:'22%',h:'22%'}, hasBack:false, printLabel:'IMPRESSÃO · PEITO 25×25cm · DTG',
              sizes:['S','M','L','XL','2XL'],
              colors:[{name:'Cinza',hex:'#9a9690',img:'assets/mockup-hoodie-real-v2.jpg'},{name:'Preto',hex:'#18191d',img:'assets/mockup-hoodie-black-v2.jpg'},{name:'Azul-marinho',hex:'#17304f',img:'assets/mockup-hoodie-navy-v2.jpg'}] },
  mug:      { name:'Mug', price:380,  zone:{l:'44%',t:'38%',w:'22%',h:'22%'}, hasBack:false, printLabel:'SUBLIMAÇÃO 360° · 330ml',
              sizes:['330ml','450ml'],
              colors:[{name:'Branco',hex:'#ffffff',img:'assets/mockup-mug-real-v2.jpg'},{name:'Preto',hex:'#18191d',img:'assets/mockup-mug-black-v2.jpg'}] },
  cap:      { name:'Boné', price:450,  zone:{l:'40%',t:'12%',w:'18%',h:'18%'}, hasBack:false, printLabel:'ÁREA FRONTAL · BORDADO/DTG · 8×4cm',
              sizes:['S/M','L/XL'],
              colors:[{name:'Cinza',hex:'#8f8f86',img:'assets/mockup-cap-real-v2.jpg'},{name:'Preto',hex:'#18191d',img:'assets/mockup-cap-black-v2.jpg'},{name:'Azul-marinho',hex:'#17304f',img:'assets/mockup-cap-navy-v2.jpg'}] },
  tote:     { name:'Tote bag', price:550,  zone:{l:'38%',t:'60%',w:'24%',h:'24%'}, hasBack:false, printLabel:'IMPRESSÃO CENTRAL · DTG 25×25cm',
              sizes:['Único'], colors:[{name:'Cru',hex:'#e7dfc5',img:'assets/mockup-tote-real-v2.jpg'}] },
  bottle:   { name:'Garrafa térmica', price:950,  zone:{l:'43%',t:'42%',w:'14%',h:'14%'}, hasBack:false, printLabel:'GRAVAÇÃO LASER · ÁREA 7×12cm',
              sizes:['500ml','750ml'], colors:[{name:'Inox',hex:'#c0c0c0',img:'assets/mockup-bottle-real-v2.jpg'}] },
  pillow:   { name:'Almofada', price:720,  zone:{l:'34%',t:'34%',w:'32%',h:'32%'}, hasBack:false, printLabel:'SUBLIMAÇÃO TOTAL · 40×40cm',
              sizes:['40×40','50×50'], colors:[{name:'Branco',hex:'#ffffff',img:'assets/mockup-pillow-real-v2.jpg'}] },
  frame:    { name:'Quadro personalizado', price:1200, zone:{l:'37%',t:'34%',w:'26%',h:'26%'}, hasBack:false, printLabel:'IMPRESSÃO ALTA RES · 30×40cm',
              sizes:['30×40','40×50'], colors:[{name:'Madeira',hex:'#3a2d1e',img:'assets/mockup-frame-real-v2.jpg'}] },
  keychain: { name:'Chaveiro', price:180,  zone:{l:'39%',t:'44%',w:'22%',h:'22%'}, hasBack:false, printLabel:'ACRÍLICO · 6×6cm · UV',
              sizes:['Único'], colors:[{name:'Transparente',hex:'#dfe6ea',img:'assets/mockup-keychain-real-v2.jpg'}] },
  giftkit:  { name:'Kit corporativo', price:2500, zone:{l:'18%',t:'18%',w:'26%',h:'26%'}, hasBack:false, printLabel:'BUNDLE: t-shirt + mug + boné + caderno',
              sizes:['Standard','Premium'], colors:[{name:'Kraft',hex:'#cbb89a',img:'assets/mockup-giftkit-real-v2.jpg'}] }
};

const state = { productId: 'tshirt', product: 'Camiseta', basePrice: 650, color: 'Branco', side: 'Frente', zoom: 1, dx: 0, dy: 0, scale: 1 };
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
  state.dx = 0; state.dy = 0; state.scale = 1;
  applyPrintTransform();
  printZone.style.left = product.zone.l;
  printZone.style.top = product.zone.t;
  printZone.style.width = product.zone.w;
  printZone.style.height = product.zone.h;
  sideToggle.style.display = product.hasBack ? '' : 'none';
  printGuide.textContent = product.printLabel;
  $('#summary-product').textContent = product.name;
  $$('.side-toggle button').forEach(b => b.classList.toggle('active', b.dataset.side === 'front'));
  shirtWrap.classList.remove('back-view');
  $('#price-line-label').textContent = product.name + (product.sizes[0] === 'Único' || /ml|×/.test(product.sizes[0]) ? '' : 's');
  renderColors(product);
  renderSizes(product);
  setColor(product.colors[0]);
  updatePrice();
}

function setColor(color) {
  state.color = color.name;
  shirtImage.src = color.img;
  shirtImage.alt = `Pré-visualização de ${state.product} ${color.name}`;
  $('#summary-color').textContent = color.name;
  $('.summary-meta').textContent = `${color.name} · Personalização frontal`;
  $$('#color-section .swatch').forEach(s => s.classList.toggle('selected', s.dataset.color === color.name));
}

function renderColors(product) {
  const single = product.colors.length <= 1;
  colorSection.style.display = single ? 'none' : '';
  $('#color-name').textContent = product.colors[0].name;
  const swatches = $('#color-section .swatches');
  swatches.innerHTML = '';
  product.colors.forEach((color, i) => {
    const button = document.createElement('button');
    button.className = 'swatch' + (i === 0 ? ' selected' : '');
    button.style.setProperty('--swatch', color.hex);
    button.dataset.color = color.name;
    button.title = color.name;
    button.addEventListener('click', () => { setColor(color); $('#color-name').textContent = color.name; });
    swatches.appendChild(button);
  });
}

function renderSizes(product) {
  const grid = $('.size-grid');
  grid.innerHTML = '';
  product.sizes.forEach((size, i) => {
    const label = document.createElement('label');
    label.innerHTML = `${size}<input class="size-qty" type="number" min="0" value="${i === 0 ? 1 : 0}">`;
    grid.appendChild(label);
  });
  $$('.size-qty').forEach(input => input.addEventListener('input', updatePrice));
}

/* ---- Guided wizard ---- */
const wSteps = $$('.wstep');
const wTabs = $$('.wstep-tab');
const stepBack = $('#step-back');
const stepNext = $('#step-next');
let wCurrent = 0;
function goStep(n) {
  wCurrent = Math.max(0, Math.min(wSteps.length - 1, n));
  wSteps.forEach((s, i) => s.classList.toggle('active', i === wCurrent));
  wTabs.forEach((t, i) => { t.classList.toggle('active', i === wCurrent); t.classList.toggle('done', i < wCurrent); });
  stepBack.disabled = wCurrent === 0;
  stepNext.innerHTML = wCurrent === wSteps.length - 1 ? 'Finalizar pedido <span>→</span>' : 'Seguinte <span>→</span>';
  $('.wizard-body').scrollTop = 0;
}
stepNext.addEventListener('click', () => {
  if (wCurrent === wSteps.length - 1) {
    const price = updatePrice();
    openCheckout([{ name: state.product, color: state.color, sizeLabel: sizeSummary(price), qty: price.quantity, total: price.total }]);
  } else goStep(wCurrent + 1);
});
stepBack.addEventListener('click', () => goStep(wCurrent - 1));
wTabs.forEach((t, i) => t.addEventListener('click', () => goStep(i)));

/* ---- Category carousel (step 1) ---- */
const catSlides = $$('.cat-slide');
const catDots = $('#cat-dots');
let catCurrent = 0;
catSlides.forEach((_, i) => { const d = document.createElement('button'); d.type = 'button'; d.addEventListener('click', () => showCat(i)); catDots.appendChild(d); });
function showCat(n) {
  catCurrent = (n + catSlides.length) % catSlides.length;
  catSlides.forEach((s, i) => s.classList.toggle('active', i === catCurrent));
  $$('#cat-dots button').forEach((d, i) => d.classList.toggle('active', i === catCurrent));
  $('#cat-name').textContent = catSlides[catCurrent].dataset.cat;
  $('#cat-count').textContent = `${catCurrent + 1} / ${catSlides.length}`;
}
$('#cat-prev').addEventListener('click', () => showCat(catCurrent - 1));
$('#cat-next').addEventListener('click', () => showCat(catCurrent + 1));
showCat(0);

/* ---- Design sub-tabs (step 2) ---- */
$$('.dsub').forEach(btn => btn.addEventListener('click', () => {
  $$('.dsub').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  $$('.dsub-content').forEach(c => c.classList.toggle('active', c.dataset.sub === btn.dataset.sub));
}));

$$('.product-option').forEach(button => button.addEventListener('click', () => {
  $$('.product-option').forEach(item => item.classList.remove('selected'));
  button.classList.add('selected');
  setProduct(button.dataset.product);
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
    button.innerHTML = `<img src="${product.colors[0].img}" alt=""><span>${product.name.split(' ')[0]}</span>`;
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
// open the carousel on the category that holds the initial product
const initSlide = catSlides.findIndex(s => s.querySelector(`[data-product="${initialProduct}"]`));
if (initSlide >= 0) showCat(initSlide);
// if arriving with ?product=, jump straight to the design step
if (queryProduct && PRODUCTS[queryProduct]) goStep(1);

/* ---- Stamp library (Modelos step) — original Scolor Print art by category ---- */
const stampPaths = (slug, n) => Array.from({ length: n }, (_, i) => `assets/estampas/${slug}-${i + 1}.png`);
const STAMPS = {
  'estilo-fas': { label: '★ Estilo Fãs', imgs: stampPaths('estilo-fas', 8) },
  'desenhos-animados': { label: 'Desenhos animados', imgs: [...stampPaths('desenhos-animados', 3), 'assets/cartoon-leao-v1.png', 'assets/cartoon-robo-v1.png', 'assets/cartoon-danca-v1.png', 'assets/cartoon-camaleao-v1.png'] },
  'anime': { label: 'Anime', imgs: stampPaths('anime', 3) },
  'super-herois': { label: 'Super-heróis', imgs: stampPaths('super-herois', 3) },
  'princesas': { label: 'Princesas', imgs: stampPaths('princesas', 3) },
  'caveiras': { label: 'Caveiras', imgs: stampPaths('caveiras', 3) },
  'streetwear': { label: 'Streetwear', imgs: stampPaths('streetwear', 3) },
  'fe-frases': { label: 'Fé & Frases', imgs: stampPaths('fe-frases', 3) },
  'motivacional': { label: 'Motivacional', imgs: stampPaths('motivacional', 3) },
  'desporto': { label: 'Desporto', imgs: stampPaths('desporto', 3) },
  'musica': { label: 'Música', imgs: stampPaths('musica', 3) },
  'cultura-mz': { label: 'Cultura MZ', imgs: stampPaths('cultura-mz', 3) },
  'animais': { label: 'Animais', imgs: stampPaths('animais', 3) },
  'floral': { label: 'Floral', imgs: stampPaths('floral', 3) },
  'datas-festas': { label: 'Datas & Festas', imgs: stampPaths('datas-festas', 3) }
};
function applyStamp(src, label) {
  uploadedArt.src = src;
  uploadedArt.alt = label || 'Estampa';
  uploadedArt.style.display = 'block';
  designContent.style.opacity = '0';
  if (typeof renderApplyToStrip === 'function') renderApplyToStrip();
}
(function buildStampLibrary() {
  const cats = $('#stamp-cats');
  const grid = $('#stamp-grid');
  if (!cats || !grid) return;
  const slugs = Object.keys(STAMPS);
  function showCat(slug) {
    $$('.stamp-cat', cats).forEach(b => b.classList.toggle('active', b.dataset.cat === slug));
    grid.innerHTML = '';
    STAMPS[slug].imgs.forEach((src, i) => {
      const button = document.createElement('button');
      button.className = 'stamp-thumb';
      button.type = 'button';
      button.title = `${STAMPS[slug].label} ${i + 1}`;
      button.innerHTML = `<img src="${src}" alt="${STAMPS[slug].label} ${i + 1}" loading="lazy" onerror="this.closest('.stamp-thumb').classList.add('missing')">`;
      button.addEventListener('click', () => applyStamp(src, `${STAMPS[slug].label} ${i + 1}`));
      grid.appendChild(button);
    });
  }
  cats.innerHTML = slugs.map((s, i) => `<button class="stamp-cat${i === 0 ? ' active' : ''}" type="button" data-cat="${s}">${STAMPS[s].label}</button>`).join('');
  $$('.stamp-cat', cats).forEach(btn => btn.addEventListener('click', () => showCat(btn.dataset.cat)));
  showCat(slugs[0]);
})();

$('#zoom-in').addEventListener('click', () => setZoom(Math.min(1.25, state.zoom + .05)));
$('#zoom-out').addEventListener('click', () => setZoom(Math.max(.75, state.zoom - .05)));
function setZoom(value) { state.zoom = value; shirtWrap.style.transform = `scale(${value})`; $('#zoom-value').textContent = `${Math.round(value * 100)}%`; }

const resizeHandle = $('#resize-handle');
function applyPrintTransform() {
  printZone.style.transform = `translate(${state.dx}px,${state.dy}px) scale(${state.scale})`;
}

let dragStart = null;
printZone.addEventListener('pointerdown', event => {
  if (event.target === resizeHandle) return;
  dragStart = { x: event.clientX, y: event.clientY, dx: state.dx, dy: state.dy };
  printZone.setPointerCapture(event.pointerId);
});
printZone.addEventListener('pointermove', event => {
  if (!dragStart) return;
  state.dx = Math.max(-90, Math.min(90, dragStart.dx + event.clientX - dragStart.x));
  state.dy = Math.max(-110, Math.min(110, dragStart.dy + event.clientY - dragStart.y));
  applyPrintTransform();
});
printZone.addEventListener('pointerup', () => dragStart = null);
printZone.addEventListener('pointercancel', () => dragStart = null);

let resizeStart = null;
resizeHandle.addEventListener('pointerdown', event => {
  event.stopPropagation();
  resizeStart = { y: event.clientY, scale: state.scale };
  resizeHandle.setPointerCapture(event.pointerId);
});
resizeHandle.addEventListener('pointermove', event => {
  if (!resizeStart) return;
  const delta = (event.clientY - resizeStart.y) / 160;
  state.scale = Math.max(0.4, Math.min(2.4, resizeStart.scale + delta));
  applyPrintTransform();
});
resizeHandle.addEventListener('pointerup', () => resizeStart = null);
resizeHandle.addEventListener('pointercancel', () => resizeStart = null);

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

/* ---------- Cart ---------- */
const CART_KEY = 'scolor_cart_v1';
let cart = [];
try { cart = JSON.parse(localStorage.getItem(CART_KEY)) || []; } catch { cart = []; }
const cartDrawer = $('#cart-drawer');
const cartOverlay = $('#cart-overlay');

function saveCart() { localStorage.setItem(CART_KEY, JSON.stringify(cart)); renderCart(); }

function currentSizes() {
  const map = {};
  $$('.size-grid label').forEach(label => {
    const size = label.childNodes[0].textContent.trim();
    const qty = Math.max(0, Number(label.querySelector('input').value) || 0);
    if (qty > 0) map[size] = qty;
  });
  return map;
}
function sizeSummary(price) {
  const sizes = currentSizes();
  return Object.keys(sizes).length ? Object.entries(sizes).map(([s, q]) => `${q}×${s}`).join(', ') : `${price.quantity} un`;
}

function addToCart() {
  const price = updatePrice();
  cart.push({ id: Date.now() + Math.random().toString(36).slice(2, 6), name: state.product, color: state.color, thumb: shirtImage.src, sizeLabel: sizeSummary(price), qty: price.quantity, total: price.total });
  saveCart();
  openCart();
}
function removeFromCart(id) { cart = cart.filter(i => i.id !== id); saveCart(); }
function cartTotal() { return cart.reduce((s, i) => s + i.total, 0); }

function renderCart() {
  const badge = $('#cart-badge');
  badge.textContent = cart.length;
  badge.hidden = cart.length === 0;
  const items = $('#cart-items');
  $('#cart-empty').style.display = cart.length ? 'none' : '';
  $('.cart-foot').style.display = cart.length ? '' : 'none';
  items.innerHTML = '';
  cart.forEach(item => {
    const el = document.createElement('div');
    el.className = 'cart-item';
    el.innerHTML = `<img src="${escapeHtml(item.thumb)}" alt=""><div class="cart-item-info"><b>${escapeHtml(item.name)}</b><small>${escapeHtml(item.color)} · ${escapeHtml(item.sizeLabel)}</small><span class="ci-price">${formatMzn(item.total)}</span></div><button class="cart-item-remove" title="Remover">×</button>`;
    el.querySelector('.cart-item-remove').addEventListener('click', () => removeFromCart(item.id));
    items.appendChild(el);
  });
  $('#cart-total').textContent = formatMzn(cartTotal());
}

function openCart() { cartDrawer.classList.add('open'); cartDrawer.setAttribute('aria-hidden', 'false'); cartOverlay.hidden = false; }
function closeCart() { cartDrawer.classList.remove('open'); cartDrawer.setAttribute('aria-hidden', 'true'); cartOverlay.hidden = true; }

function openCheckout(items) {
  const lines = items.map(i => `• ${i.qty}× ${i.name} (${i.color}, ${i.sizeLabel}) — ${formatMzn(i.total)}`).join('\n');
  const total = items.reduce((s, i) => s + i.total, 0);
  const units = items.reduce((n, i) => n + i.qty, 0);
  $('#order-summary').value = `${lines}\nTOTAL ESTIMADO: ${formatMzn(total)}`;
  $('#modal-recap-text').textContent = `${items.length} ${items.length === 1 ? 'artigo' : 'artigos'} · ${units} un`;
  $('#modal-recap-price').textContent = formatMzn(total);
  closeCart();
  modal.showModal();
}

$('#add-to-cart').addEventListener('click', addToCart);
$('#cart-button').addEventListener('click', openCart);
$('#cart-close').addEventListener('click', closeCart);
cartOverlay.addEventListener('click', closeCart);
$('#cart-checkout').addEventListener('click', () => { if (cart.length) openCheckout(cart); });

$('#continue-order').addEventListener('click', () => {
  const price = updatePrice();
  openCheckout([{ name: state.product, color: state.color, sizeLabel: sizeSummary(price), qty: price.quantity, total: price.total }]);
});

$('.modal-close').addEventListener('click', () => modal.close());
modal.addEventListener('click', event => { if (event.target === modal) modal.close(); });
renderCart();

$('#order-form').addEventListener('submit', async event => {
  event.preventDefault();
  const submit = $('button[type="submit"]', event.target);
  const status = $('#form-status');
  submit.disabled = true; submit.textContent = 'A enviar...'; status.textContent = '';
  try {
    const response = await fetch(event.target.action, { method: 'POST', body: new FormData(event.target), headers: { Accept: 'application/json' } });
    if (!response.ok) throw new Error();
    status.className = 'form-status success'; status.textContent = 'Pedido enviado. Vamos responder em breve.'; submit.textContent = 'Pedido enviado ✓';
    cart = []; saveCart();
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
