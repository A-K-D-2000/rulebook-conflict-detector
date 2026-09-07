import os
import re
import json
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in your .env file!")

client = genai.Client(api_key=api_key)

def parse_rulebook(file_path="rulebook.md"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not find {file_path}")

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    # Normalize line breaks
    text = text.replace("\r\n", "\n")

    # Match sections whether preceded by ### or nothing at all
    # Matches "Section 1.1: Title" or "### Section 1.1: Title"
    section_pattern = re.compile(
        r"(?:^|\n)(?:###\s*)?(Section\s+(\d+\.\d+):?\s*([^\n]+))\n(.*?)(?=(?:\n(?:###\s*)?Section\s+\d+\.\d+|\Z))",
        re.DOTALL
    )

    # Match chapters whether preceded by ## or nothing at all
    chapter_pattern = re.compile(
        r"(?:^|\n)(?:##\s*)?(Chapter\s+\d+:\s*[^\n]+)"
    )

    chapter_matches = list(chapter_pattern.finditer(text))
    sections = []

    for match in section_pattern.finditer(text):
        full_sec_header = match.group(1).strip()
        sec_id = f"Section {match.group(2).strip()}"
        sec_title = match.group(3).strip()
        sec_body = match.group(4).strip()
        sec_start = match.start()

        current_chapter = "General Regulations"
        for ch in chapter_matches:
            if ch.start() < sec_start:
                current_chapter = ch.group(1).strip()
            else:
                break

        sections.append({
            "id": sec_id,
            "title": sec_title,
            "chapter": current_chapter,
            "text": sec_body,
            "full_reference": f"{current_chapter} - {sec_id}: {sec_title}"
        })

    return sections

def generate_embeddings_and_save(sections, output_file="sections_index.json"):
    print(f"Found {len(sections)} sections in rulebook.md.")
    if len(sections) == 0:
        print("Warning: No sections found! Check the text in rulebook.md.")
        return

    print("Generating embeddings using Google Gemini (gemini-embedding-001)...")
    indexed_data = []

    for idx, sec in enumerate(sections, 1):
        embed_input = f"{sec['full_reference']}\n{sec['text']}"
        try:
            response = client.models.embed_content(
                model="gemini-embedding-001",
                contents=embed_input
            )
            embedding = response.embeddings[0].values
            indexed_data.append({
                "id": sec["id"],
                "title": sec["title"],
                "chapter": sec["chapter"],
                "text": sec["text"],
                "full_reference": sec["full_reference"],
                "embedding": embedding
            })
            print(f"  [{idx}/{len(sections)}] Indexed: {sec['id']} - {sec['title']}")
            time.sleep(0.3)
        except Exception as e:
            print(f"  Error indexing {sec['id']}: {e}")

    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(indexed_data, out, indent=2)

    print(f"\nDone! Successfully saved {len(indexed_data)} indexed sections to {output_file}")

if __name__ == "__main__":
    parsed_sections = parse_rulebook("rulebook.md")
    generate_embeddings_and_save(parsed_sections)