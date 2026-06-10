"""
server.py — MCP server da base de conhecimento FoundLab (Database-IA).

Expõe a base como ferramentas MCP para que qualquer agente (Claude Code, etc.)
descubra e puxe o conhecimento certo sob demanda, em vez de depender de alguém
abrir um README. Toda a lógica de busca vive em kb_index.py (testável sem o mcp).

Execução:
    pip install -r requirements.txt
    python3 server.py            # transporte stdio (padrão p/ Claude Code)

Wiring no Claude Code: ver .mcp.json na raiz do repositório.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Garante que kb_index é importável independentemente do CWD com que o
# Claude Code (ou outro host MCP) lança o servidor.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from kb_index import KnowledgeBase

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # mensagem clara em vez de stack trace críptico
    raise SystemExit(
        "Pacote 'mcp' não instalado. Rode: pip install -r tools/kb-mcp/requirements.txt"
    ) from exc

mcp = FastMCP("foundlab-kb")

# Índice construído uma vez no startup. Rebuild explícito via refresh_index.
_kb = KnowledgeBase()


def _json(data) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
def search_kb(query: str, top_k: int = 5) -> str:
    """Busca por relevância (BM25) em TODA a base de conhecimento FoundLab.

    Use isto primeiro quando precisar de qualquer procedimento, padrão, conceito
    ou playbook FoundLab (ex.: "deploy do REX Guard", "contrato de evidência BCB",
    "como escrever um RFC"). Retorna os documentos mais relevantes com caminho,
    score e um trecho. Depois, use get_document/get_skill para o conteúdo completo.
    """
    return _json(_kb.search(query, top_k=top_k))


@mcp.tool()
def list_skills() -> str:
    """Lista todas as skills FoundLab (nome, categoria, descrição, caminho).

    Use para descobrir quais capacidades existem antes de escolher uma com get_skill.
    """
    return _json(_kb.list_skills())


@mcp.tool()
def get_skill(name: str) -> str:
    """Retorna o conteúdo COMPLETO de uma skill pelo nome (ou slug da pasta).

    Ex.: get_skill("rex-guard-deploy"). Use depois de search_kb/list_skills.
    """
    content = _kb.get_skill(name)
    return content if content else f"Skill não encontrada: {name!r}. Use list_skills."


@mcp.tool()
def get_document(path: str) -> str:
    """Retorna o conteúdo COMPLETO de um documento pelo caminho relativo ao repo.

    Ex.: get_document("Core/Standards/security.md"). Os caminhos vêm de search_kb.
    """
    content = _kb.get_by_path(path)
    return content if content else f"Documento não encontrado ou inválido: {path!r}"


@mcp.tool()
def list_catalog() -> str:
    """Retorna o catálogo completo da base agrupado por categoria (Core, Models, Skills, Reference)."""
    return _json(_kb.catalog())


@mcp.tool()
def refresh_index() -> str:
    """Reconstrói o índice a partir do disco. Use após editar arquivos da base."""
    _kb.build()
    return _json({"status": "ok", "documentos": len(_kb.docs), "skills": len(_kb.list_skills())})


if __name__ == "__main__":
    # Transporte selecionável para suportar tanto clientes MCP locais quanto
    # APIs hospedadas (OpenAI remote MCP, Gemini, Claude mcp_servers).
    #   KB_TRANSPORT=stdio           -> clientes locais (Claude Code, Cursor, Gemini CLI...)
    #   KB_TRANSPORT=streamable-http -> MCP remoto via URL (qualquer provider hospedado)
    transport = os.environ.get("KB_TRANSPORT", "stdio")
    if transport == "streamable-http":
        # host/port configuráveis; o endpoint MCP fica em http://<host>:<port>/mcp
        mcp.settings.host = os.environ.get("KB_HOST", "127.0.0.1")
        mcp.settings.port = int(os.environ.get("KB_PORT", "8000"))
        mcp.run(transport="streamable-http")
    else:
        mcp.run()
