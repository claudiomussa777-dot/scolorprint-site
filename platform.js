const $ = (selector, scope = document) => scope.querySelector(selector);
const $$ = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));

const PHONE = '258849900402';

const imageDimensions = {
  'assets/generated/hero-studio-v1.webp': [1536, 1024],
  'assets/generated/tshirt-studio-v1.webp': [1024, 1536],
  'assets/generated/rollup-studio-v1.webp': [1024, 1536],
  'assets/generated/cards-studio-v1.webp': [1254, 1254],
  'assets/generated/vinyl-studio-v1.webp': [1024, 1536],
  'assets/generated/gifts-studio-v1.webp': [1024, 1536],
  'assets/trabalhos/folders-e-flyers-impressos.jpg': [675, 900],
  'assets/mockup-giftkit-real-v2.jpg': [1024, 1024],
  'assets/trabalhos/backdrop-evento-institucional.jpg': [900, 900],
  'assets/mockup-cap-real-v2.jpg': [1024, 1024],
  'assets/categorias/placas-sinaletica.jpg': [900, 675],
  'assets/mockup-mug-real-v2.jpg': [1024, 1024],
  'assets/categorias/coletes-uniformes.jpg': [900, 1200]
};

function imageSizeAttributes(src) {
  const [width, height] = imageDimensions[src] || [1200, 900];
  return `width="${width}" height="${height}"`;
}

const products = [
  { id: 'camisetas', name: 'Camisetas personalizadas', short: 'Camisetas', category: 'vestuario', categoryLabel: 'Vestuário', image: 'assets/generated/tshirt-studio-v1.webp', price: 'Desde 800 MT/un.', reference: 'Desde 800 MT por unidade', description: 'Para marcas, equipas, igrejas, escolas, aniversários e eventos.', badge: 'Mais pedido' },
  { id: 'rollup', name: 'Roll-up Executivo', short: 'Roll-up', category: 'eventos', categoryLabel: 'Eventos', image: 'assets/generated/rollup-studio-v1.webp', price: 'Desde 7.000 MT', reference: 'Desde 7.000 MT por unidade', description: 'Presença visual profissional para conferências, feiras e receções.', badge: 'Pronto para eventos' },
  { id: 'cartoes', name: 'Cartões de visita', short: 'Cartões', category: 'impressos', categoryLabel: 'Impressos', image: 'assets/generated/cards-studio-v1.webp', price: 'Desde 5.000 MT/100 un.', reference: 'Desde 5.000 MT por 100 unidades', description: 'Cartões profissionais com opções de papel e acabamento.', badge: 'Para negócios' },
  { id: 'vinil', name: 'Vinil para montras', short: 'Vinil', category: 'espacos', categoryLabel: 'Espaços', image: 'assets/generated/vinyl-studio-v1.webp', price: 'Sob orçamento', reference: 'Preço após medidas e fotografia', description: 'Transforme montras, portas e paredes em comunicação de marca.', badge: 'Feito à medida' },
  { id: 'canetas', name: 'Brindes corporativos', short: 'Brindes', category: 'brindes', categoryLabel: 'Brindes', image: 'assets/generated/gifts-studio-v1.webp', price: 'Canetas: mínimo 50 un.', reference: 'Preço conforme a composição e quantidade', description: 'Canecas, canetas, cadernos e kits para campanhas, equipas e eventos.', badge: 'Corporativo' },
  { id: 'flyers', name: 'Flyers e folders', short: 'Flyers', category: 'impressos', categoryLabel: 'Impressos', image: 'assets/trabalhos/folders-e-flyers-impressos.jpg', price: 'Sob orçamento', reference: 'Preço conforme formato e quantidade', description: 'Apresente serviços, campanhas e promoções com clareza.', badge: 'Comunicação' },
  { id: 'brindes', name: 'Kits e brindes', short: 'Brindes', category: 'brindes', categoryLabel: 'Brindes', image: 'assets/mockup-giftkit-real-v2.jpg', price: 'Sob orçamento', reference: 'Preço conforme composição do kit', description: 'Combine produtos para clientes, equipas e campanhas especiais.', badge: 'Personalizável' },
  { id: 'banners', name: 'Banners e backdrops', short: 'Banners', category: 'eventos', categoryLabel: 'Eventos', image: 'assets/trabalhos/backdrop-evento-institucional.jpg', price: 'Sob orçamento', reference: 'Preço conforme medida e estrutura', description: 'Fundos, painéis e comunicação de grande formato para eventos.', badge: 'Grande formato' },
  { id: 'bones', name: 'Bonés personalizados', short: 'Bonés', category: 'vestuario', categoryLabel: 'Vestuário', image: 'assets/mockup-cap-real-v2.jpg', price: 'Sob orçamento', reference: 'Preço conforme modelo e quantidade', description: 'Bonés para equipas, marcas, ativações e campanhas.', badge: 'Equipas' },
  { id: 'sinaletica', name: 'Placas e sinalética', short: 'Sinalética', category: 'espacos', categoryLabel: 'Espaços', image: 'assets/categorias/placas-sinaletica.jpg', price: 'Sob orçamento', reference: 'Preço após medidas e material', description: 'Identificação, direção e presença de marca em espaços físicos.', badge: 'Espaços' },
  { id: 'canecas', name: 'Canecas personalizadas', short: 'Canecas', category: 'brindes', categoryLabel: 'Brindes', image: 'assets/mockup-mug-real-v2.jpg', price: 'Sob orçamento', reference: 'Preço conforme quantidade e arte', description: 'Presentes e brindes personalizados para todas as ocasiões.', badge: 'Presentes' },
  { id: 'coletes', name: 'Coletes e uniformes', short: 'Uniformes', category: 'vestuario', categoryLabel: 'Vestuário', image: 'assets/categorias/coletes-uniformes.jpg', price: 'Sob orçamento', reference: 'Preço conforme peça e quantidade', description: 'Identidade e visibilidade para equipas, obras e serviços.', badge: 'Empresas' }
];

