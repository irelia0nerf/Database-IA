"""
kb_index.py — Engine de indexação e busca da base de conhecimento FoundLab.

Sem dependências de rede. Constrói um índice em memória de todos os arquivos
Markdown do repositório e oferece busca por relevância (BM25). É o núcleo do
MCP server (server.py), mas é totalmente utilizável e testável de forma isolada:

    python3 tools/kb-mcp/kb_index.py "deploy do rex guard"

Isso imprime os documentos mais relevantes — útil para smoke test sem o pacote mcp.
"""

from __future__ import annotations

import math
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Raiz do repositório: por padrão, dois níveis acima deste arquivo
# (tools/kb-mcp/kb_index.py -> raiz). Pode ser sobrescrita por KB_ROOT.
DEFAULT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(os.environ.get("KB_ROOT", DEFAULT_ROOT)).resolve()

# Diretórios ignorados na varredura.
IGNORE_DIRS = {".git", "node_modules", ".claude", "__pycache__", "tools"}

# Stopwords PT + EN — reduz ruído no ranking sem precisar de NLP pesado.
STOPWORDS = {
    # PT
    "a", "o", "as", "os", "um", "uma", "de", "do", "da", "dos", "das", "e",
    "em", "no", "na", "nos", "nas", "por", "para", "com", "que", "se", "ao",
    "aos", "à", "às", "ou", "como", "mais", "mas", "ser", "ter", "é", "são",
    "foi", "está", "este", "esta", "isso", "qual", "quais", "seu", "sua",
    # EN
    "the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "is", "are",
    "be", "with", "as", "by", "at", "from", "this", "that", "it", "you", "your",
    "use", "used", "using", "when", "what", "how", "which",
}

TOKEN_RE = re.compile(r"[a-zA-Z0-9_]{2,}")


def tokenize(text: str) -> list[str]:
    """Lowercase, separa em tokens alfanuméricos e remove stopwords."""
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]


def parse_front_matter(text: str) -> tuple[dict, str]:
    """Extrai o bloco YAML de front-matter (entre --- ... ---), se houver.

    Retorna (metadados, corpo). Defensivo: nunca levanta exceção — front-matter
    malformado vira {} e o texto inteiro é tratado como corpo.
    """
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    data: dict = {}
    try:
        import yaml  # PyYAML é o caminho feliz para YAML real (multiline >-, listas)
        loaded = yaml.safe_load(block)
        if isinstance(loaded, dict):
            data = loaded
    except Exception:
        # Fallback sem dependências: captura name/description simples.
        for key in ("name", "description"):
            m = re.search(rf"^{key}:\s*(.+)$", block, re.MULTILINE)
            if m:
                data[key] = m.group(1).strip().strip("'\"")
    return data, body


@dataclass
class Doc:
    path: str                 # caminho relativo à raiz do repo (POSIX)
    category: str             # primeiro segmento do caminho (Core, Models, Skills...)
    kind: str                 # "skill" | "doc"
    name: str                 # nome canônico (front-matter name, ou nome do arquivo)
    description: str          # descrição (front-matter), se houver
    body: str                 # corpo sem o front-matter
    tokens: list[str] = field(default_factory=list)

    def summary(self) -> dict:
        return {
            "name": self.name,
            "path": self.path,
            "category": self.category,
            "kind": self.kind,
            "description": self.description,
        }


