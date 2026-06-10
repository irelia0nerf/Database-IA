# Database-IA — Base de Conhecimento FoundLab

> Repositório central de **arquitetura, standards, modelos de prompt e biblioteca de skills**
> da **FoundLab ATI** (Auditable Trust Infrastructure) — middleware criptográfico de
> governança de IA para instituições financeiras reguladas pelo BCB.
>
> *Don't trust, verify. — O LLM aconselha; a regra decide.*

---

## O que é este repositório

Este **não é código de produção**. É o cérebro operacional da FoundLab: a fonte única
de verdade para como pensamos, escrevemos código, engenheiramos prompts, auditamos
evidência e operamos as verticais **REX Guard** e **VEX-OS**.

Quatro tipos de ativo vivem aqui:

| Ativo | O que é | Onde |
|-------|---------|------|
| **Fundamentos** | Charter do projeto, arquitetura e standards de engenharia | [`Core/`](Core/) |
| **Modelos** | Prompts canônicos, frameworks de auditoria, guias por provider de LLM | [`Models/`](Models/) |
| **Skills** | Especialidades reutilizáveis (`SKILL.md`) para agentes de IA | [`Skills/`](Skills/) |
| **Referência** | Documentação de produto/mercado e recursos estáticos | [`Reference/`](Reference/) |

---

## Quick Start — por onde começar

| Seu papel | Comece por | Depois leia |
|-----------|-----------|-------------|
| **Dev novo (eng)** | [`Core/Project-Charter/CLAUDE.md`](Core/Project-Charter/CLAUDE.md) | [`Core/Standards/`](Core/Standards/) + [`Skills/`](Skills/README.md) |
| **Engenharia de prompt** | [`Models/`](Models/README.md) | [`Core/Standards/prompt-engineering.md`](Core/Standards/prompt-engineering.md) |
| **Security / Compliance** | [`Core/Standards/security.md`](Core/Standards/security.md) | [`Skills/Security-Compliance/`](Skills/Security-Compliance/README.md) + [`Models/Founder-Framework/`](Models/Founder-Framework/README.md) |
| **Auditor externo** | [`Models/Founder-Framework/Concepts/concept.md`](Models/Founder-Framework/Concepts/concept.md) | [`Models/Founder-Framework/Audit-Prompts/`](Models/Founder-Framework/Audit-Prompts/README.md) |
| **Arquiteto** | [`Core/Architecture/`](Core/Architecture/README.md) | [`Skills/Cloud-Infrastructure/`](Skills/Cloud-Infrastructure/README.md) |

---

## Mapa do repositório

```
Database-IA/
├── Core/                       Fundamentos institucionais
│   ├── Project-Charter/        Charter executivo (CLAUDE.md, stack, compliance)
│   ├── Architecture/           Design system, spec de agente, arquitetura técnica
│   └── Standards/              Code style, testes, segurança, git, prompt engineering
│
├── Models/                     Modelos de prompt e frameworks
│   ├── Founder-Framework/      Framework de auditoria FoundLab
│   │   ├── Audit-Prompts/      Prompts auditáveis + exemplos de referência
│   │   ├── Concepts/           EAC, VEX-OS, integração Grok
│   │   └── OpenAI-Models/      Guias específicos OpenAI
│   └── Model-Comparison/       Best practices por LLM (Grok/GPT/Gemini/Claude)
│
├── Skills/                     Biblioteca de especialidades (SKILL.md)
│   ├── AI-Development/         LLMs, agentes, memória, contexto de auditoria
│   ├── Cloud-Infrastructure/   GCP, DevOps, Cloud Run, WAF, pentest
│   ├── Security-Compliance/    BCB 538, audit trail, blockers, frontend security
│   ├── Frontend-Development/   React 19, Next.js 15
│   ├── Blockchain-Web3/        Smart contracts, DeFi, Web3
│   └── Market-Research/        Apify, RFC FoundLab, deploy REX Guard
│
├── Reference/                  Documentação operacional
│   ├── REX-Guard/              Material de produto/mercado
│   └── Resources/              Arquivos estáticos (HTML)
│
└── tools/
    └── kb-mcp/                 MCP server: serve a base a agentes (busca BM25)
```

---

## Entrega ativa — MCP Server

Esta base não é só para ler: ela é **servida ativamente** a agentes via
[`tools/kb-mcp/`](tools/kb-mcp/README.md). Um MCP server expõe todo o repositório como
ferramentas (`search_kb`, `get_skill`, `get_document`…), com busca por relevância (BM25,
sem rede). Assim o agente **descobre e puxa o conhecimento certo sozinho**:

> *"qual o procedimento de deploy do REX?"* → `search_kb` → `rex-guard-deploy` → playbook completo.

O wiring para Claude Code já está em [`.mcp.json`](.mcp.json). Setup:

```bash
pip install -r tools/kb-mcp/requirements.txt
# teste o engine sem precisar do mcp:
python3 tools/kb-mcp/kb_index.py "deploy do rex guard"
```

---

## Convenções

**Nomenclatura**
- Pastas e arquivos: `kebab-case` (ex.: `cloud-devops`, `code-style.md`)
- Cada skill é auto-contida em `Skills/<Categoria>/<nome-da-skill>/SKILL.md`
- Front-matter YAML obrigatório em todo `SKILL.md` (`name`, `description`)

**Links internos**
- Use caminhos relativos a partir do arquivo atual.

**Glossário rápido**
- **ATI** — Auditable Trust Infrastructure (a infraestrutura núcleo)
- **REX Guard** — proxy reverso de segurança GenAI, fail-closed, P99 < 50ms
- **VEX-OS** — compliance OS para decisões de IA auditáveis
- **EAC** — Evidence Artifact Compiler
- **SealedRecibo / DecisionID** — primitivas do contrato de evidência (BCB 538/2025)
- **CG-001/002/003** — critical gaps (blockers) abertos do REX Guard

---

## Contexto regulatório ativo

BCB 538/2025 (enforcement desde 01/03/2026) · LGPD · DORA · EU AI Act · SOX.

---

*FoundLab Tecnologia Ltda. · Auditable Trust Infrastructure · Uso interno*
*Estrutura v2.0 · Atualizado em 2026-06-10*