const heroThemes = {
  colecao: { productId: 'camisetas', label: 'Coleção', image: 'assets/generated/hero-studio-v1.webp', price: 'à medida' },
  camisetas: { productId: 'camisetas', label: 'Camisetas', image: 'assets/generated/tshirt-studio-v1.webp', price: '800 MT' },
  eventos: { productId: 'rollup', label: 'Eventos', image: 'assets/generated/rollup-studio-v1.webp', price: '7.000 MT' },
  empresas: { productId: 'cartoes', label: 'Empresas', image: 'assets/generated/cards-studio-v1.webp', price: '5.000 MT' },
  lojas: { productId: 'vinil', label: 'Lojas', image: 'assets/generated/vinyl-studio-v1.webp', price: 'sob análise' }
};

const state = {
  filter: 'todos',
  query: '',
  selectedId: sessionStorage.getItem('scp-product') || 'camisetas',
  step: 1,
  dialogId: null,
  heroIndex: 0
};

const productById = id => products.find(product => product.id === id) || products[0];
const whatsappUrl = message => `https://wa.me/${PHONE}?text=${encodeURIComponent(message)}`;

function initHeader() {
  const header = $('[data-header]');
  const menuToggle = $('[data-menu-toggle]');
  const menu = $('[data-mobile-menu]');
  if (!header || !menuToggle || !menu) return;

  const updateHeader = () => header.classList.toggle('is-scrolled', scrollY > 24);
  updateHeader();
  addEventListener('scroll', updateHeader, { passive: true });

  const closeMenu = () => {
    menu.hidden = true;
    menuToggle.setAttribute('aria-expanded', 'false');
    menuToggle.setAttribute('aria-label', 'Abrir menu');
    document.body.classList.remove('menu-open');
  };

  menuToggle.addEventListener('click', () => {
    const open = menuToggle.getAttribute('aria-expanded') === 'true';
    menu.hidden = open;
    menuToggle.setAttribute('aria-expanded', String(!open));
    menuToggle.setAttribute('aria-label', open ? 'Abrir menu' : 'Fechar menu');
    document.body.classList.toggle('menu-open', !open);
  });
  $$('a', menu).forEach(link => link.addEventListener('click', closeMenu));

  const sections = $$('main section[id]');
  const navLinks = $$('.desktop-nav a[href^="#"]');
  if ('IntersectionObserver' in window) {
    const sectionObserver = new IntersectionObserver(entries => {
      const current = entries.filter(entry => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!current) return;
      navLinks.forEach(link => link.classList.toggle('is-active', link.getAttribute('href') === `#${current.target.id}`));
    }, { rootMargin: '-25% 0px -60%', threshold: [0.05, .3] });
    sections.forEach(section => sectionObserver.observe(section));
  }
}

function initReveal() {
  const items = $$('.reveal');
  if (!('IntersectionObserver' in window)) {
    items.forEach(item => item.classList.add('is-visible'));
    return;
  }
  const observer = new IntersectionObserver(entries => entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    }
  }), { threshold: .12, rootMargin: '0px 0px -40px' });
  items.forEach(item => observer.observe(item));
}

