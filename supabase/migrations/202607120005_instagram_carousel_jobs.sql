alter table public.scp_instagram_publish_jobs
  add column if not exists image_urls jsonb;

update public.scp_instagram_publish_jobs
set image_urls = jsonb_build_array(image_url)
where image_urls is null;

alter table public.scp_instagram_publish_jobs
  alter column image_urls set not null;

alter table public.scp_instagram_publish_jobs
  drop constraint if exists scp_instagram_publish_jobs_image_urls_check;

alter table public.scp_instagram_publish_jobs
  add constraint scp_instagram_publish_jobs_image_urls_check
  check (
    jsonb_typeof(image_urls) = 'array'
    and jsonb_array_length(image_urls) between 1 and 10
  );

comment on column public.scp_instagram_publish_jobs.image_urls is
  'Lista ordenada de imagens; uma imagem cria post simples e duas a dez criam carrossel.';
