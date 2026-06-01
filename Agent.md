# FoundLab — CoS Agent (Chief of Staff) · Spec v0.1

> **Status:** Blueprint executável. Não é produção até as validações de pré-flight passarem.
> **Invariante mestre:** o LLM é **advisory**. `decision.status` é **rule-based e fail-closed** — nunca sai do modelo.
> **Stack-alvo:** ADK (Agent Development Kit) + Gemini Enterprise Agent Platform / Agent Runtime · GCP `foundlab-ati`.

-----

## 1. O que é (e o que não é)

O CoS sintetiza inputs estratégicos, operacionais e regulatórios em um **briefing executivo** para Alex/Raissa.
Ele **propõe**; ele **não decide**, **não aprova deploy**, **não declara conformidade**.

- **É:** orquestrador advisory que produz um *candidate briefing* com classe de evidência em cada afirmação.
- **Não é:** autoridade de decisão. Toda saída passa por um **Decision Gate determinístico** antes de virar entregável.

Isso é o mesmo contrato do REX Guard aplicado a um agente de produtividade: `input → candidate → contrato de validação → decision artifact`.

-----

## 2. Arquitetura

```
        ┌─────────────── inputs (sanitizados, identity-aware) ───────────────┐
        │  calendário · Slack · repos · pipeline · regulatório · finanças     │
        └────────────────────────────────────────────────────────────────────┘
                                      │   (Python tools wrap APIs; nada cru pro modelo)
                                      ▼
   ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  ┌──────────────────────┐
   │ STRATEGIST   │  │ OPERATOR     │  │ COMPLIANCE       │  │ EVIDENCE/RISK AUDITOR │   ← especialistas (advisory)
   │ visão/comerc.│  │ delivery/ETA │  │ BCB/LGPD/DORA    │  │ classifica evidência  │
   └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  └───────────┬──────────┘
          └─────────────────┴────────────┬──────┴──────────────────────-─┘
                                          ▼
                              ┌────────────────────────┐
                              │ COORDINATOR (CoS, LLM)  │  ← sintetiza um *candidate briefing*
                              └───────────┬────────────┘
                                          ▼
                              ╔════════════════════════╗
                              ║  DECISION GATE (código) ║  ← determinístico, fail-closed
                              ║  valida evidência·stub· ║     define decision.status
                              ║  model·owner·overclaim  ║     (LLM NUNCA toca aqui)
                              ╚═══════════╤════════════╝
                                          ▼
                                Briefing assinado + decision artifact
```

Especialistas e coordenador são **LLM**. O Decision Gate é **Python puro**. Essa fronteira é a tese inteira.

-----

## 3. Config declarativa (`cos_agent.config.json`)

```json
{
  "name": "foundlab_chief_of_staff",
  "version": "0.1",
  "project": "foundlab-ati",
  "region": "southamerica-east1",
  "_validation": {
    "models": "VALIDAR cada model string em `gcloud ai models list` (ou Model Garden) ANTES de rodar. NÃO assumir nomes — incidente gemini-3-flash. Gate recusa model fora da allowlist.",
    "iam": "Tools identity-aware via tool_context (OAuth). Agente só lê dado autorizado ao usuário logado.",
    "secrets": "Nenhum segredo no prompt/sink. Secret Manager apenas."
  },
  "models": {
    "reasoning":  "${COS_MODEL_REASONING}",
    "synthesis":  "${COS_MODEL_SYNTHESIS}",
    "fast":       "${COS_MODEL_FAST}"
  },
  "allowlisted_models": ["${COS_MODEL_REASONING}", "${COS_MODEL_SYNTHESIS}", "${COS_MODEL_FAST}"],
  "specialists": [
    { "name": "strategist", "model": "reasoning",
      "instruction": "Advisor estratégico FoundLab. Posicionamento, comercial, fundraising, board Mira Ativa. NÃO inventar números; marcar lacuna como PENDING." },
    { "name": "operator", "model": "synthesis",
      "instruction": "Delivery lead. ETA, blockers, estado de REX Guard/Permaneo. Reporta fato observável; ETA é projeção, marcar como tal." },
    { "name": "compliance", "model": "reasoning",
      "instruction": "Escopo regulatório: BCB 538/2025, LGPD, DORA, EU AI Act. Linguagem de controle técnico, nunca declaração de conformidade autônoma." },
    { "name": "evidence_auditor", "model": "fast",
      "instruction": "Classifica TODA afirmação dos demais em classe de evidência. Sinaliza stub/mock. Rebaixa overclaim. Não produz conteúdo novo — só audita." }
  ],
  "coordinator": {
    "name": "chief_of_staff", "model": "synthesis",
    "instruction": "Sintetiza os especialistas em um candidate briefing. Cada afirmação carrega evidence_class. Declarar limitações. Proibido inflar hipótese a fato.",
    "produces": "candidate_briefing"
  },
  "tools": {
    "wrap": "Toda API (Calendar, Slack, repos, BigQuery, billing) via Python tool que sanitiza saída antes do modelo ver.",
    "identity_aware": true,
    "no_raw_api_to_model": true
  },
  "memory": {
    "service": "ADK MemoryService | persistência gerenciada (Firestore/Cloud SQL)",
    "scope": "feedback estratégico ao longo do tempo; sem PII crua; sem segredo"
  },
  "decision_gate": {
    "deterministic": true,
    "llm_may_set_status": false,
    "evidence_classes": ["EVIDENCED","INFERRED","HIPOTESE","NAO_AVALIADA","EXTERNA_PENDENTE","DECLARADA"],
    "rules": [
      "Toda claim sem evidence_class válida → REJECTED.",
      "Qualquer item com stub=true rotulado como produção → REJECTED (o caso mock/BURN_ENGINE).",
      "Risco severidade alta sem owner → BLOCK.",
      "Model string fora de allowlisted_models → REFUSE (fail-closed, não roda).",
      "Claim regulatória em tom de conformidade autônoma → rebaixar para 'controle técnico compatível'.",
      "Faltou input crítico → INSUFFICIENT_DATA (nunca preencher com suposição)."
    ],
    "status_enum": ["APPROVED","APPROVED_WITH_CONDITIONS","REJECTED","INSUFFICIENT_DATA","BLOCK"]
  }
}
```