function initHero() {
  const stage = $('[data-hero-studio]');
  const image = $('[data-hero-image]');
  const label = $('[data-hero-label]');
  const price = $('[data-hero-price]');
  const card = $('.hero-product-card');
  const tabs = $$('[data-hero-theme]');
  if (!stage || !image || !card || !tabs.length) return;

  const keys = Object.keys(heroThemes);
  let timer;

  const setTheme = (key, userInitiated = false) => {
    const theme = heroThemes[key];
    if (!theme) return;
    state.heroIndex = keys.indexOf(key);
    tabs.forEach(tab => tab.setAttribute('aria-selected', String(tab.dataset.heroTheme === key)));
    card.classList.add('is-changing');
    setTimeout(() => {
      const [width, height] = imageDimensions[theme.image] || [1200, 900];
      image.src = theme.image;
      image.alt = `${theme.label} personalizados pela Smart Color Print`;
      image.width = width;
      image.height = height;
      label.textContent = theme.label;
      price.textContent = theme.price;
      card.classList.remove('is-changing');
    }, 220);
    if (userInitiated && timer) {
      clearInterval(timer);
      startRotation();
    }
  };

  const startRotation = () => {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    timer = setInterval(() => setTheme(keys[(state.heroIndex + 1) % keys.length]), 5200);
  };

  tabs.forEach(tab => tab.addEventListener('click', () => setTheme(tab.dataset.heroTheme, true)));
  stage.addEventListener('mouseenter', () => timer && clearInterval(timer));
  stage.addEventListener('mouseleave', startRotation);
  startRotation();
}

function renderProducts() {
  const grid = $('[data-product-grid]');
  const empty = $('[data-empty-state]');
  if (!grid) return;
  const term = state.query.trim().toLocaleLowerCase('pt');
  const visible = products.filter(product => {
    const matchesFilter = state.filter === 'todos' || product.category === state.filter;
    const haystack = `${product.name} ${product.categoryLabel} ${product.description}`.toLocaleLowerCase('pt');
    return matchesFilter && (!term || haystack.includes(term));
  });

  grid.innerHTML = visible.map((product, index) => {
    const sizeClass = index === 0 && visible.length > 2 ? 'is-wide' : index > 4 ? 'is-small' : '';
    return `<button class="product-card ${sizeClass}" type="button" data-product-id="${product.id}" aria-label="Configurar ${product.name}">
      <span class="product-card-media"><img src="${product.image}" alt="${product.name}" ${imageSizeAttributes(product.image)} loading="lazy"><span class="product-badge">${product.badge}</span><span class="product-arrow">↗</span></span>
      <span class="product-info"><span><small>${product.categoryLabel}</small><strong>${product.name}</strong></span><span class="product-price">${product.price}</span></span>
    </button>`;
  }).join('');

  empty.hidden = visible.length > 0;
  $$('[data-product-id]', grid).forEach(card => card.addEventListener('click', () => openProductDialog(card.dataset.productId)));
}

function initExplorer() {
  const search = $('[data-product-search]');
  const filterList = $('[data-filter-list]');
  if (search) search.addEventListener('input', () => { state.query = search.value; renderProducts(); });
  if (filterList) $$('[data-filter]', filterList).forEach(button => button.addEventListener('click', () => {
    state.filter = button.dataset.filter;
    $$('[data-filter]', filterList).forEach(item => item.classList.toggle('is-active', item === button));
    renderProducts();
  }));
  renderProducts();
}

function initProductDialog() {
  const dialog = $('[data-product-dialog]');
  if (!dialog) return;
  $('[data-dialog-close]', dialog).addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  $('[data-dialog-add]', dialog).addEventListener('click', () => {
    const quantity = Number($('[data-dialog-quantity]', dialog).value) || 1;
    const designHelp = $('[data-dialog-design]', dialog).checked;
    selectProduct(state.dialogId, { quantity, designHelp });
    dialog.close();
    openQuote();
  });
}

function openProductDialog(id) {
  const dialog = $('[data-product-dialog]');
  const product = productById(id);
  if (!dialog) return;
  state.dialogId = product.id;
  $('[data-dialog-image]', dialog).src = product.image;
  $('[data-dialog-image]', dialog).alt = product.name;
  $('[data-dialog-category]', dialog).textContent = product.categoryLabel;
  $('[data-dialog-title]', dialog).textContent = product.name;
  $('[data-dialog-description]', dialog).textContent = product.description;
  $('[data-dialog-price]', dialog).textContent = product.reference;
  $('[data-dialog-quantity]', dialog).value = product.id === 'cartoes' ? 100 : product.id === 'canetas' ? 50 : 10;
  $('[data-dialog-design]', dialog).checked = false;
  dialog.showModal();
}

