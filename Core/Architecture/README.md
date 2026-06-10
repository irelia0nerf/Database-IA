# Architecture — Design e Especificações

Como os sistemas da FoundLab são desenhados — do visual ao contrato de decisão dos agentes.

| Documento | O que cobre |
|-----------|-------------|
| [design-system.md](design-system.md) | Design system Veritas: linguagem visual, voz, tipografia, componentes e tom |
| [agent-spec.md](agent-spec.md) | Spec do **CoS Agent** (Chief of Staff). LLM é advisory; `decision.status` é rule-based e fail-closed. Arquitetura de especialistas + Decision Gate determinístico |
| [arquitetura.md](arquitetura.md) | Arquitetura técnica de stack e deployment |

> **Invariante mestre (agent-spec):** o LLM **propõe**; ele **não decide**, não aprova
> deploy, não declara conformidade. Toda saída passa por um Decision Gate em código puro.
