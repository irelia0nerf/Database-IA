# OpenAI.md

**Status:** Canonical base file for agents that prepare inputs for OpenAI models  
**Owner context:** FoundLab  
**Purpose:** Make upstream agents send the right inputs so OpenAI models receive clear, low-ambiguity, low-waste, production-grade instructions.

---

## 1) What this file is for

This file is a **reference layer**, not the behavior layer.

Use it to:
- normalize how other AIs package tasks before sending them to OpenAI;
- reduce ambiguity, token waste, and output drift;
- standardize output contracts, tool usage, and cost controls;
- improve first-pass quality for ChatGPT, custom GPTs, Projects, and API integrations.

Do **not** assume that attaching this file alone is enough to govern model behavior. OpenAI explicitly recommends putting **rules, tone, and workflow guidance in instructions**, while uploaded knowledge should be treated as **reference material**. Also prefer **clear, text-forward files** over complex layouts.[^gpts]

---

## 2) OpenAI doctrine: the non-negotiables

### 2.1 Behavior contract goes in instructions

For OpenAI, the highest-value control surface is the instruction layer:
- put the main instructions **at the beginning**;
- separate instructions from source material with delimiters like `###` or `"""`;
- be explicit about **context, outcome, length, format, and style**.[^prompting]

**Implication for FoundLab:**
- The database stores reusable reference material.
- The runtime prompt must still carry the active contract.

### 2.2 Reference files are not policy files

If this markdown is uploaded into a GPT or Project:
- treat it as **reference knowledge**;
- put operational rules in the instruction block, not only inside the file.[^gpts]

### 2.3 Show the target shape

OpenAI’s official guidance is clear: models respond better when shown the required output format, and examples improve reliability and parseability.[^prompting_examples]

**Operational rule:** Every non-trivial task must include either:
- a strict schema, or
- a small output example, or
- both.

### 2.4 Prefer positive constraints

Do not write only prohibitions like “don’t do X”. OpenAI recommends telling the model what it **should do instead**.[^prompting_positive]

**Bad:**
- Do not be vague.

**Good:**
- Use exactly 5 bullets, one metric per bullet, and end with a recommendation.

---

## 3) Canonical input contract for upstream agents

Any agent sending work to OpenAI should assemble input in this shape.

```json
{
  "task_id": "string",
  "objective": "What success looks like in one sentence",
  "task_type": "analysis|rewrite|spec|code|summary|classification|extraction|strategy|qa",
  "audience": "Who the answer is for",
  "deliverable": "Exact artifact expected",
  "source_material": [
    {
      "type": "text|file|url|notes",
      "content": "normalized source content or excerpt",
      "priority": "high|medium|low"
    }
  ],
  "must_include": ["required elements"],
  "must_avoid": ["forbidden behaviors or content"],
  "tone": "professional|technical|executive|direct|etc",
  "language": "pt-BR|en-US|...",
  "constraints": {
    "max_length": "optional hard cap",
    "format": "markdown|json|html|table|bullets|...",
    "citation_policy": "none|required|official-only|...",
    "tool_policy": "no-tools|allow-tools|tool-specific",
    "deadline_context": "if relevant",
    "sensitivity": "public|internal|restricted"
  },
  "output_contract": {
    "type": "freeform|json_schema|template",
    "schema": {},
    "acceptance_tests": ["objective pass/fail checks"]
  },
  "quality_bar": {
    "first_pass_required": true,
    "hallucination_tolerance": "low",
    "verbosity": "low|medium|high"
  },
  "cost_mode": "economy|balanced|quality-first",
  "model_hint": "optional"
}
```

### Minimum required fields

If upstream context is poor, still send at least:
- `objective`
- `deliverable`
- `source_material`
- `must_include`
- `constraints.format`
- `output_contract`

Without that, the model is being asked to improvise mission, structure, and acceptance criteria at the same time. That is where drift starts.

---

## 4) Canonical prompt assembly for OpenAI

Use this order.

### Layer A — Developer instruction / system contract
This is where behavior lives.

