# Engineering Review — REX Guard PoC

**Branch:** `claude/rex-guard-bradesco-poc-0qF0q` → `main`  
**Data:** 18 Abril 2026  
**Projecto:** FoundLab Tecnologia Ltda × Bradesco — SAD v1.4.3  
**Valor contratual:** R$ 22.000.000

---

## 1. Contexto e Objectivo

O Bradesco exige que toda inferência de IA em contexto Open Finance cumpra o **BCB 538/2025** antes de entrar em produção. O REX Guard é o mecanismo de compliance técnico: intercepta cada chamada ao Gemini (Vertex AI), valida consentimento OPIN, mascara PII, verifica listas OFAC, assina criptograficamente a decisão com ECDSA P-256 e escreve um registo WORM em BigQuery com timestamp TrueTime de Cloud Spanner.

**REX Guard não é um modelo de linguagem.** É um proxy de segurança fail-closed. O Gemini continua a ser o modelo respondente — o REX Guard é a camada de compliance sobre ele.

---

## 2. O Que Este Branch Entrega

### 2.1 Commits neste branch (não em main)

| Commit | Descrição |
|--------|-----------|
| `9f8d1d0` | feat(tests): GCP integration test suite — Tier 2 (BigQuery, KMS, Spanner, Redis reais) |
| `ef21d2f` | docs: README actualizado com CI badge |
| `c12c827` | docs: rewrite README + STATUS.md com estado real do projecto |
| `41ec9a5` | feat(inference): resposta `/v1/infer` inclui `timestamp` Spanner TrueTime |
| `81beb21` | docs: STATUS.md criado |

### 2.2 Já em main (PRs anteriores)

| PR | O que entrou |
|----|-------------|
| #9 | ci: Node.js 22 + FORCE_JAVASCRIPT_ACTIONS_TO_NODE24; fix Gemini bot review (CVE-2025-66478, uid, payloadType, projectId, build artifacts) |
| #7 | feat(frontend): Next.js 15.5.15 + React 19 — UI completa; Firebase Hosting + Cloud Run rewrites + CORS |
| #6 | fix(pilar-iii): TrueTime no RFC 3161 mock; fix(pilar-ii): KMS AES-256-GCM no appeal reason |
| #5 | Backend inicial: Pilares I, II, III; testes unitários e de integração |

---

