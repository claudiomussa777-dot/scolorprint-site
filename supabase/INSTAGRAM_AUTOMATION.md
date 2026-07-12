# Publicação oficial multi-conta no Instagram

Esta implementação usa a **Instagram API with Instagram Login** e pede somente:

- `instagram_business_basic`
- `instagram_business_content_publish`

O token nunca é enviado ao site, escrito em logs ou guardado em texto simples. O callback cifra-o com AES-GCM antes de o guardar numa tabela sem acesso para `anon` ou `authenticated`.

## Contas isoladas

A integração aceita somente estes identificadores internos fixos:

- `smart_colorprint`
- `smart_home`

Cada credencial é guardada por `account`. A função de publicação exige esse campo e nunca escolhe a credencial mais recente. A idempotência é composta por `account + idempotency_key`, permitindo a mesma chave lógica em contas diferentes sem misturar conteúdo ou estado.

## Componentes locais

- `migrations/202607120003_create_instagram_automation.sql`: credencial cifrada e jobs idempotentes originais.
- `migrations/202607120004_instagram_multi_account.sql`: preserva os dados existentes como `smart_colorprint` e adiciona isolamento por conta.
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
- `INSTAGRAM_EXPECTED_USERNAME_SMART_COLORPRINT`
- `INSTAGRAM_EXPECTED_USERNAME_SMART_HOME`

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

Smart Color Print:

`https://ljhylqpsfvmjhvhjkokk.supabase.co/functions/v1/instagram-oauth?account=smart_colorprint`

Smart Home:

`https://ljhylqpsfvmjhvhjkokk.supabase.co/functions/v1/instagram-oauth?account=smart_home`

O endpoint mostra primeiro qual conta será ligada, cria um `state` aleatório num cookie `HttpOnly` separado por conta, redireciona para o Instagram e valida o `username` autorizado contra a configuração esperada. Só então troca e guarda a credencial cifrada. Uma conta incorreta é rejeitada sem substituir a credencial anterior.

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
  "account": "smart_colorprint",
  "idempotency_key": "instagram-isca-orcamento-v1",
  "image_url": "https://scolorprint.com/assets/campanhas/instagram-isca-orcamento-v1.jpg",
  "caption": "Legenda da publicação"
}
```

Para a Smart Home, use `"account": "smart_home"`. O campo é obrigatório; valores ausentes ou diferentes dos dois identificadores permitidos são rejeitados antes de qualquer chamada de publicação.

## Testes seguros

Os testes automatizados validam os identificadores e o isolamento estrutural sem criar contentores nem publicar no Instagram:

```sh
deno test supabase/functions/_shared/instagram_test.ts
```

Não use a função `instagram-publish` como teste sem aprovação explícita da imagem e da legenda: criar e publicar conteúdo é uma operação externa irreversível.

Não guarde `pedido-instagram.json` no Git se a legenda ainda não for pública.

## Storage

O repositório não contém configuração de Supabase Storage. Para a campanha atual, o caminho mais simples é servir a imagem no próprio `scolorprint.com`, que já é um host público aceito pela Meta. Se for criado um bucket no futuro, permita escrita somente à `service_role`; a Meta precisa apenas de leitura pública temporária ou de uma URL assinada válida durante todo o processamento.