class KnowledgeBase:
    """Índice em memória + busca BM25 sobre os Markdown do repositório."""

    K1 = 1.5
    B = 0.75

    def __init__(self, root: Path = REPO_ROOT):
        self.root = Path(root).resolve()
        self.docs: list[Doc] = []
        self._df: dict[str, int] = {}        # document frequency por termo
        self._avg_len: float = 0.0
        self.build()

    # ---- construção ----
    def build(self) -> None:
        self.docs = []
        for path in sorted(self.root.rglob("*.md")):
            rel_parts = path.relative_to(self.root).parts
            if any(p in IGNORE_DIRS for p in rel_parts):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            fm, body = parse_front_matter(text)
            rel = path.relative_to(self.root).as_posix()
            category = rel_parts[0] if len(rel_parts) > 1 else "(root)"
            is_skill = path.name == "SKILL.md"
            name = str(fm.get("name") or "").strip()
            if not name:
                # READMEs e docs: usa o caminho legível como nome
                name = path.stem if path.stem.lower() != "readme" else f"{category} (índice)"
            desc = str(fm.get("description") or "").strip()
            # Peso extra para name/description: entram no corpo tokenizado 2x.
            searchable = f"{name}\n{desc}\n{name}\n{desc}\n{body}"
            doc = Doc(
                path=rel,
                category=category,
                kind="skill" if is_skill else "doc",
                name=name,
                description=desc,
                body=body,
                tokens=tokenize(searchable),
            )
            self.docs.append(doc)
        self._index()

    def _index(self) -> None:
        self._df = {}
        total_len = 0
        for doc in self.docs:
            total_len += len(doc.tokens)
            for term in set(doc.tokens):
                self._df[term] = self._df.get(term, 0) + 1
        self._avg_len = (total_len / len(self.docs)) if self.docs else 0.0

    # ---- busca ----
    def _idf(self, term: str) -> float:
        n = len(self.docs)
        df = self._df.get(term, 0)
        # BM25 IDF com suavização; max(., 0) evita negativos em termos muito comuns.
        return max(math.log((n - df + 0.5) / (df + 0.5) + 1.0), 0.0)

    def search(self, query: str, top_k: int = 5, kind: str | None = None) -> list[dict]:
        q_terms = tokenize(query)
        if not q_terms:
            return []
        results = []
        for doc in self.docs:
            if kind and doc.kind != kind:
                continue
            tf: dict[str, int] = {}
            for t in doc.tokens:
                tf[t] = tf.get(t, 0) + 1
            dl = len(doc.tokens) or 1
            score = 0.0
            for term in q_terms:
                if term not in tf:
                    continue
                freq = tf[term]
                denom = freq + self.K1 * (1 - self.B + self.B * dl / (self._avg_len or 1))
                score += self._idf(term) * (freq * (self.K1 + 1)) / denom
            if score > 0:
                results.append((score, doc))
        results.sort(key=lambda x: x[0], reverse=True)
        out = []
        for score, doc in results[:top_k]:
            r = doc.summary()
            r["score"] = round(score, 3)
            r["snippet"] = self._snippet(doc, q_terms)
            out.append(r)
        return out

    @staticmethod
    def _snippet(doc: Doc, q_terms: list[str], width: int = 240) -> str:
        """Trecho do corpo ao redor da primeira ocorrência de um termo da query."""
        body = doc.body
        low = body.lower()
        pos = -1
        for term in q_terms:
            p = low.find(term)
            if p != -1:
                pos = p
                break
        if pos == -1:
            return (doc.description or body[:width]).strip()[:width]
        start = max(0, pos - width // 3)
        end = min(len(body), start + width)
        snippet = body[start:end].replace("\n", " ").strip()
        return ("…" if start > 0 else "") + snippet + ("…" if end < len(body) else "")

    # ---- catálogo / acesso direto ----
    def list_skills(self) -> list[dict]:
        return [d.summary() for d in self.docs if d.kind == "skill"]

    def catalog(self) -> dict:
        cats: dict[str, list[dict]] = {}
        for d in self.docs:
            cats.setdefault(d.category, []).append(d.summary())
        return cats

    def get_by_path(self, rel_path: str) -> str | None:
        target = (self.root / rel_path).resolve()
        # Impede path traversal para fora do repo.
        if self.root not in target.parents and target != self.root:
            return None
        if not target.exists() or target.suffix != ".md":
            return None
        try:
            return target.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None

    def get_skill(self, name: str) -> str | None:
        name_l = name.strip().lower()
        for d in self.docs:
            if d.kind == "skill" and d.name.lower() == name_l:
                return self.get_by_path(d.path)
        # tolera busca por slug da pasta (ex.: rex-guard-deploy)
        for d in self.docs:
            if d.kind == "skill" and name_l in d.path.lower():
                return self.get_by_path(d.path)
        return None


def _cli() -> int:
    kb = KnowledgeBase()
    if len(sys.argv) < 2:
        print(f"Indexados {len(kb.docs)} documentos de {kb.root}")
        print(f"Skills: {len(kb.list_skills())} | avg_len={kb._avg_len:.1f} tokens")
        print('Uso: python3 kb_index.py "sua busca aqui"')
        return 0
    query = " ".join(sys.argv[1:])
    hits = kb.search(query, top_k=5)
    if not hits:
        print("Nenhum resultado.")
        return 0
    for i, h in enumerate(hits, 1):
        print(f"{i}. [{h['score']}] {h['name']}  ({h['path']})")
        print(f"   {h['snippet'][:160]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
