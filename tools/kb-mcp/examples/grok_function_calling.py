"""
grok_function_calling.py — Caminho C: usar a base de conhecimento FoundLab com
Grok (xAI) via function calling nativo, SEM MCP.

A API da xAI é compatível com o SDK da OpenAI, então usamos o cliente `openai`
apontado para o endpoint da xAI. Os tools são ligados diretamente ao engine
provider-neutral `kb_index.py` — o mesmo que alimenta o MCP server.

Setup:
    pip install openai
    export XAI_API_KEY=...            # sua chave da xAI
    # opcional:
    export GROK_MODEL=grok-4.3        # valide em https://docs.x.ai/docs/models
    export XAI_BASE_URL=https://api.x.ai/v1

Uso:
    python3 tools/kb-mcp/examples/grok_function_calling.py "qual o procedimento de deploy do REX?"

O modelo decide quando chamar search_kb/get_skill/etc., o script executa contra a
base local e devolve o resultado — o Grok sintetiza a resposta final com a fonte.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Importa o engine da base (pasta pai: tools/kb-mcp/).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kb_index import KnowledgeBase

try:
    from openai import OpenAI
except ImportError:
    raise SystemExit("Pacote 'openai' não instalado. Rode: pip install openai")

# --- Base de conhecimento (engine provider-neutral) ---------------------------
_kb = KnowledgeBase()


def _search_kb(query: str, top_k: int = 5) -> str:
    return json.dumps(_kb.search(query, top_k=top_k), ensure_ascii=False)


def _get_skill(name: str) -> str:
    return _kb.get_skill(name) or f"Skill não encontrada: {name!r}"


def _get_document(path: str) -> str:
    return _kb.get_by_path(path) or f"Documento não encontrado: {path!r}"


def _list_catalog() -> str:
    return json.dumps(_kb.catalog(), ensure_ascii=False)


# Dispatch: nome da tool -> função Python.
DISPATCH = {
    "search_kb": _search_kb,
    "get_skill": _get_skill,
    "get_document": _get_document,
    "list_catalog": _list_catalog,
}

# Schemas no formato de tools da OpenAI (que a xAI aceita).
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_kb",
            "description": "Busca por relevância (BM25) em toda a base de conhecimento "
                           "FoundLab. Use primeiro para achar procedimentos, padrões, "
                           "conceitos ou playbooks. Retorna caminho, score e trecho.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "O que procurar"},
                    "top_k": {"type": "integer", "description": "Quantos resultados (default 5)"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_skill",
            "description": "Retorna o conteúdo completo de uma skill pelo nome ou slug "
                           "(ex.: rex-guard-deploy). Use após search_kb.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_document",
            "description": "Retorna o conteúdo completo de um documento pelo caminho "
                           "relativo ao repo (ex.: Core/Standards/security.md).",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_catalog",
            "description": "Catálogo completo da base agrupado por categoria.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def run(question: str) -> str:
    # Fail-closed: sem chave, não roda (mesmo princípio do CLAUDE.md).
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        raise SystemExit("XAI_API_KEY não definida — exporte sua chave da xAI antes de rodar.")

    client = OpenAI(
        api_key=api_key,
        base_url=os.environ.get("XAI_BASE_URL", "https://api.x.ai/v1"),
    )
    model = os.environ.get("GROK_MODEL", "grok-4.3")  # valide em https://docs.x.ai/docs/models

    messages = [
        {"role": "system", "content": "Você é um assistente FoundLab. Use as ferramentas para "
                                      "buscar na base de conhecimento antes de responder. "
                                      "Cite o caminho do arquivo-fonte de cada afirmação."},
        {"role": "user", "content": question},
    ]

    # Loop de tool calling: o modelo pode encadear várias buscas.
    for _ in range(6):  # teto de segurança contra loop infinito
        resp = client.chat.completions.create(model=model, messages=messages, tools=TOOLS)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content or ""
        # Anexa a mensagem do assistente (com os tool_calls) ao histórico.
        messages.append(msg)
        for call in msg.tool_calls:
            fn = DISPATCH.get(call.function.name)
            args = json.loads(call.function.arguments or "{}")
            result = fn(**args) if fn else f"Tool desconhecida: {call.function.name}"
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })
    return "Limite de iterações de tool calling atingido."


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "qual o procedimento de deploy do REX Guard?"
    print(run(q))
