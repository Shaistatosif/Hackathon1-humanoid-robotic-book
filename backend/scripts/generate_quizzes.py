#!/usr/bin/env python3
"""
Quiz Generation Script using Gemini.

This script:
1. Reads chapter content from content/source/
2. Uses Gemini to generate quiz questions based on content
3. Saves quizzes as JSON files in content/quizzes/

Usage:
    python -m scripts.generate_quizzes [--chapter chapter-1] [--questions 5]
"""

import argparse
import asyncio
import json
import re
import sys
import uuid
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

import google.generativeai as genai

from src.core.config import settings


# Quiz generation prompt
QUIZ_GENERATION_PROMPT = """You are an expert educator creating quiz questions for a humanoid robotics textbook.

Based on the following chapter content, generate {num_questions} quiz questions that test understanding of the key concepts.

REQUIREMENTS:
1. Generate a mix of question types:
   - Multiple choice (MCQ) questions with 4 options (A, B, C, D)
   - True/False questions
   - Short answer questions (1-2 sentence answers)

2. Questions should:
   - Test understanding, not just memorization
   - Cover the most important concepts in the chapter
   - Be clear and unambiguous
   - Have definitive correct answers

3. For each question, provide:
   - The question text
   - Question type (multiple_choice, true_false, or short_answer)
   - For MCQ: Four options labeled A, B, C, D
   - The correct answer (for MCQ, just the letter; for T/F, "True" or "False"; for short answer, a brief correct response)
   - A brief explanation of why the answer is correct

OUTPUT FORMAT (JSON):
{{
  "title": "Chapter X Quiz",
  "description": "Test your understanding of [chapter topic]",
  "questions": [
    {{
      "type": "multiple_choice",
      "question": "What is...?",
      "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
      "correct_answer": "A",
      "explanation": "Option A is correct because..."
    }},
    {{
      "type": "true_false",
      "question": "Statement to evaluate",
      "options": ["True", "False"],
      "correct_answer": "True",
      "explanation": "This is true because..."
    }},
    {{
      "type": "short_answer",
      "question": "Explain briefly...",
      "options": null,
      "correct_answer": "Expected answer content",
      "explanation": "A complete answer should include..."
    }}
  ]
}}

CHAPTER CONTENT:
{content}

Generate {num_questions} high-quality quiz questions now. Respond ONLY with valid JSON.
"""


