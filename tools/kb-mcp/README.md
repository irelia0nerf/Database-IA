# FoundLab KB — MCP Server

Entrega **ativa** da base de conhecimento Database-IA: um servidor
[MCP](https://modelcontextprotocol.io) que expõe todo o repositório como ferramentas,
para qualquer agente (Claude Code, etc.) **descobrir e puxar o conhecimento certo sob
demanda** — em vez de depender de alguém abrir um README.

> *"qual o procedimento de deploy do REX?"* → o agente chama `search_kb` → acha
> `rex-guard-deploy` → puxa o playbook completo com `get_skill`. Sem intervenção humana.

## Como funciona

- **`kb_index.py`** — engine de indexação + busca por relevância (**BM25**, sem rede,
  sem embeddings, sem API externa). Varre todos os `*.md` do repo, faz parse do
  front-matter YAML das skills e rankeia. É testável de forma isolada.
- **`server.py`** — wrapper fino que expõe o engine como tools MCP (stdio).

## Ferramentas expostas

| Tool | O que faz |
|------|-----------|
| `search_kb(query, top_k=5)` | Busca por relevância em toda a base. **Comece sempre por aqui.** |
| `list_skills()` | Lista as 18 skills (nome, categoria, descrição, caminho) |
| `get_skill(name)` | Conteúdo completo de uma skill (por nome ou slug da pasta) |
| `get_document(path)` | Conteúdo completo de qualquer doc pelo caminho relativo |
| `list_catalog()` | Catálogo completo agrupado por categoria |
| `refresh_index()` | Reconstrói o índice após editar arquivos |

## Instalação

```bash
pip install -r tools/kb-mcp/requirements.txt
```

## Uso no Claude Code

O wiring já está em [`.mcp.json`](../../.mcp.json) na raiz do repositório. Ao abrir o
repo no Claude Code, aprove o servidor `foundlab-kb` quando solicitado. Depois, o agente
pode chamar `search_kb`, `get_skill`, etc. automaticamente.

Para registrar manualmente em outro projeto:

```bash
claude mcp add foundlab-kb -- python3 /caminho/para/Database-IA/tools/kb-mcp/server.py
```

> O servidor descobre a raiz do repo automaticamente (dois níveis acima de `server.py`).
> Para apontar para outro local, defina a variável de ambiente `KB_ROOT`.

## Teste rápido (sem o pacote mcp)

O engine roda sozinho — útil para validar o ranking:

```bash
python3 tools/kb-mcp/kb_index.py                       # estatísticas do índice
python3 tools/kb-mcp/kb_index.py "deploy do rex guard" # top-5 resultados
```

## Usar com outros LLMs (não só Claude)

MCP é um protocolo aberto e o engine é Python agnóstico de provider — há 3 caminhos:

### A) Mesmo servidor, outros clientes MCP locais (stdio)
Funciona sem mudança em **Cursor, Windsurf, VS Code (Copilot agent), Zed, Gemini CLI,
OpenAI Agents SDK**. Cada um tem seu próprio modelo por baixo; basta apontar o comando:

```bash
python3 tools/kb-mcp/server.py
```

### B) MCP remoto (HTTP) para APIs hospedadas
APIs que aceitam um **URL de MCP server** (OpenAI remote MCP, Gemini, Claude `mcp_servers`)
precisam de Streamable HTTP. O mesmo servidor serve isso via env var:

```bash
KB_TRANSPORT=streamable-http KB_HOST=0.0.0.0 KB_PORT=8000 python3 tools/kb-mcp/server.py
# endpoint MCP: http://<host>:8000/mcp
```

### C) Sem MCP — function calling nativo
Para qualquer LLM com tool/function calling, pule o MCP e chame o engine direto. Ele é
provider-neutral:

```python
from kb_index import KnowledgeBase
kb = KnowledgeBase()

# declare como tool no SDK do provider (OpenAI/Gemini/Grok) com este schema:
#   name: "search_kb", params: { query: string, top_k: int }
# e no handler:
def search_kb(query, top_k=5):
    return kb.search(query, top_k=top_k)
```

O mesmo vale para `get_skill`, `get_document`, `list_catalog`.

**Exemplo executável (Grok / xAI):** [`examples/grok_function_calling.py`](examples/grok_function_calling.py)
— usa o SDK `openai` apontado para o endpoint da xAI, com os 4 tools ligados ao engine
e um loop de tool calling pronto.

```bash
pip install openai
export XAI_API_KEY=...                 # sua chave da xAI
export GROK_MODEL=grok-4.3             # valide em https://docs.x.ai/docs/models
python3 tools/kb-mcp/examples/grok_function_calling.py "qual o procedimento de deploy do REX?"
```

> Como a API da xAI é compatível com a da OpenAI, o mesmo script roda no **OpenAI** trocando
> `XAI_BASE_URL`/`XAI_API_KEY` pelas credenciais da OpenAI e o modelo. Para **Gemini**, o
> formato de tool é diferente (function declarations), mas o handler que chama `kb_index` é idêntico.

## Por que BM25 e não embeddings?

Para ~60 documentos curados, BM25 entrega ranking excelente com **zero dependência de
rede, zero custo e zero latência de API** — coerente com o princípio fail-closed da
FoundLab (a base funciona mesmo offline/sem provider). O engine é modular: trocar o
`search()` por um índice vetorial depois é um ponto de extensão isolado, sem mexer no
`server.py`.
