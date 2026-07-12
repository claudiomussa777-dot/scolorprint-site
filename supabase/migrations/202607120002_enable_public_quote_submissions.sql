-- Permite ao site estatico criar pedidos sem expor qualquer dado existente.
-- A publishable key usa o role anon; nenhuma chave administrativa vai para o browser.

alter table public.scp_quote_requests enable row level security;

revoke all on table public.scp_quote_requests from public, anon, authenticated;

grant insert (
  product_id,
  product_name,
  quantity,
  city,
  deadline,
  design_help,
  customer_name,
  whatsapp,
  description,
  page_url
) on table public.scp_quote_requests to anon;

drop policy if exists "scp_website_can_create_quote_requests" on public.scp_quote_requests;

create policy "scp_website_can_create_quote_requests"
on public.scp_quote_requests
for insert
to anon
with check (
  source = 'website'
  and status = 'new'
  and quantity between 1 and 100000
  and char_length(btrim(product_id)) between 1 and 80
  and char_length(btrim(product_name)) between 1 and 160
  and char_length(btrim(city)) between 1 and 120
  and (deadline is null or deadline in ('flexivel', '1-semana', '2-semanas', 'data'))
  and char_length(btrim(customer_name)) between 1 and 160
  and char_length(btrim(whatsapp)) between 7 and 30
  and whatsapp ~ '^\+?[0-9 ()-]{7,30}$'
  and char_length(regexp_replace(whatsapp, '[^0-9]', '', 'g')) between 7 and 15
  and (description is null or char_length(description) <= 2000)
  and (page_url is null or char_length(page_url) <= 500)
);

comment on policy "scp_website_can_create_quote_requests" on public.scp_quote_requests is
  'O visitante pode apenas criar um pedido novo e validado; nao pode ler, editar ou apagar pedidos.';