function renderWizardProducts() {
  const container = $('[data-wizard-products]');
  if (!container) return;
  container.innerHTML = products.map(product => `<option value="${product.id}" ${state.selectedId === product.id ? 'selected' : ''}>${product.name}</option>`).join('');
  container.addEventListener('change', () => selectProduct(container.value));
}

function selectProduct(id, options = {}) {
  const product = productById(id);
  state.selectedId = product.id;
  sessionStorage.setItem('scp-product', product.id);
  const productSelect = $('[data-wizard-products]');
  if (productSelect) productSelect.value = product.id;
  const quantityInput = $('[data-quantity]');
  if (quantityInput && options.quantity) quantityInput.value = options.quantity;
  const designInput = $('[name="design_help"]');
  if (designInput && typeof options.designHelp === 'boolean') designInput.checked = options.designHelp;
  updateQuoteSummary();
}

function updateQuoteSummary() {
  const product = productById(state.selectedId);
  const canvas = $('.lab-canvas');
  const image = $('[data-quote-image]');
  const quantity = Number($('[data-quantity]')?.value) || 1;
  if (canvas) canvas.classList.add('is-changing');
  setTimeout(() => {
    if (image) {
      const [width, height] = imageDimensions[product.image] || [1200, 900];
      image.src = product.image;
      image.alt = `Pré-visualização: ${product.name}`;
      image.width = width;
      image.height = height;
    }
    if (canvas) canvas.classList.remove('is-changing');
  }, 170);
  if ($('[data-summary-category]')) $('[data-summary-category]').textContent = product.categoryLabel;
  if ($('[data-summary-product]')) $('[data-summary-product]').textContent = product.name;
  if ($('[data-summary-quantity]')) $('[data-summary-quantity]').textContent = `Quantidade: ${quantity}`;
  if ($('[data-quote-reference]')) $('[data-quote-reference]').textContent = product.reference;
  updateWhatsAppLink();
}

function setStep(step) {
  state.step = 1;
  $$('[data-step]').forEach(panel => {
    const active = Number(panel.dataset.step) === state.step;
    panel.hidden = !active;
    panel.classList.toggle('is-active', active);
  });
  if ($('[data-step-current]')) $('[data-step-current]').textContent = state.step;
  if ($('[data-progress]')) $('[data-progress]').style.width = '100%';
}

function validateCurrentStep() {
  const panel = $(`[data-step="${state.step}"]`);
  if (!panel) return true;
  const fields = $$('input, select, textarea', panel).filter(field => field.required);
  for (const field of fields) {
    if (!field.reportValidity()) return false;
  }
  return true;
}

function buildPayload() {
  const form = $('[data-quote-form]');
  const data = new FormData(form);
  const product = productById(state.selectedId);
  return {
    product_id: product.id,
    product_name: product.name,
    quantity: Number(data.get('quantity')) || 1,
    city: String(data.get('city') || '').trim(),
    deadline: String(data.get('deadline') || ''),
    design_help: data.get('design_help') === 'sim',
    customer_name: String(data.get('name') || '').trim(),
    whatsapp: String(data.get('whatsapp') || '').trim(),
    description: String(data.get('description') || '').trim(),
    page_url: `${location.origin}${location.pathname}`.slice(0, 500)
  };
}

function getSupabaseConfig() {
  const config = window.SCP_SUPABASE || {};
  const url = String(config.url || '').replace(/\/$/, '');
  const publishableKey = String(config.publishableKey || '');
  const validUrl = /^https:\/\/[a-z0-9]{20}\.supabase\.co$/i.test(url);
  const validKey = (publishableKey.startsWith('sb_publishable_') || publishableKey.startsWith('eyJ'))
    && !publishableKey.includes('SUBSTITUA');
  if (!validUrl || !validKey) throw new Error('SUPABASE_NOT_CONFIGURED');
  return { url, publishableKey };
}

