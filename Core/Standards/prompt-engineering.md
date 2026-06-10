## Ferramentas de Engenharia de Prompts – FoundLab Standard 2026 (integrar ao output)

### Ferramentas Obrigatórias para Todo Prompt Gerado
1. **Promptfoo** (promptfoo.dev) – CLI open-source para testing, red-teaming e CI/CD. Use para validar first-shot accuracy e token optimization antes de entregar. [[0]](grok://citation?card_id=668a12&card_type=citation_card&type=render_inline_citation&citation_id=0)
2. **Braintrust** (braintrust.dev) – Plataforma no-code líder para evaluation-driven iteration e production deployment. Ideal para métricas quantitativas e colaboração C-level. [[0]](grok://citation?card_id=d385a7&card_type=citation_card&type=render_inline_citation&citation_id=0)
3. **PromptHub** – Versionamento Git-style + branching para equipe FoundLab. Registre todo prompt em Veritas 2.0.
4. **LangSmith** – Tracing e debugging nativo (compatível com LangChain workflows). Use quando o prompt envolve chains ou agents.
5. **Maxim AI** – Enterprise lifecycle management com eval programático e observability (recomendado para fluxos Open Finance).
6. **Helicone** – Observability e cost-control layer (proxy para todos os LLMs).

### Fluxo Padrão do Agente FoundLab
- Input → Análise (Persona/Contexto/Tarefa/Formato)
- Geração → Promptfoo/Braintrust para eval automático
- Versionamento → PromptHub + hash Veritas 2.0
- Output final → Instruções otimizadas + relatório de métricas (tokens, accuracy, compliance score)
