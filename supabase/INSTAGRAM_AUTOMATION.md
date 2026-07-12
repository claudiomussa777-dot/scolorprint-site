# Publicação oficial no Instagram

Esta implementação usa a **Instagram API with Instagram Login** e pede somente:

- `instagram_business_basic`
- `instagram_business_content_publish`

O token nunca é enviado ao site, escrito em logs ou guardado em texto simples. O callback cifra-o com AES-GCM antes de o guardar numa tabela sem acesso para `anon` ou `authenticated`.

## Componentes locais

- `migrations/202607120003_create_instagram_automation.sql`: credencial cifrada e jobs idempotentes.
- `functions/instagram-oauth/index.ts`: início OAuth, validação `state` e callback.
- `functions/instagram-publish/index.ts`: contentor, espera de processamento e `media_publish`.
- `functions/_shared/instagram.ts`: cifra, PostgREST interno e erros sanitizados.

## Configuração necessária

No painel Meta, registe exatamente este **Valid OAuth Redirect URI**:

`https://ljhylqpsfvmjhvhjkokk.supabase.co/functions/v1/instagram-oauth`

Guarde estes valores apenas como Supabase Edge Function secrets:

- `INSTAGRAM_APP_ID`
- `INSTAGRAM_APP_SECRET`
- `INSTAGRAM_OAUTH_REDIRECT_URI`
- `INSTAGRAM_TOKEN_ENCRYPTION_KEY`
- `INSTAGRAM_PUBLISHER_SECRET`
- `INSTAGRAM_GRAPH_API_VERSION`
- `INSTAGRAM_ALLOWED_MEDIA_HOSTS`

`SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` já são fornecidos pelo runtime hospedado do Supabase. Não os copie para o frontend.

Para gerar os dois segredos aleatórios, use localmente `openssl rand -base64 48`. Guarde os valores num ficheiro como `.env.instagram.local`, que já está ignorado pelo Git. Nunca cole os valores no README, código, terminal partilhado ou conversa.

Depois de autenticar o CLI, a sequência de ativação é:

```sh
npx supabase link --project-ref ljhylqpsfvmjhvhjkokk
npx supabase db push
npx supabase secrets set --env-file .env.instagram.local --project-ref ljhylqpsfvmjhvhjkokk
npx supabase functions deploy instagram-oauth --project-ref ljhylqpsfvmjhvhjkokk
npx supabase functions deploy instagram-publish --project-ref ljhylqpsfvmjhvhjkokk
```

Estas instruções não foram executadas automaticamente: alteram o projeto remoto e exigem autenticação do proprietário.

## Ligar a conta

Após o deploy, abra no navegador:

`https://ljhylqpsfvmjhvhjkokk.supabase.co/functions/v1/instagram-oauth`

O endpoint cria um `state` aleatório num cookie `HttpOnly`, redireciona para o Instagram, troca o código por uma credencial de longa duração e guarda somente a versão cifrada.

## Publicar sem duplicar

A imagem tem de estar numa URL HTTPS pública e num host listado em `INSTAGRAM_ALLOWED_MEDIA_HOSTS`. A publicação exige um identificador único; repetir um job já publicado devolve o mesmo resultado em vez de publicar novamente.

Exemplo sem incluir o segredo no comando:

```sh
curl --fail-with-body \
  -X POST 'https://ljhylqpsfvmjhvhjkokk.supabase.co/functions/v1/instagram-publish' \
  -H 'content-type: application/json' \
  -H "x-publisher-secret: ${INSTAGRAM_PUBLISHER_SECRET}" \
  --data-binary @pedido-instagram.json
```

Estrutura de `pedido-instagram.json`:

```json
{
  "idempotency_key": "instagram-isca-orcamento-v1",
  "image_url": "https://scolorprint.com/assets/campanhas/instagram-isca-orcamento-v1.jpg",
  "caption": "Legenda da publicação"
}
```

Não guarde `pedido-instagram.json` no Git se a legenda ainda não for pública.

## Storage

O repositório não contém configuração de Supabase Storage. Para a campanha atual, o caminho mais simples é servir a imagem no próprio `scolorprint.com`, que já é um host público aceito pela Meta. Se for criado um bucket no futuro, permita escrita somente à `service_role`; a Meta precisa apenas de leitura pública temporária ou de uma URL assinada válida durante todo o processamento.
