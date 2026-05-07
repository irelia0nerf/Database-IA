---
name: foundlab-rfc-format
description: >-
  Use SEMPRE que o usuário pedir para criar, revisar ou estruturar um RFC FoundLab, documento técnico institucional, decisão arquitetural, ou qualquer artefato no formato RFC-POS-001/RFC-F2F-XXX. Triggers literais: "criar RFC", "novo RFC", "formato RFC FoundLab", "RFC honesto", "RFC-POS", "RFC-F2F", "decision document", "ADR", "documento técnico para banco". NÃO use para README, comentários de código, ou docs informais — esta skill é exclusiva para RFCs institucionais que vão para Bradesco, BTG, GCP Marketplace ou board.
---

# FoundLab RFC Format — Template Canônico

RFC honesto > RFC bonito. Documento que esconde gap morre na primeira pergunta de auditor. RFC-POS-001 e AUDIT-2026-0409 são as referências de qualidade — qualquer RFC novo precisa ter o mesmo nível de exposição honesta de trade-offs.

## Estrutura obrigatória

Toda RFC FoundLab segue 9 seções fixas. Pular seção = RFC rejeitada em review.

```markdown
# RFC-<TIPO>-<NNN>: <Título descritivo>

**Status**: Draft | Under Review | Approved | Implemented | Deprecated
**Author(s)**: <Nome> (<role>)
**Reviewers**: <Lista — incluir validadores externos quando aplicável: Glauco Sampaio, Lísias Lauretti, etc.>
**Created**: YYYY-MM-DD
**Last updated**: YYYY-MM-DD
**Target audience**: <Engineering | Compliance | Board | Bradesco | BTG | GCP>

---

## 1. Context

<2-4 parágrafos. O que existe hoje, qual é o problema operacional ou regulatório, qual é a janela de decisão. NUNCA começar com "queremos implementar X" — começar com PROBLEMA, não solução.>

## 2. Problem Statement

<1 parágrafo declarativo. Forma: "O sistema atualmente <comportamento>. Isso causa <impacto>. Sem mudança, <consequência>."

Exemplo bom:
"O REX Guard sela todas as decisões com `policy_snapshot_hash` hardcoded. Auditoria forense não consegue distinguir qual policy estava ativa em decisão histórica. Sem mudança, defesa regulatória contra contestação de decisão é impossível e BCB 538/2025 § X.Y não é atendido."

Exemplo ruim:
"Precisamos melhorar o audit trail."
>

## 3. Goals & Non-Goals

### Goals
- <Lista de 3-7 itens, mensuráveis>

### Non-Goals
- <Lista do que esta RFC NÃO se propõe a resolver. Crítico para escopo.>

## 4. Proposal

<Solução técnica. Se múltiplas opções foram consideradas, esta é a opção ESCOLHIDA. As alternativas vão na seção 5.

Subseções típicas:
- 4.1. Architecture diagram (mermaid ou referência a /docs/diagrams/)
- 4.2. Data model
- 4.3. API contract
- 4.4. Failure modes & recovery>

## 5. Alternatives Considered

<NUNCA pular esta seção. Se não há alternativas, isso é red flag.

Para cada alternativa:
- Descrição
- Pros
- Cons
- Por que NÃO foi escolhida (justificativa explícita)>

## 6. Trade-offs & Gaps

<SEÇÃO MAIS IMPORTANTE — RFC honesto.

Listar EXPLICITAMENTE:
- O que esta proposta NÃO resolve
- Que dívida técnica é introduzida
- Que assunções estão sendo feitas (e o que quebra se forem falsas)
- Custo operacional (FinOps)
- Latência adicional (com números)
- Complexidade adicional para equipe operar

Se você está com vontade de pular esta seção: pare. O auditor da Bradesco vai perguntar isso. Melhor estar escrito.>

## 7. Regulatory Mapping

<Mandatório para qualquer RFC com superfície de compliance. Tabela:

| Requirement | Source | How this RFC addresses it | Gap |
|---|---|---|---|
| <descrição> | BCB 538/2025 § X | <implementação> | <none|partial|TBD> |
| <descrição> | LGPD Art. Y | <implementação> | <none|partial|TBD> |
| <descrição> | BCB Res. 400/2024 | <implementação> | <none|partial|TBD> |

Marcar gap honestamente. "Partial" e "TBD" são aceitáveis se justificados — esconder não é.>

## 8. Validation Plan

<Como vamos provar que a RFC funciona em produção.

- Test strategy (unit, integration, E2E, chaos)
- Acceptance criteria (mensuráveis — números, não adjetivos)
- Rollback plan (specific commands/procedures)
- Observability (que métrica/log/dashboard valida sucesso)
- External validators (quem precisa assinar — Glauco? Auditor externo?)>

## 9. Decision & Next Steps

**Decision**: <Approved | Rejected | Approved with caveats>
**Decision date**: YYYY-MM-DD
**Decided by**: <Nome(s)>

### Immediate next steps
1. <Ação específica — owner — deadline>
2. <Ação específica — owner — deadline>
3. <Ação específica — owner — deadline>

### Linked artifacts
- Implementation PR: <link>
- Related RFCs: <links>
- External validations: <links/anexos>
```

