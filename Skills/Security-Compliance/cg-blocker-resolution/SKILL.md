---
name: cg-blocker-resolution
description: >-
  Use SEMPRE que o usuário mencionar critical gap, CG-001, CG-002, CG-003, fechamento de bloqueador, pentest blocker, Bradesco blocker, hardcoded policy hash, audit gate ausente, shred_key simulado, localStorage JWT, AES-128 → AES-256-GCM, ou qualquer hygiene item que trava demo bancária. Triggers literais: "CG-001", "CG-002", "CG-003", "critical gap", "bloqueador Bradesco", "pentest", "policy_snapshot_hash", "shred_key fake", "JWT localStorage", "hygiene". NÃO use para bugs comuns ou refactors genéricos — esta skill é cirúrgica para os 4 críticos abertos do REX Guard.
---

# CG Blocker Resolution — Fechamento Cirúrgico

Quatro itens travando Bradesco ($25K USD expansion approved, demo aprovada). Cada CG aberto é credibilidade perdida com Glauco Sampaio (CISO Brief promete coisas que código não entrega). Esta skill é o playbook de fechamento — sem fluff, sem "melhorias genéricas", critério de aceite explícito por CG.

## CG-001 — `policy_snapshot_hash` hardcoded

### Sintoma
Hash da policy ativa está fixo no código. Toda inferência sela com o mesmo hash, independente da policy real em vigor. Auditoria forense fica impossível: "qual policy estava ativa quando a decisão X foi tomada?" → resposta única, sempre a mesma. Fraude técnica disfarçada de feature.

### Root cause provável
Stub de desenvolvimento que migrou para prod porque ninguém puxou o cabo do `// TODO: replace with dynamic load`.

### Fix

```typescript
// ANTES (atual, errado)
const POLICY_SNAPSHOT_HASH = 'sha256:abc123...';  // hardcoded — CG-001

// DEPOIS (correto)
import { createHash } from 'node:crypto';

interface PolicyResolver {
  getActivePolicy(tenantId: string, modelId: string): Promise<PolicySnapshot>;
  computeSnapshotHash(snapshot: PolicySnapshot): string;
}

class FirestorePolicyResolver implements PolicyResolver {
  private cache = new LRUCache<string, PolicySnapshot>({
    max: 1000,
    ttl: 60_000,  // 1min — invalidação rápida em mudança de policy
  });

  async getActivePolicy(tenantId: string, modelId: string): Promise<PolicySnapshot> {
    const cacheKey = `${tenantId}:${modelId}`;
    const cached = this.cache.get(cacheKey);
    if (cached) return cached;

    const doc = await firestore
      .collection('policies')
      .doc(tenantId)
      .collection('active')
      .doc(modelId)
      .get();

    if (!doc.exists) {
      throw new PolicyNotFoundError(`No active policy for ${tenantId}/${modelId}`);
    }

    const snapshot = doc.data() as PolicySnapshot;
    this.cache.set(cacheKey, snapshot);
    return snapshot;
  }

  computeSnapshotHash(snapshot: PolicySnapshot): string {
    // Canonical JSON — chaves ordenadas. Hash determinístico.
    const canonical = canonicalize(snapshot);
    return 'sha256:' + createHash('sha256').update(canonical).digest('hex');
  }
}
```

### Critério de aceite
1. Grep `grep -rn "policy_snapshot_hash.*=.*'sha256:" src/` retorna **zero matches**
2. Teste de integração: 2 policies diferentes ativas em 2 tenants → 2 hashes diferentes nos respectivos SealedRecibos
3. Cache invalida em < 60s após policy update (medido em teste)
4. Falha em resolver policy = **inferência rejeitada** (não fallback silencioso)

---

## CG-002 — CI/CD audit gate ausente

### Sintoma
Pipeline `.github/workflows/deploy.yml` (ou Cloud Build equivalente) não tem step de validação de audit trail antes de promover. Deploy passa mesmo se `recibos_sealed` está com schema drift, signature inválida, ou Merkle chain quebrada na última janela.

### Fix

