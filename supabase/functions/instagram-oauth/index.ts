import {
  INSTAGRAM_SCOPES,
  SafeError,
  metaJson,
  requireEnv,
  saveCredential
} from '../_shared/instagram.ts';

const STATE_COOKIE = 'scp_ig_oauth_state';

const randomState = (): string => {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replaceAll('+', '-').replaceAll('/', '_').replaceAll('=', '');
};

const cookieValue = (request: Request, name: string): string | null => {
  const cookieHeader = request.headers.get('cookie') ?? '';
  for (const entry of cookieHeader.split(';')) {
    const [key, ...rest] = entry.trim().split('=');
    if (key === name) return decodeURIComponent(rest.join('='));
  }
  return null;
};

const cookiePath = (redirectUri: string): string => {
  const path = new URL(redirectUri).pathname;
  return path || '/';
};

const stateCookie = (state: string, redirectUri: string): string => [
  `${STATE_COOKIE}=${encodeURIComponent(state)}`,
  `Path=${cookiePath(redirectUri)}`,
  'Max-Age=600',
  'HttpOnly',
  'Secure',
  'SameSite=Lax'
].join('; ');

const clearStateCookie = (redirectUri: string): string => [
  `${STATE_COOKIE}=`,
  `Path=${cookiePath(redirectUri)}`,
  'Max-Age=0',
  'HttpOnly',
  'Secure',
  'SameSite=Lax'
].join('; ');

const html = (title: string, message: string, status = 200, cookie?: string): Response => {
  const headers = new Headers({
    'Content-Type': 'text/html; charset=utf-8',
    'Cache-Control': 'no-store',
    'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'",
    'Referrer-Policy': 'no-referrer',
    'X-Content-Type-Options': 'nosniff'
  });
  if (cookie) headers.set('Set-Cookie', cookie);
  return new Response(`<!doctype html>
<html lang="pt"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${title}</title><style>
body{margin:0;min-height:100vh;display:grid;place-items:center;background:#11110f;color:#fff;font:16px/1.55 system-ui,sans-serif}
main{max-width:560px;margin:24px;padding:34px;border:1px solid #34342e;border-radius:20px;background:#191916}
strong{display:block;margin-bottom:10px;color:#d7ff3f;font-size:24px}p{margin:0;color:#deded4}
</style></head><body><main><strong>${title}</strong><p>${message}</p></main></body></html>`, { status, headers });
};

type ShortTokenResponse = { access_token: string; user_id: number | string };
type LongTokenResponse = { access_token: string; token_type?: string; expires_in?: number };

const startAuthorization = (redirectUri: string): Response => {
  const state = randomState();
  const authorizationUrl = new URL('https://www.instagram.com/oauth/authorize/');
  authorizationUrl.search = new URLSearchParams({
    client_id: requireEnv('INSTAGRAM_APP_ID'),
    redirect_uri: redirectUri,
    response_type: 'code',
    scope: INSTAGRAM_SCOPES.join(','),
    state
  }).toString();

  return new Response(null, {
    status: 302,
    headers: {
      Location: authorizationUrl.toString(),
      'Set-Cookie': stateCookie(state, redirectUri),
      'Cache-Control': 'no-store',
      'Referrer-Policy': 'no-referrer'
    }
  });
};

const exchangeAuthorizationCode = async (
  code: string,
  redirectUri: string
): Promise<{ userId: string; accessToken: string; expiresAt: string | null }> => {
  const appId = requireEnv('INSTAGRAM_APP_ID');
  const appSecret = requireEnv('INSTAGRAM_APP_SECRET');
  const body = new FormData();
  body.set('client_id', appId);
  body.set('client_secret', appSecret);
  body.set('grant_type', 'authorization_code');
  body.set('redirect_uri', redirectUri);
  body.set('code', code);

  const shortToken = await metaJson<ShortTokenResponse>('https://api.instagram.com/oauth/access_token', {
    method: 'POST',
    body
  });
  if (!shortToken.access_token || !shortToken.user_id) {
    throw new SafeError('INVALID_TOKEN_RESPONSE', 'A Meta devolveu uma resposta incompleta', 502);
  }

  const exchangeUrl = new URL('https://graph.instagram.com/access_token');
  exchangeUrl.search = new URLSearchParams({
    grant_type: 'ig_exchange_token',
    client_secret: appSecret,
    access_token: shortToken.access_token
  }).toString();
  const longToken = await metaJson<LongTokenResponse>(exchangeUrl);
  if (!longToken.access_token) {
    throw new SafeError('INVALID_LONG_TOKEN_RESPONSE', 'Não foi possível obter a credencial de longa duração', 502);
  }

  const expiresIn = Number(longToken.expires_in);
  const expiresAt = Number.isFinite(expiresIn) && expiresIn > 0
    ? new Date(Date.now() + expiresIn * 1000).toISOString()
    : null;
  return {
    userId: String(shortToken.user_id),
    accessToken: longToken.access_token,
    expiresAt
  };
};

Deno.serve(async (request: Request) => {
  let redirectUri = '';
  try {
    if (request.method !== 'GET') return html('Método inválido', 'Use esta ligação diretamente no navegador.', 405);
    redirectUri = requireEnv('INSTAGRAM_OAUTH_REDIRECT_URI');
    const requestUrl = new URL(request.url);
    const code = requestUrl.searchParams.get('code');
    const returnedState = requestUrl.searchParams.get('state');
    const oauthError = requestUrl.searchParams.get('error');

    if (oauthError) {
      return html('Ligação cancelada', 'O Instagram não autorizou a ligação. Pode tentar novamente.', 400, clearStateCookie(redirectUri));
    }
    if (!code) return startAuthorization(redirectUri);

    const expectedState = cookieValue(request, STATE_COOKIE);
    if (!expectedState || !returnedState || expectedState !== returnedState) {
      throw new SafeError('INVALID_OAUTH_STATE', 'A sessão de autorização expirou. Inicie a ligação novamente.', 400);
    }

    const token = await exchangeAuthorizationCode(code, redirectUri);
    await saveCredential({
      instagramUserId: token.userId,
      accessToken: token.accessToken,
      expiresAt: token.expiresAt
    });

    return html(
      'Instagram ligado',
      'A conta foi autorizada com sucesso. A credencial ficou cifrada no servidor; pode fechar esta janela.',
      200,
      clearStateCookie(redirectUri)
    );
  } catch (error) {
    const status = error instanceof SafeError ? error.status : 500;
    const message = error instanceof SafeError ? error.message : 'Ocorreu um erro interno durante a ligação.';
    if (!(error instanceof SafeError)) console.error('Instagram OAuth failed', error instanceof Error ? error.name : 'UnknownError');
    return html('Não foi possível ligar', message, status, redirectUri ? clearStateCookie(redirectUri) : undefined);
  }
});