## Convenção de numeração

- `RFC-POS-NNN` — Positioning / strategic
- `RFC-F2F-NNN` — Founder-to-founder / commercial
- `RFC-ENG-NNN` — Engineering / technical
- `RFC-SEC-NNN` — Security / threat modeling
- `RFC-OPS-NNN` — Operations / infrastructure
- `RFC-COMP-NNN` — Compliance / regulatory

NNN é sequencial dentro do tipo, zero-padded (001, 002, ..., 099, 100).

## Audiência → tom

- **Engineering interno**: técnico denso, gírias OK, sarcasmo OK, palavrões OK em contexto
- **Bradesco / BTG / Banco**: institucional, sem gírias, sem startup-ese, terminologia regulatória precisa
- **Board**: estratégico, com números (LTV, CAC, runway), sem profundidade técnica desnecessária
- **GCP / Marketplace**: técnico mas formal, foco em arquitetura e compliance, mapeamento WAF (Well-Architected Framework)

**NUNCA** usar o mesmo RFC para audiências diferentes sem revisão. Mistura BTG metrics em doc Bradesco = vazamento estratégico imediato.

## Output Contract — RFC pronta para review

Antes de marcar status como "Under Review":

- [ ] Todas as 9 seções preenchidas (não "TBD" em Context, Problem, Proposal)
- [ ] Pelo menos 2 alternativas consideradas
- [ ] Trade-offs & Gaps com no mínimo 3 itens explícitos
- [ ] Regulatory mapping com no mínimo BCB 538/2025 e LGPD se a RFC toca dado
- [ ] Acceptance criteria com números, não adjetivos
- [ ] Rollback plan com comandos concretos
- [ ] Reviewer externo identificado quando RFC é compliance-sensitive

## Anti-patterns — rejeição automática

RFCs com qualquer destes itens voltam para draft sem review aprofundado:

1. **"Best practice" sem justificativa**: "Vamos usar X porque é best practice" — qual é o trade-off de NÃO usar? Por que X e não Y? Argumento de autoridade não é argumento.
2. **Métricas vagas**: "Sistema mais rápido", "melhor segurança" — números ou nada.
3. **Gap section vazia**: Toda RFC tem trade-off. Se você não encontrou, você não procurou.
4. **Compliance handwaving**: "Atende BCB 538" sem mapear seção e implementação específica.
5. **Mistura de competidores**: BTG e Bradesco no mesmo doc = vazamento.
6. **Linguagem startup em RFC bancário**: "Vamos quebrar isso", "ship fast", "pivot" — fora.
7. **"Phase 2 fixes that"**: Se Phase 2 é onde o gap real é resolvido, Phase 1 não pode ser marketed como solução.

## Boundaries (CRITICAL)

- **NUNCA** publicar RFC com seção 6 (Trade-offs & Gaps) vazia ou superficial
- **NUNCA** misturar dados de cliente A em RFC destinada a cliente B
- **NUNCA** marcar status "Approved" sem assinatura registrada (data + nome)
- **NUNCA** alterar RFC após "Approved" sem incrementar versão e justificar mudança
- **SEMPRE** linkar implementation PR quando status muda para "Implemented"
- **SEMPRE** preferir RFC com gaps explícitos sobre RFC com gaps escondidos
- **SEMPRE** revisar tom contra audiência antes de enviar externamente