## 3. Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                   Firebase Hosting                       │
│         https://bradesco-rex-guard.web.app               │
│         Next.js 15.5.15 · React 19 · static export      │
└────────────────────┬────────────────────────────────────┘
                     │ /v1/** rewrite (Cloud Run)
                     ▼
┌─────────────────────────────────────────────────────────┐
│                REX Guard (Cloud Run)                     │
│                Fastify · Node.js 22                      │
│                                                          │
│  POST /v1/infer                                          │
│  ├─ 1. ConsentValidator    → Redis 60s cache + OPIN API  │
│  ├─ 2. SecurityGates.PII   → mask CPF/CNPJ              │
│  ├─ 3. SecurityGates.OFAC  → lista sanções (stub)        │
│  ├─ 4. SecurityGates.Burn  → prompt injection (stub)     │
│  │        ↓ ALLOWED                                      │
│  ├─ 5. Guardian AI         → Gemini via Vertex AI        │
│  ├─ 6. Output validation   → PII residual                │
│  ├─ 7. ReciboSigner        → ECDSA P-256 via Cloud KMS   │
│  │      └─ Merkle chain    → prev_hash de BigQuery       │
│  └─ 8. BigQuery WORM       → TrueTime via Cloud Spanner  │
│                                                          │
│  POST /v1/appeal → KMS AES-256-GCM + BigQuery           │
│  POST /v1/admin/notarize-day → RFC 3161 mock             │
└─────────────────────────────────────────────────────────┘
         │                    │                │
    Cloud KMS            Cloud Spanner      BigQuery
    ECDSA P-256           TrueTime         audit_trail
    AES-256-GCM                            dataset
         │
    Memorystore
    Redis (consent)
```

### 3.1 Princípios de Design

**Fail-closed** — qualquer falha em KMS, BigQuery, Spanner ou validação de consentimento resulta em `BLOCKED`. Nunca em sucesso silencioso.

**Zero-persistence** — buffers com dados sensíveis são zerados com `shredBuffer()` + `requestGC()` após uso. Exigência do Pilar II do SAD.

**Audit trail imutável** — cada `SealedRecibo` contém: hash do output, assinatura ECDSA P-256, `prev_hash` para encadeamento Merkle, timestamp TrueTime. BigQuery WORM impede modificação retroactiva.

**Separação de responsabilidades** — REX Guard nunca armazena o output de Gemini. Armazena apenas o hash (SHA-256) do output mascarado.

---

## 4. Modelo de Segurança

### 4.1 Superfície de Ataque

| Vector | Mitigação |
|--------|-----------|
| Prompt injection no input | BurnEngine (keyword detection; stub → real em P1) |
| PII no input/output | SecurityGates.maskPII (regex CPF/CNPJ) |
| Entidade sancionada | OFAC gate (stub → real em P1) |
| Timestamp forge | TrueTime via Cloud Spanner (externally consistent) |
| Adulteração de recibo | ECDSA P-256 + Merkle chain (prev_hash) |
| Acesso não autorizado à razão de recurso | KMS AES-256-GCM field-level encryption |
| CORS cross-origin | Restrito a `bradesco-rex-guard.web.app` em produção |
| Dados em memória | shredBuffer() zera buffers; GC sweep |

### 4.2 O Que É Stub (Não Pronto para Produção)

| Componente | Estado | Impacto |
|-----------|--------|---------|
| OFAC gate | Keyword match simples | Falsos negativos contra entidades reais |
| BurnEngine | Keyword match simples | Falsos negativos contra prompt injection sofisticado |
| RFC 3161 TSA | Mock base64 | Notarização não é auditável por terceiros |

**Estes stubs são conhecidos e documentados.** Não bloqueiam o PoC mas devem ser substituídos antes de Go-Live.

### 4.3 Vulnerabilidades Conhecidas e Corrigidas

| CVE / Issue | Estado |
|------------|--------|
| CVE-2025-66478 (Next.js 15.3.1) | Corrigido — 15.5.15 |
| `Math.random()` para IDs de mensagem | Corrigido — `crypto.randomUUID()` |
| `projectId ?? ''` em BigQuery (ADC bypass) | Corrigido — `projectId ? { projectId } : {}` |
| Build artifacts (`frontend/out/`) em git | Corrigido — `.gitignore` |
| `new Date()` em timestamps de auditoria | Corrigido — Spanner TrueTime |
| `notarization-service` silencia erros BigQuery | Corrigido — `throw err` (fail-closed) |

---

## 5. Testes

### 5.1 Tier 1 — CI Automático (mocks, sem GCP)

```
npm run test:ci
```

| Métrica | Valor |
|---------|-------|
| Test suites | 11 passam |
| Testes | 109 passam |
| Branch coverage | 71.34% (threshold: 70%) |
| Statements | 92.23% (threshold: 85%) |
| Duração | ~14s |

Cobre: lógica de negócio, encadeamento Merkle, zero-persistence, ECDSA, KMS operations, appeal service, security gates, notarization.

### 5.2 Tier 2 — GCP Integration (real, manual)

```
npm run test:gcp   # requer credenciais GCP via ADC
```

Activado via `workflow_dispatch` em `.github/workflows/test-gcp-integration.yml`.

| Suite | O que valida |
|-------|-------------|
| `kms.gcp.spec.ts` | `KMSOperations.signAsRawHex()` — P-256 real, 128 hex chars, key_version com path completo |
| `spanner.gcp.spec.ts` | `getSpannerTrueTime()` — ISO com microsegundos, monotónico |
| `notarization.gcp.spec.ts` | BigQuery WORM insert real; fail-closed no timeout |
| `redis.gcp.spec.ts` | Memorystore ping, set/get, expiração TTL |

**Tier 2 deve passar antes de qualquer deploy para staging.**

### 5.3 Cobertura por Pilar

| Pilar | Cobertura (Tier 1) | Cobertura (Tier 2) |
|-------|------------------|--------------------|
| I — Consent | 75.4% branch | Redis real + OPIN mock |
| II — Zero-persistence | 98% statements | — |
| III — Audit trail | 100% (recibo-signer) | BigQuery + KMS reais |
| BCB 538 Art. 32 (appeal) | 97.36% statements | KMS encrypt real |

---

## 6. Dependências Externas

### 6.1 GCP — Recursos Necessários

| Recurso | Variável de Ambiente | Utilização |
|---------|---------------------|------------|
| Cloud KMS (ECDSA P-256) | `KMS_KEY_RESOURCE` | Assinar cada recibo |
| Cloud KMS (AES-256-GCM) | `KMS_APPEAL_KEY_RESOURCE` | Cifrar razão de recurso |
| Cloud Spanner | `SPANNER_INSTANCE` + `SPANNER_DATABASE` | TrueTime |
| BigQuery dataset `audit_trail` | `BQ_DATASET` | WORM — tabelas `recibos`, `appeals`, `daily_notarizations` |
| Memorystore Redis | `REDIS_HOST` + `REDIS_PASSWORD` | Consent cache 60s |
| Vertex AI / Guardian AI | `GUARDIAN_AI_URL` | Inferência Gemini |
| OPIN API | `OPUS_BASE_URL` | Validação de consentimento |
| Cloud Run (`rex-guard`, `southamerica-east1`) | — | Serve o backend |

### 6.2 GitHub — Secrets Necessários

| Secret | Valor |
|--------|-------|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Resource name do Workload Identity Provider |
| `GCP_SA_EMAIL` | Email do Service Account de CI/CD |
| `KMS_KEY_RESOURCE` | Resource name completo da chave ECDSA (para Tier 2) |
| `KMS_APPEAL_KEY_RESOURCE` | Resource name da chave AES-256-GCM (para Tier 2) |
| `REDIS_PASSWORD` | Auth string do Memorystore (para Tier 2) |

---

## 7. Checklist de Code Review

### 7.1 Segurança (obrigatório — bloqueia merge)

- [ ] Nenhum dado pessoal (CPF, CNPJ, nome, conta) em logs — verificar `logger.*` calls
- [ ] Nenhum secret hardcoded — verificar `process.env.*` e `.env` não commitado
- [ ] `shredBuffer()` chamado após uso de qualquer buffer com dados sensíveis
- [ ] Todas as respostas de erro retornam apenas identificadores seguros (nunca conteúdo do recibo)
- [ ] CORS restrito em produção (`NODE_ENV === 'production'`)
- [ ] `npm audit` sem vulnerabilidades críticas ou altas

```bash
# Verificar
npm audit
grep -r "console.log" src/          # deve ser vazio (usar logger)
grep -r "Math.random" src/          # deve ser vazio
```

### 7.2 Compliance BCB 538 (obrigatório — bloqueia merge)

- [ ] Todo `BLOCKED` path não cria recibo no BigQuery
- [ ] Todo `ALLOWED` path cria exactamente um recibo com assinatura válida
- [ ] Timestamp de todos os recibos vem de `getSpannerTrueTime()` — nunca de `new Date()`
- [ ] Appeal reason cifrado com KMS antes de qualquer persistência
- [ ] `notarizeDailyChain()` lança em falha de BigQuery (fail-closed)

```bash
# Verificar ausência de new Date() em paths de audit
grep -n "new Date()" src/services/
# Esperado: apenas em kms-operations.ts (destroy_timestamp — não é timestamp de audit)
```

### 7.3 Qualidade de Código (recomendado — não bloqueia)

- [ ] `npm run type-check` sem erros
- [ ] `npm run test:ci` — 109 testes, branch coverage ≥ 70%
- [ ] Sem `any` desnecessário em novos ficheiros
- [ ] Dependências de injecção (DI) usadas em todos os services — não instanciar GCP clients nos construtores sem override possível

### 7.4 Infra / Deploy (obrigatório antes de staging)

- [ ] `npm run test:gcp` passa com credenciais GCP reais (Tier 2)
- [ ] `firebase.json` aponta para Cloud Run correcto (`rex-guard`, `southamerica-east1`)
- [ ] Dockerfile usa `--expose-gc` no CMD (necessário para `requestGC()`)
- [ ] Variáveis de ambiente documentadas em README.md secção "Variáveis de Ambiente"

---

## 8. Processo de Merge

### 8.1 Critérios de Aprovação

Exige **2 aprovações**:
1. **Engenheiro de Segurança / CISO** — valida secções 4 e 7.1 e 7.2
2. **Engenheiro Backend sénior** — valida secções 3, 5, 7.3 e 7.4

### 8.2 Gates Automáticos (GitHub Actions)

O merge só é possível quando:
- `REX Guard CI/CD / Test & Type-check` — verde
- Tier 2 (`REX Guard GCP Integration Tests`) — executado e verde manualmente pelo responsável de infra

### 8.3 Sequência Recomendada

```
1. Code review (2 aprovações — segurança + backend)
2. npm run test:gcp  →  verde com GCP real
3. Merge para main
4. docker build + push para Artifact Registry (CI automático)
5. gcloud run deploy rex-guard --region southamerica-east1
6. firebase deploy --only hosting:bradesco
7. Smoke test em https://bradesco-rex-guard.web.app
```

---

## 9. Dívida Técnica Conhecida

### Alta Prioridade (antes de Go-Live)

| Item | Localização | Esforço |
|------|-------------|---------|
| OFAC gate real (API de sanções) | `src/services/security-gates.ts` | 2–3 dias |
| BurnEngine real (modelo de classificação) | `src/services/security-gates.ts` | 3–5 dias |
| RFC 3161 TSA real (FreeTSA ou BCB-approved) | `src/services/notarization-service.ts` | 1–2 dias |
| Circuit breaker no Guardian AI (Vertex AI) | `src/services/inference-engine.ts` | 1 dia |

### Média Prioridade (antes de GA)

| Item | Localização | Esforço |
|------|-------------|---------|
| `kms_key_version: '1'` hardcoded | `src/services/inference-engine.ts:147` | 0.5 dia |
| `USER_ID` / `CONSENT_ID` hardcoded no frontend | `frontend/app/page.tsx` | 1 dia (Firebase Auth) |
| Dockerfile: Node 20 Alpine → Node 22 | `infra/docker/Dockerfile` | 0.5 dia |
| `notarization-service.ts` projectId fallback hardcoded | `src/services/notarization-service.ts:31` | 0.5 dia |

---

## 10. Como Executar a Review

```bash
# 1. Clonar e instalar
git clone https://github.com/irelia0nerf/GCPPoCB
git checkout claude/rex-guard-bradesco-poc-0qF0q
npm install && cd frontend && npm install && cd ..

# 2. Verificações de segurança
npm audit
grep -rn "new Date()" src/services/    # só deve aparecer em kms-operations.ts
grep -rn "console.log" src/            # deve ser vazio
grep -rn "Math.random" src/            # deve ser vazio

# 3. Testes Tier 1
npm run type-check
npm run test:ci
# Esperado: 109 testes, branch coverage 71.34%

# 4. Testes Tier 2 (requer GCP)
# Via GitHub Actions → workflow_dispatch → "REX Guard GCP Integration Tests"
# Ou localmente com ADC configurado:
# export GOOGLE_CLOUD_PROJECT=... SPANNER_INSTANCE=... etc
# npm run test:gcp

# 5. Build frontend
cd frontend && npm run build
# Esperado: sem erros, gera frontend/out/
```

---

*Documento confidencial — FoundLab Tecnologia Ltda × Bradesco. Não partilhar externamente sem aprovação de Alex Bolson.*
