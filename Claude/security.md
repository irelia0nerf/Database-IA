# security.md
<!-- FoundLab ATI · v1.0 · 2026-04-17 -->
<!-- Referências normativas: BCB 538/2025, LGPD Arts. 46-49, DORA Arts. 28-30, EU AI Act Arts. 13-17 -->

## Princípio Central

Zero-persistence é física, não política. Dado sensível que toca disco, Cloud Storage, ou BigQuery (exceto hash) é falha de arquitetura, não de configuração.

---

## Validação de Entrada — Obrigatória

Todo payload que entra no REX Guard pipeline deve passar pela camada de validação antes de qualquer operação:

```typescript
import { z } from 'zod';

// Esquema de entrada obrigatório — Zod com .strict() para rejeitar campos desconhecidos
const inferenceRequestSchema = z.object({
  sessionId: z.string().uuid(),
  actorId: z.string().min(1).max(128),
  payload: z.string().max(4 * 1024 * 1024), // 4MB hard limit
  policyVersion: z.string().regex(/^v\d+\.\d+$/),
}).strict();

// Validação falha fechada — qualquer erro bloqueia, nunca passa adiante
export function validateInferenceRequest(raw: unknown): InferenceRequest {
  const result = inferenceRequestSchema.safeParse(raw);
  if (!result.success) {
    throw new ValidationError('INVALID_INFERENCE_REQUEST', result.error.flatten());
  }
  return result.data;
}
```

### Regras adicionais

- Tamanho máximo de payload: 4MB. Rejeitar com 413 antes de deserializar.
- Content-Type obrigatório em todas as rotas POST/PUT. Rejeitar 415 se ausente ou inválido.
- Nenhum campo do schema pode ser `any` ou `unknown` sem validação explícita posterior.
- OFAC/SANCTION/TERROR verificados antes de qualquer operação de scoring ou inferência — não é validação de entrada genérica, é gate de segurança nacional. Ordem de execução é invariante.

---

## Gestão de Secrets

### Regras absolutas

- **Proibido** hardcodar qualquer secret, chave, token, connection string, ou credencial no código-fonte.
- **Proibido** commitar arquivos `.env` com valores reais. `.env.example` com placeholders é permitido.
- **Proibido** logar secrets, mesmo parcialmente (ex: primeiros 4 chars de API key).
- **Proibido** passar secrets via variáveis de ambiente em Cloud Run sem Secret Manager como fonte.

### Padrão obrigatório — GCP Secret Manager

```typescript
import { SecretManagerServiceClient } from '@google-cloud/secret-manager';

const client = new SecretManagerServiceClient();

export async function loadSecret(secretId: string): Promise<string> {
  const [version] = await client.accessSecretVersion({
    name: `projects/${PROJECT_ID}/secrets/${secretId}/versions/latest`,
  });
  const payload = version.payload?.data;
  if (!payload) {
    throw new SecretNotFoundError(secretId);
  }
  return Buffer.from(payload as Uint8Array).toString('utf-8');
}
```

### Rotação

- Qualquer secret exposto em PR histórico (mesmo após rebase/squash): rotacionar imediatamente.
- Firebase API keys expostas em PRs históricos: rotar + verificar regras de security no Firebase Console.
- Rotação documentada em `docs/secret-rotation-log.md` com timestamp e responsável.

---

## UmbrellaKMS — Envelope Encryption

```typescript
// Algoritmo atual: AES-128-Fernet
// Algoritmo alvo: AES-256-GCM (PENDENTE — ver RFC-F2F-005)
// NIST SP 800-131A: AES-256 obrigatório para novos sistemas desde 2015

// Estrutura de envelope obrigatória
interface EncryptedEnvelope {
  ciphertext: Buffer;
  encryptedDek: Buffer;      // DEK cifrado com KEK do Cloud KMS
  kekVersion: string;        // projects/.../cryptoKeyVersions/N
  algorithm: 'AES-128-GCM' | 'AES-256-GCM';
  crc32c: number;            // integridade do ciphertext
  ts: number;                // timestamp de criação (Unix ms)
}

// Crypto-shredding real — CG-003
// shredKey() DEVE chamar cryptoKeyVersions.destroy() — não simular, não logar
export async function shredKey(keyVersionName: string): Promise<void> {
  const [destroyedVersion] = await kmsClient.destroyCryptoKeyVersion({
    name: keyVersionName,
  });
  if (destroyedVersion.state !== 'DESTROYED') {
    throw new CryptoShredError(`Key ${keyVersionName} não foi destruída: ${destroyedVersion.state}`);
  }
  // Apenas após confirmação de DESTROYED, registrar no Veritas ledger
  await emitKeyDestructionEvent(keyVersionName, destroyedVersion);
}
```

