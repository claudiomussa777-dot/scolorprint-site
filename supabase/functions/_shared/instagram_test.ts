import {
  INSTAGRAM_ACCOUNTS,
  SafeError,
  credentialQueryPath,
  parseInstagramAccount,
  publishJobQueryPath
} from './instagram.ts';

const assertEquals = (actual: unknown, expected: unknown): void => {
  if (actual !== expected) throw new Error(`Expected ${String(expected)}, received ${String(actual)}`);
};

Deno.test('accepts only the two fixed Instagram account identifiers', () => {
  assertEquals(INSTAGRAM_ACCOUNTS.length, 2);
  assertEquals(parseInstagramAccount('smart_colorprint'), 'smart_colorprint');
  assertEquals(parseInstagramAccount('smart_home'), 'smart_home');
});

Deno.test('rejects a missing or unknown account identifier', () => {
  for (const value of [undefined, null, '', 'smart-home', 'smart_color_print']) {
    try {
      parseInstagramAccount(value);
      throw new Error('Expected parseInstagramAccount to reject the value');
    } catch (error) {
      if (!(error instanceof SafeError) || error.code !== 'INVALID_INSTAGRAM_ACCOUNT') throw error;
    }
  }
});

Deno.test('credential lookup is scoped to the requested account and never ordered by recency', () => {
  const colorPrintPath = credentialQueryPath('smart_colorprint', 'account,instagram_user_id');
  const smartHomePath = credentialQueryPath('smart_home', 'account,instagram_user_id');
  assertEquals(colorPrintPath.includes('account=eq.smart_colorprint'), true);
  assertEquals(smartHomePath.includes('account=eq.smart_home'), true);
  assertEquals(colorPrintPath.includes('order=updated_at'), false);
  assertEquals(smartHomePath.includes('order=updated_at'), false);
  assertEquals(colorPrintPath === smartHomePath, false);
});

Deno.test('idempotency lookup is isolated by account plus key', () => {
  const key = 'campaign-001';
  const colorPrintPath = publishJobQueryPath('smart_colorprint', key);
  const smartHomePath = publishJobQueryPath('smart_home', key);
  assertEquals(colorPrintPath.includes('account=eq.smart_colorprint&idempotency_key=eq.campaign-001'), true);
  assertEquals(smartHomePath.includes('account=eq.smart_home&idempotency_key=eq.campaign-001'), true);
  assertEquals(colorPrintPath === smartHomePath, false);
});
