# git-workflow.md
<!-- FoundLab ATI · v1.0 · 2026-04-17 -->

## Branches

### Estrutura

```
main          → produção — deploy automático via GitHub Actions
staging       → pré-produção — testes de integração e pentest
develop       → integração contínua — base para feature branches
feat/*        → novas funcionalidades
fix/*         → correções de bug
cg/*          → fechamento de compliance gaps (CG-001, CG-002, CG-003)
sec/*         → patches de segurança (P0 — bypass do processo normal permitido)
chore/*       → mudanças de infra, deps, CI, documentação
```

### Regras

- `main` e `staging` são protegidas — push direto proibido. Apenas merge via PR aprovado.
- Branch `cg/*` tem prioridade de revisão sobre qualquer outra. CGs são blockers, não roadmap.
- Branch `sec/*` pode ser mergeada com aprovação de 1 revisor (ao invés de 2) para agilizar patches P0.
- Branches vivem no máximo 5 dias úteis. Branches antigas sem atividade são deletadas sem aviso.
- Proibido rebase de branch que já foi pushed para origin sem `--force-with-lease`.

---

## Padrão de Commits — Conventional Commits

```
<tipo>(<escopo>): <descrição imperativa em português>

[corpo opcional — o quê e por quê, não como]

[rodapé opcional — refs, breaking changes]
```

### Tipos válidos

| Tipo | Quando usar |
|------|------------|
| `feat` | Nova funcionalidade que adiciona valor ao produto |
| `fix` | Correção de bug em código existente |
| `cg` | Fechamento de compliance gap (CG-001/002/003) |
| `sec` | Patch de segurança (P0/P1) |
| `perf` | Melhoria de performance sem mudança funcional |
| `refactor` | Refatoração sem mudança de comportamento externo |
| `test` | Adição ou correção de testes |
| `docs` | Documentação, ADRs, RFCs |
| `chore` | CI, deps, Terraform, configuração |
| `revert` | Reversão de commit anterior |

### Escopo — componentes ATI

`veritas` · `umbrella` · `rex-guard` · `burn-engine` · `spezzatura` · `optical-sieve` · `api` · `infra` · `auth` · `terraform`

### Exemplos

```bash
# Correto
git commit -m "cg(umbrella): implementa cryptoKeyVersions.destroy() real — fecha CG-003"
git commit -m "fix(veritas): lê chain_tip do BigQuery WORM por emit em multi-instance"
git commit -m "sec(auth): substitui localStorage por httpOnly cookies em authService"
git commit -m "feat(rex-guard): adiciona rate limiting por actorId no pipeline de inferência"
git commit -m "chore(terraform): atualiza módulo cloud-run para v3.2.1"

# Proibido
git commit -m "fix bug"
git commit -m "WIP"
git commit -m "ajustes"
git commit -m "update"
git commit -m "."
```

### Breaking Changes

```bash
git commit -m "feat(veritas)!: migra sequencer de BigQuery para Cloud Spanner TrueTime

BREAKING CHANGE: ChainEntry agora requer campo spannerTimestamp.
Clients que escrevem diretamente na tabela BigQuery precisam ser migrados.
Ref: ADR-F2F-004"
```

---

## Pull Requests

### Título do PR

Seguir o mesmo padrão de commits: `tipo(escopo): descrição`.

### Template obrigatório

Todo PR deve preencher o template em `.github/pull_request_template.md`:

```markdown
## O que este PR faz
<!-- Descrição objetiva — máximo 3 linhas -->

## Tipo de mudança
- [ ] feat — nova funcionalidade
- [ ] fix — correção de bug
- [ ] cg — fechamento de compliance gap
- [ ] sec — patch de segurança
- [ ] refactor / perf / chore / docs

## Compliance Gaps impactados
- [ ] CG-001 (policy_snapshot_hash) — [ ] fechado [ ] parcial [ ] não impactado
- [ ] CG-002 (CI/CD gate audit vectors) — [ ] fechado [ ] parcial [ ] não impactado
- [ ] CG-003 (shred_key real) — [ ] fechado [ ] parcial [ ] não impactado

## Checklist técnico
- [ ] `npm run lint` passa sem erros
- [ ] `npm test` passa com cobertura acima do mínimo por módulo
- [ ] `npm run audit:vectors` passa (obrigatório se tocou core/ ou compliance/)
- [ ] Nenhum `localStorage`/`sessionStorage` introduzido
- [ ] Nenhum secret hardcodado ou logado
- [ ] `del + gc.collect()` aplicado em todo novo uso de dado sensível em RAM
- [ ] `prevHash` lido do BigQuery WORM (nunca de state de classe)
- [ ] Trivy scan sem CRITICAL/HIGH
- [ ] ADR ou RFC atualizado se mudança arquitetural

## Como testar
<!-- Passo a passo para reproduzir e validar -->

## Referências
<!-- ADRs, RFCs, issues, PRs relacionados -->
```

### Aprovações necessárias

| Tipo de PR | Aprovações |
|------------|------------|
| `feat`, `refactor`, `chore` | 1 aprovação |
| `cg/*` (compliance gaps) | 2 aprovações |
| `sec/*` (security patches P0) | 1 aprovação (agilidade) |
| Qualquer mudança em `core/`, `compliance/` | 2 aprovações |
| Mudança em `terraform/env/prod.*` | 2 aprovações + manual apply |

---

## Checklist Antes do Merge

**Automático (CI bloqueia se falhar):**
- [ ] Lint e type check passam
- [ ] Testes unitários passam com cobertura mínima
- [ ] Trivy scan sem CRITICAL
- [ ] Checkov scan sem CRITICAL em Terraform
- [ ] `audit_vectors_v1.json` gate passa (CG-002)

**Manual (revisor verifica):**
- [ ] Sem secret, key, ou credencial no diff
- [ ] Sem `localStorage` ou `sessionStorage`
- [ ] Sem `shred_key()` simulado (grep por "console.log" próximo a "shred")
- [ ] Sem `_chain_tip_hash` lido de state de classe
- [ ] Sem `any` não justificado em TypeScript
- [ ] Sem `test.skip` sem referência a issue rastreável
- [ ] ADR/RFC atualizado se mudança arquitetural foi feita
- [ ] Mensagens de commit seguem Conventional Commits

---

## Tags e Releases

```bash
# Versão: MAJOR.MINOR.PATCH seguindo SemVer
# MAJOR: mudança breaking em contrato de API ou schema do ledger
# MINOR: nova funcionalidade backward-compatible
# PATCH: fix ou melhoria sem mudança de contrato

git tag -a v2.6.0 -m "feat: Spezzatura Engine v2.6 com decay temporal"
git push origin v2.6.0
```

Tags em `main` disparam o pipeline de release. Tags em `staging` disparam o pipeline de staging.

---

## Revert e Hotfix

```bash
# Revert via git (preferível — mantém histórico)
git revert <commit-hash> --no-edit
git commit --amend -m "revert(veritas): reverte CG-002 gate — causa falso positivo em prod"

# Hotfix em produção
git checkout main
git checkout -b sec/hotfix-jwt-storage-leak
# ... fix ...
git push origin sec/hotfix-jwt-storage-leak
# Abrir PR direto para main com label "hotfix"
# 1 aprovação suficiente para sec/*
```

---

*FoundLab · git-workflow.md v1.0 · 2026-04-17*