async function saveQuoteRequest(payload) {
  const { url, publishableKey } = getSupabaseConfig();
  const response = await fetch(`${url}/rest/v1/scp_quote_requests`, {
    method: 'POST',
    headers: {
      apikey: publishableKey,
      'Content-Type': 'application/json',
      Prefer: 'return=minimal'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    console.warn('Não foi possível registar o pedido no Supabase.', response.status);
    throw new Error('QUOTE_INSERT_FAILED');
  }
}

function buildWhatsAppMessage(payload = buildPayload()) {
  return [
    'Olá Smart Color Print, quero pedir um orçamento.',
    `Produto: ${payload.product_name}`,
    `Quantidade: ${payload.quantity}`,
    payload.city && `Cidade: ${payload.city}`,
    payload.deadline && `Prazo: ${payload.deadline}`,
    payload.design_help && 'Preciso de ajuda com a arte: Sim',
    payload.customer_name && `Nome: ${payload.customer_name}`,
    payload.description && `Detalhes: ${payload.description}`
  ].filter(Boolean).join('\n');
}

function updateWhatsAppLink() {
  const link = $('[data-whatsapp-link]');
  if (link) link.href = whatsappUrl(buildWhatsAppMessage());
}

function openQuote() {
  $('#estudio')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function initQuoteWizard() {
  const form = $('[data-quote-form]');
  if (!form) return;
  const whatsappField = $('[name="whatsapp"]', form);
  const validateWhatsApp = () => {
    if (!whatsappField) return;
    if (!whatsappField.value) {
      whatsappField.setCustomValidity('');
      return;
    }
    const value = whatsappField.value.trim();
    const digitCount = value.replace(/\D/g, '').length;
    const valid = /^\+?[0-9 ()-]{7,30}$/.test(value) && digitCount >= 7 && digitCount <= 15;
    whatsappField.setCustomValidity(valid ? '' : 'Indique um WhatsApp válido com 7 a 15 algarismos.');
  };
  renderWizardProducts();
  updateQuoteSummary();
  setStep(1);

  $$('[data-open-quote]').forEach(button => button.addEventListener('click', openQuote));
  $$('[data-next-step]').forEach(button => button.addEventListener('click', () => { if (validateCurrentStep()) setStep(state.step + 1); }));
  $$('[data-prev-step]').forEach(button => button.addEventListener('click', () => setStep(state.step - 1)));
  $$('input, select, textarea', form).forEach(field => {
    field.addEventListener('input', () => { if (field === whatsappField) validateWhatsApp(); updateQuoteSummary(); updateWhatsAppLink(); });
    field.addEventListener('change', () => { if (field === whatsappField) validateWhatsApp(); updateQuoteSummary(); updateWhatsAppLink(); });
  });

  form.addEventListener('submit', async event => {
    event.preventDefault();
    validateWhatsApp();
    if (!form.reportValidity()) return;
    const status = $('[data-form-status]');
    const submit = $('button[type="submit"]', form);
    const payload = buildPayload();
    const original = submit.innerHTML;
    submit.disabled = true;
    submit.textContent = 'A enviar...';
    status.className = 'form-status';
    status.textContent = '';

    try {
      if ($('[name="company_website"]', form)?.value) {
        status.className = 'form-status success';
        status.textContent = 'Pedido registado. Vamos responder pelo WhatsApp.';
        submit.textContent = 'Pedido registado ✓';
        return;
      }
      await saveQuoteRequest(payload);
      status.className = 'form-status success';
      status.textContent = 'Pedido registado. Vamos responder pelo WhatsApp com preço, prazo e condições.';
      submit.textContent = 'Pedido registado ✓';
      sessionStorage.removeItem('scp-product');
    } catch (error) {
      status.className = 'form-status error';
      status.textContent = error?.message === 'SUPABASE_NOT_CONFIGURED'
        ? 'O registo online está a ser configurado. Continue pelo WhatsApp abaixo.'
        : 'Não foi possível registar agora. Os seus dados continuam preenchidos; continue pelo WhatsApp abaixo.';
      submit.disabled = false;
      submit.innerHTML = original;
      $('[data-whatsapp-link]')?.focus();
    }
  });
}

function initPortfolio() {
  const track = $('[data-work-track]');
  if (!track) return;
  $('[data-work-prev]')?.addEventListener('click', () => track.scrollBy({ left: -Math.min(track.clientWidth * .8, 500), behavior: 'smooth' }));
  $('[data-work-next]')?.addEventListener('click', () => track.scrollBy({ left: Math.min(track.clientWidth * .8, 500), behavior: 'smooth' }));

  const lightbox = $('[data-lightbox]');
  $$('[data-work-image]').forEach(card => card.addEventListener('click', () => {
    $('[data-lightbox-image]', lightbox).src = card.dataset.workImage;
    $('[data-lightbox-image]', lightbox).alt = card.dataset.workTitle;
    $('[data-lightbox-title]', lightbox).textContent = card.dataset.workTitle;
    lightbox.showModal();
  }));
  $('[data-lightbox-close]', lightbox)?.addEventListener('click', () => lightbox.close());
  lightbox?.addEventListener('click', event => { if (event.target === lightbox) lightbox.close(); });
}

initHeader();
initReveal();
initHero();
initExplorer();
initProductDialog();
initQuoteWizard();
initPortfolio();