```text
ROLE
You are a [precise role] operating for FoundLab.

MISSION
Complete the task exactly as specified.

SUCCESS CRITERIA
- [criterion 1]
- [criterion 2]
- [criterion 3]

CONSTRAINTS
- [hard constraint]
- [hard constraint]

OUTPUT FORMAT
[exact structure or JSON schema expectation]
```

### Layer B — Task packet
This is the live request.

```text
TASK
[exact user objective]

AUDIENCE
[target reader/user]

DELIVERABLE
[artifact expected]

SOURCE MATERIAL
"""
[pasted or retrieved content]
"""
```

### Layer C — Example or schema
Use at least one when output precision matters.

```text
EXAMPLE OUTPUT
[short canonical example]
```

or

```json
{
  "response_format": {
    "type": "json_schema",
    "json_schema": {}
  }
}
```

---

## 5) OpenAI-specific best practices that matter in production

### 5.1 Put instructions first, then context
Official OpenAI guidance: instructions should come first, and long context should be separated with delimiters such as `###` or `"""`.[^prompting]

### 5.2 Be concrete about output
Specify:
- exact output type;
- length or cap;
- style;
- audience;
- whether citations are required;
- whether the answer may make assumptions.

OpenAI explicitly recommends being specific about **context, outcome, length, format, and style**.[^prompting_specific]

### 5.3 Show the format whenever parsing matters
If another system will consume the result, do not rely on “return JSON please” alone. OpenAI recommends showing the desired format and examples because that improves reliability.[^prompting_examples]

### 5.4 Start zero-shot, escalate only when needed
OpenAI’s official guidance: start with zero-shot, then few-shot, then fine-tune only if the task still fails consistently.[^prompting_examples]

### 5.5 Use positive directives, not only negative bans
Instead of only forbidding bad behavior, define the substitute behavior you want.[^prompting_positive]

### 5.6 Control length explicitly
OpenAI documents several output controls:
- for **Responses API**, use `max_output_tokens`;
- for **Chat Completions** with reasoning models, use `max_completion_tokens` / `max_tokens`;
- use exact length instructions and `stop` sequences when needed.[^length]

### 5.7 Prefer structured outputs over loose JSON
The API reference states that `response_format` with `json_schema` enables **Structured Outputs**, which ensures the model matches your supplied schema.[^api_structured]

**Rule:** if the result feeds code, workflow automation, evaluators, or databases, prefer `json_schema` over plain prose.

### 5.8 If you use JSON mode, still instruct JSON explicitly
OpenAI warns that JSON mode alone is not enough; you should explicitly instruct the model to produce JSON, otherwise requests may behave poorly.[^runs_json]

### 5.9 Validate tool arguments server-side
OpenAI’s API reference explicitly warns that model-generated function arguments may be invalid or include hallucinated parameters. Always validate before execution.[^api_tools]

### 5.10 Prefer `developer` instructions for newer chat models
The API reference states that with `o1` models and newer, `developer` messages replace previous `system` messages for top-level instructions.[^api_roles]

---

## 6) Cost optimization rules for OpenAI

### 6.1 Use the smallest model that reliably passes the task
OpenAI recommends using the latest, most capable models for best results, but pricing also differentiates flagship, mini, and nano tiers. Route by task complexity, not ego.[^prompting_latest][^pricing]

**Recommended routing heuristic:**
- `quality-first`: flagship reasoning model;
- `balanced`: mini model;
- `economy`: nano or equivalent low-cost model for simple classification, extraction, routing, or formatting.

### 6.2 Compress context before sending
Do not dump raw source material if you can normalize it first.

Upstream agents should:
- strip boilerplate;
- deduplicate repeated paragraphs;
- keep only the passages relevant to the objective;
- convert slides/PDF clutter into plain text notes where possible.

This aligns with OpenAI’s recommendation to use clear, text-forward reference material.[^gpts]

### 6.3 Reuse stable prompt prefixes
OpenAI’s pricing page shows discounted **cached input** pricing for supported models, so repeated static instructions can reduce cost when reused consistently.[^pricing]

**Rule:** keep the stable part of the instruction block stable.

### 6.4 Use Batch for asynchronous, high-volume work
OpenAI’s pricing page states that Batch can reduce cost by 50% for inputs and outputs in exchange for asynchronous execution.[^pricing]

