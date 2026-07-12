import {
  CredentialRecord,
  InstagramAccount,
  SafeError,
  constantTimeEqual,
  databaseRequest,
  decryptToken,
  errorResponse,
  jsonResponse,
  loadCredential,
  metaJson,
  parseInstagramAccount,
  publishJobQueryPath,
  requireEnv,
  saveCredential
} from '../_shared/instagram.ts';

type PublishInput = {
  account?: unknown;
  image_url?: unknown;
  caption?: unknown;
  idempotency_key?: unknown;
};

type PublishJob = {
  id: string;
  account: InstagramAccount;
  idempotency_key: string;
  image_url: string;
  caption: string;
  status: 'creating' | 'processing' | 'publishing' | 'published' | 'failed';
  container_id: string | null;
  media_id: string | null;
  error_code: string | null;
  created_at: string;
  updated_at: string;
};

type IdResponse = { id?: string };
type ContainerStatusResponse = { status_code?: string; status?: string; id?: string };
type RefreshTokenResponse = { access_token?: string; token_type?: string; expires_in?: number };

const graphVersion = (): string => {
  const value = Deno.env.get('INSTAGRAM_GRAPH_API_VERSION')?.trim() || 'v25.0';
  if (!/^v\d+\.\d+$/.test(value)) {
    throw new SafeError('INVALID_GRAPH_VERSION', 'Versão da Graph API inválida', 503);
  }
  return value;
};

const graphUrl = (path: string): URL => new URL(
  `https://graph.instagram.com/${graphVersion()}/${path.replace(/^\//, '')}`
);

const authorizeRequest = (request: Request): void => {
  const expected = requireEnv('INSTAGRAM_PUBLISHER_SECRET');
  const received = request.headers.get('x-publisher-secret') ?? '';
  if (!received || !constantTimeEqual(received, expected)) {
    throw new SafeError('UNAUTHORIZED', 'Não autorizado', 401);
  }
};

export const validateInput = (body: PublishInput): { account: InstagramAccount; imageUrl: string; caption: string; idempotencyKey: string } => {
  const account = parseInstagramAccount(body.account);
  const imageUrl = typeof body.image_url === 'string' ? body.image_url.trim() : '';
  const caption = typeof body.caption === 'string' ? body.caption.trim() : '';
  const idempotencyKey = typeof body.idempotency_key === 'string' ? body.idempotency_key.trim() : '';

  if (!/^[A-Za-z0-9][A-Za-z0-9._:-]{0,119}$/.test(idempotencyKey)) {
    throw new SafeError('INVALID_IDEMPOTENCY_KEY', 'Identificador de publicação inválido', 400);
  }
  if (!caption || caption.length > 2200) {
    throw new SafeError('INVALID_CAPTION', 'A legenda deve ter entre 1 e 2200 caracteres', 400);
  }

  let parsedUrl: URL;
  try {
    parsedUrl = new URL(imageUrl);
  } catch {
    throw new SafeError('INVALID_IMAGE_URL', 'Ligação da imagem inválida', 400);
  }
  if (parsedUrl.protocol !== 'https:' || parsedUrl.username || parsedUrl.password) {
    throw new SafeError('INVALID_IMAGE_URL', 'A imagem deve usar uma ligação HTTPS pública', 400);
  }

  const defaultHosts = 'scolorprint.com,www.scolorprint.com,ljhylqpsfvmjhvhjkokk.supabase.co';
  const allowedHosts = new Set(
    (Deno.env.get('INSTAGRAM_ALLOWED_MEDIA_HOSTS') || defaultHosts)
      .split(',')
      .map((host) => host.trim().toLowerCase())
      .filter(Boolean)
  );
  if (!allowedHosts.has(parsedUrl.hostname.toLowerCase())) {
    throw new SafeError('MEDIA_HOST_NOT_ALLOWED', 'O domínio da imagem não está autorizado', 400);
  }
  return { account, imageUrl: parsedUrl.toString(), caption, idempotencyKey };
};

const getJob = async (account: InstagramAccount, idempotencyKey: string): Promise<PublishJob | null> => {
  const { response, data } = await databaseRequest<PublishJob[]>(
    publishJobQueryPath(account, idempotencyKey)
  );
  if (!response.ok) throw new SafeError('PUBLISH_JOB_READ_FAILED', 'Não foi possível ler o estado da publicação', 502);
  return data?.[0] ?? null;
};

