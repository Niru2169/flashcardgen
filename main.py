#!/usr/bin/env python3
"""
Flashcard Generator - Main Entry Point
Combines web scraping, RAG pipeline, and flashcard generation
"""

import sys
from pathlib import Path
from rag_pipeline import (
    load_and_chunk_txt_files,
    build_faiss_index,
    load_faiss_index,
    answer_question,
    generate_flashcards,
)
from scrape import save_text


def print_menu():
    """Display main menu options"""
    print("\n" + "=" * 60)
    print("🎓 FLASHCARD GENERATOR")
    print("=" * 60)
    print("1. Scrape URL and save to data/raw/")
    print("2. Build FAISS index from existing text files")
    print("3. Generate flashcards for a topic")
    print("4. Ask a question (Q&A mode)")
    print("5. Full pipeline (scrape → build → generate)")
    print("6. Exit")
    print("=" * 60)


def mode_scrape():
    """Scrape URL and save text"""
    print("\n[SCRAPE MODE]")
    url = input("Enter URL to scrape: ").strip()
    if not url:
        print("[ERROR] URL cannot be empty")
        return
    
    filename = input("Enter filename (press Enter for auto-generated): ").strip()
    filename = filename if filename else None
    
    result = save_text(url, filename)
    if result:
        print(f"✅ Successfully saved to {result}")
    else:
        print("❌ Failed to scrape URL")


def mode_build_index():
    """Build FAISS index from raw text files"""
    print("\n[BUILD INDEX MODE]")
    
    raw_dir = Path("data/raw/dsa")
    if not raw_dir.exists():
        print(f"[ERROR] Directory not found: {raw_dir}")
        print("Please add .txt files to data/raw/dsa/")
        return
    
    txt_files = list(raw_dir.glob("*.txt"))
    if not txt_files:
        print(f"[ERROR] No .txt files found in {raw_dir}")
        return
    
    print(f"Found {len(txt_files)} text files")
    print("Loading and chunking...")
    docs = load_and_chunk_txt_files()
    print(f"Created {len(docs)} chunks")
    
    print("Building FAISS index...")
    index, metas, docs_texts = build_faiss_index(docs)
    print("✅ FAISS index built successfully")
    print(f"   - Vector index: data/models/faiss_index.bin")
    print(f"   - Metadata: data/models/docs_meta.json")


def mode_generate_flashcards(index=None, metas=None, docs_texts=None):
    """Generate flashcards for a topic"""
    print("\n[FLASHCARD GENERATION MODE]")
    
    # Load index if not provided
    if index is None:
        try:
            index, metas = load_faiss_index()
            # Reload docs_texts
            docs = load_and_chunk_txt_files()
            docs_texts = [d.page_content for d in docs]
        except Exception as e:
            print(f"[ERROR] Could not load FAISS index: {e}")
            print("Run mode 2 first to build the index")
            return
    
    topic = input("Enter topic for flashcard generation: ").strip()
    if not topic:
        print("[ERROR] Topic cannot be empty")
        return
    
    csv_path = input("Enter output CSV filename (default: anki_cards.csv): ").strip()
    csv_path = csv_path if csv_path else "anki_cards.csv"
    
    print(f"Generating flashcards for '{topic}'...")
    generate_flashcards(topic, index, metas, docs_texts)
    print(f"✅ Flashcards generated: {csv_path}")


def mode_qa(index=None, metas=None, docs_texts=None):
    """Q&A mode - answer questions about the documents"""
    print("\n[Q&A MODE]")
    print("Type 'exit' to return to main menu")
    
    # Load index if not provided
    if index is None:
        try:
            index, metas = load_faiss_index()
            docs = load_and_chunk_txt_files()
            docs_texts = [d.page_content for d in docs]
        except Exception as e:
            print(f"[ERROR] Could not load FAISS index: {e}")
            print("Run mode 2 first to build the index")
            return
    
    while True:
        query = input("\nAsk a question: ").strip()
        if query.lower() == "exit":
            break
        if not query:
            continue
        
        print("Searching and generating answer...")
        answer = answer_question(query, index, metas, docs_texts)
        print(f"\n📝 Answer:\n{answer}")


def mode_full_pipeline():
    """Full pipeline: scrape → build → generate"""
    print("\n[FULL PIPELINE MODE]")
    
    # Step 1: Scrape
    print("\n--- Step 1: Web Scraping ---")
    scrape_choice = input("Scrape a URL? (y/n, default: n): ").strip().lower()
    if scrape_choice == "y":
        mode_scrape()
    
    # Step 2: Build index
    print("\n--- Step 2: Build FAISS Index ---")
    raw_dir = Path("data/raw/dsa")
    txt_files = list(raw_dir.glob("*.txt"))
    if txt_files:
        print(f"Found {len(txt_files)} text files, building index...")
        docs = load_and_chunk_txt_files()
        index, metas, docs_texts = build_faiss_index(docs)
        print("✅ Index built successfully")
        
        # Step 3: Generate flashcards
        print("\n--- Step 3: Generate Flashcards ---")
        generate_choice = input("Generate flashcards? (y/n, default: y): ").strip().lower()
        if generate_choice != "n":
            topic = input("Enter topic: ").strip()
            if topic:
                generate_flashcards(topic, index, metas, docs_texts)
                print("✅ Flashcards generated: anki_cards.csv")
    else:
        print(f"[ERROR] No .txt files found in {raw_dir}")
        print("Please scrape URLs first or add text files manually")


def main():
    """Main application loop"""
    try:
        while True:
            print_menu()
            choice = input("Enter choice (1-6): ").strip()
            
            if choice == "1":
                mode_scrape()
            elif choice == "2":
                mode_build_index()
            elif choice == "3":
                mode_generate_flashcards()
            elif choice == "4":
                mode_qa()
            elif choice == "5":
                mode_full_pipeline()
            elif choice == "6":
                print("\n👋 Goodbye!")
                sys.exit(0)
            else:
                print("[ERROR] Invalid choice. Please try again.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
