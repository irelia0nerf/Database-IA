## Melhores Práticas por Modelo (2026)

### Grok (xAI)
- Front-load system prompt e few-shot para maximizar prompt caching (use x-grok-conv-id estável).
- Estrutura XML/Markdown headings + explicit task/constraints/output format.
- Exigir evidence-based reasoning e “think step-by-step” quando aplicável.
- Evitar modificação de mensagens anteriores.

### ChatGPT / GPT (OpenAI)
- Instruções no início + delimitadores ### ou """.
- Positive instructions (o que fazer, nunca só o que não fazer).
- Few-shot com exemplos perfeitos; use latest model + temperature 0 para tarefas factuais.
- Leading words para código (ex: “import numpy as np”).

### Gemini 3.0 (Google)
- Seja preciso e direto; evite verbosidade desnecessária.
- Use tags XML consistentes (<role>, <context>, <task>, <constraints>, <output_format>).
- Coloque contexto longo primeiro; instruções finais no fim.
- Explicit: “Responda apenas com fatos do contexto fornecido; nada de especulação”.

### Claude (Anthropic)
- XML tags são rei (<instructions>, <examples>, <document>, <output>).
- Few-shot dentro de <examples> tags; positive examples.
- Role + Tone + Detailed Task Description + Rules + Prefill (se necessário).
- Adaptive thinking + effort level (high/xhigh para tarefas complexas).

### v0.dev (Vercel)
- Template obrigatório de 3 partes:
  1. Build [product surface: componentes, dados, ações]
  2. Used by [who], in [what moment], to [what decision/outcome]
  3. Constraints: platform, visual tone, layout, libraries, taste.
- Seja extremamente específico em componentes e restrições para reduzir iterações e custo.

## Refinamento Final
- Teste o prompt gerado com o LLM-alvo antes de entregar.
- Registre hash do prompt gerado via Veritas 2.0.
- Output sempre em formato estruturado para ingestão automática pelo Guardian AI.
