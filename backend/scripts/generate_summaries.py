#!/usr/bin/env python3
"""Generate AI-powered chapter summaries using Gemini.

This script reads chapter content and generates concise summaries
with key concepts as bullet points.

Usage:
    python -m scripts.generate_summaries [--chapter CHAPTER_ID]
"""

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.gemini import GeminiClient


# Configuration
CONTENT_DIR = Path(__file__).parent.parent.parent / "content" / "source"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "content" / "summaries"

# Chapter metadata
CHAPTERS = {
    "chapter-1": {
        "title": "Introduction to Humanoid Robotics",
        "file": "chapter-1/index.md",
    },
    "chapter-2": {
        "title": "Robot Components and Architecture",
        "file": "chapter-2/index.md",
    },
    "chapter-3": {
        "title": "Sensors and Actuators",
        "file": "chapter-3/index.md",
    },
}

SUMMARY_PROMPT = """You are an expert educational content summarizer specializing in robotics and engineering.

Analyze the following chapter from a humanoid robotics textbook and generate a comprehensive summary.

Your summary should include:
1. A brief overview paragraph (2-3 sentences) explaining what this chapter covers
2. 5-8 key concepts as bullet points, each with a concise explanation
3. 3-5 important takeaways for students

Format your response as JSON with this structure:
{
    "overview": "Brief overview paragraph...",
    "key_concepts": [
        {
            "concept": "Concept name",
            "explanation": "Brief explanation of the concept"
        }
    ],
    "takeaways": [
        "Important takeaway 1",
        "Important takeaway 2"
    ]
}

Chapter Title: {title}

Chapter Content:
{content}

Generate the summary JSON:"""


def read_chapter_content(chapter_id: str) -> str | None:
    """Read chapter markdown content.

    Args:
        chapter_id: Chapter identifier (e.g., "chapter-1").

    Returns:
        Chapter content as string, or None if not found.
    """
    if chapter_id not in CHAPTERS:
        print(f"Unknown chapter: {chapter_id}")
        return None

    file_path = CONTENT_DIR / CHAPTERS[chapter_id]["file"]
    if not file_path.exists():
        print(f"Chapter file not found: {file_path}")
        return None

    content = file_path.read_text(encoding="utf-8")

    # Remove frontmatter
    content = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL)

    # Remove code blocks for summary generation (keep focus on concepts)
    content = re.sub(r"```[\s\S]*?```", "[code example]", content)

    return content.strip()


def extract_json_from_response(response: str) -> dict | None:
    """Extract JSON from Gemini response.

    Args:
        response: Raw response from Gemini.

    Returns:
        Parsed JSON dict or None if parsing fails.
    """
    # Try to find JSON block
    json_match = re.search(r"```json\s*([\s\S]*?)\s*```", response)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find raw JSON
        json_match = re.search(r"\{[\s\S]*\}", response)
        if json_match:
            json_str = json_match.group(0)
        else:
            return None

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return None


async def generate_summary(chapter_id: str, client: GeminiClient) -> dict | None:
    """Generate summary for a chapter using Gemini.

    Args:
        chapter_id: Chapter identifier.
        client: Gemini client instance.

    Returns:
        Summary dict or None if generation fails.
    """
    content = read_chapter_content(chapter_id)
    if not content:
        return None

    title = CHAPTERS[chapter_id]["title"]
    prompt = SUMMARY_PROMPT.format(title=title, content=content[:15000])  # Limit content length

    print(f"Generating summary for {chapter_id}...")

    try:
        response = await client.generate_text(prompt)
        summary = extract_json_from_response(response)

        if summary:
            summary["chapter_id"] = chapter_id
            summary["title"] = title
            return summary
        else:
            print(f"Failed to parse summary for {chapter_id}")
            return None

    except Exception as e:
        print(f"Error generating summary for {chapter_id}: {e}")
        return None


def save_summary(summary: dict, chapter_id: str) -> None:
    """Save summary to JSON file.

    Args:
        summary: Summary dict to save.
        chapter_id: Chapter identifier for filename.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{chapter_id}-summary.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Saved summary to {output_path}")


async def main() -> None:
    """Main entry point for summary generation."""
    parser = argparse.ArgumentParser(description="Generate chapter summaries")
    parser.add_argument(
        "--chapter",
        type=str,
        help="Generate summary for specific chapter (e.g., chapter-1)",
    )
    args = parser.parse_args()

    client = GeminiClient()

    if args.chapter:
        # Generate for specific chapter
        if args.chapter not in CHAPTERS:
            print(f"Unknown chapter: {args.chapter}")
            print(f"Available chapters: {', '.join(CHAPTERS.keys())}")
            sys.exit(1)

        summary = await generate_summary(args.chapter, client)
        if summary:
            save_summary(summary, args.chapter)
    else:
        # Generate for all chapters
        for chapter_id in CHAPTERS:
            summary = await generate_summary(chapter_id, client)
            if summary:
                save_summary(summary, chapter_id)
            await asyncio.sleep(1)  # Rate limiting

    print("Summary generation complete!")


if __name__ == "__main__":
    asyncio.run(main())