```yaml
# .github/workflows/deploy.yml
name: REX Guard Deploy

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  audit-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Auth GCP
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.AUDIT_VALIDATOR_SA }}

      - name: Validate last 1000 recibos
        run: |
          ./scripts/validate-audit-trail.sh \
            --project=${{ secrets.PROJECT_ID }} \
            --window=last-1h \
            --min-recibos=1 \
            --max-failure-rate=0
          # Exit code != 0 = block deploy

      - name: Validate Merkle chain integrity
        run: |
          npm run audit:verify-chain -- --hours=24 --strict

      - name: Validate schema compliance
        run: |
          npm run audit:schema-check -- --reject-unknown-fields

  deploy:
    needs: audit-validation  # GATE
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: ./scripts/deploy.sh
```

Script `validate-audit-trail.sh` minimal:
```bash
#!/usr/bin/env bash
set -euo pipefail

PROJECT=$1
WINDOW=$2  # last-1h, last-24h
MIN=$3
MAX_FAIL=$4

QUERY="
SELECT
  COUNT(*) as total,
  COUNTIF(signature IS NULL OR merkle_root IS NULL) as missing_proofs,
  COUNTIF(LENGTH(policy_snapshot_hash) != 71) as malformed_hash
FROM \`${PROJECT}.audit_trail.recibos_sealed\`
WHERE sealed_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
"

result=$(bq query --use_legacy_sql=false --format=json "$QUERY")
total=$(echo "$result" | jq -r '.[0].total')
fails=$(echo "$result" | jq -r '.[0].missing_proofs + .[0].malformed_hash')

if [ "$total" -lt "$MIN" ]; then
  echo "FAIL: only $total recibos in window (min $MIN)"
  exit 1
fi

fail_rate=$(echo "scale=4; $fails / $total" | bc)
if (( $(echo "$fail_rate > $MAX_FAIL" | bc -l) )); then
  echo "FAIL: failure rate $fail_rate > $MAX_FAIL"
  exit 1
fi

echo "PASS: $total recibos, $fails failures"
```

### Critério de aceite
1. PR com Merkle chain quebrada na window de teste = pipeline bloqueia
2. PR com schema drift (campo extra ou faltando) = pipeline bloqueia
3. Tempo de gate < 90s (não pode virar friction de produtividade)
4. Logs do gate vão pro audit trail (meta-auditoria)

---

## CG-003 — `shred_key()` simulado

### Sintoma
Função `shred_key()` retorna `true` sem destruir nada. Zero-Persistence virou narrativa de marketing. Se Glauco pedir prova de crypto-shredding em pentest, FoundLab vai precisar explicar por que CISO Brief mente. Risco de credibilidade: total.

### Root cause
Provavelmente foi marcado como "implementar depois" para destravar demo, e ninguém voltou. Padrão clássico de débito técnico que vira fraude.

### Fix

Ver skill `audit-trail-bcb538` seção "Crypto-shredding (CG-003 fix)" para implementação canônica. Resumo do critério de aceite:

```typescript
// Não vou colar de novo — referência cruzada.
// Pontos não-negociáveis da implementação:
// 1. Cloud KMS destroyCryptoKeyVersion (NÃO marcar como deletado em DB)
// 2. Audit event CRYPTO_SHRED_INITIATED ANTES da chamada KMS
// 3. Validação pós-shred: state == DESTROY_SCHEDULED ou DESTROYED
// 4. Recibo permanece na tabela (compliance), payload original inacessível
```

### Critério de aceite
1. Teste E2E: usuário chama deleção LGPD → `shred_key()` executa → Cloud KMS Console mostra version DESTROY_SCHEDULED
2. Após 24h+ (grace period KMS), tentativa de descriptografar payload original retorna `KeyNotFoundError`
3. Audit event `CRYPTO_SHRED_INITIATED` está em `recibos_sealed` ou tabela paralela `lgpd_deletions`
4. SealedRecibo do payload original **permanece íntegro** e verificável (provando que apenas a chave morreu, não o registro)
5. Documentação para auditor externo: como provar deleção criptográfica, quais artefatos KMS apresentar

---

## Hygiene 1 — JWT no localStorage → httpOnly cookie

### Sintoma
Frontend armazena JWT em `localStorage`. Vulnerável a XSS — qualquer script injetado lê o token. Padrão OWASP Top 10 violado em produto que vende segurança.

### Fix

Backend:
```typescript
// Login endpoint
reply
  .setCookie('rex_session', jwt, {
    httpOnly: true,
    secure: true,           // HTTPS only
    sameSite: 'strict',     // CSRF mitigation
    domain: '.foundlab.com.br',
    path: '/',
    maxAge: 3600,           // 1h, refresh via /refresh endpoint
    signed: true,           // Fastify signed cookie
  })
  .send({ user: sanitizedUser });
```

