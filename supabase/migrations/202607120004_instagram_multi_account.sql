-- Torna a integração Instagram explicitamente multi-conta sem substituir a
-- credencial já existente. Todos os registos anteriores pertencem à Smart Color Print.

alter table public.scp_instagram_credentials
  add column if not exists account text;

update public.scp_instagram_credentials
set account = 'smart_colorprint'
where account is null;

alter table public.scp_instagram_credentials
  alter column account set not null;

alter table public.scp_instagram_credentials
  drop constraint if exists scp_instagram_credentials_account_check;

alter table public.scp_instagram_credentials
  add constraint scp_instagram_credentials_account_check
  check (account in ('smart_colorprint', 'smart_home'));

create unique index if not exists scp_instagram_credentials_account_key
  on public.scp_instagram_credentials (account);

alter table public.scp_instagram_publish_jobs
  add column if not exists account text;

update public.scp_instagram_publish_jobs
set account = 'smart_colorprint'
where account is null;

alter table public.scp_instagram_publish_jobs
  alter column account set not null;

alter table public.scp_instagram_publish_jobs
  drop constraint if exists scp_instagram_publish_jobs_account_check;

alter table public.scp_instagram_publish_jobs
  add constraint scp_instagram_publish_jobs_account_check
  check (account in ('smart_colorprint', 'smart_home'));

alter table public.scp_instagram_publish_jobs
  drop constraint if exists scp_instagram_publish_jobs_idempotency_key_key;

create unique index if not exists scp_instagram_publish_jobs_account_idempotency_key
  on public.scp_instagram_publish_jobs (account, idempotency_key);

create index if not exists scp_instagram_publish_jobs_account_created_at_idx
  on public.scp_instagram_publish_jobs (account, created_at desc);

comment on column public.scp_instagram_credentials.account is
  'Identificador interno fixo da conta: smart_colorprint ou smart_home.';

comment on column public.scp_instagram_publish_jobs.account is
  'Conta Instagram que recebe exclusivamente este conteúdo.';
