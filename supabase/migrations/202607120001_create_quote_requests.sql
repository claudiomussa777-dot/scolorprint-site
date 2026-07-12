create extension if not exists pgcrypto;

create table if not exists public.quote_requests (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  product_id text not null,
  product_name text not null,
  quantity integer not null check (quantity > 0),
  city text not null,
  deadline text,
  design_help boolean not null default false,
  customer_name text not null,
  whatsapp text not null,
  description text,
  source text not null default 'website',
  page_url text,
  status text not null default 'new' check (status in ('new', 'contacted', 'quoted', 'won', 'lost'))
);

alter table public.quote_requests enable row level security;

comment on table public.quote_requests is 'Pedidos de orçamento recebidos pelo site da Smart Color Print.';
comment on column public.quote_requests.status is 'Estado interno do pedido; nunca exposto publicamente.';

create index if not exists quote_requests_created_at_idx on public.quote_requests (created_at desc);
create index if not exists quote_requests_status_idx on public.quote_requests (status);

-- Não são criadas políticas públicas. A função serverless da Vercel usa a
-- service role para inserir pedidos; o browser nunca recebe essa chave.
