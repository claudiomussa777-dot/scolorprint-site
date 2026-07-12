type QuoteRecord = {
  id: string;
  created_at: string;
  product_name: string;
  quantity: number;
  city: string;
  deadline: string | null;
  design_help: boolean;
  customer_name: string;
  whatsapp: string;
  description: string | null;
};

type DatabaseWebhookPayload = {
  type: string;
  table: string;
  schema: string;
  record: QuoteRecord | null;
};

const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY') ?? '';
const WEBHOOK_SECRET = Deno.env.get('QUOTE_WEBHOOK_SECRET') ?? '';
const NOTIFICATION_TO = Deno.env.get('QUOTE_NOTIFICATION_TO') ?? 'info@scolorprint.com';
const NOTIFICATION_FROM = Deno.env.get('QUOTE_NOTIFICATION_FROM') ?? 'Smart Color Print <pedidos@izitender.com>';

const escapeHtml = (value: unknown) => String(value ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#039;');

const deadlineLabel = (deadline: string | null) => ({
  flexivel: 'Prazo flexível',
  '1-semana': 'Dentro de 1 semana',
  '2-semanas': 'Dentro de 2 semanas',
  data: 'Data específica'
}[deadline ?? ''] ?? deadline ?? 'Não indicado');

Deno.serve(async (request: Request) => {
  if (request.method !== 'POST') {
    return Response.json({ error: 'Method not allowed' }, { status: 405 });
  }

  if (!WEBHOOK_SECRET || request.headers.get('x-webhook-secret') !== WEBHOOK_SECRET) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  if (!RESEND_API_KEY) {
    return Response.json({ error: 'Email provider not configured' }, { status: 503 });
  }

  let payload: DatabaseWebhookPayload;
  try {
    payload = await request.json();
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 });
  }

  if (payload.type !== 'INSERT' || payload.schema !== 'public' || payload.table !== 'scp_quote_requests' || !payload.record) {
    return Response.json({ error: 'Unsupported event' }, { status: 400 });
  }

  const quote = payload.record;
  const subject = `Novo pedido: ${quote.product_name} — ${quote.customer_name}`;
  const rows = [
    ['Cliente', quote.customer_name],
    ['WhatsApp', quote.whatsapp],
    ['Produto', quote.product_name],
    ['Quantidade', quote.quantity],
    ['Cidade', quote.city],
    ['Prazo', deadlineLabel(quote.deadline)],
    ['Ajuda com a arte', quote.design_help ? 'Sim' : 'Não'],
    ['Descrição', quote.description || 'Não indicada'],
    ['Recebido em', new Date(quote.created_at).toLocaleString('pt-MZ', { timeZone: 'Africa/Maputo' })]
  ];

  const htmlRows = rows.map(([label, value]) => `
    <tr>
      <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;color:#667085;font-size:13px;vertical-align:top">${escapeHtml(label)}</td>
      <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;color:#101828;font-size:14px;font-weight:600;white-space:pre-wrap">${escapeHtml(value)}</td>
    </tr>`).join('');

  const text = [
    'Novo pedido recebido no site Smart Color Print',
    '',
    ...rows.map(([label, value]) => `${label}: ${value}`)
  ].join('\n');

  const emailResponse = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${RESEND_API_KEY}`,
      'Content-Type': 'application/json',
      'Idempotency-Key': `scp-quote-${quote.id}`
    },
    body: JSON.stringify({
      from: NOTIFICATION_FROM,
      to: [NOTIFICATION_TO],
      reply_to: 'info@scolorprint.com',
      subject,
      text,
      html: `
        <!doctype html>
        <html lang="pt">
          <body style="margin:0;background:#f5f1e8;font-family:Arial,sans-serif;color:#101828">
            <div style="max-width:640px;margin:0 auto;padding:32px 16px">
              <div style="background:#11110f;padding:24px;border-radius:16px 16px 0 0">
                <p style="margin:0 0 8px;color:#d7ff3f;font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase">Smart Color Print</p>
                <h1 style="margin:0;color:#fff;font-size:25px;line-height:1.25">Novo pedido recebido</h1>
              </div>
              <div style="background:#fff;padding:12px 20px 24px;border-radius:0 0 16px 16px">
                <table role="presentation" style="width:100%;border-collapse:collapse">${htmlRows}</table>
                <a href="https://wa.me/${quote.whatsapp.replace(/\D/g, '')}" style="display:inline-block;margin-top:22px;padding:13px 18px;background:#25d366;color:#07120c;text-decoration:none;border-radius:9px;font-weight:700">Responder no WhatsApp</a>
              </div>
            </div>
          </body>
        </html>`
    })
  });

  if (!emailResponse.ok) {
    console.error('Resend notification failed', emailResponse.status);
    return Response.json({ error: 'Email delivery failed' }, { status: 502 });
  }

  const result = await emailResponse.json();
  return Response.json({ ok: true, email_id: result.id });
});