Use it for:
- nightly backfills;
- large classification queues;
- document normalization at scale;
- evaluation jobs.

### 6.5 Cap verbosity on purpose
OpenAI documents that shorter outputs reduce cost and latency, and that GPT-5 family models support controls such as `verbosity` and `reasoning.effort`.[^length]

**Operational rule:**
- default to `verbosity: low` for pipeline tasks;
- raise only when reasoning trace density or narrative quality is actually needed.

---

## 7) Security and deployment rules

### 7.1 Never expose API keys client-side
OpenAI’s official security guidance: never deploy API keys in browsers or mobile apps; route requests through your backend.[^key_safety]

### 7.2 One key per human / service boundary
OpenAI recommends a unique API key per team member and warns against sharing keys.[^key_safety]

### 7.3 Never trust model output as executable truth
For production systems:
- validate schema;
- validate enums;
- sanitize strings;
- verify tool permissions;
- fail closed on malformed outputs.

This is especially mandatory when using function/tool calling, because arguments may be hallucinated.[^api_tools]

---

## 8) How to package this for ChatGPT, GPTs, Projects, and API

### 8.1 ChatGPT Projects
OpenAI says Projects keep chats, files, and custom instructions together so ChatGPT stays on-topic for repeated work.[^projects]

**Use Projects when:**
- the workflow is ongoing;
- the same corpus is reused;
- you need persistent instruction + file context.

### 8.2 Custom GPTs
OpenAI’s GPT guidance says:
- use uploaded knowledge as reference material;
- keep instructions as the source of behavior;
- prefer text-forward files;
- test in Preview after upload.[^gpts]

### 8.3 Playground prompt management
OpenAI now provides project-level prompt management with version history and one-click rollback, which is useful for experimentation and production hardening.[^prompt_mgmt]

**Use it for:**
- prompt versioning;
- A/B prompt evaluation;
- rollback after regressions;
- freezing known-good prompt IDs.

### 8.4 API integrations
Prefer the API when you need:
- deterministic contracts;
- backend security;
- schema enforcement;
- tool orchestration;
- observability and evaluation loops.

---

## 9) FoundLab operating pattern for upstream agents

When an upstream AI receives FoundLab material, it should execute this pipeline:

1. **Ingest**  
   Extract only the relevant parts of the source.

2. **Classify**  
   Determine task type: strategy, code, review, extraction, rewrite, investor narrative, regulatory brief, etc.

3. **Normalize**  
   Convert messy content into text-forward context blocks.

4. **Contract**  
   Build explicit objective, constraints, acceptance tests, and output schema.

5. **Route**  
   Choose model tier by `cost_mode` and task difficulty.

6. **Constrain**  
   Apply length caps, schema, citations, and tool policy.

7. **Execute**  
   Send to OpenAI with clear developer instructions first.

8. **Validate**  
   Check structure, completeness, and hallucination risk before downstream use.

---

## 10) Anti-patterns

Do not do this:
- send only “help me with this” plus a large attachment;
- use reference files as the only place where hard rules live;
- ask for JSON without schema when machines will consume it;
- paste huge duplicated context blocks;
- use only prohibitions without telling the model what to do instead;
- execute tool calls without validation;
- expose API keys in client apps;
- use a flagship reasoning model for trivial classification at scale.

---

## 11) Canonical templates

### Template A — high-quality manual prompt for ChatGPT / Project / GPT

```markdown
ROLE
You are a FoundLab AI Engineering Operator specialized in converting raw materials into high-performance LLM instructions.

OBJECTIVE
Transform the provided source material into a production-grade prompt for OpenAI.

SUCCESS CRITERIA
- Preserve mission fidelity
- Minimize ambiguity
- Reduce token waste
- Produce a first-pass usable result

CONSTRAINTS
- Use explicit structure
- Prefer concise language
- Include only necessary context
- Return the result in the requested format

TASK
Create a prompt for the following deliverable: [DELIVERABLE]

AUDIENCE
[AUDIENCE]

SOURCE MATERIAL
"""
[PASTED CONTENT]
"""

REQUIRED OUTPUT
1. Final prompt
2. Recommended model tier
3. Suggested parameters
4. Risks / failure modes
```

