export const INSTAGRAM_SCOPES = [
  'instagram_business_basic',
  'instagram_business_content_publish'
] as const;

export type CredentialRecord = {
  instagram_user_id: string;
  username: string | null;
  access_token_ciphertext: string;
  access_token_iv: string;
  scopes: string[];
  expires_at: string | null;
  updated_at: string;
};

export class SafeError extends Error {
  status: number;
  code: string;

  constructor(code: string, message: string, status = 500) {
    super(message);
    this.name = 'SafeError';
    this.code = code;
    this.status = status;
  }
}

export const requireEnv = (name: string): string => {
  const value = Deno.env.get(name)?.trim();
  if (!value) throw new SafeError('CONFIGURATION_ERROR', `Configuração em falta: ${name}`, 503);
  return value;
};

const bytesToBase64 = (bytes: Uint8Array): string => {
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary);
};

const base64ToBytes = (value: string): Uint8Array<ArrayBuffer> => {
  const binary = atob(value);
  const buffer = new ArrayBuffer(binary.length);
  const bytes = new Uint8Array(buffer);
  for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
  return bytes;
};

const tokenEncryptionKey = async (): Promise<CryptoKey> => {
  // Aceita um segredo aleatório longo e deriva uma chave AES-256 estável.
  const material = new TextEncoder().encode(requireEnv('INSTAGRAM_TOKEN_ENCRYPTION_KEY'));
  const digest = await crypto.subtle.digest('SHA-256', material);
  return crypto.subtle.importKey('raw', digest, { name: 'AES-GCM' }, false, ['encrypt', 'decrypt']);
};

export const encryptToken = async (token: string): Promise<{ ciphertext: string; iv: string }> => {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const encrypted = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    await tokenEncryptionKey(),
    new TextEncoder().encode(token)
  );
  return {
    ciphertext: bytesToBase64(new Uint8Array(encrypted)),
    iv: bytesToBase64(iv)
  };
};

export const decryptToken = async (ciphertext: string, iv: string): Promise<string> => {
  try {
    const decrypted = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: base64ToBytes(iv) },
      await tokenEncryptionKey(),
      base64ToBytes(ciphertext)
    );
    return new TextDecoder().decode(decrypted);
  } catch {
    throw new SafeError('TOKEN_DECRYPTION_FAILED', 'Não foi possível abrir a credencial guardada', 503);
  }
};

export const databaseRequest = async <T>(
  path: string,
  init: RequestInit = {}
): Promise<{ response: Response; data: T | null }> => {
  const supabaseUrl = requireEnv('SUPABASE_URL').replace(/\/$/, '');
  const serviceRoleKey = requireEnv('SUPABASE_SERVICE_ROLE_KEY');
  const headers = new Headers(init.headers);
  headers.set('apikey', serviceRoleKey);
  headers.set('Authorization', `Bearer ${serviceRoleKey}`);
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');

  const response = await fetch(`${supabaseUrl}/rest/v1/${path}`, { ...init, headers });
  let data: T | null = null;
  if (response.status !== 204) {
    try {
      data = await response.json() as T;
    } catch {
      data = null;
    }
  }
  return { response, data };
};

export const saveCredential = async (input: {
  instagramUserId: string;
  username?: string | null;
  accessToken: string;
  expiresAt?: string | null;
}): Promise<void> => {
  const encrypted = await encryptToken(input.accessToken);
  const { response } = await databaseRequest(
    'scp_instagram_credentials?on_conflict=instagram_user_id',
    {
      method: 'POST',
      headers: { Prefer: 'resolution=merge-duplicates,return=minimal' },
      body: JSON.stringify({
        instagram_user_id: input.instagramUserId,
        username: input.username ?? null,
        access_token_ciphertext: encrypted.ciphertext,
        access_token_iv: encrypted.iv,
        scopes: [...INSTAGRAM_SCOPES],
        expires_at: input.expiresAt ?? null,
        updated_at: new Date().toISOString()
      })
    }
  );
  if (!response.ok) throw new SafeError('CREDENTIAL_STORE_FAILED', 'Não foi possível guardar a credencial', 502);
};

export const loadCredential = async (): Promise<CredentialRecord> => {
  const select = [
    'instagram_user_id',
    'username',
    'access_token_ciphertext',
    'access_token_iv',
    'scopes',
    'expires_at',
    'updated_at'
  ].join(',');
  const { response, data } = await databaseRequest<CredentialRecord[]>(
    `scp_instagram_credentials?select=${select}&order=updated_at.desc&limit=1`
  );
  if (!response.ok) throw new SafeError('CREDENTIAL_READ_FAILED', 'Não foi possível ler a credencial', 502);
  if (!data?.[0]) throw new SafeError('INSTAGRAM_NOT_CONNECTED', 'A conta Instagram ainda não foi ligada', 409);
  return data[0];
};

type MetaErrorBody = {
  error?: { code?: number; error_subcode?: number; type?: string; fbtrace_id?: string };
};

export const metaJson = async <T>(url: URL | string, init?: RequestInit): Promise<T> => {
  let response: Response;
  try {
    response = await fetch(url, init);
  } catch {
    throw new SafeError('META_NETWORK_ERROR', 'Não foi possível contactar o Instagram', 502);
  }

  let body: (T & MetaErrorBody) | MetaErrorBody | null = null;
  try {
    body = await response.json() as (T & MetaErrorBody);
  } catch {
    body = null;
  }

  if (!response.ok || body?.error) {
    const error = body?.error;
    // Não registar URL, payload ou token. Estes campos são seguros para diagnóstico.
    console.error('Instagram API request failed', {
      status: response.status,
      code: error?.code,
      subcode: error?.error_subcode,
      type: error?.type,
      trace: error?.fbtrace_id
    });
    throw new SafeError(
      error?.code ? `META_${error.code}` : 'META_API_ERROR',
      'O Instagram recusou a operação',
      response.status >= 400 && response.status < 500 ? 409 : 502
    );
  }
  return body as T;
};

export const jsonResponse = (body: unknown, status = 200): Response => Response.json(body, {
  status,
  headers: {
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff'
  }
});

export const errorResponse = (error: unknown): Response => {
  if (error instanceof SafeError) {
    return jsonResponse({ ok: false, error: error.code, message: error.message }, error.status);
  }
  console.error('Instagram function failed', error instanceof Error ? error.name : 'UnknownError');
  return jsonResponse({ ok: false, error: 'INTERNAL_ERROR', message: 'Erro interno' }, 500);
};

export const constantTimeEqual = (left: string, right: string): boolean => {
  const encoder = new TextEncoder();
  const a = encoder.encode(left);
  const b = encoder.encode(right);
  let mismatch = a.length ^ b.length;
  const length = Math.max(a.length, b.length);
  for (let index = 0; index < length; index += 1) {
    mismatch |= (a[index % Math.max(a.length, 1)] ?? 0) ^ (b[index % Math.max(b.length, 1)] ?? 0);
  }
  return mismatch === 0;
};
