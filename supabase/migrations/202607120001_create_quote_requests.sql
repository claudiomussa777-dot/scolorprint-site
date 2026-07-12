create table if not exists public.scp_quote_requests (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  product_id text not null check (product_id ~ '^[a-z0-9][a-z0-9_-]{0,79}$'),
  product_name text not null check (char_length(btrim(product_name)) between 1 and 160),
  quantity integer not null check (quantity between 1 and 100000),
  city text not null check (char_length(btrim(city)) between 1 and 120),
  deadline text check (deadline in ('flexivel', '1-semana', '2-semanas', 'data')),
  design_help boolean not null default false,
  customer_name text not null check (char_length(btrim(customer_name)) between 1 and 160),
  whatsapp text not null check (
    char_length(btrim(whatsapp)) between 7 and 30
    and whatsapp ~ '^\+?[0-9 ()-]{7,30}$'
    and char_length(regexp_replace(whatsapp, '[^0-9]', '', 'g')) between 7 and 15
  ),
  description text check (description is null or char_length(description) <= 2000),
  source text not null default 'website' check (source = 'website'),
  page_url text check (page_url is null or char_length(page_url) <= 500),
  status text not null default 'new' check (status in ('new', 'contacted', 'quoted', 'won', 'lost'))
);

alter table public.scp_quote_requests enable row level security;

comment on table public.scp_quote_requests is 'Pedidos de orçamento recebidos pelo site da Smart Color Print.';
comment on column public.scp_quote_requests.status is 'Estado interno do pedido; nunca exposto publicamente.';

create index if not exists scp_quote_requests_created_at_idx on public.scp_quote_requests (created_at desc);
create index if not exists scp_quote_requests_status_idx on public.scp_quote_requests (status);

-- A política pública de inserção é aplicada na migração seguinte. O browser
-- recebe apenas a publishable key e nunca uma secret/service-role key.
