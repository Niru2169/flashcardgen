# flashcard_maker.py
import pandas as pd
from langchain_community.llms import LlamaCpp
from langchain.prompts import PromptTemplate

LLAMA_GGUF_PATH = "data/models/llama-2-7b-chat.Q5_K_M.gguf"

# init LLM
llm = LlamaCpp(model_path=LLAMA_GGUF_PATH, n_ctx=4096, n_threads=6, verbose=False)

FLASHCARD_PROMPT = """
You are a flashcard generator. 
Your ONLY task is to generate 3-5 concise flashcards from the text. 
Do not explain anything, do not add extra text, only output flashcards.

Each flashcard MUST be in exactly this format (one after another, no numbering, no bullet points):
Question: <short clear question>
Answer: <short correct answer>

Text:
{passage}
"""


prompt = PromptTemplate(template=FLASHCARD_PROMPT, input_variables=["passage"])

def make_flashcards(passage: str, csv_path="anki_cards.csv"):
    chain = prompt | llm
    raw = chain.invoke({"passage": passage})
    print("\n[DEBUG RAW FLASHCARDS OUTPUT]\n", raw)

    cards = []
    front, back = None, None
    for line in raw.splitlines():
        line = line.strip()
        if line.lower().startswith(("question:", "q:")):
            front = line.split(":", 1)[1].strip()
        elif line.lower().startswith(("answer:", "a:")):
            back = line.split(":", 1)[1].strip()
            if front and back:
                cards.append({"Front": front, "Back": back})
                front, back = None, None

    # Fallback: auto-convert definitions into Q/A
    if not cards:
        for line in raw.splitlines():
            line = line.strip()
            if len(line.split()) > 4 and not line.lower().startswith(("question:", "answer:")):
                # create flashcard: first 4 words → Question, full line → Answer
                first_word = line.split()[0].capitalize()
                question = f"What is {first_word}?"
                answer = line
                cards.append({"Front": question, "Back": answer})

    if cards:
        df = pd.DataFrame(cards)
        df.to_csv(csv_path, index=False, encoding="utf-8")
        print(f"[INFO] {len(cards)} flashcards saved to {csv_path}")
        return cards
    else:
        print("[INFO] No flashcards generated.")
        return []
