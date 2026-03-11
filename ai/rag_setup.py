"""
GST law RAG — local ChromaDB + sentence-transformers. No cloud.
Run once: python ai/rag_setup.py
Then use search_law(query) from backend.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure we can run as script from repo root or from backend
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR.parent))

CHROMA_PATH = _SCRIPT_DIR / "chroma_db"
COLLECTION_NAME = "gst_law_corpus"

# 10 sample GST law sections (placeholder text; replace with real content later)
GST_SECTIONS = [
    {
        "section_id": "Section 16(4)",
        "title": "ITC claim time limit",
        "summary": "Time limit for claiming input tax credit.",
        "full_text": "Section 16(4) of the CGST Act provides that input tax credit in respect of invoices or debit notes for supply of goods or services or both shall not be availed after the due date of furnishing the return under section 39 for the month of September following the end of financial year to which such invoice or debit note pertains, or furnishing of the relevant annual return, whichever is earlier.",
    },
    {
        "section_id": "Section 73",
        "title": "Tax not paid — show cause notice",
        "summary": "Show cause notice for tax not paid or short paid without fraud.",
        "full_text": "Section 73 of the CGST Act deals with determination of tax not paid or short paid or erroneously refunded or input tax credit wrongly availed or utilised for any reason other than fraud or wilful misstatement or suppression of facts. The proper officer shall serve a notice requiring the person to show cause why he should not pay the amount specified in the notice along with interest and penalty.",
    },
    {
        "section_id": "Section 74",
        "title": "Tax not paid — fraud/suppression",
        "summary": "Proceedings where tax short paid or not paid due to fraud or suppression.",
        "full_text": "Section 74 of the CGST Act applies where tax has not been paid or short paid or erroneously refunded or input tax credit has been wrongly availed or utilised by reason of fraud, or any wilful misstatement or suppression of facts. The proper officer may serve a notice and the person may be liable to penalty. The time limits and procedure differ from section 73.",
    },
    {
        "section_id": "Section 61",
        "title": "Scrutiny of returns",
        "summary": "Scrutiny of returns and related verification by the proper officer.",
        "full_text": "Section 61 of the CGST Act provides for scrutiny of returns. The proper officer may scrutinise the return and related particulars for verification of the correctness of the return. If any discrepancy is found, the registered person shall be informed and may be required to explain or take corrective action.",
    },
    {
        "section_id": "Section 65",
        "title": "Audit by tax authorities",
        "summary": "Audit of records by the Commissioner or officer authorised by him.",
        "full_text": "Section 65 of the CGST Act provides for audit by the tax authorities. The Commissioner or any officer authorised by him may conduct audit of the records, books of account and other documents of a registered person. The person shall be given at least fifteen days notice. The audit shall be completed within a specified period.",
    },
    {
        "section_id": "Section 75",
        "title": "General provisions for demand",
        "summary": "General provisions relating to determination of tax and issuance of order.",
        "full_text": "Section 75 of the CGST Act contains general provisions relating to determination of tax. Where the proper officer is of the opinion that the amount of tax or interest or penalty has not been correctly determined, he may pass an order. The order shall be passed within a prescribed period. Opportunity of hearing shall be given.",
    },
    {
        "section_id": "Rule 36(4)",
        "title": "ITC matching conditions",
        "summary": "Conditions and restrictions for claiming ITC based on matching.",
        "full_text": "Rule 36(4) of the CGST Rules provides conditions for availing input tax credit in respect of invoices or debit notes not reflected in GSTR-2B. The registered person may avail credit to the extent of a specified percentage of the eligible credit available in respect of invoices or debit notes. The rest shall be availed when the details are furnished by the supplier.",
    },
    {
        "section_id": "Rule 86A",
        "title": "Blocking of ITC",
        "summary": "Power to block input tax credit in certain circumstances.",
        "full_text": "Rule 86A of the CGST Rules empowers the Commissioner to block the input tax credit available in the electronic credit ledger if he has reason to believe that the credit has been fraudulently availed or is ineligible. The block may be for such period as the Commissioner deems fit. The person shall be informed in writing.",
    },
    {
        "section_id": "Section 50",
        "title": "Interest on delayed payment",
        "summary": "Interest payable on delayed payment of tax.",
        "full_text": "Section 50 of the CGST Act provides for interest on delayed payment of tax. Every person who is liable to pay tax and fails to pay the tax or any part thereof within the period prescribed shall pay interest at such rate as may be notified. Interest shall be calculated from the day succeeding the day on which tax was due to be paid.",
    },
    {
        "section_id": "Section 122",
        "title": "Penalties",
        "summary": "Penalties for certain offences under the Act.",
        "full_text": "Section 122 of the CGST Act specifies penalties for various offences such as supply of goods or services without invoice, issue of invoice without supply, availing or utilising input tax credit without receipt of goods or services, and other contraventions. The penalty may extend to a specified amount. In case of repeat offence, higher penalty may apply.",
    },
]


def _get_client():
    import chromadb
    from chromadb.config import Settings
    return chromadb.PersistentClient(path=str(CHROMA_PATH), settings=Settings(anonymized_telemetry=False))


def _get_embedding_function():
    from chromadb.utils import embedding_functions
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")


def init_collection():
    """Create or get collection and add documents if empty. Call when running as script."""
    client = _get_client()
    ef = _get_embedding_function()
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"description": "GST law corpus for notice reply drafting"},
    )
    if collection.count() == 0:
        ids = []
        documents = []
        metadatas = []
        for i, sec in enumerate(GST_SECTIONS):
            ids.append(sec["section_id"].replace(" ", "_").replace("(", "").replace(")", ""))
            doc_text = f"{sec['title']}. {sec['summary']} {sec['full_text']}"
            documents.append(doc_text)
            metadatas.append({
                "section_id": sec["section_id"],
                "title": sec["title"],
                "summary": sec["summary"],
            })
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        print(f"Added {len(GST_SECTIONS)} GST law sections to '{COLLECTION_NAME}'.")
    else:
        print(f"Collection '{COLLECTION_NAME}' already has {collection.count()} documents.")
    return collection


def search_law(query: str, top_k: int = 3) -> list[dict]:
    """
    Search the GST law corpus. Returns top_k matching sections with section_id, title, summary.
    Runs fully local (ChromaDB + sentence-transformers).
    """
    if not query or not query.strip():
        return []
    try:
        client = _get_client()
        ef = _get_embedding_function()
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=ef,
        )
        results = collection.query(query_texts=[query.strip()], n_results=min(top_k, collection.count() or 1))
        out = []
        if results and results.get("metadatas") and len(results["metadatas"]) > 0:
            for meta in results["metadatas"][0]:
                out.append({
                    "section_id": meta.get("section_id", ""),
                    "title": meta.get("title", ""),
                    "summary": meta.get("summary", ""),
                })
        return out
    except Exception:
        return []


if __name__ == "__main__":
    init_collection()
    # Quick test
    test = search_law("show cause notice tax not paid")
    print("Sample search result:", test[:1] if test else "none")
