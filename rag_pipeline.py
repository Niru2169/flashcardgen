# rag_pipeline.py
import os
import json
from pathlib import Path
from typing import List
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from flashcard_maker import make_flashcards

# ------ CONFIG ------
RAW_DIR = Path("data/raw/dsa")
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200
TOP_K = 8
VECTOR_INDEX_PATH = "data/models/faiss_index.bin"
DOCS_META_PATH = "data/models/docs_meta.json"

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
LLAMA_GGUF_PATH = "data/models/llama-2-7b-chat.Q5_K_M.gguf"  # <- set this

# ------ 1. Embedding model ------
embed_model = SentenceTransformer(EMBED_MODEL_NAME)

def embed_texts(texts: List[str]) -> np.ndarray:
    return embed_model.encode(texts, show_progress_bar=True, convert_to_numpy=True).astype("float32")

# ------ 2. Load and chunk all .txt files ------
def load_and_chunk_txt_files() -> List[Document]:
    docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    for txt_file in RAW_DIR.glob("*.txt"):
        with open(txt_file, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = splitter.split_text(text)
        for i, chunk in enumerate(chunks):
            meta = {"source": str(txt_file), "chunk_id": f"{txt_file.stem}_c{i}"}
            docs.append(Document(page_content=chunk, metadata=meta))
    return docs

# ------ 3. Build FAISS index ------
def build_faiss_index(docs: List[Document]):
    texts = [d.page_content for d in docs]
    metas = [d.metadata for d in docs]
    vectors = embed_texts(texts)
    d = vectors.shape[1]
    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(d)  # inner product similarity
    index.add(vectors)
    faiss.write_index(index, VECTOR_INDEX_PATH)
    with open(DOCS_META_PATH, "w", encoding="utf-8") as f:
        json.dump(metas, f, ensure_ascii=False, indent=2)
    print(f"[INFO] FAISS index and metadata saved.")
    return index, metas, texts

# ------ 4. Load FAISS index ------
def load_faiss_index():
    index = faiss.read_index(VECTOR_INDEX_PATH)
    with open(DOCS_META_PATH, "r", encoding="utf-8") as f:
        metas = json.load(f)
    return index, metas

# ------ 5. Simple retriever ------
class FaissRetriever:
    def __init__(self, index, metas, embedder, top_k=TOP_K):
        self.index = index
        self.metas = metas
        self.embedder = embedder
        self.top_k = top_k

    def retrieve(self, query: str):
        qvec = self.embedder.encode([query], convert_to_numpy=True).astype("float32")
        faiss.normalize_L2(qvec)
        D, I = self.index.search(qvec, self.top_k)
        results = [self.metas[i] for i in I[0] if 0 <= i < len(self.metas)]
        return results, I[0], D[0]

# ------ 6. Load LLM ------
def get_llm():
    if not os.path.exists(LLAMA_GGUF_PATH):
        raise FileNotFoundError(f"GGUF model not found at {LLAMA_GGUF_PATH}")
    return LlamaCpp(model_path=LLAMA_GGUF_PATH, n_ctx=4096, n_threads=6, verbose=False)

# ------ 7. Prompts ------
QA_PROMPT = """
You are an assistant that **only answers** from the provided context. 
If the answer cannot be found in the context, respond exactly: "I do not have enough information to answer this question."

Context:
{context}

Question:
{question}

Answer concisely and cite sources when appropriate.
"""

qa_prompt_template = PromptTemplate(template=QA_PROMPT, input_variables=["context", "question"])

# ------ 8. Answer question ------
def answer_question(query: str, index, metas, docs_texts):
    retriever = FaissRetriever(index, metas, embed_model)
    results, idxs, dists = retriever.retrieve(query)
    context = "\n\n---\n\n".join([docs_texts[i] for i in idxs if i < len(docs_texts)])
    if not context.strip():
        return "I do not have enough information to answer this question."
    llm = get_llm()
    chain = qa_prompt_template | llm
    return chain.invoke({"context": context, "question": query}).strip()

# ------ 9. Flashcard generation ------
def generate_flashcards(topic: str, index, metas, docs_texts, top_k=4):
    retriever = FaissRetriever(index, metas, embed_model, top_k=top_k)
    results, idxs, dists = retriever.retrieve(topic)
    passages = [docs_texts[i] for i in idxs if i < len(docs_texts)]
    passage = "\n\n".join(passages)
    if not passage.strip():
        return []

    make_flashcards(passage, "anki_cards.csv")
    return []

# ------ 10. Full pipeline example ------
if __name__ == "__main__":
    print("[INFO] Loading and chunking .txt files from ../../data/flashcard/raw/dsa ...")
    docs = load_and_chunk_txt_files()
    index, metas, docs_texts = build_faiss_index(docs)

    # Example: answer a DSA question
    query = "What is the time complexity of inserting a node in a singly linked list?"
    answer = answer_question(query, index, metas, [d.page_content for d in docs])
    print("\n[QA ANSWER]:\n", answer)

    # Example: generate flashcards
    topic = "Binary Search Tree"
    generate_flashcards(topic, index, metas, [d.page_content for d in docs])
