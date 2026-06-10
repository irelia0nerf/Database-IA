---
name: audit-trail-bcb538
description: >-
  Use SEMPRE que o usuário mencionar SealedRecibo, DecisionID, Merkle chain, audit trail, evidência criptográfica, BCB 538/2025, retention paradox, LGPD vs retenção bancária, RFC 3161 timestamping, TSA, Zero-Persistence, shred_key, crypto-shredding, ou WORM tier no BigQuery. Triggers literais: "audit trail", "Merkle", "SealedRecibo", "DecisionID", "BCB 538", "retention paradox", "Zero-Persistence", "shred_key", "RFC 3161". Esta skill NÃO é genérica — é específica do contrato de evidência do REX Guard. Se o pedido for sobre logging/observabilidade comum, use outra skill.
---

# Audit Trail BCB 538/2025 — Contrato de Evidência

ATI (Auditable Trust Infrastructure) vive ou morre por causa desse pipeline. Se SealedRecibo está fraco, o moat regulatório que o AUDIT-2026-0409 confirmou (compliance layer, NÃO Thought Signatures) cai. Esta skill é o playbook canônico para implementar/validar o stack de evidência.

## Conceitos não-negociáveis

### SealedRecibo
Estrutura criptograficamente selada que prova que uma decisão de inferência aconteceu, com qual policy, em qual timestamp, com qual input/output. Selo = hash assinado + posição na Merkle chain + timestamp TSA RFC 3161.

### DecisionID
Identificador único e globalmente ordenável de uma decisão. Recomendação: **UUID v7** (timestamp embutido + entropy) — NÃO UUID v4 (perde ordenação) e NÃO ULID (compatibilidade BigQuery pior).

### Retention Paradox
BCB 538/2025 exige retenção de logs de decisão por períodos específicos (5-10 anos dependendo do contexto). LGPD Art. 18 VI dá direito de deleção ao titular. Conflito estrutural. ATI resolve via **crypto-shredding**: o registro permanece (compliance bancário), a chave é destruída (deleção criptográfica satisfaz LGPD).

### Zero-Persistence
Promessa do CISO Brief: dado sensível NÃO persiste em forma legível após inferência. Implementação real exige `shred_key()` que destrói chave de envelope encryption — não é flag, é deleção física da chave em Cloud KMS.

## Schema canônico — SealedRecibo

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SealedRecibo",
  "type": "object",
  "required": [
    "decision_id",
    "policy_snapshot_hash",
    "input_hash",
    "output_hash",
    "model_id",
    "model_version",
    "tenant_id",
    "sealed_at",
    "merkle_position",
    "merkle_root",
    "tsa_token",
    "signature"
  ],
  "properties": {
    "decision_id": {
      "type": "string",
      "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
      "description": "UUID v7 — ordenável por timestamp"
    },
    "policy_snapshot_hash": {
      "type": "string",
      "pattern": "^sha256:[a-f0-9]{64}$",
      "description": "Hash da policy ATIVA no momento da decisão. NUNCA hardcoded (CG-001)."
    },
    "input_hash": {
      "type": "string",
      "pattern": "^sha256:[a-f0-9]{64}$",
      "description": "Hash do input após normalização canônica. Input NÃO persistido em claro."
    },
    "output_hash": {
      "type": "string",
      "pattern": "^sha256:[a-f0-9]{64}$",
      "description": "Hash do output. Output NÃO persistido em claro."
    },
    "model_id": { "type": "string" },
    "model_version": { "type": "string" },
    "tenant_id": { "type": "string", "description": "Isolamento multi-tenant" },
    "sealed_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 com timezone — NUNCA naive"
    },
    "merkle_position": {
      "type": "integer",
      "minimum": 0,
      "description": "Índice na chain dentro da janela de batch"
    },
    "merkle_root": {
      "type": "string",
      "pattern": "^sha256:[a-f0-9]{64}$",
      "description": "Root da árvore que contém este recibo"
    },
    "tsa_token": {
      "type": "string",
      "description": "Token RFC 3161 base64 — TSA externa autoritativa"
    },
    "signature": {
      "type": "string",
      "pattern": "^[A-Za-z0-9+/=]+$",
      "description": "Assinatura ECDSA P-256 sobre os campos canonicalizados"
    },
    "envelope_key_ref": {
      "type": "string",
      "description": "Cloud KMS key resource. Após shred_key(), referência aponta para chave destruída — recibo permanece, payload original inacessível."
    }
  },
  "additionalProperties": false
}
```

## Procedure — Construção da Merkle Chain

```typescript
// Streaming SHA-256 — não carregar batch inteiro em memória.
// Janela de batch: configurável (default 1000 ou 60s, o que vier primeiro).

import { createHash } from 'node:crypto';

interface MerkleNode {
  hash: string;        // sha256:<hex>
  left?: MerkleNode;
  right?: MerkleNode;
}

function leafHash(recibo: SealedReciboCore): string {
  // Canonical JSON — chaves ordenadas, sem espaços
  const canonical = canonicalize(recibo);
  return 'sha256:' + createHash('sha256').update(canonical).digest('hex');
}

function pairHash(left: string, right: string): string {
  // Concatenar SEM separador — qualquer separador vira ataque de extensão
  const concat = left.replace('sha256:', '') + right.replace('sha256:', '');
  return 'sha256:' + createHash('sha256').update(concat, 'hex').digest('hex');
}

