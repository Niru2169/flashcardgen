# chunker.py
import os
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter

RAW_DIR = Path("../../data/flashcard/raw")
CHUNK_DIR = Path("../../data/flashcard/chunk")
CHUNK_DIR.mkdir(parents=True, exist_ok=True)

def chunk_text(text, chunk_size=2000, chunk_overlap=200):
    """Split text into overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    return splitter.split_text(text)

def process_files():
    for txt_file in RAW_DIR.glob("*.txt"):
        with open(txt_file, "r", encoding="utf-8") as f:
            text = f.read()

        # Split into chunks
        chunks = chunk_text(text)

        # Save each chunk as its own file in data/chunk
        for i, chunk in enumerate(chunks, start=1):
            chunk_filename = f"{txt_file.stem}_chunk{i}.txt"
            chunk_path = CHUNK_DIR / chunk_filename
            with open(chunk_path, "w", encoding="utf-8") as cf:
                cf.write(chunk)

        print(f"[INFO] {txt_file.name} → {len(chunks)} chunks saved in {CHUNK_DIR}/")

if __name__ == "__main__":
    process_files()
