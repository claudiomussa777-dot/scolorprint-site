-- Dados internos da integração Instagram. Tokens são cifrados na Edge Function
-- antes de chegarem à base de dados; a chave de cifra fica apenas nos secrets.

create table if not exists public.scp_instagram_credentials (
  instagram_user_id text primary key check (instagram_user_id ~ '^[0-9]+$'),
  username text check (username is null or char_length(username) between 1 and 64),
  access_token_ciphertext text not null,
  access_token_iv text not null,
  scopes text[] not null default array[]::text[],
  expires_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.scp_instagram_credentials enable row level security;
revoke all on table public.scp_instagram_credentials from public, anon, authenticated;

comment on table public.scp_instagram_credentials is
  'Credenciais Instagram cifradas pela Edge Function; acessíveis apenas com service_role.';

create table if not exists public.scp_instagram_publish_jobs (
  id uuid primary key default gen_random_uuid(),
  idempotency_key text not null unique check (idempotency_key ~ '^[A-Za-z0-9][A-Za-z0-9._:-]{0,119}$'),
  image_url text not null check (image_url ~ '^https://'),
  caption text not null check (char_length(caption) between 1 and 2200),
  status text not null default 'creating' check (
    status in ('creating', 'processing', 'publishing', 'published', 'failed')
  ),
  container_id text,
  media_id text,
  error_code text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.scp_instagram_publish_jobs enable row level security;
revoke all on table public.scp_instagram_publish_jobs from public, anon, authenticated;

create index if not exists scp_instagram_publish_jobs_created_at_idx
  on public.scp_instagram_publish_jobs (created_at desc);

comment on table public.scp_instagram_publish_jobs is
  'Controlo de idempotência para impedir publicações duplicadas no Instagram.';
