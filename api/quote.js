const requiredText = (value, max = 500) => typeof value === 'string' ? value.trim().slice(0, max) : '';

module.exports = async function handler(request, response) {
  if (request.method !== 'POST') {
    response.setHeader('Allow', 'POST');
    return response.status(405).json({ error: 'Método não permitido' });
  }

  const supabaseUrl = process.env.SUPABASE_URL;
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!supabaseUrl || !serviceKey) {
    return response.status(503).json({ error: 'Integração de pedidos não configurada' });
  }

  const body = request.body || {};
  const record = {
    product_id: requiredText(body.product_id, 80),
    product_name: requiredText(body.product_name, 160),
    quantity: Number.isFinite(Number(body.quantity)) ? Math.max(1, Math.min(100000, Number(body.quantity))) : 1,
    city: requiredText(body.city, 120),
    deadline: requiredText(body.deadline, 80),
    design_help: Boolean(body.design_help),
    customer_name: requiredText(body.customer_name, 160),
    whatsapp: requiredText(body.whatsapp, 60),
    description: requiredText(body.description, 2000),
    source: 'website',
    page_url: requiredText(body.page_url, 500),
    status: 'new'
  };

  if (!record.product_name || !record.customer_name || !record.whatsapp || !record.city) {
    return response.status(400).json({ error: 'Dados obrigatórios em falta' });
  }

  try {
    const result = await fetch(`${supabaseUrl.replace(/\/$/, '')}/rest/v1/scp_quote_requests`, {
      method: 'POST',
      headers: {
        apikey: serviceKey,
        Authorization: `Bearer ${serviceKey}`,
        'Content-Type': 'application/json',
        Prefer: 'return=minimal'
      },
      body: JSON.stringify(record)
    });

    if (!result.ok) {
      const details = await result.text();
      console.error('Supabase quote insert failed', result.status, details.slice(0, 500));
      return response.status(502).json({ error: 'Não foi possível guardar o pedido' });
    }

    return response.status(201).json({ ok: true });
  } catch (error) {
    console.error('Quote endpoint failed', error);
    return response.status(500).json({ error: 'Erro interno' });
  }
}
