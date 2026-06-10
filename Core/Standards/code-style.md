# code-style.md
<!-- FoundLab ATI · v1.0 · 2026-04-17 -->

## Indentação e Formatação

- **2 espaços** — sem tabs, sem 4 espaços, sem exceção.
- **Prettier** como formatter autoritativo. Configuração canônica em `.prettierrc`:

```json
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2,
  "arrowParens": "always"
}
```

- Linha em branco obrigatória entre blocos lógicos dentro de uma função.
- Uma exportação por arquivo como regra geral. Exceção permitida apenas para tipos auxiliares do mesmo módulo.
- `import` sempre no topo, agrupados: (1) Node built-ins, (2) dependências externas, (3) imports internos `@/`. Separar grupos com linha em branco.

---

## TypeScript — Restrições

```typescript
// PROIBIDO — any implícito
function process(data: any) { ... }

// CORRETO — tipo explícito ou genérico constrainado
function process<T extends VeritasEvent>(data: T): Promise<SealedRecord<T>> { ... }
```

- `strict: true` no `tsconfig.json` — sem exceções.
- `noUncheckedIndexedAccess: true` — acesso a array/objeto sempre verificado.
- `exactOptionalPropertyTypes: true` — `undefined` não é equivalente a ausência de propriedade.
- Proibido: `as unknown as X` (double cast). Se necessário, expor o gap como comentário `// TODO(CG-XXX)`.
- `readonly` em arrays e objetos que não devem ser mutados após construção.

---

## Nomenclatura de Variáveis e Funções

### Funções

```typescript
// Ação explícita no nome — evitar verbos genéricos (process, handle, do)
async function sealVeritasEvent(event: RawEvent): Promise<SealedRecord> { ... }
async function evaluatePolicySnapshot(payload: EncryptedPayload): Promise<PolicyResult> { ... }
async function emitChainEntry(entry: ChainEntry, spannerTx: Transaction): Promise<void> { ... }

// Boolean: prefixo is/has/can/should
function isOfacMatch(entityId: string): boolean { ... }
function hasValidChainHead(tip: ChainTip): boolean { ... }
```

### Constantes e Configuração

```typescript
// Constantes de módulo: SCREAMING_SNAKE_CASE
const CHAIN_TIP_QUERY = `SELECT lock_hash FROM veritas_chain ORDER BY index DESC LIMIT 1`;
const MAX_INFERENCE_LATENCY_MS = 50;

// Configurações de runtime: objeto tipado, nunca variáveis soltas
const rexGuardConfig = {
  maxPayloadBytes: 4 * 1024 * 1024,
  policyTimeoutMs: 30_000,
  failClosed: true, // nunca alterar para false
} as const satisfies RexGuardConfig;
```

### Interfaces e Types

```typescript
// Interfaces para contratos de domínio (VeritasEvent, ChainEntry, PolicyResult)
// Types para unions, aliases e mapeamentos

interface VeritasEvent {
  readonly index: number;
  readonly ts: Timestamp;
  readonly actor: string;
  readonly action: EventAction;
  readonly artifact: string;
  readonly prevHash: string; // nunca deixar vazio — CG-002
}

type BurnDecision = 'APPROVE' | 'FLAG_REVIEW' | 'FREEZE_ASSETS' | 'BURN_IMMEDIATE';
```

---

## Organização de Arquivos

### Estrutura interna de cada arquivo

```typescript
// 1. Imports (agrupados, na ordem: built-in → external → internal)
import { createHash } from 'node:crypto';
import { Spanner } from '@google-cloud/spanner';
import { type VeritasEvent, type SealedRecord } from '@/types/veritas.js';

// 2. Constantes de módulo
const HASH_ALGORITHM = 'sha256' as const;

// 3. Tipos locais (se não exportados)
type InternalState = { ... };

// 4. Implementação
export async function sealVeritasEvent(...): Promise<SealedRecord> { ... }

// 5. Exports nomeados no final (nunca default export em módulos de domínio)
export { sealVeritasEvent };
```

### Tamanho de arquivo

- Máximo indicativo: 300 linhas. Acima disso, decompor em submódulos.
- Exceção documentada permitida para: schemas Terraform gerados, vetores de auditoria, mocks de integração.

---

## Aritmética de Ponto Fixo

Qualquer cálculo envolvendo score, valor financeiro ou métrica de risco:

```typescript
// PROIBIDO — ponto flutuante nativo em scores e valores financeiros
const score = 0.1 + 0.2; // 0.30000000000000004

// CORRETO — rust_decimal via WASM ou Decimal.js com escala 10^8
import Decimal from 'decimal.js';
Decimal.set({ precision: 28, rounding: Decimal.ROUND_HALF_EVEN });

const score = new Decimal(rawScore).toDecimalPlaces(8);
```

Referência: RFC-F2F-003 — LOG2_LUT_LERP_4096, todos os 27 test vectors.

---

## Async e Concorrência

- Proibido `Promise.all` sem timeout explícito em chamadas GCP. Usar `Promise.race` com `AbortSignal`.
- Streams SSE: nunca bufferizar resposta inteira em memória. GCP API Gateway removido — não reintroduzir buffering.
- `await` em loops (`for await`) preferível a `Promise.all` quando a ordem importa para o hash chain.

---

## Comentários

- Comentários explicam **por quê**, não **o quê**. O código diz o quê.
- `// TODO(CG-XXX):` para gaps rastreados. Nenhum TODO sem referência a gap ou issue.
- `// INVARIANT:` para asserções de segurança críticas que não podem ser removidas.
- JSDoc obrigatório em todas as funções exportadas de módulos de domínio (`core/`, `compliance/`).

```typescript
/**
 * Emite uma entrada na VeritasChain via Cloud Spanner TrueTime.
 * INVARIANT: prevHash deve ser lido do BigQuery WORM neste emit — nunca de state de classe.
 * @see ADR-F2F-004
 */
export async function emitChainEntry(
  entry: ChainEntry,
  spannerTx: Transaction,
): Promise<SealedRecord> { ... }
```

---

*FoundLab · code-style.md v1.0 · 2026-04-17*
