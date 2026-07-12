import {
  INSTAGRAM_SCOPES,
  InstagramAccount,
  SafeError,
  metaJson,
  parseInstagramAccount,
  requireEnv,
  saveCredential
} from '../_shared/instagram.ts';

const STATE_COOKIE = 'scp_ig_oauth_state';
const stateCookieName = (account: InstagramAccount): string => `${STATE_COOKIE}_${account}`;

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

const stateCookie = (account: InstagramAccount, state: string, redirectUri: string): string => [
  `${stateCookieName(account)}=${encodeURIComponent(state)}`,
  `Path=${cookiePath(redirectUri)}`,
  'Max-Age=600',
  'HttpOnly',
  'Secure',
  'SameSite=Lax'
].join('; ');

const clearStateCookie = (account: InstagramAccount, redirectUri: string): string => [
  `${stateCookieName(account)}=`,
  `Path=${cookiePath(redirectUri)}`,
  'Max-Age=0',
  'HttpOnly',
  'Secure',
  'SameSite=Lax'
].join('; ');

const html = (title: string, message: string, status = 200, cookie?: string): Response => {
  const headers = new Headers({
    'Content-Type': 'text/html',
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
type InstagramProfileResponse = { id?: string; user_id?: string | number; username?: string };

const confirmation = (account: InstagramAccount, redirectUri: string): Response => {
  const label = account === 'smart_home' ? 'Smart Home' : 'Smart Color Print';
  // O request.url interno do Edge Runtime não preserva necessariamente
  // /functions/v1. O redirect URI é a origem pública canónica já validada.
  const next = new URL(redirectUri);
  next.searchParams.set('account', account);
  next.searchParams.set('confirm', account);
  return html(
    `Ligar ${label}`,
    `Confirme que vai autorizar o Instagram profissional da ${label}. Se o Instagram mostrar outra conta, cancele e mude de conta antes de continuar. <a href="${next.toString()}" style="display:inline-block;margin-top:18px;color:#111;background:#d7ff3f;padding:12px 18px;border-radius:10px;text-decoration:none;font-weight:700">Continuar com ${label}</a>`
  );
};

const startAuthorization = (account: InstagramAccount, redirectUri: string): Response => {
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
      'Set-Cookie': stateCookie(account, state, redirectUri),
      'Cache-Control': 'no-store',
      'Referrer-Policy': 'no-referrer'
    }
  });
};

const loadInstagramProfile = async (token: string): Promise<{ userId: string; username: string }> => {
  const version = Deno.env.get('INSTAGRAM_GRAPH_API_VERSION')?.trim() || 'v25.0';
  const url = new URL(`https://graph.instagram.com/${version}/me`);
  url.searchParams.set('fields', 'user_id,username');
  const profile = await metaJson<InstagramProfileResponse>(url, {
    headers: { Authorization: `Bearer ${token}` }
  });
  const userId = profile.user_id ?? profile.id;
  if (!userId || !profile.username) {
    throw new SafeError('INSTAGRAM_PROFILE_MISSING', 'Não foi possível confirmar a conta Instagram autorizada', 502);
  }
  return { userId: String(userId), username: profile.username };
};

const assertExpectedUsername = (account: InstagramAccount, username: string): void => {
  const envName = account === 'smart_home'
    ? 'INSTAGRAM_EXPECTED_USERNAME_SMART_HOME'
    : 'INSTAGRAM_EXPECTED_USERNAME_SMART_COLORPRINT';
  const expected = requireEnv(envName).replace(/^@/, '').toLowerCase();
  if (username.replace(/^@/, '').toLowerCase() !== expected) {
    throw new SafeError(
      'INSTAGRAM_ACCOUNT_MISMATCH',
      `A conta autorizada não corresponde a ${account}. A credencial anterior foi preservada.`,
      409
    );
  }
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
      return html('Ligação cancelada', 'O Instagram não autorizou a ligação. Pode tentar novamente.', 400);
    }
    if (!code) {
      const account = parseInstagramAccount(requestUrl.searchParams.get('account'));
      if (requestUrl.searchParams.get('confirm') !== account) return confirmation(account, redirectUri);
      return startAuthorization(account, redirectUri);
    }

    const matchingAccounts = (['smart_colorprint', 'smart_home'] as InstagramAccount[])
      .filter((account) => cookieValue(request, stateCookieName(account)) === returnedState);
    if (!returnedState || matchingAccounts.length !== 1) {
      throw new SafeError('INVALID_OAUTH_STATE', 'A sessão de autorização expirou. Inicie a ligação novamente.', 400);
    }
    const account = matchingAccounts[0];

    const token = await exchangeAuthorizationCode(code, redirectUri);
    const profile = await loadInstagramProfile(token.accessToken);
    assertExpectedUsername(account, profile.username);
    await saveCredential({
      account,
      instagramUserId: profile.userId || token.userId,
      username: profile.username,
      accessToken: token.accessToken,
      expiresAt: token.expiresAt
    });

    return html(
      'Instagram ligado',
      `${account} foi autorizada com sucesso. A credencial ficou cifrada e isolada no servidor; pode fechar esta janela.`,
      200,
      clearStateCookie(account, redirectUri)
    );
  } catch (error) {
    const status = error instanceof SafeError ? error.status : 500;
    const message = error instanceof SafeError ? error.message : 'Ocorreu um erro interno durante a ligação.';
    if (!(error instanceof SafeError)) console.error('Instagram OAuth failed', error instanceof Error ? error.name : 'UnknownError');
    return html('Não foi possível ligar', message, status);
  }
});