const claimJob = async (input: ReturnType<typeof validateInput>): Promise<{ job: PublishJob; created: boolean }> => {
  const { response, data } = await databaseRequest<PublishJob[]>('scp_instagram_publish_jobs', {
    method: 'POST',
    headers: { Prefer: 'return=representation' },
    body: JSON.stringify({
      account: input.account,
      idempotency_key: input.idempotencyKey,
      image_url: input.imageUrl,
      caption: input.caption,
      status: 'creating'
    })
  });
  if (response.ok && data?.[0]) return { job: data[0], created: true };
  if (response.status !== 409) {
    throw new SafeError('PUBLISH_JOB_CREATE_FAILED', 'Não foi possível iniciar a publicação', 502);
  }

  const existing = await getJob(input.account, input.idempotencyKey);
  if (!existing) throw new SafeError('PUBLISH_JOB_CONFLICT', 'A publicação já foi iniciada', 409);
  if (existing.image_url !== input.imageUrl || existing.caption !== input.caption) {
    throw new SafeError('IDEMPOTENCY_KEY_REUSED', 'Este identificador já pertence a outro conteúdo', 409);
  }
  return { job: existing, created: false };
};

const updateJob = async (jobId: string, values: Partial<PublishJob>): Promise<void> => {
  const { response } = await databaseRequest(`scp_instagram_publish_jobs?id=eq.${encodeURIComponent(jobId)}`, {
    method: 'PATCH',
    headers: { Prefer: 'return=minimal' },
    body: JSON.stringify({ ...values, updated_at: new Date().toISOString() })
  });
  if (!response.ok) throw new SafeError('PUBLISH_JOB_UPDATE_FAILED', 'Não foi possível atualizar o estado da publicação', 502);
};

const tokenForPublishing = async (credential: CredentialRecord): Promise<string> => {
  const currentToken = await decryptToken(credential.access_token_ciphertext, credential.access_token_iv);
  const expiry = credential.expires_at ? Date.parse(credential.expires_at) : Number.NaN;
  const refreshThreshold = Date.now() + 7 * 24 * 60 * 60 * 1000;
  if (!Number.isFinite(expiry) || expiry > refreshThreshold) return currentToken;

  const refreshUrl = new URL('https://graph.instagram.com/refresh_access_token');
  refreshUrl.search = new URLSearchParams({
    grant_type: 'ig_refresh_token',
    access_token: currentToken
  }).toString();

  try {
    const refreshed = await metaJson<RefreshTokenResponse>(refreshUrl);
    if (!refreshed.access_token) return currentToken;
    const expiresIn = Number(refreshed.expires_in);
    const expiresAt = Number.isFinite(expiresIn) && expiresIn > 0
      ? new Date(Date.now() + expiresIn * 1000).toISOString()
      : credential.expires_at;
    await saveCredential({
      account: credential.account,
      instagramUserId: credential.instagram_user_id,
      username: credential.username,
      accessToken: refreshed.access_token,
      expiresAt
    });
    return refreshed.access_token;
  } catch (error) {
    // Um erro de renovação não deve impedir o uso de um token ainda válido.
    if (Number.isFinite(expiry) && expiry > Date.now() + 60 * 60 * 1000) {
      console.error('Instagram token refresh deferred', error instanceof SafeError ? error.code : 'UNKNOWN');
      return currentToken;
    }
    throw error;
  }
};

const createContainer = async (
  instagramUserId: string,
  token: string,
  imageUrl: string,
  caption: string
): Promise<string> => {
  const result = await metaJson<IdResponse>(graphUrl(`${instagramUserId}/media`), {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ image_url: imageUrl, caption })
  });
  if (!result.id) throw new SafeError('CONTAINER_ID_MISSING', 'O Instagram não devolveu o contentor da publicação', 502);
  return result.id;
};

