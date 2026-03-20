"""
RAG setup: ChromaDB corpus with 200+ GST documents.
Collection: gst_law_corpus.
Store: CGST Act sections (1-174), key CGST Rules, Notifications, Circulars, common notice responses.
"""
import os
from pathlib import Path
from typing import Any


_COLLECTION_NAME = "gst_law_corpus"
_chroma_client = None
_collection = None


def _get_chroma():
    global _chroma_client, _collection
    if _collection is not None:
        return _collection
    try:
        import chromadb
        from chromadb.config import Settings
    except ImportError:
        return None
    persist_dir = os.environ.get("CHROMA_PERSIST_DIR")
    if not persist_dir:
        base = Path(__file__).resolve().parent
        persist_dir = str(base / "gst_law_corpus" / "chroma_db")
    os.makedirs(persist_dir, exist_ok=True)
    _chroma_client = chromadb.PersistentClient(path=persist_dir, settings=Settings(anonymized_telemetry=False))
    _collection = _chroma_client.get_or_create_collection(name=_COLLECTION_NAME, metadata={"description": "GST law corpus"})
    return _collection


def search_law(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """
    ChromaDB similarity search on GST law corpus.
    Returns list of { document, metadata, section_id, ... }.
    """
    col = _get_chroma()
    if col is None:
        return []
    try:
        res = col.query(query_texts=[query], n_results=top_k, include=["documents", "metadatas"])
        out = []
        if res and res.get("documents") and res["documents"][0]:
            for i, doc in enumerate(res["documents"][0]):
                meta = (res.get("metadatas") or [[]])[0]
                m = meta[i] if i < len(meta) else {}
                out.append({
                    "document": doc,
                    "metadata": m,
                    "section_id": m.get("section_id") or m.get("id", ""),
                })
        return out
    except Exception:
        return []


def add_documents(docs: list[dict[str, Any]]) -> None:
    """
    Add documents to corpus. Each doc: { id, text, metadata }.
    metadata can include section_id, source, title.
    """
    col = _get_chroma()
    if col is None or not docs:
        return
    ids = [d.get("id", str(i)) for i, d in enumerate(docs)]
    texts = [d.get("text", d.get("content", "")) for d in docs]
    metadatas = [d.get("metadata", {}) for d in docs]
    col.add(ids=ids, documents=texts, metadatas=metadatas)


def build_corpus_from_folder(folder: str | Path) -> int:
    """
    Load 200+ GST docs from folder (e.g. ai/gst_law_corpus/) and add to ChromaDB.
    Expected: text/md files or structured JSON with id, text, metadata.
    Returns count of documents added.
    """
    folder = Path(folder)
    if not folder.is_dir():
        return 0
    docs = []
    for f in folder.rglob("*"):
        if f.suffix.lower() in (".txt", ".md"):
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
                section_id = f.stem
                if "section" in f.stem.lower() or f.stem.isdigit():
                    section_id = f.stem
                docs.append({"id": f.stem + "_" + f.suffix, "text": text, "metadata": {"section_id": section_id, "source": str(f.name)}})
            except Exception:
                continue
    if docs:
        add_documents(docs)
    return len(docs)


# Stub content for CGST Act sections 1-20 (sample) so corpus is usable without external files
_STUB_SECTIONS = [
    ("1", "Short title, extent and commencement."),
    ("2", "Definitions."),
    ("3", "Officers under this Act."),
    ("4", "Levy and collection."),
    ("5", "Composition levy."),
    ("6", "Power to grant exemption from tax."),
    ("7", "Scope of supply."),
    ("8", "Tax liability on composite and mixed supplies."),
    ("9", "Levy and collection."),
    ("10", "Composition scheme."),
    ("11", "Power to grant exemption."),
    ("12", "Place of supply of goods."),
    ("13", "Place of supply of services."),
    ("14", "Time of supply of goods."),
    ("15", "Valuation of supply."),
    ("16", "Eligibility and conditions for taking input tax credit."),
    ("17", "Apportionment of credit and blocked credits."),
    ("18", "Availability of credit in special circumstances."),
    ("73", "Determination of tax not paid or short paid or erroneously refunded or input tax credit wrongly availed (other than fraud)."),
    ("74", "Determination of tax in case of fraud."),
]


def ensure_stub_corpus() -> int:
    """Ensure at least stub sections exist in the collection for search_law to return results."""
    col = _get_chroma()
    if col is None:
        return 0
    try:
        existing = col.count()
        if existing >= 10:
            return existing
    except Exception:
        pass
    docs = [
        {"id": f"cgst_{num}", "text": f"CGST Act Section {num}. {text}", "metadata": {"section_id": f"Section {num}", "source": "CGST Act"}}
        for num, text in _STUB_SECTIONS
    ]
    add_documents(docs)
    return len(docs)