Frontend:
```typescript
// REMOVER todos os usos de localStorage.getItem('jwt') / setItem
// Trocar por fetch com credentials: 'include'
fetch(API_URL, {
  credentials: 'include',  // cookies enviados automaticamente
  headers: { 'Content-Type': 'application/json' },
});
```

CSRF protection adicional:
- Endpoint `/csrf-token` que retorna token sincronizador
- Header `X-CSRF-Token` validado em todas as mutations
- ou double-submit cookie pattern

### Critério de aceite
1. `grep -rn "localStorage" frontend/src/` retorna **apenas** ocorrências sem JWT/auth
2. DevTools Application → Local Storage não mostra token
3. Cookie `rex_session` aparece com flags HttpOnly + Secure + SameSite=Strict
4. Pentest XSS simulado não consegue exfiltrar credencial

---

## Hygiene 2 — AES-128 → AES-256-GCM

### Sintoma
Encryption em repouso (ou em trânsito interno) usa AES-128. Não é "inseguro" academicamente, mas para banco brasileiro auditado é olhar de lado. AES-256-GCM é o padrão de mercado e custa basicamente o mesmo em performance moderna.

### Fix

```typescript
// ANTES
const cipher = createCipheriv('aes-128-cbc', key, iv);

// DEPOIS
import { createCipheriv, createDecipheriv, randomBytes } from 'node:crypto';

function encryptAESGCM(plaintext: Buffer, key: Buffer, aad?: Buffer): EncryptedPayload {
  if (key.length !== 32) throw new Error('AES-256 requires 32-byte key');

  const iv = randomBytes(12);  // GCM standard
  const cipher = createCipheriv('aes-256-gcm', key, iv);
  if (aad) cipher.setAAD(aad);

  const ciphertext = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  const authTag = cipher.getAuthTag();

  return { iv, ciphertext, authTag, aad };
}

function decryptAESGCM(payload: EncryptedPayload, key: Buffer): Buffer {
  const decipher = createDecipheriv('aes-256-gcm', key, payload.iv);
  decipher.setAuthTag(payload.authTag);
  if (payload.aad) decipher.setAAD(payload.aad);

  return Buffer.concat([decipher.update(payload.ciphertext), decipher.final()]);
}
```

Migração de dados existentes:
1. Re-encrypt em batch durante janela de manutenção
2. Manter compatibilidade temporária (read-only AES-128 + write AES-256) por 1 ciclo
3. Após validação, remover paths AES-128 completamente

### Critério de aceite
1. `grep -rn "aes-128" src/` retorna **zero matches**
2. Todos os payloads novos usam AES-256-GCM com IV de 12 bytes
3. Auth tag validado em decrypt (rejeitar payload tamperado)
4. AAD usado quando contexto criptográfico precisa ser amarrado (ex: tenant_id como AAD)

---

## Pentest readiness — checklist consolidado

Antes de liberar pentest pra Bradesco:

- [ ] CG-001 fechado e provado em teste de integração
- [ ] CG-002 fechado e gate testado em PR sintético com falha proposital
- [ ] CG-003 fechado e crypto-shred validado em ambiente staging com Cloud KMS real
- [ ] Hygiene 1 (httpOnly) validado com tentativa de XSS sintética
- [ ] Hygiene 2 (AES-256-GCM) validado com vetor de teste conhecido
- [ ] Zero `// TODO`, `// FIXME`, `// stub` em paths críticos (`grep -rn` no src/)
- [ ] Documentação atualizada: CISO Brief reflete o que código entrega, sem hipérbole
- [ ] Threat model revisado e assinado pelo Glauco antes do pentest começar

## Boundaries (CRITICAL)

- **NUNCA** fechar CG sem teste automatizado que prove o fechamento
- **NUNCA** marcar CG como "closed" sem PR review por alguém que NÃO escreveu o fix
- **NUNCA** liberar pentest com qualquer CG aberto — risco de relatório público de vulnerabilidade crítica
- **NUNCA** alterar CISO Brief para "esconder" gap — se o Brief promete e código não entrega, o Brief muda OU o código entrega. Mentir é fraude.
- **SEMPRE** registrar fechamento de CG no audit trail com referência ao PR
- **SEMPRE** notificar Glauco Sampaio antes de marcar todos os CGs como fechados — ele é o validador externo, não decoração