function buildMerkleTree(leaves: string[]): MerkleNode {
  if (leaves.length === 0) throw new Error('Empty batch — never seal nothing');
  if (leaves.length === 1) return { hash: leaves[0] };

  // Padding: duplicar último se ímpar (padrão Bitcoin — sujeito a CVE-2012-2459 em outros contextos,
  // não aplicável aqui pois rejeitamos batch vazio e validamos length na verificação)
  const padded = leaves.length % 2 === 1 ? [...leaves, leaves[leaves.length - 1]] : leaves;

  const nextLevel: string[] = [];
  for (let i = 0; i < padded.length; i += 2) {
    nextLevel.push(pairHash(padded[i], padded[i + 1]));
  }
  return buildMerkleTree(nextLevel);
}
```

## Procedure — TSA RFC 3161

Em produção: integrar com TSA autoritativa (DigiCert, GlobalSign, ICP-Brasil — preferência por ICP-Brasil para defesa em juízo brasileiro).

```typescript
// PSEUDO — adaptar ao cliente TSA real
async function getTSAToken(merkleRoot: string): Promise<string> {
  const tsq = buildTimeStampRequest({
    messageImprint: merkleRoot,
    hashAlgorithm: 'SHA-256',
    nonce: crypto.randomBytes(8),
    certReq: true,
  });

  const response = await fetch(TSA_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/timestamp-query' },
    body: tsq,
  });

  if (!response.ok) {
    // FAIL-CLOSED — sem timestamp não há SealedRecibo
    throw new TSAUnavailableError(`TSA returned ${response.status}`);
  }

  const tsr = await response.arrayBuffer();
  return Buffer.from(tsr).toString('base64');
}
```

**Stub aceitável para staging/dev**: timestamp local + assinatura própria, claramente marcado `tsa_token: "DEV-STUB:<iso8601>"`. **NUNCA aceitável em produção** — defesa regulatória cai.

## Procedure — Crypto-shredding (CG-003 fix)

```typescript
// IMPLEMENTAÇÃO REAL — não stub
import { KeyManagementServiceClient } from '@google-cloud/kms';

async function shredKey(envelopeKeyRef: string): Promise<ShredProof> {
  const kms = new KeyManagementServiceClient();

  // 1. Schedule destruction (24h grace period — recovery window mandatório do KMS)
  const [version] = await kms.destroyCryptoKeyVersion({ name: envelopeKeyRef });

  // 2. Audit log da destruição — registro PERMANECE, chave morre
  const shredEvent = {
    key_ref: envelopeKeyRef,
    scheduled_destroy_time: version.destroyTime,
    requested_at: new Date().toISOString(),
    requestor: getActorIdentity(),
    legal_basis: 'LGPD Art. 18 VI — direito de deleção',
  };

  await writeAuditEvent('CRYPTO_SHRED_INITIATED', shredEvent);

  return {
    key_destroyed: true,
    destruction_scheduled_at: version.destroyTime,
    audit_event_id: shredEvent.audit_event_id,
  };
}
```

**Validação obrigatória pós-shred**:
```bash
gcloud kms keys versions describe ${VERSION} \
  --key=${KEY} --keyring=${KEYRING} --location=${LOCATION} \
  --format="value(state)"
# Esperado: DESTROY_SCHEDULED ou DESTROYED.
# Qualquer outro estado = shred falhou = LGPD violada.
```

## BigQuery WORM Tier

Tabela `audit_trail.recibos_sealed` precisa ser write-once:

```sql
-- Schema mandatório
CREATE TABLE `${PROJECT}.audit_trail.recibos_sealed` (
  decision_id STRING NOT NULL,
  policy_snapshot_hash STRING NOT NULL,
  input_hash STRING NOT NULL,
  output_hash STRING NOT NULL,
  model_id STRING NOT NULL,
  model_version STRING NOT NULL,
  tenant_id STRING NOT NULL,
  sealed_at TIMESTAMP NOT NULL,
  merkle_position INT64 NOT NULL,
  merkle_root STRING NOT NULL,
  tsa_token STRING NOT NULL,
  signature STRING NOT NULL,
  envelope_key_ref STRING,
  ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(sealed_at)
CLUSTER BY tenant_id, model_id
OPTIONS (
  description = "WORM audit trail — BCB 538/2025 compliance",
  partition_expiration_days = 3650  -- 10 anos default
);

-- IAM: bloquear DELETE/UPDATE via deny policy
-- (Org Policy + Conditional IAM — ver iam-security)
```

## Output Contract — Validação de SealedRecibo

Função pública mandatória:

```typescript
interface VerificationResult {
  valid: boolean;
  checks: {
    schema_valid: boolean;
    signature_valid: boolean;
    merkle_inclusion_valid: boolean;
    tsa_token_valid: boolean;
    policy_hash_resolvable: boolean;
  };
  failures: string[];
}

async function verifyRecibo(recibo: SealedRecibo): Promise<VerificationResult> {
  // Implementação: cada check independente, todos devem passar
  // Falhas são listadas, não silenciadas
}
```

## Boundaries (CRITICAL)

- **NUNCA** persistir input ou output em claro — apenas hashes
- **NUNCA** usar UUID v4 para DecisionID — perde ordenação cronológica
- **NUNCA** aceitar TSA stub em produção — só staging/dev claramente marcado
- **NUNCA** implementar `shred_key()` como `return true` — é fraude do CISO Brief
- **NUNCA** permitir DELETE/UPDATE na tabela `recibos_sealed`
- **NUNCA** misturar tenants no mesmo Merkle batch — cross-contamination de evidência
- **SEMPRE** validar `policy_snapshot_hash` resolvível antes de selar (CG-001)
- **SEMPRE** fail-closed: TSA down = recibo não emitido = inferência rejeitada
- **SEMPRE** registrar `CRYPTO_SHRED_INITIATED` antes de chamar KMS destroy
- **SEMPRE** preferir ICP-Brasil para TSA quando defesa em juízo brasileiro for relevante
