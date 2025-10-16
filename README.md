# 🎓 Flashcard Generator

An intelligent flashcard generation tool that uses RAG (Retrieval-Augmented Generation) and LLMs to automatically create study flashcards from your documents.

## Features

✨ **Web Scraping** - Extract text from URLs and save to local storage
🤖 **RAG Pipeline** - Retrieve relevant document chunks using FAISS vector search
📇 **Flashcard Generation** - Auto-generate Q&A flashcards using Llama 2
❓ **Q&A Mode** - Ask questions about your documents and get AI-powered answers
🔄 **Full Pipeline** - One-command workflow: scrape → index → generate

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_flashcard.txt
```

### 2. Download the LLM Model

Download the Llama 2 model and place it in `data/models/`:

- **Model**: `llama-2-7b-chat.Q5_K_M.gguf`
- **Download**: [Hugging Face - TheBloke](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF)
- **Size**: ~4.58 GB
- **Location**: `data/models/llama-2-7b-chat.Q5_K_M.gguf`

### 3. Add Your Documents

Place your text files in:
```
data/raw/
```

### 4. Run the Application

```bash
python main.py
```

## Usage

### Interactive Menu Options

```
1. Scrape URL and save to data/raw/
2. Build FAISS index from existing text files
3. Generate flashcards for a topic
4. Ask a question (Q&A mode)
5. Full pipeline (scrape → build → generate)
6. Exit
```

### Example Workflow

**Option 1: Scrape from URL**
```
Enter URL: https://example.com/article
Enter filename: my_article.txt
✅ Successfully saved
```

**Option 2: Build Index**
- Loads all `.txt` files from `data/raw/`
- Creates FAISS vector index
- Saves to `data/models/`

**Option 3: Generate Flashcards**
```
Enter topic: Binary Search Trees
✅ Flashcards generated: anki_cards.csv
```

**Option 4: Ask Questions**
```
Ask a question: What is a hash table?
📝 Answer: [AI-generated answer from documents]
```

## Project Structure

```
flashcardgen/
├── main.py                    # Entry point - interactive CLI
├── rag_pipeline.py            # RAG pipeline with FAISS indexing
├── flashcard_maker.py         # Flashcard generation using Llama
├── scrape.py                  # Web scraper
├── requirements_flashcard.txt # Python dependencies
├── README.md                  # This file
├── .gitignore                 # Git configuration
└── data/
    ├── models/                # LLM models and indices
    │   ├── llama-2-7b-chat.Q5_K_M.gguf  # Main LLM
    │   ├── faiss_index.bin              # Vector index
    │   └── docs_meta.json               # Metadata
    ├── raw/                   # Original text files (input)
    ├── chunk/                 # Chunked text files
    └── scraped_text/          # Scraped content
```

## Where to Upload Documents

### Method 1: Manual Upload
Place `.txt` files directly in:
```
data/raw/
```

Example:
```
data/raw/chapter1.txt
data/raw/article.txt
data/raw/notes.txt
```

### Method 2: Web Scraping
Use **Option 1** in the interactive menu to scrape URLs:
- Enter any webpage URL
- Automatically saves to `data/raw/` with auto-generated filename
- Or specify custom filename

### Supported File Formats
- `.txt` (plain text) ✅
- `.md` (markdown) ✅
- `.pdf` (PDF) - requires additional setup

## Output

### Generated Flashcards
- **File**: `anki_cards.csv`
- **Format**: CSV with columns: `Front`, `Back`
- **Compatible with**: Anki, Quizlet, Notion

Example:
```csv
Front,Back
What is a hash table?,A hash table is a data structure that implements an associative array...
How does binary search work?,Binary search works by repeatedly dividing a sorted array in half...
```

## Configuration

Edit these files to customize:

**`rag_pipeline.py`**:
```python
RAW_DIR = Path("data/raw/dsa")        # Change input directory
CHUNK_SIZE = 2000                      # Adjust chunk size
TOP_K = 8                              # Number of retrieved chunks
```

**`flashcard_maker.py`**:
```python
LLAMA_GGUF_PATH = "data/models/llama-2-7b-chat.Q5_K_M.gguf"
```

## Requirements

- Python 3.8+
- 8+ GB RAM (for LLM inference)
- 5+ GB disk space (for model)
- GPU recommended (CUDA support for faster inference)

## Troubleshooting

### "Module not found"
```bash
pip install -r requirements_flashcard.txt
```

### "GGUF model not found"
Download from Hugging Face and place in `data/models/`

### "No .txt files found"
Add files to `data/raw/` or use Option 1 to scrape URLs

### Slow inference
- Use GPU with CUDA support
- Reduce `TOP_K` in `rag_pipeline.py`
- Use a smaller model (GGUF quantization)

## License

MIT License

## Author

Flashcard Generator - AI-powered study tool
