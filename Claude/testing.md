# testing.md
<!-- FoundLab ATI · v1.0 · 2026-04-17 -->

## Framework

**Vitest** — único framework de teste. Proibido Jest, Mocha, ou qualquer outro.

```bash
npm test                   # vitest run (todos os testes, sem watch)
npm run test:coverage      # vitest run --coverage --reporter=v8
npm run test:watch         # vitest watch (desenvolvimento local apenas)
npm run test:integration   # vitest run --config vitest.integration.config.ts
npm run audit:vectors      # node scripts/run-audit-vectors.ts (gate CG-002)
```

Configuração canônica em `vitest.config.ts`:

```typescript
export default defineConfig({
  test: {
    globals: false,          // imports explícitos obrigatórios — sem globals implícitos
    environment: 'node',
    coverage: {
      provider: 'v8',
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
      exclude: [
        'src/types/**',
        'terraform/**',
        '**/*.d.ts',
        '**/index.ts',       // re-exports não contam para cobertura
      ],
    },
  },
});
```

---

## Cobertura Mínima

| Módulo | Linhas | Funções | Branches |
|--------|--------|---------|----------|
| `core/` (VeritasChain, UmbrellaKMS, BurnEngine) | **90%** | **90%** | **85%** |
| `proxy/` (REX Guard pipeline) | **85%** | **85%** | **80%** |
| `compliance/` (Spezzatura Engine) | **90%** | **90%** | **85%** |
| `api/` (Fastify routes) | **75%** | **75%** | **70%** |
| `infra/` (clientes GCP) | **70%** | **70%** | **65%** |

Cobertura abaixo do mínimo em `core/` e `compliance/` bloqueia merge. Sem exceção.

---

## Nomenclatura de Testes

```typescript
// Padrão: describe('unidade') → it('contexto + comportamento esperado')
// Proibido: it('test 1'), it('funciona'), it('deve funcionar')

describe('VeritasChain.emitChainEntry', () => {
  it('rejeita entrada quando prevHash está vazio', async () => { ... });
  it('lê chain_tip do BigQuery WORM, nunca de state de classe', async () => { ... });
  it('falha com SpannerUnavailableError quando Spanner está down (fail-closed)', async () => { ... });
});

describe('BurnEngine.evaluate', () => {
  it('retorna BURN_IMMEDIATE para match OFAC antes de calcular Spezzatura score', async () => { ... });
  it('retorna FREEZE_ASSETS quando final_score < threshold configurado', async () => { ... });
  it('avalia TERROR gate antes de qualquer scoring', async () => { ... });
});

describe('UmbrellaKMS.shredKey', () => {
  it('chama cryptoKeyVersions.destroy() na API do Cloud KMS — não simula', async () => { ... });
  it('falha explicitamente quando destroy retorna status != DESTROYED', async () => { ... });
});
```

---

## Vetores de Auditoria (Gate CG-002)

`test/audit/audit_vectors_v1.json` contém os vetores normativos que validam conformidade BCB 538.
Este arquivo é gerado e versionado — nunca editado manualmente.

```typescript
// test/audit/run-audit-vectors.test.ts
describe('audit_vectors_v1.json — gate BCB 538/2025', () => {
  const vectors = JSON.parse(readFileSync('test/audit/audit_vectors_v1.json', 'utf-8'));

  for (const vector of vectors) {
    it(`vetor ${vector.id}: ${vector.description}`, async () => {
      const result = await executeVector(vector);
      expect(result.hash).toBe(vector.expectedHash);
      expect(result.decision).toBe(vector.expectedDecision);
      expect(result.policySnapshotHash).not.toBe('hardcoded'); // CG-001 guard
    });
  }
});
```

Se qualquer vetor falhar, o pipeline CI bloqueia o merge. Não existe override.

---

## Testes de Segurança Obrigatórios

Estes testes existem especificamente para garantir que os CGs não regridam:

```typescript
// test/security/cg-regression.test.ts

describe('CG-001 — policy_snapshot_hash dinâmico', () => {
  it('hash da política muda quando a política muda', async () => {
    const hash1 = await computePolicySnapshotHash(policyV1);
    const hash2 = await computePolicySnapshotHash(policyV2);
    expect(hash1).not.toBe(hash2);
    expect(hash1).not.toBe('hardcoded_placeholder'); // regressão explícita
  });
});

describe('CG-003 — crypto-shredding real', () => {
  it('shredKey invoca cryptoKeyVersions.destroy() na API KMS', async () => {
    const destroySpy = vi.spyOn(kmsClient, 'destroyCryptoKeyVersion');
    await umbrellaKMS.shredKey(testKeyId);
    expect(destroySpy).toHaveBeenCalledOnce();
    expect(destroySpy).toHaveBeenCalledWith(
      expect.objectContaining({ name: expect.stringContaining(testKeyId) }),
    );
  });
});

describe('JWT — ausência de localStorage', () => {
  it('authService não persiste token em localStorage', () => {
    // Verificação estática: grep no authService.ts não retorna localStorage
    const source = readFileSync('src/api/authService.ts', 'utf-8');
    expect(source).not.toMatch(/localStorage/);
    expect(source).not.toMatch(/sessionStorage/);
  });
});
```

---

## Mocks e Stubs

### GCP Clients

Nunca chamar APIs GCP reais em testes unitários. Usar sempre emuladores ou mocks explícitos:

```typescript
// src/infra/__mocks__/spanner.ts
export const mockSpannerClient = {
  runTransaction: vi.fn(),
  table: vi.fn(() => ({ read: vi.fn(), insert: vi.fn() })),
};

vi.mock('@google-cloud/spanner', () => ({
  Spanner: vi.fn(() => mockSpannerClient),
}));
```

### Zero-Persistence

Mocks que testam destruição de dados devem verificar que `gc.collect()` equivalente foi chamado:

```typescript
it('OpticalSieve destrói buffer após OCR', async () => {
  const deleteSpy = vi.spyOn(global, 'Buffer').mockImplementation(...);
  await opticalSieve.process(testImageBuffer);
  // Verificar que nenhuma referência ao buffer sobrevive no escopo
  expect(leakDetector.hasLeak()).toBe(false);
});
```

---

## Testes de Integração

Rodam contra emuladores GCP locais (`gcloud beta emulators`) ou projeto `foundlab-ati` em staging.

```bash
# Subir emuladores
npm run emulators:start   # Spanner + BigQuery + KMS emulator

# Rodar integração
npm run test:integration
```

Testes de integração não rodam no CI padrão (PR). Rodam apenas em pipelines de staging e pré-release.

---

## Proibições

- Proibido: `test.skip` ou `it.skip` sem comentário `// TODO(CG-XXX)` e issue rastreável.
- Proibido: `vi.mock` de módulos de domínio core em testes de integração.
- Proibido: `console.log` em testes — usar `vi.spyOn(console, 'error')` se necessário.
- Proibido: testes que passam sem asserção (`expect`). Vitest detecta isso — não ignorar.
- Proibido: dados reais de cliente em fixtures. Usar geradores sintéticos com `@faker-js/faker`.

---

*FoundLab · testing.md v1.0 · 2026-04-17*
