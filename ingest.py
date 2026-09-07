import os
import re
import json
import time
from dotenv import load_dotenv
from google import genai

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in your .env file!")

client = genai.Client(api_key=api_key)

def parse_rulebook(file_path="rulebook.md"):
    """
    Parses rulebook.md into structured sections with Chapter, Section number,
    title, and body text.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by chapters
    chapter_pattern = r"(## Chapter \d+: [^\n]+)"
    chapters_raw = re.split(chapter_pattern, content)

    sections = []
    current_chapter = "General"

    for part in chapters_raw:
        part = part.strip()
        if not part:
            continue
        if part.startswith("## Chapter"):
            current_chapter = part.replace("## ", "").strip()
            continue

        # Split current chapter into sections
        section_pattern = r"(### Section \d+\.\d+: [^\n]+)"
        section_parts = re.split(section_pattern, part)

        current_section_header = None
        for sec_part in section_parts:
            sec_part = sec_part.strip()
            if not sec_part:
                continue
            if sec_part.startswith("### Section"):
                current_section_header = sec_part.replace("### ", "").strip()
            elif current_section_header:
                # Extract section number and title
                match = re.match(r"(Section \d+\.\d+):\s*(.*)", current_section_header)
                sec_id = match.group(1) if match else current_section_header
                sec_title = match.group(2) if match else ""

                sections.append({
                    "id": sec_id,
                    "title": sec_title,
                    "chapter": current_chapter,
                    "text": sec_part,
                    "full_reference": f"{current_chapter} - {current_section_header}"
                })
                current_section_header = None

    return sections

def generate_embeddings_and_save(sections, output_file="sections_index.json"):
    """
    Computes text embeddings using Gemini's text-embedding-004
    and saves the indexed data locally.
    """
    print(f"Found {len(sections)} sections in rulebook.md.")
    print("Generating embeddings using Google Gemini (text-embedding-004)...")

    indexed_data = []

    for idx, sec in enumerate(sections, 1):
        # Embed header + content together for rich context retrieval
        embed_input = f"{sec['full_reference']}\n{sec['text']}"

        try:
            response = client.models.embed_content(
                model="text-embedding-004",
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
            time.sleep(0.3)  # Gentle delay to respect free rate limits
        except Exception as e:
            print(f"  Error indexing {sec['id']}: {e}")

    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(indexed_data, out, indent=2)

    print(f"\nDone! Successfully saved indexed data to {output_file}")

if __name__ == "__main__":
    parsed_sections = parse_rulebook("rulebook.md")
    generate_embeddings_and_save(parsed_sections)