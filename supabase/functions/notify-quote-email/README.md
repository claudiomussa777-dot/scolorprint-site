# Notificação de novos pedidos

Esta Edge Function recebe o evento `INSERT` de `public.scp_quote_requests` e envia um email pelo Resend.

## Segredos necessários

- `RESEND_API_KEY`: chave Resend limitada a envio e ao domínio autorizado.
- `QUOTE_WEBHOOK_SECRET`: valor aleatório enviado no header `x-webhook-secret`.
- `QUOTE_NOTIFICATION_TO`: destinatário, atualmente `info@scolorprint.com`.
- `QUOTE_NOTIFICATION_FROM`: remetente autorizado pelo Resend.

## Webhook da base de dados

O webhook deve observar apenas `INSERT` em `public.scp_quote_requests` e fazer `POST` para:

`https://<project-ref>.supabase.co/functions/v1/notify-quote-email`

Headers obrigatórios:

- `Content-Type: application/json`
- `x-webhook-secret: <mesmo valor de QUOTE_WEBHOOK_SECRET>`

A função usa o ID do pedido como chave de idempotência para evitar emails duplicados quando o webhook é repetido.