### Template B — strict API contract

```json
{
  "developer_instruction": {
    "role": "FoundLab AI Engineering Operator",
    "mission": "Convert source material into a precise OpenAI-ready prompt",
    "constraints": [
      "Minimize ambiguity",
      "Minimize token waste",
      "Use exact output structure",
      "Do not invent missing facts"
    ]
  },
  "task_packet": {
    "objective": "",
    "audience": "",
    "deliverable": "",
    "source_material": ""
  },
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "openai_prompt_packet",
      "schema": {
        "type": "object",
        "properties": {
          "final_prompt": { "type": "string" },
          "model_tier": { "type": "string" },
          "parameters": {
            "type": "object",
            "properties": {
              "temperature": { "type": "number" },
              "max_output_tokens": { "type": "number" }
            },
            "required": ["temperature", "max_output_tokens"],
            "additionalProperties": false
          },
          "risks": {
            "type": "array",
            "items": { "type": "string" }
          }
        },
        "required": ["final_prompt", "model_tier", "parameters", "risks"],
        "additionalProperties": false
      }
    }
  }
}
```

---

## 12) Bottom line

If another AI is preparing work for OpenAI, the winning pattern is simple:

- keep **behavior** in instructions;
- keep **reference material** in text-forward files;
- specify **objective + constraints + output contract**;
- use **schema or examples** when precision matters;
- validate any tool/function arguments before execution;
- cap length and route to the cheapest model that still clears the bar.

This is the difference between “LLM chatting” and production-grade prompt engineering.

---

## Sources (official OpenAI)

[^prompting]: OpenAI Help Center — *Best practices for prompt engineering with the OpenAI API* (instructions first; delimiters; specificity): https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api
[^prompting_specific]: OpenAI Help Center — *Best practices for prompt engineering with the OpenAI API* (be specific about context, outcome, length, format, style): https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api
[^prompting_examples]: OpenAI Help Center — *Best practices for prompt engineering with the OpenAI API* (show format through examples; zero-shot → few-shot → fine-tune): https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api
[^prompting_positive]: OpenAI Help Center — *Best practices for prompt engineering with the OpenAI API* (say what to do, not only what not to do): https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api
[^prompting_latest]: OpenAI Help Center — *Best practices for prompt engineering with the OpenAI API* (use the latest, most capable model for best results): https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api
[^key_safety]: OpenAI Help Center — *Best Practices for API Key Safety*: https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety
[^prompt_mgmt]: OpenAI Help Center — *Prompt management in Playground* (project-level prompts, version history, rollback): https://help.openai.com/en/articles/9824968-prompt-management-in-playground
[^projects]: OpenAI Help Center — *Projects in ChatGPT* (group chats, files, instructions in one workspace): https://help.openai.com/en/articles/10169521-projects-in-chatgpt
[^gpts]: OpenAI Help Center — *Creating and editing GPTs* (knowledge as reference; rules in instructions; prefer text-forward files): https://help.openai.com/en/articles/8554397-creating-and-editing-gpts
[^api_roles]: OpenAI API Reference — *Chat* (`developer` messages replace `system` for newer models): https://developers.openai.com/api/reference/resources/chat
[^api_tools]: OpenAI API Reference — *Chat* (tool/function arguments may be invalid or hallucinated; validate them): https://developers.openai.com/api/reference/resources/chat
[^api_structured]: OpenAI API Reference — *Chat / response_format* (Structured Outputs via `json_schema`): https://developers.openai.com/api/reference/resources/chat
[^runs_json]: OpenAI API Reference — *Runs / response_format* (JSON mode caveat; explicitly instruct JSON): https://platform.openai.com/docs/api-reference/runs
[^length]: OpenAI Help Center — *Controlling the length of OpenAI model responses* (`max_output_tokens`, `max_completion_tokens`, stop sequences, verbosity, reasoning effort): https://help.openai.com/en/articles/5072518-controlling-the-length-of-openai-model-responses
[^pricing]: OpenAI API Pricing (cached input pricing, Batch -50%, model tier differences): https://openai.com/api/pricing/
