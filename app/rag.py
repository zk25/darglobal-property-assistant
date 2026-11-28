"""Knowledge base loading, chunking and hybrid TF-IDF retrieval.

Documents are Markdown files with a short header:

    ---
    title: ...
    source: https://..., https://...
    site: DarGlobal
    ---

Each document is split on headings. Search combines word TF-IDF (names, numbers,
exact terms) with character n-gram TF-IDF (typos, partial words like "lambo").
The corpus is small, so this is accurate, needs no model download and loads in
well under a second on a free CPU container.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer

MAX_CHUNK_CHARS = 1400
URL_RE = re.compile(r"https?://[^\s,]+")
WORD_RE = re.compile(r"[a-z0-9]+")

# How people actually phrase property questions -> wording used on the sites.
QUERY_REWRITES = [
    (r"\b(\d)\s*-?\s*(bhk|br|bed|beds|bedrooms?)\b", r"\1 bedroom"),
    (r"\bbhk\b", "bedroom"),
    (r"\bflats?\b", "apartment"),
    (r"\bapts?\b", "apartment"),
    (r"\bsq\.?\s*ft\b|\bsqft\b", "sq ft"),
    (r"\b(costs?|pricing|prices|priced|rates?)\b", "price"),
    (r"\bksa\b", "saudi arabia"),
    (r"\bceo\b", "ceo chief executive"),
    (r"\bhandover\b", "completion"),
    (r"\bpossession\b", "completion"),
]


# Used when picking lines: "when will it be completed?" should match a "Completion: ..." line.
COMPLETION_RE = re.compile(r"\b(complete|completed|completes|ready|delivered)\b")


def normalize_query(query: str) -> str:
    text = query.lower()
    for pattern, repl in QUERY_REWRITES:
        text = re.sub(pattern, repl, text)
    return text


def light_stem(text: str) -> str:
    """Lowercase and drop simple plurals so 'apartments' matches 'apartment' and 'villas' matches 'villa'."""
    text = text.lower()
    text = re.sub(r"\b([a-z]{3,})ies\b", r"\1y", text)
    return re.sub(r"\b([a-z]{3,}[^s\W])s\b", r"\1", text)


STOPWORDS = {
    "the", "and", "for", "with", "are", "was", "from", "that", "this", "its", "about", "what",
    "which", "where", "when", "who", "how", "does", "can", "tell", "into", "per", "all", "any",
    "has", "have", "been", "also", "their", "they", "you", "your", "our", "not", "but", "of",
    "to", "in", "on", "at", "by", "a", "an", "is", "or", "as", "me", "do", "it", "be",
}


def content_words(text: str) -> set[str]:
    return {w for w in WORD_RE.findall(light_stem(text)) if w not in STOPWORDS}


# Words too common in headings to signal that a question is about that section.
GENERIC_HEADING_WORDS = {"other", "project", "darglobal", "wasalt", "overview", "new", "news", "buy", "update"}


@dataclass
class Chunk:
    doc_id: str
    title: str
    site: str
    url: str
    heading: str
    text: str
    source_title: str = ""

    @property
    def search_text(self) -> str:
        # The section heading is repeated so it outweighs the document title.
        return f"{self.heading}. {self.heading}. {self.title}. {self.text}"

    @property
    def label(self) -> str:
        """Short display name for the chunk, e.g. 'DG1 (DarGlobal)' or 'Services (Wasalt)'."""
        heading = self.heading
        if heading == self.title:
            return heading
        if len(heading.split()) <= 3 and self.site.split()[0].lower() not in heading.lower():
            return f"{heading} ({self.site})"
        return heading


@dataclass
class Document:
    doc_id: str
    title: str
    site: str
    sources: list[str]
    body: str
    chunks: list[Chunk] = field(default_factory=list)


def parse_document(path: Path, root: Path) -> Document:
    raw = path.read_text(encoding="utf-8")
    meta: dict[str, str] = {}
    body = raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) == 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta[key.strip().lower()] = value.strip()
            body = parts[2]
    return Document(
        doc_id=str(path.relative_to(root).with_suffix("")),
        title=meta.get("title") or path.stem.replace("-", " ").title(),
        site=meta.get("site") or path.parent.name.title(),
        sources=URL_RE.findall(meta.get("source", "")),
        body=body.strip(),
    )


SECTION_SOURCE_RE = re.compile(r"^\s*source:\s*(https?://\S+)\s*$", re.I)


def split_into_chunks(doc: Document) -> list[Chunk]:
    """Split on Markdown headings, then pack long sections line by line.

    A file that combines several pages can give a section its own page with a
    `Source: https://...` line under the heading; otherwise the file's first URL is used.
    """
    sections: list[tuple[str, list[str]]] = []
    heading, lines = doc.title, []
    for line in doc.body.splitlines():
        match = re.match(r"^#{1,6}\s+(.*)", line)
        if match:
            if any(l.strip() for l in lines):
                sections.append((heading, lines))
            heading, lines = match.group(1).strip(), []
        else:
            lines.append(line)
    if any(l.strip() for l in lines):
        sections.append((heading, lines))

    chunks = []
    for heading, sec_lines in sections:
        url, source_title = (doc.sources[0] if doc.sources else ""), doc.title
        kept = []
        for line in sec_lines:
            match = SECTION_SOURCE_RE.match(line)
            if match:
                url, source_title = match.group(1), heading
            else:
                kept.append(line)
        text = "\n".join(kept).strip()
        if not text:
            continue
        for piece in ([text] if len(text) <= MAX_CHUNK_CHARS else _pack(text)):
            chunks.append(Chunk(doc.doc_id, doc.title, doc.site, url, heading, piece.strip(), source_title))
    return chunks


def _pack(text: str) -> list[str]:
    pieces, current = [], ""
    for line in text.splitlines():
        if current and len(current) + len(line) + 1 > MAX_CHUNK_CHARS:
            pieces.append(current)
            current = ""
        current = f"{current}\n{line}" if current else line
    if current.strip():
        pieces.append(current)
    return pieces


class KnowledgeBase:
    def __init__(self, documents: list[Document]):
        if not documents:
            raise ValueError("No documents found for the knowledge base.")
        self.documents = documents
        self.chunks: list[Chunk] = []
        for doc in documents:
            doc.chunks = split_into_chunks(doc)
            self.chunks.extend(doc.chunks)

        corpus = [c.search_text for c in self.chunks]
        stop = sorted(ENGLISH_STOP_WORDS | {light_stem(w) for w in ENGLISH_STOP_WORDS})
        self.word_vec = TfidfVectorizer(
            analyzer="word", ngram_range=(1, 2), sublinear_tf=True, preprocessor=light_stem,
            stop_words=stop, token_pattern=r"(?u)\b\w+\b",
        )
        # Headings (or titles, for single-section pages) that name the topic: "Services", "DG1", "Trump Tower Jeddah".
        self.heading_words = [content_words(c.heading) - GENERIC_HEADING_WORDS for c in self.chunks]
        self.char_vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
        self.word_matrix = self.word_vec.fit_transform(corpus)
        self.char_matrix = self.char_vec.fit_transform(corpus)
        # Raw scraped pages are noisier than the cleaned files, so they rank slightly lower.
        self.weights = np.array([0.85 if c.doc_id.startswith("scraped") else 1.0 for c in self.chunks])

    @classmethod
    def from_directory(cls, root: Path, include_scraped: bool = True) -> "KnowledgeBase":
        root = Path(root)
        files = sorted(
            p for p in root.rglob("*.md")
            if p.is_file() and (include_scraped or "scraped" not in p.relative_to(root).parts)
        )
        return cls([parse_document(p, root) for p in files])

    def search(self, query: str, k: int = 6, min_score: float = 0.04) -> list[tuple[Chunk, float]]:
        query = normalize_query(query.strip())
        if not query:
            return []
        word = (self.word_matrix @ self.word_vec.transform([query]).T).toarray().ravel()
        char = (self.char_matrix @ self.char_vec.transform([query]).T).toarray().ravel()
        scores = 0.6 * word + 0.4 * char
        # Small boost when the question names a section; more shared words give a bigger boost.
        q_words = content_words(query)
        for i, h in enumerate(self.heading_words):
            overlap = len(h & q_words)
            if overlap:
                scores[i] += 0.12 * (overlap / len(h)) * min(1.0, overlap / 2)
        scores *= self.weights

        results: list[tuple[Chunk, float]] = []
        per_doc: dict[str, int] = {}
        for idx in np.argsort(-scores):
            score = float(scores[idx])
            if score < min_score or len(results) >= k:
                break
            chunk = self.chunks[idx]
            if per_doc.get(chunk.doc_id, 0) >= 3:  # keep the context varied
                continue
            per_doc[chunk.doc_id] = per_doc.get(chunk.doc_id, 0) + 1
            results.append((chunk, score))
        return results

    def rank_lines(self, query: str, lines: list[str]) -> np.ndarray:
        """Relevance of individual lines to the query (used for answers without the LLM)."""
        def prepare(text: str) -> str:
            return COMPLETION_RE.sub("completion", normalize_query(text))

        q = self.word_vec.transform([prepare(query)])
        return (self.word_vec.transform([prepare(l) for l in lines]) @ q.T).toarray().ravel()

    def stats(self) -> dict:
        sites: dict[str, int] = {}
        for doc in self.documents:
            sites[doc.site] = sites.get(doc.site, 0) + 1
        return {"documents": len(self.documents), "chunks": len(self.chunks), "by_site": sites}
