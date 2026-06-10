# Skills — Biblioteca de Especialidades

Especialidades reutilizáveis para agentes de IA. Cada skill é **auto-contida** em
`<Categoria>/<nome-da-skill>/SKILL.md`, com front-matter YAML (`name`, `description`)
que define quando ela deve ser acionada.

São **18 skills** em 6 categorias.

---

## [AI-Development/](AI-Development/) — Desenvolvimento com IA
| Skill | Para quê |
|-------|----------|
| [claude-code-expert](AI-Development/claude-code-expert/SKILL.md) | Maximizar produtividade no Claude Code: hooks, MCPs, sub-agentes, CLAUDE.md |
| [claude-code-guide](AI-Development/claude-code-guide/SKILL.md) | Referência de configuração e uso avançado do Claude Code |
| [agent-memory-systems](AI-Development/agent-memory-systems/SKILL.md) | Arquitetura de memória de agentes: o difícil é recuperar a memória certa na hora certa |
| [audit-context-building](AI-Development/audit-context-building/SKILL.md) | Análise linha-a-linha para construir contexto arquitetural antes de achar bug/vuln |

## [Cloud-Infrastructure/](Cloud-Infrastructure/) — Infraestrutura Cloud
| Skill | Para quê |
|-------|----------|
| [cloud-devops](Cloud-Infrastructure/cloud-devops/SKILL.md) | AWS/Azure/GCP, Kubernetes, Terraform, CI/CD, observabilidade |
| [gcp-cloud-run](Cloud-Infrastructure/gcp-cloud-run/SKILL.md) | Workloads stateless em containers no Cloud Run |
| [google-cloud-waf](Cloud-Infrastructure/google-cloud-waf/SKILL.md) | Segurança via Google Cloud Well-Architected Framework (IAM, rede, dados) |
| [cloud-penetration-testing](Cloud-Infrastructure/cloud-penetration-testing/SKILL.md) | Pentest de infra cloud (Azure, AWS, GCP) |
| [claude-win11-speckit-update-skill](Cloud-Infrastructure/claude-win11-speckit-update-skill/SKILL.md) | Gerenciamento de sistema Windows 11 |

## [Security-Compliance/](Security-Compliance/) — Segurança e Compliance
| Skill | Para quê |
|-------|----------|
| [007](Security-Compliance/007/SKILL.md) | Audit de segurança, hardening, threat modeling (STRIDE/PASTA), Red/Blue Team, OWASP |
| [audit-trail-bcb538](Security-Compliance/audit-trail-bcb538/SKILL.md) | Contrato de evidência BCB 538/2025: SealedRecibo, DecisionID, Merkle chain, RFC 3161 |
| [cg-blocker-resolution](Security-Compliance/cg-blocker-resolution/SKILL.md) | Fechamento cirúrgico dos critical gaps CG-001/002/003 do REX Guard |
| [frontend-security-coder](Security-Compliance/frontend-security-coder/SKILL.md) | Código frontend seguro: prevenção de XSS, sanitização, padrões client-side |

## [Frontend-Development/](Frontend-Development/) — Frontend
| Skill | Para quê |
|-------|----------|
| [frontend-developer](Frontend-Development/frontend-developer/SKILL.md) | Componentes React 19, Next.js 15, layouts responsivos, state management |

## [Blockchain-Web3/](Blockchain-Web3/) — Blockchain / Web3
| Skill | Para quê |
|-------|----------|
| [blockchain-developer](Blockchain-Web3/blockchain-developer/SKILL.md) | Smart contracts, DeFi, NFT, DAOs e integrações blockchain enterprise |

## [Market-Research/](Market-Research/) — Pesquisa e Operações
| Skill | Para quê |
|-------|----------|
| [apify-market-research](Market-Research/apify-market-research/SKILL.md) | Pesquisa de mercado via Apify (Google Maps, Facebook, Instagram, Booking, TripAdvisor) |
| [foundlab-rfc-format](Market-Research/foundlab-rfc-format/SKILL.md) | Template canônico de RFC institucional FoundLab (RFC-POS/RFC-F2F) |
| [rex-guard-deploy](Market-Research/rex-guard-deploy/SKILL.md) | Playbook de deploy do REX Guard (GKE Autopilot, P99 < 50ms, rollback) |

---

## Como adicionar uma skill

1. Escolha a categoria certa (ou proponha uma nova).
2. Crie `Skills/<Categoria>/<nome-kebab-case>/SKILL.md`.
3. Inclua front-matter YAML com no mínimo `name` e `description` — a `description` deve
   deixar claro **quando acionar** (triggers literais ajudam muito).
4. Adicione a linha correspondente neste índice e no README da categoria.
