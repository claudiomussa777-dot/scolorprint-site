#!/usr/bin/env node

import { execFileSync } from 'node:child_process';
import dns from 'node:dns/promises';
import { readFile } from 'node:fs/promises';

const ACCOUNT = 'smart_colorprint';
const KEYCHAIN_SERVICE = 'scolorprint-instagram-publisher-secret';
const KEYCHAIN_ACCOUNT = 'claudiomussa';
const DEFAULT_ENDPOINT = 'https://ljhylqpsfvmjhvhjkokk.supabase.co/functions/v1/instagram-publish';
const ALLOWED_ENDPOINTS = new Set([DEFAULT_ENDPOINT]);
const ALLOWED_MEDIA_HOSTS = new Set(['scolorprint.com', 'www.scolorprint.com']);

const args = parseArgs(process.argv.slice(2));
const imageUrls = await loadImageUrls(args);
const caption = await loadCaption(args['caption-file']);
const idempotencyKey = validateIdempotencyKey(args['idempotency-key']);
const endpoint = validateEndpoint(args.endpoint || DEFAULT_ENDPOINT);

await validatePublicImages(imageUrls);

if (args['dry-run']) {
  console.log(JSON.stringify({
    ok: true,
    status: 'validated',
    dry_run: true,
    account: ACCOUNT,
    image_count: imageUrls.length,
    caption_length: caption.length,
    idempotency_key: idempotencyKey,
    endpoint_host: endpoint.hostname,
  }));
  process.exit(0);
}

await assertEndpointReachable(endpoint);
const publisherSecret = readPublisherSecret();
const body = JSON.stringify({
  account: ACCOUNT,
  image_urls: imageUrls,
  caption,
  idempotency_key: idempotencyKey,
});

const result = await publishWithSafeRetry(endpoint, publisherSecret, body);
console.log(JSON.stringify(result));
if (!result.ok || result.status !== 'published') process.exitCode = 1;

function parseArgs(values) {
  const parsed = { 'image-url': [] };
  for (let index = 0; index < values.length; index += 1) {
    const value = values[index];
    if (!value.startsWith('--')) throw new Error(`Argumento inesperado: ${value}`);

    const name = value.slice(2);
    if (name === 'dry-run') {
      parsed[name] = true;
      continue;
    }

    const next = values[index + 1];
    if (!next || next.startsWith('--')) throw new Error(`Falta o valor de --${name}`);
    index += 1;

    if (name === 'image-url') parsed[name].push(next);
    else if (parsed[name] !== undefined) throw new Error(`Argumento repetido: --${name}`);
    else parsed[name] = next;
  }
  return parsed;
}

async function loadImageUrls(parsed) {
  const urls = [...parsed['image-url']];
  if (parsed['image-urls-file']) {
    const fileContents = await readFile(parsed['image-urls-file'], 'utf8');
    urls.push(...fileContents.split(/\r?\n/).map((line) => line.trim()).filter(Boolean));
  }

  if (urls.length < 1 || urls.length > 10) {
    throw new Error('Forneça entre 1 e 10 imagens com --image-url ou --image-urls-file');
  }

  return urls.map((value) => {
    let url;
    try {
      url = new URL(value);
    } catch {
      throw new Error('Ligação de imagem inválida');
    }
    if (
      url.protocol !== 'https:' ||
      url.username ||
      url.password ||
      !ALLOWED_MEDIA_HOSTS.has(url.hostname.toLowerCase())
    ) {
      throw new Error('As imagens devem usar HTTPS em scolorprint.com');
    }
    return url.toString();
  });
}

async function loadCaption(filePath) {
  if (!filePath) throw new Error('Falta --caption-file');
  const value = (await readFile(filePath, 'utf8')).trim();
  if (!value || value.length > 2200) throw new Error('A legenda deve ter entre 1 e 2200 caracteres');
  return value;
}

function validateIdempotencyKey(value) {
  if (!value || !/^[A-Za-z0-9][A-Za-z0-9._:-]{0,119}$/.test(value)) {
    throw new Error('Chave de idempotência inválida');
  }
  return value;
}

function validateEndpoint(value) {
  let endpoint;
  try {
    endpoint = new URL(value);
  } catch {
    throw new Error('Endpoint de publicação inválido');
  }

  if (
    endpoint.protocol !== 'https:' ||
    endpoint.username ||
    endpoint.password ||
    endpoint.search ||
    endpoint.hash ||
    !ALLOWED_ENDPOINTS.has(endpoint.toString())
  ) {
    throw new Error('Endpoint de publicação não autorizado');
  }
  return endpoint;
}

async function validatePublicImages(urls) {
  for (const url of urls) {
    let response;
    try {
      response = await fetch(url, {
        method: 'HEAD',
        redirect: 'error',
        signal: AbortSignal.timeout(20_000),
      });
    } catch {
      throw new Error('Não foi possível validar uma imagem pública');
    }
    if (!response.ok || !response.headers.get('content-type')?.toLowerCase().startsWith('image/')) {
      throw new Error('Uma imagem pública não respondeu como imagem');
    }
  }
}

async function assertEndpointReachable(endpoint) {
  try {
    await dns.lookup(endpoint.hostname);
  } catch (error) {
    const code = error?.code || error?.cause?.code;
    if (code === 'ENOTFOUND') {
      throw new Error('O endpoint seguro de publicação está indisponível por erro DNS');
    }
    throw new Error(`O endpoint seguro de publicação está indisponível${code ? ` (${code})` : ''}`);
  }
}

function readPublisherSecret() {
  try {
    return execFileSync(
      '/usr/bin/security',
      ['find-generic-password', '-w', '-s', KEYCHAIN_SERVICE, '-a', KEYCHAIN_ACCOUNT],
      { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }
    ).trim();
  } catch {
    throw new Error('Não foi possível ler a credencial segura de publicação');
  }
}

async function publishWithSafeRetry(endpoint, secret, body) {
  let lastResult;
  for (let attempt = 0; attempt < 2; attempt += 1) {
    lastResult = await publishOnce(endpoint, secret, body);
    if (lastResult.ok && lastResult.status === 'published') return lastResult;
    if (lastResult.status !== 'processing') return lastResult;
    if (attempt === 0) await new Promise((resolve) => setTimeout(resolve, 5_000));
  }
  return lastResult;
}

async function publishOnce(endpoint, secret, body) {
  let response;
  try {
    response = await fetch(endpoint, {
      method: 'POST',
      redirect: 'error',
      headers: {
        'content-type': 'application/json',
        'x-publisher-secret': secret,
      },
      body,
      signal: AbortSignal.timeout(90_000),
    });
  } catch (error) {
    const code = error?.cause?.code || error?.code;
    throw new Error(`Falha ao contactar o canal seguro de publicação${code ? ` (${code})` : ''}`);
  }

  const payload = await response.json().catch(() => ({}));
  return {
    ok: payload.ok === true,
    account: payload.account,
    status: payload.status,
    media_id: payload.media_id,
    duplicate: payload.duplicate === true,
    error: payload.error,
    message: payload.message,
  };
}