---

## VeritasChain — Integridade do Hash Chain

```typescript
// lock_hash = SHA256(index || ts || actor || action || artifact || prevHash)
// prevHash: NUNCA de state de classe — ler do BigQuery WORM a cada emit

export async function computeLockHash(entry: Omit<ChainEntry, 'lockHash'>): Promise<string> {
  const canonical = [
    entry.index.toString(),
    entry.ts.toString(),
    entry.actor,
    entry.action,
    entry.artifact,
    entry.prevHash,
  ].join('|');

  return createHash('sha256').update(canonical, 'utf-8').digest('hex');
}

// INVARIANT: prevHash deve ser lido do Spanner TrueTime nesta transação
// Qualquer leitura de cache ou state local aqui é CG-002 (hash chain inconsistente)
export async function readChainTip(spannerTx: Transaction): Promise<string> {
  const [rows] = await spannerTx.run({
    sql: `SELECT lock_hash FROM veritas_chain ORDER BY index DESC LIMIT 1`,
  });
  return rows[0]?.toJSON()?.lock_hash ?? GENESIS_HASH;
}
```

---

## Autenticação e Autorização

### JWT — Padrão obrigatório

```typescript
// PROIBIDO: localStorage, sessionStorage
// OBRIGATÓRIO: httpOnly cookies + SameSite=Strict

// Em Fastify:
fastify.addHook('onSend', async (request, reply) => {
  reply.header('Set-Cookie', [
    `token=${jwt}; HttpOnly; SameSite=Strict; Secure; Path=/; Max-Age=3600`,
  ]);
});

// Validação de token em toda rota protegida
fastify.addHook('preHandler', async (request) => {
  const token = request.cookies['token'];
  if (!token) throw fastify.httpErrors.unauthorized();
  request.user = await verifyJwt(token);
});
```

### OIDC Keyless Auth — CI/CD

```yaml
# GitHub Actions — nunca usar Service Account keys em CI
permissions:
  id-token: write
  contents: read

- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: 'projects/PROJECT_NUM/locations/global/workloadIdentityPools/POOL/providers/PROVIDER'
    service_account: 'github-actions@foundlab-ati.iam.gserviceaccount.com'
```

---

## Proteção Contra Vulnerabilidades Comuns

### Headers de segurança — Fastify

```typescript
await fastify.register(import('@fastify/helmet'), {
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      objectSrc: ["'none'"],
      upgradeInsecureRequests: [],
    },
  },
  hsts: { maxAge: 31536000, includeSubDomains: true },
  noSniff: true,
  xssFilter: true,
});
```

### Rate Limiting

```typescript
// Todas as rotas públicas: rate limit obrigatório
await fastify.register(import('@fastify/rate-limit'), {
  max: 100,
  timeWindow: '1 minute',
  keyGenerator: (request) => request.ip,
  errorResponseBuilder: () => ({
    statusCode: 429,
    error: 'Too Many Requests',
    message: 'Rate limit exceeded',
  }),
});
```

### Injeção e XSS

- Proibido interpolação direta de input do usuário em queries Spanner/BigQuery. Usar parameterized queries sempre.
- Proibido `innerHTML` em qualquer componente frontend. Usar `textContent` ou sanitização via `DOMPurify`.
- Proibido `eval()`, `new Function()`, ou `setTimeout(string)`.

---

## Postura de Segurança de Infraestrutura

### Cloud Run

```hcl
# terraform/modules/cloud-run/main.tf
resource "google_cloud_run_v2_service" "rex_guard" {
  ingress = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    service_account = google_service_account.rex_guard.email

    containers {
      env {
        # Secrets via Secret Manager — nunca valor direto
        name = "KMS_KEY_NAME"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.kms_key_name.secret_id
            version = "latest"
          }
        }
      }
    }

    vpc_access {
      connector = google_vpc_access_connector.rex_guard.id
      egress    = "ALL_TRAFFIC"
    }
  }
}
```

### Scanning de Imagem — CI obrigatório

```yaml
- name: Trivy scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: '${{ env.IMAGE }}'
    format: 'sarif'
    exit-code: '1'          # falha o build se CRITICAL encontrado
    severity: 'CRITICAL,HIGH'
```

---

## Resposta a Incidentes

Qualquer vulnerabilidade encontrada em código de produção:

1. Abrir issue com label `P0-security` — privado se sensível.
2. Não publicar detalhes em canais públicos até patch deployed.
3. Se dados de cliente potencialmente expostos: notificação obrigatória conforme LGPD Art. 48 (72h à ANPD).
4. Documentar em `docs/incident-log.md` após resolução.

---

*FoundLab · security.md v1.0 · 2026-04-17*
