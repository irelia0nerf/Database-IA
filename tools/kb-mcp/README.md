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

## Por que BM25 e não embeddings?

Para ~60 documentos curados, BM25 entrega ranking excelente com **zero dependência de
rede, zero custo e zero latência de API** — coerente com o princípio fail-closed da
FoundLab (a base funciona mesmo offline/sem provider). O engine é modular: trocar o
`search()` por um índice vetorial depois é um ponto de extensão isolado, sem mexer no
`server.py`.
