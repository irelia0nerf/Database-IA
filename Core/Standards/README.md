# Standards — Padrões de Engenharia

Padrões **obrigatórios**. Não são sugestões: PRs que os violam não passam.

| Standard | Escopo |
|----------|--------|
| [code-style.md](code-style.md) | TypeScript, Prettier, ordenação de imports, nomenclatura |
| [testing.md](testing.md) | Vitest, cobertura mínima (80%), unit/integration/audit |
| [security.md](security.md) | Secrets, OWASP, fail-closed, zero-persistence |
| [git-workflow.md](git-workflow.md) | Branching, mensagens de commit, fluxo de PR |
| [prompt-engineering.md](prompt-engineering.md) | Ferramentas obrigatórias (Promptfoo, Braintrust, PromptHub…) e fluxo padrão do agente FoundLab |

> Estes arquivos eram importados pelo `CLAUDE.md` via `@.claude/rules/...`. Esse caminho
> está documentado em [`.claude/rules.md`](../../.claude/rules.md).
