const $ = (selector, scope = document) => scope.querySelector(selector);
const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];

$('#year').textContent = new Date().getFullYear();
$('.menu-button').addEventListener('click', () => $('.site-header').classList.toggle('open'));

const state = { product: 'Camiseta Clássica', basePrice: 650, color: 'Branco', side: 'Frente', zoom: 1, dx: 0, dy: 0 };
const shirtImage = $('#shirt-image');
const shirtWrap = $('#shirt-wrap');
const designContent = $('#design-content');
const uploadedArt = $('#uploaded-art');
const printZone = $('#print-zone');

$$('.tool').forEach(button => button.addEventListener('click', () => {
  $$('.tool').forEach(item => item.classList.remove('active'));
  $$('.panel').forEach(panel => panel.classList.remove('active'));
  button.classList.add('active');
  $('#' + button.dataset.panel).classList.add('active');
}));

$$('.product-option').forEach(button => button.addEventListener('click', () => {
  $$('.product-option').forEach(item => item.classList.remove('selected'));
  button.classList.add('selected');
  state.product = button.dataset.name;
  state.basePrice = Number(button.dataset.price);
  $('#summary-product').textContent = state.product;
  updatePrice();
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
  $$('.side-toggle button').forEach(item => item.classList.remove('active'));
  button.classList.add('active');
  const isBack = button.dataset.side === 'back';
  state.side = isBack ? 'Costas' : 'Frente';
  shirtImage.src = isBack ? 'assets/tshirt-designer-back-white-v1.png' : 'assets/tshirt-designer-white-v1.png';
  shirtImage.alt = isBack ? 'Pré-visualização das costas da camiseta' : 'Pré-visualização da frente da camiseta';
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

$('#generate-ai').addEventListener('click', () => {
  const button = $('#generate-ai');
  const idea = $('#ai-prompt').value.trim();
  const words = idea ? idea.split(/\s+/).filter(word => word.length > 3).slice(0, 2) : ['MAPUTO', 'CRIA'];
  button.innerHTML = '<span>✦</span> A criar...';
  button.disabled = true;
  setTimeout(() => {
    designContent.className = 'design-content style-event';
    designContent.innerHTML = `<small>EDIÇÃO LOCAL</small><strong>${escapeHtml((words[0] || 'MAPUTO').toUpperCase())}<br>${escapeHtml((words[1] || 'CRIA').toUpperCase())}</strong><i>✦</i>`;
    uploadedArt.style.display = 'none';
    designContent.style.opacity = '1';
    if (['Preto', 'Azul-marinho', 'Vermelho', 'Verde'].includes(state.color)) designContent.style.color = '#ffffff';
    button.innerHTML = '<span>✦</span> Gerar outro conceito';
    button.disabled = false;
  }, 900);
});

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
