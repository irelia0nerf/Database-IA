# Core — Fundamentos Institucionais

Tudo que define **como a FoundLab opera**: o charter do projeto, a arquitetura dos
sistemas e os standards de engenharia. Se há conflito entre qualquer documento do
repositório e o que está aqui, **o `Core/` prevalece**.

## Conteúdo

### [Project-Charter/](Project-Charter/)
O documento canônico do projeto.
- **[CLAUDE.md](Project-Charter/CLAUDE.md)** — visão geral da ATI, stack canônico, comandos
  de build/teste, convenções de nomenclatura, blockers ativos e princípios invariantes
  (fail-closed, zero-persistence, crypto-shredding real).

### [Architecture/](Architecture/)
Design de sistema e especificações.
- **[design-system.md](Architecture/design-system.md)** — design system Veritas (visual, voz, padrões de UI)
- **[agent-spec.md](Architecture/agent-spec.md)** — spec do CoS Agent (Chief of Staff): arquitetura advisory + Decision Gate determinístico
- **[arquitetura.md](Architecture/arquitetura.md)** — arquitetura técnica de stack e deployment

### [Standards/](Standards/)
Padrões obrigatórios de engenharia.
- **[code-style.md](Standards/code-style.md)** — TypeScript, formatação, ordenação de imports
- **[testing.md](Standards/testing.md)** — Vitest, cobertura mínima, estratégia de testes
- **[security.md](Standards/security.md)** — práticas de segurança, secrets, OWASP
- **[git-workflow.md](Standards/git-workflow.md)** — branching, commits, PRs
- **[prompt-engineering.md](Standards/prompt-engineering.md)** — ferramentas obrigatórias e fluxo padrão de engenharia de prompt
