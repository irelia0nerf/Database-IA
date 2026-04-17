# FoundLab ATI — CLAUDE.md
<!-- Versão: 1.0 · 2026-04-17 · Autor: Alex Bolson (Chief Architect) -->
<!-- Classificação: USO INTERNO — não compartilhar com parceiros externos -->

## Visão Geral do Projeto

**FoundLab Tecnologia Ltda.** constrói o ATI — Auditable Trust Infrastructure.
Middleware criptográfico de governança de IA para instituições financeiras reguladas pelo BCB.

Este repositório **não é um produto SaaS**. É infraestrutura crítica deployada dentro do tenant GCP do cliente via Terraform. Dados nunca saem do perímetro do cliente.

**Verticais:**
- `REX Guard` — proxy reverso de segurança GenAI, fail-closed, overhead < 50ms P99
- `VEX-OS` — compliance OS para decisões de IA auditáveis

**Regulatório ativo:** BCB 538/2025 (enforcement desde 01/03/2026), LGPD, DORA, EU AI Act, SOX.

---

## Stack Canônico

```
Runtime:          Node.js 22 ESM / Fastify 4 / TypeScript
Deploy:           GCP Cloud Run (multi-instance) / GKE Autopilot (security-plane)
Sequencer:        Cloud Spanner TrueTime — ÚNICO autorizado para VeritasChain
Ledger:           BigQuery WORM append-only — projeção analítica, não ordenação
KMS:              Cloud KMS (AES-256-GCM após upgrade) / UmbrellaKMS envelope encryption
TEE:              GCP Confidential Space (AMD SEV-SNP + Intel TDX)
AI:               Vertex AI Gemini sovereign / Guardian AI (rack RTX local)
Crypto:           SHA-256 hash-chaining / ECDSA P-256 / CRC32C integrity
IaC:              Terraform / Helm Chart v3
CI/CD:            GitHub Actions (OIDC keyless auth) / Trivy + Checkov scanning
Pagamentos:       AbacatePay (Pix BR)
Email:            Resend (relatorios@foundlab.com.br)
```

---

## Comandos de Build e Teste

```bash
# Instalação
npm ci                          # nunca npm install em CI

# Build
npm run build                   # tsc --noEmit + esbuild bundle
npm run build:check             # type check sem emit

# Testes
npm test                        # vitest run
npm run test:coverage           # vitest run --coverage (mínimo 80%)
npm run test:security           # auditores de vulnerabilidade
npm run test:integration        # testes de integração contra emuladores GCP

# Lint e Format
npm run lint                    # eslint + tsc
npm run format                  # prettier --write

# Infra
npm run terraform:plan          # terraform plan -var-file=env/prod.tfvars
npm run terraform:apply         # terraform apply (requer aprovação manual)

# Auditoria ATI
npm run audit:vectors           # executa audit_vectors_v1.json (CG-002 gate)
npm run veritas:check           # verifica integridade do hash chain no Spanner
```

---

## Convenções de Nomenclatura

### Arquivos e Diretórios

```
src/
  core/           → componentes ATI (VeritasChain, UmbrellaKMS, BurnEngine)
  proxy/          → REX Guard pipeline (OpticalSieve, policy eval, crypto seal)
  compliance/     → Spezzatura Engine, regulatory analyzers
  api/            → Fastify routes e plugins
  infra/          → clientes GCP tipados (Spanner, BigQuery, KMS)
  types/          → interfaces e DTOs — sem implementação
  utils/          → funções puras, sem side effects
test/
  unit/           → testes de unidade por módulo espelhando src/
  integration/    → testes contra emuladores ou staging
  audit/          → vetores de auditoria normativos (audit_vectors_v1.json)
terraform/
  modules/        → módulos reutilizáveis GCP
  env/            → tfvars por ambiente (dev / staging / prod)
```

### Identificadores

- Funções e variáveis: `camelCase`
- Classes e interfaces: `PascalCase`
- Constantes de módulo: `SCREAMING_SNAKE_CASE`
- Arquivos: `kebab-case.ts` (nunca PascalCase em nomes de arquivo)
- Tipos de evento Veritas: `SNAKE_UPPER` (ex: `POLICY_EVAL_START`)
- IDs de decisão: formato canônico `VEX-ADR-[COMP]-[YYYY-MM-DD]-[STATUS]-[SEQ]`

---

## Blockers Ativos — Estado Corrente

Estes gaps fecham antes de qualquer dado real de cliente. Não são roadmap.

| Gap | Problema | Estado |
|-----|----------|--------|
| CG-001 | `policy_snapshot_hash` hardcoded | PR open — BLOCKER |
| CG-002 | CI/CD gate `audit_vectors_v1.json` | PENDING — BLOCKER |
| CG-003 | `shred_key()` simulado — não chama `cryptoKeyVersions.destroy()` real | NOT_IMPLEMENTED — BLOCKER |

---

## Princípios Invariantes

1. **Fail-closed** — KMS ou BigQuery indisponível → bloqueia inferência. Nunca fail-open.
2. **Zero-persistence é física** — `del + gc.collect()` após cada uso de dado sensível. Não é mantra, é a única implementação válida.
3. **Crypto-shredding real** — `shred_key()` sem chamar `cryptoKeyVersions.destroy()` é CG-003, não solução.
4. **Mitigates, nunca resolves** — o Retention Paradox (BCB × LGPD) é mitigado arquiteturalmente.
5. **`_chain_tip_hash` nunca como state de classe** — em multi-instance Cloud Run quebra o hash chain. Leitura obrigatória do BigQuery WORM por emit.
6. **OFAC/SANCTION/TERROR avaliados antes de qualquer scoring** — é gate, não feature.

---

## Rules Importadas

@.claude/rules/code-style.md
@.claude/rules/testing.md
@.claude/rules/security.md
@.claude/rules/git-workflow.md

---

*FoundLab · dont trust, verify. · CLAUDE.md v1.0 · 2026-04-17*