const waitForContainer = async (containerId: string, token: string): Promise<boolean> => {
  for (let attempt = 0; attempt < 10; attempt += 1) {
    const url = graphUrl(containerId);
    url.search = new URLSearchParams({ fields: 'status_code,status' }).toString();
    const result = await metaJson<ContainerStatusResponse>(url, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const status = result.status_code?.toUpperCase();
    if (status === 'FINISHED') return true;
    if (status === 'ERROR' || status === 'EXPIRED') {
      throw new SafeError('MEDIA_PROCESSING_FAILED', 'O Instagram não conseguiu processar a imagem', 409);
    }
    if (attempt < 9) await new Promise((resolve) => setTimeout(resolve, 5000));
  }
  return false;
};

const publishContainer = async (instagramUserId: string, token: string, containerId: string): Promise<string> => {
  const result = await metaJson<IdResponse>(graphUrl(`${instagramUserId}/media_publish`), {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ creation_id: containerId })
  });
  if (!result.id) throw new SafeError('MEDIA_ID_MISSING', 'O Instagram não confirmou a publicação', 502);
  return result.id;
};

Deno.serve(async (request: Request) => {
  let activeJob: PublishJob | null = null;
  try {
    if (request.method !== 'POST') {
      return jsonResponse({ ok: false, error: 'METHOD_NOT_ALLOWED', message: 'Método não permitido' }, 405);
    }
    authorizeRequest(request);

    let body: PublishInput;
    try {
      body = await request.json();
    } catch {
      throw new SafeError('INVALID_JSON', 'Corpo JSON inválido', 400);
    }
    const input = validateInput(body);
    const claimed = await claimJob(input);
    activeJob = claimed.job;

    if (activeJob.status === 'published') {
      return jsonResponse({ ok: true, account: input.account, status: 'published', media_id: activeJob.media_id, duplicate: true });
    }
    if (activeJob.status === 'failed') {
      throw new SafeError('PREVIOUS_ATTEMPT_FAILED', 'A tentativa anterior falhou; use um novo identificador após corrigir a causa', 409);
    }
    if (activeJob.status === 'publishing') {
      throw new SafeError('PUBLISH_STATE_UNCERTAIN', 'A confirmação da tentativa anterior está pendente; não será repetida para evitar duplicação', 409);
    }
    if (!claimed.created && activeJob.status === 'creating' && !activeJob.container_id) {
      throw new SafeError('PUBLISH_STATE_UNCERTAIN', 'A tentativa anterior ficou incompleta; confirme o Instagram antes de repetir', 409);
    }

    const credential = await loadCredential(input.account);
    if (credential.account !== input.account) {
      throw new SafeError('CREDENTIAL_ACCOUNT_MISMATCH', 'A credencial não corresponde à conta pedida', 409);
    }
    const token = await tokenForPublishing(credential);
    let containerId = activeJob.container_id;
    if (!containerId) {
      containerId = await createContainer(credential.instagram_user_id, token, input.imageUrl, input.caption);
      await updateJob(activeJob.id, { status: 'processing', container_id: containerId, error_code: null });
      activeJob = { ...activeJob, status: 'processing', container_id: containerId };
    }

    const ready = await waitForContainer(containerId, token);
    if (!ready) {
      return jsonResponse({ ok: false, account: input.account, status: 'processing', retry_with_same_idempotency_key: true }, 202);
    }

    // Mudar primeiro para publishing é deliberado: se a rede cair depois do POST,
    // uma repetição automática poderia criar um post duplicado.
    await updateJob(activeJob.id, { status: 'publishing', error_code: null });
    activeJob = { ...activeJob, status: 'publishing' };
    const mediaId = await publishContainer(credential.instagram_user_id, token, containerId);
    await updateJob(activeJob.id, { status: 'published', media_id: mediaId, error_code: null });

    return jsonResponse({ ok: true, account: input.account, status: 'published', media_id: mediaId }, 201);
  } catch (error) {
    // Antes de chamar media_publish, uma falha explícita é segura para marcar.
    // Durante publishing deixamos o estado incerto para impedir repetição cega.
    if (activeJob && activeJob.status !== 'publishing' && activeJob.status !== 'published') {
      try {
        const code = error instanceof SafeError ? error.code : 'INTERNAL_ERROR';
        await updateJob(activeJob.id, { status: 'failed', error_code: code });
      } catch {
        console.error('Could not persist Instagram job failure');
      }
    }
    return errorResponse(error);
  }
});