def extract_text_content(markdown: str) -> str:
    """Extract readable text from markdown, removing code blocks.

    Args:
        markdown: Raw markdown content

    Returns:
        Cleaned text content
    """
    # Remove frontmatter
    if markdown.startswith("---"):
        parts = markdown.split("---", 2)
        if len(parts) >= 3:
            markdown = parts[2]

    # Remove code blocks
    markdown = re.sub(r'```[\s\S]*?```', '[CODE EXAMPLE]', markdown)

    # Remove inline code
    markdown = re.sub(r'`[^`]+`', '', markdown)

    # Remove images
    markdown = re.sub(r'!\[.*?\]\(.*?\)', '', markdown)

    # Remove links but keep text
    markdown = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', markdown)

    # Clean up excessive whitespace
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)

    return markdown.strip()


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from markdown.

    Args:
        content: Raw markdown content

    Returns:
        Tuple of (frontmatter dict, remaining content)
    """
    frontmatter = {}

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip()
            content = parts[2]

    return frontmatter, content


async def generate_quiz_for_chapter(
    chapter_path: Path,
    num_questions: int,
    model: genai.GenerativeModel,
) -> dict | None:
    """Generate quiz questions for a chapter using Gemini.

    Args:
        chapter_path: Path to chapter markdown file
        num_questions: Number of questions to generate
        model: Gemini model instance

    Returns:
        Quiz data dict or None on error
    """
    print(f"Processing: {chapter_path.name}")

    # Read content
    content = chapter_path.read_text(encoding='utf-8')
    frontmatter, body = extract_frontmatter(content)

    # Extract chapter info
    chapter_id = chapter_path.parent.name
    title = frontmatter.get("title", chapter_id.replace("-", " ").title())

    # Clean content for quiz generation
    text_content = extract_text_content(body)

    # Truncate if too long (Gemini has context limits)
    max_chars = 30000
    if len(text_content) > max_chars:
        text_content = text_content[:max_chars] + "\n\n[Content truncated...]"

    print(f"  - Content length: {len(text_content)} chars")

    # Generate quiz using Gemini
    prompt = QUIZ_GENERATION_PROMPT.format(
        num_questions=num_questions,
        content=text_content
    )

    try:
        response = await model.generate_content_async(prompt)
        response_text = response.text

        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        quiz_data = json.loads(response_text.strip())

        # Add metadata
        quiz_data["chapter_id"] = chapter_id
        quiz_data["chapter_title"] = title

        print(f"  - Generated {len(quiz_data.get('questions', []))} questions")
        return quiz_data

    except json.JSONDecodeError as e:
        print(f"  - Error parsing JSON: {e}")
        print(f"  - Response: {response_text[:500]}...")
        return None
    except Exception as e:
        print(f"  - Error generating quiz: {e}")
        return None


def save_quiz(quiz_data: dict, output_dir: Path) -> Path:
    """Save quiz data to JSON file.

    Args:
        quiz_data: Quiz data dictionary
        output_dir: Directory to save quiz files

    Returns:
        Path to saved file
    """
    chapter_id = quiz_data.get("chapter_id", "unknown")
    output_path = output_dir / f"{chapter_id}-quiz.json"

    # Add UUIDs to questions
    for i, question in enumerate(quiz_data.get("questions", [])):
        question["id"] = str(uuid.uuid4())
        question["order"] = i + 1
        question["points"] = 1

    # Add quiz UUID
    quiz_data["id"] = str(uuid.uuid4())

    output_path.write_text(
        json.dumps(quiz_data, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )

    return output_path


async def main():
    """Main quiz generation function."""
    parser = argparse.ArgumentParser(description="Generate quizzes for textbook chapters")
    parser.add_argument(
        "--chapter",
        help="Generate quiz for specific chapter (e.g., chapter-1)"
    )
    parser.add_argument(
        "--questions",
        type=int,
        default=5,
        help="Number of questions per quiz (default: 5)"
    )
    parser.add_argument(
        "--content-dir",
        default="content/source",
        help="Directory containing chapter content"
    )
    parser.add_argument(
        "--output-dir",
        default="content/quizzes",
        help="Directory for output quiz files"
    )

    args = parser.parse_args()

    # Configure Gemini
    if not settings.gemini_api_key:
        print("Error: GEMINI_API_KEY not set in environment")
        sys.exit(1)

    genai.configure(api_key=settings.gemini_api_key)

    # Create model with appropriate settings
    model = genai.GenerativeModel(
        model_name=settings.generation_model,
        generation_config=genai.GenerationConfig(
            temperature=0.7,  # Some creativity for varied questions
            top_p=0.9,
        ),
    )

    # Find content directory
    content_dir = Path(args.content_dir)
    if not content_dir.exists():
        content_dir = Path(__file__).parent.parent.parent / args.content_dir

    if not content_dir.exists():
        print(f"Error: Content directory not found: {args.content_dir}")
        sys.exit(1)

    # Create output directory
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = Path(__file__).parent.parent.parent / args.output_dir

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Content directory: {content_dir.absolute()}")
    print(f"Output directory: {output_dir.absolute()}")
    print(f"Questions per quiz: {args.questions}")

    # Find chapter files
    if args.chapter:
        md_files = list(content_dir.glob(f"{args.chapter}/*.md"))
    else:
        md_files = list(content_dir.glob("**/index.md"))

    if not md_files:
        print("No markdown files found")
        sys.exit(1)

    print(f"Found {len(md_files)} chapter(s) to process")

    # Generate quizzes
    generated = 0
    for chapter_path in md_files:
        quiz_data = await generate_quiz_for_chapter(
            chapter_path,
            args.questions,
            model
        )

        if quiz_data:
            output_path = save_quiz(quiz_data, output_dir)
            print(f"  - Saved to: {output_path}")
            generated += 1

        # Rate limiting
        await asyncio.sleep(2)

    print(f"\nQuiz generation complete! Generated {generated} quiz(es).")


if __name__ == "__main__":
    asyncio.run(main())