-----

## 4. Esqueleto ADK (mínimo)

> ⚠️ A superfície de API abaixo **espelha o sample do ADK que você me passou** (`LlmAgent`, `sub_agents`,
> `instruction`, `model`, `description`). O ADK evolui rápido — **valide import paths e assinaturas no
> doc atual** (`github.com/google/adk-python`) antes de rodar. Eu não invento método de ADK que não posso confirmar.

```python
import os
from google.adk.agents import LlmAgent

def model(key: str) -> str:
    """Resolve + valida model string. Fail-closed: sem allowlist, não sobe."""
    allow = set(filter(None, os.environ.get("COS_ALLOWLISTED_MODELS", "").split(",")))
    m = os.environ[{"reasoning":"COS_MODEL_REASONING",
                    "synthesis":"COS_MODEL_SYNTHESIS",
                    "fast":"COS_MODEL_FAST"}[key]]
    if m not in allow:                       # <- impede o "gemini-3-flash" silencioso
        raise RuntimeError(f"model '{m}' fora da allowlist — valide em `gcloud ai models list`")
    return m

strategist       = LlmAgent(name="strategist",       model=model("reasoning"),  instruction="...")
operator         = LlmAgent(name="operator",         model=model("synthesis"),  instruction="...")
compliance       = LlmAgent(name="compliance",       model=model("reasoning"),  instruction="...")
evidence_auditor = LlmAgent(name="evidence_auditor", model=model("fast"),       instruction="...")

chief_of_staff = LlmAgent(
    name="chief_of_staff",
    model=model("synthesis"),
    instruction="Coordene os especialistas e produza um CANDIDATE briefing. "
                "Cada afirmação carrega evidence_class. NÃO defina status — isso é do gate.",
    description="CoS advisory da FoundLab; saída é candidata até passar pelo Decision Gate.",
    sub_agents=[strategist, operator, compliance, evidence_auditor],
)

# O gate é Python puro, FORA do agente. O LLM nunca o executa.
from cos_gate import decision_gate          # implementa as rules da §3
def run(inputs: dict) -> dict:
    candidate = chief_of_staff.run(inputs)   # advisory  (assinatura: confirmar no ADK atual)
    return decision_gate(candidate)          # determinístico → decision artifact
```

-----

## 5. Contrato de saída (briefing + decisão)

```json
{
  "briefing": {
    "sections": [
      { "title": "string",
        "claims": [
          { "text": "string", "evidence_class": "EVIDENCED|INFERRED|HIPOTESE|...",
            "source": "repo:arquivo:linha | tool | externo", "stub": false }
        ]
      }
    ],
    "risks": [
      { "id": "R1", "severity": "P0|P1|P2", "owner": "string", "evidence_class": "..." }
    ]
  },
  "generated_by": "chief_of_staff (LLM, advisory)",
  "gated_by": "decision_gate (determinístico)",
  "decision": { "status": "APPROVED|APPROVED_WITH_CONDITIONS|REJECTED|INSUFFICIENT_DATA|BLOCK",
                "conditions": [], "reasons": [] }
}
```

-----

## 6. Deliverable Gate — o teu próprio checklist, virado código

(O mesmo gate que você pediu pra Anthropic ativar por padrão. Aqui ele é nosso, e roda sempre.)

1. **Intent** — resolveu o objetivo real ou a frase literal?
1. **Tool** — usou as tools quando o fato exigia dado externo/documento?
1. **Substance** — melhorou argumento, estrutura, evidência — ou só formatou?
1. **Tone** — bateu a voz e a audiência (Alex / banco / board)?
1. **Risk** — evitou retrabalho, falsa confiança, filler?
1. **Output contract** — é entregável pronto, ou rascunho fingindo de pronto?

Reprovou qualquer item → `APPROVED_WITH_CONDITIONS` no mínimo, com a condição explícita.

-----

## 7. Pré-flight (antes de chamar de produção)

- [ ] **Model strings validados** em `gcloud ai models list` e gravados em `COS_ALLOWLISTED_MODELS`. Sem isso o gate recusa subir.
- [ ] Tools com **tool_context** (OAuth) — agente só lê o que o usuário logado pode ler.
- [ ] **Zero segredo** em prompt/memória/sink; Secret Manager apenas.
- [ ] Stubs (ex.: `BURN_ENGINE_STATISTICAL=mock`) marcados `stub:true` em qualquer claim — nunca como produção.
- [ ] MemoryService sem PII crua; retenção definida.
- [ ] Decision Gate coberto por teste unitário (as 6 rules da §3) antes do primeiro briefing real.

-----

## 8. Limitações honestas

- A **assinatura exata** de `LlmAgent.run`, do `MemoryService` e do deploy em Agent Runtime **não está confirmada** por mim — ADK muda rápido. Tratar §4 como esqueleto, validar no doc atual.
- Os **nomes de modelo** são variáveis de ambiente *de propósito*. Qualquer string fixa de modelo neste arquivo seria chute — e chute de model name já nos custou caro.
- Este spec define **arquitetura e contrato**, não substitui revisão humana do primeiro briefing real.

-----

*FoundLab · Auditable Trust Infrastructure · “Don’t Trust, Verify.” · O LLM aconselha; a regra decide.*
