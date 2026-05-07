---
name: rex-guard-deploy
description: >-
  Use SEMPRE que o usuário mencionar deploy do REX Guard, subida de versão em GKE Autopilot, build/push de imagem Artifact Registry para o REX, Firebase Hosting do frontend, validação de policy_snapshot_hash, gate de CI/CD do audit trail, smoke test sub-50ms P99, ou rollback do REX Guard. Triggers literais: "deploy REX", "sobe REX", "rex-guard release", "policy_snapshot_hash", "audit gate", "vamos subir", "rollback REX". NÃO use para Cloud Run genérico ou outros serviços FoundLab — esta skill é exclusiva da pipeline REX Guard.
---

# REX Guard Deploy — Playbook Operacional

Pipeline de deploy do REX Guard (Node.js 22 / Fastify / GKE Autopilot / Firebase Hosting). Orçamento operacional ~$1,300/mês. SLA: P99 < 50ms inferência. Zero-Persistence é contrato — qualquer regressão aqui é credibilidade morta.

## CRITICAL — Pré-flight obrigatório

Antes de qualquer build, validar os critical gaps abertos. Deploy com CG aberto é roleta russa com a Bradesco:

1. **CG-001 — policy_snapshot_hash NÃO hardcoded**
   ```bash
   grep -rn "policy_snapshot_hash" src/ | grep -v "process.env\|loadPolicy\|computeHash"
   # Output esperado: vazio. Qualquer match é hardcode → BLOCK.
   ```

2. **CG-002 — CI/CD audit gate ativo**
   ```bash
   cat .github/workflows/deploy.yml | grep -A2 "audit-validation"
   # Output esperado: step "audit-validation" antes de "deploy" job.
   # Se ausente: BLOCK. Pipeline sem gate = sem deploy.
   ```

3. **CG-003 — shred_key() NÃO simulado**
   ```bash
   grep -rn "shred_key\|cryptoShred" src/crypto/ | grep -i "// TODO\|// stub\|// simulated\|return true;.*//"
   # Output esperado: vazio. Stub vivo = Zero-Persistence é teatro.
   ```

Se qualquer um falhar: PARAR. Documentar no PR. Sem exceção. CISO Brief promete Zero-Persistence delivered — entregar stub é fraude técnica.

## Procedure — Build & Deploy

### 1. Build da imagem

```bash
# Variáveis canônicas
export PROJECT_ID="mvp-elitte"
export REGION="us-central1"
export REPO="rex-guard"
export IMAGE_TAG="$(git rev-parse --short HEAD)"
export IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/rex-guard:${IMAGE_TAG}"

# Build com Cloud Build (não local — reprodutibilidade)
gcloud builds submit --tag "${IMAGE_URI}" \
  --machine-type=e2-highcpu-8 \
  --timeout=900s \
  .
```

Notas:
- Tag por commit SHA, NUNCA `:latest` em prod. `:latest` é antipattern de auditoria.
- Se build local for necessário (debug), usar `docker buildx build --platform linux/amd64` — GKE Autopilot é amd64.

### 2. Validação pré-deploy

```bash
# Container starts e responde no $PORT
docker run --rm -p 8080:8080 -e PORT=8080 "${IMAGE_URI}" &
sleep 5
curl -fsS http://localhost:8080/health || { echo "HEALTHCHECK FAIL"; exit 1; }
docker stop $(docker ps -q --filter ancestor="${IMAGE_URI}")

# Verificar tamanho da imagem (> 500MB = revisar Dockerfile)
docker images "${IMAGE_URI}" --format "{{.Size}}"
```

### 3. Deploy GKE Autopilot

```bash
# Atualizar manifesto
sed -i.bak "s|image:.*rex-guard:.*|image: ${IMAGE_URI}|g" k8s/deployment.yaml

# Apply com namespace correto
kubectl apply -f k8s/deployment.yaml -n rex-prod
kubectl apply -f k8s/service.yaml -n rex-prod

# Watch rollout — falha em 5min = rollback automático
kubectl rollout status deployment/rex-guard -n rex-prod --timeout=5m
```

Se `rollout status` falhar:
```bash
kubectl rollout undo deployment/rex-guard -n rex-prod
kubectl logs -l app=rex-guard -n rex-prod --tail=200 --previous
# Investigar antes de retry. Falha em produção não vira "tenta de novo".
```

### 4. Frontend — Firebase Hosting

```bash
cd frontend/
npm ci && npm run build

# Deploy com channel — production é gate manual
firebase hosting:channel:deploy "preview-${IMAGE_TAG}" --expires 7d
# Validar visualmente. Se OK:
firebase deploy --only hosting:production
```

### 5. Smoke test pós-deploy

```bash
# P99 latency check (precisa < 50ms)
hey -n 1000 -c 50 -m POST \
  -H "Authorization: Bearer ${SMOKE_TEST_JWT}" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"smoke test","context":"validation"}' \
  https://rex-guard.foundlab.com.br/v1/inference \
  | grep -E "99%|Slowest|Fastest"

# SealedRecibo gerado?
LAST_DECISION_ID=$(curl -s https://rex-guard.foundlab.com.br/v1/last-decision \
  -H "Authorization: Bearer ${SMOKE_TEST_JWT}" | jq -r .decision_id)

# Audit trail registrou no BigQuery?
bq query --use_legacy_sql=false \
  "SELECT decision_id, sealed_at FROM \`${PROJECT_ID}.audit_trail.recibos_sealed\` \
   WHERE decision_id = '${LAST_DECISION_ID}' LIMIT 1"
```

Se P99 > 50ms ou audit trail vazio: **rollback imediato**. SLA violado é regression report obrigatório.

## Rollback — procedure

```bash
# GKE
kubectl rollout undo deployment/rex-guard -n rex-prod
kubectl rollout status deployment/rex-guard -n rex-prod --timeout=3m

# Firebase Hosting
firebase hosting:rollback --only production

# Notificar canal #incident-response com:
# - Commit SHA da versão problemática
# - Sintoma observado (P99, error rate, audit miss)
# - Window de impacto
```

## Output Contract — release notes

Após deploy bem-sucedido, gerar release note em `releases/rex-guard-${IMAGE_TAG}.md`:

```markdown
# REX Guard Release ${IMAGE_TAG}
**Date**: <YYYY-MM-DD HH:MM BRT>
**Deployer**: <github_user>
**Commit**: <full_sha>

## Critical Gaps Status
- CG-001: <CLOSED|OPEN — explicação>
- CG-002: <CLOSED|OPEN — explicação>
- CG-003: <CLOSED|OPEN — explicação>

## Performance
- P99 inference: <X>ms (SLA: < 50ms)
- Audit write success rate: <X>%

## Regulatory mapping
- BCB 538/2025: <compliant|gap>
- LGPD Art. 18 VI: <compliant|gap>

## Rollback plan
- Previous SHA: <sha>
- Rollback ETA: <X>min
```

## Boundaries (CRITICAL)

- **NUNCA** deploy com qualquer CG aberto sem RFC explícito autorizando o risco
- **NUNCA** usar tag `:latest` em produção
- **NUNCA** pular smoke test pós-deploy — Zero-Persistence é contrato, não promessa
- **NUNCA** fazer build local em ambiente não-Linux sem `buildx` cross-compile
- **NUNCA** misturar credenciais Bradesco e BTG no mesmo deploy/secret manager
- **SEMPRE** registrar deploy no audit trail, mesmo se for rollback
- **SEMPRE** validar P99 contra SLA antes de marcar deploy como sucesso
- **SEMPRE** testar shred_key() real (não simulado) em staging antes de promover
