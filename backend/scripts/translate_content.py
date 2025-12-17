#!/usr/bin/env python3
"""
Content Translation Script for Urdu.

This script:
1. Reads English markdown files from content/source/
2. Preserves code blocks (keeps them in English)
3. Translates text content using Gemini
4. Saves translated files to content/translations/ur/

Usage:
    python -m scripts.translate_content [--source content/source] [--output content/translations/ur]
"""

import argparse
import asyncio
import re
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

import google.generativeai as genai

from src.core.config import settings


# Translation system prompt
TRANSLATION_SYSTEM_PROMPT = """You are an expert translator specializing in technical and educational content translation from English to Urdu.

IMPORTANT RULES:
1. Translate the text naturally into Urdu while maintaining the technical accuracy
2. Keep technical terms in English when they don't have a common Urdu equivalent
3. Preserve all markdown formatting (headings, lists, bold, italic, links)
4. DO NOT translate text inside code blocks or inline code - these MUST remain in English
5. Preserve all placeholders like [CODE_BLOCK_N] exactly as they are
6. Maintain the same document structure and formatting
7. Use formal Urdu appropriate for academic/educational content
8. Transliterate names of robots, companies, and proper nouns

The text may contain [CODE_BLOCK_N] placeholders - leave these exactly as they are.

Translate the following content to Urdu:"""


def extract_code_blocks(content: str) -> tuple[str, list[str]]:
    """Extract code blocks from markdown and replace with placeholders.

    Args:
        content: Markdown content

    Returns:
        Tuple of (content with placeholders, list of code blocks)
    """
    code_blocks = []

    # Pattern for fenced code blocks (```...```)
    pattern = r'```[\s\S]*?```'

    def replace_block(match):
        code_blocks.append(match.group(0))
        return f'[CODE_BLOCK_{len(code_blocks) - 1}]'

    modified_content = re.sub(pattern, replace_block, content)

    return modified_content, code_blocks


def extract_inline_code(content: str) -> tuple[str, list[str]]:
    """Extract inline code from markdown and replace with placeholders.

    Args:
        content: Markdown content (after code blocks extracted)

    Returns:
        Tuple of (content with placeholders, list of inline code)
    """
    inline_codes = []

    # Pattern for inline code (`...`)
    pattern = r'`[^`]+`'

    def replace_code(match):
        inline_codes.append(match.group(0))
        return f'[INLINE_CODE_{len(inline_codes) - 1}]'

    modified_content = re.sub(pattern, replace_code, content)

    return modified_content, inline_codes


def restore_code_blocks(content: str, code_blocks: list[str]) -> str:
    """Restore code blocks from placeholders.

    Args:
        content: Content with placeholders
        code_blocks: List of original code blocks

    Returns:
        Content with code blocks restored
    """
    for i, block in enumerate(code_blocks):
        content = content.replace(f'[CODE_BLOCK_{i}]', block)

    return content


def restore_inline_code(content: str, inline_codes: list[str]) -> str:
    """Restore inline code from placeholders.

    Args:
        content: Content with placeholders
        inline_codes: List of original inline code

    Returns:
        Content with inline code restored
    """
    for i, code in enumerate(inline_codes):
        content = content.replace(f'[INLINE_CODE_{i}]', code)

    return content


def extract_frontmatter(content: str) -> tuple[str, str]:
    """Extract and preserve YAML frontmatter.

    Args:
        content: Full markdown content

    Returns:
        Tuple of (frontmatter string, body content)
    """
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = f'---{parts[1]}---\n'
            body = parts[2]
            return frontmatter, body

    return '', content


def translate_frontmatter(frontmatter: str) -> str:
    """Translate frontmatter title and description to Urdu.

    Only translates specific fields, keeps others as-is.

    Args:
        frontmatter: YAML frontmatter string

    Returns:
        Translated frontmatter
    """
    # For now, keep frontmatter mostly unchanged
    # In a full implementation, we'd translate title and description
    return frontmatter


async def translate_text(text: str, model: genai.GenerativeModel) -> str:
    """Translate text using Gemini.

    Args:
        text: Text to translate
        model: Gemini model instance

    Returns:
        Translated text
    """
    prompt = f"{TRANSLATION_SYSTEM_PROMPT}\n\n{text}"

    try:
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        print(f"Translation error: {e}")
        raise


async def translate_file(
    source_path: Path,
    output_path: Path,
    model: genai.GenerativeModel,
) -> None:
    """Translate a single markdown file.

    Args:
        source_path: Path to source English file
        output_path: Path for translated file
        model: Gemini model instance
    """
    print(f"Translating: {source_path.name}")

    # Read source content
    content = source_path.read_text(encoding='utf-8')

    # Extract frontmatter
    frontmatter, body = extract_frontmatter(content)

    # Extract code blocks (preserve them)
    body_no_code, code_blocks = extract_code_blocks(body)

    # Extract inline code
    body_no_inline, inline_codes = extract_inline_code(body_no_code)

    print(f"  - Found {len(code_blocks)} code blocks, {len(inline_codes)} inline code")

    # Split into chunks for translation (avoid token limits)
    # Translate in sections based on headings
    sections = re.split(r'(^#{1,6}\s+.+$)', body_no_inline, flags=re.MULTILINE)

    translated_sections = []
    for i, section in enumerate(sections):
        if not section.strip():
            translated_sections.append(section)
            continue

        # Translate section
        try:
            translated = await translate_text(section, model)
            translated_sections.append(translated)
            print(f"  - Translated section {i + 1}/{len(sections)}")
        except Exception as e:
            print(f"  - Error translating section {i + 1}: {e}")
            translated_sections.append(section)  # Keep original on error

        # Rate limiting
        await asyncio.sleep(1)

    # Reassemble
    translated_body = ''.join(translated_sections)

    # Restore inline code
    translated_body = restore_inline_code(translated_body, inline_codes)

    # Restore code blocks
    translated_body = restore_code_blocks(translated_body, code_blocks)

    # Combine with frontmatter
    final_content = frontmatter + translated_body

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write translated file
    output_path.write_text(final_content, encoding='utf-8')
    print(f"  - Saved to: {output_path}")


async def main():
    """Main translation function."""
    parser = argparse.ArgumentParser(description="Translate textbook content to Urdu")
    parser.add_argument(
        "--source",
        default="content/source",
        help="Source directory with English content"
    )
    parser.add_argument(
        "--output",
        default="content/translations/ur",
        help="Output directory for Urdu translations"
    )
    parser.add_argument(
        "--chapter",
        help="Translate only a specific chapter (e.g., chapter-1)"
    )

    args = parser.parse_args()

    # Configure Gemini
    if not settings.gemini_api_key:
        print("Error: GEMINI_API_KEY not set in environment")
        sys.exit(1)

    genai.configure(api_key=settings.gemini_api_key)

    # Create model
    model = genai.GenerativeModel(
        model_name=settings.generation_model,
        generation_config=genai.GenerationConfig(
            temperature=0.3,  # Low temperature for consistent translations
        ),
    )

    # Find source directory
    source_dir = Path(args.source)
    if not source_dir.exists():
        source_dir = Path(__file__).parent.parent.parent / args.source

    if not source_dir.exists():
        print(f"Error: Source directory not found: {args.source}")
        sys.exit(1)

    output_dir = Path(args.output)
    if not output_dir.is_absolute():
        output_dir = Path(__file__).parent.parent.parent / args.output

    print(f"Source: {source_dir.absolute()}")
    print(f"Output: {output_dir.absolute()}")

    # Find markdown files
    if args.chapter:
        md_files = list(source_dir.glob(f"{args.chapter}/*.md"))
    else:
        md_files = list(source_dir.glob("**/index.md"))

    if not md_files:
        print("No markdown files found")
        sys.exit(1)

    print(f"Found {len(md_files)} files to translate")

    # Translate each file
    for source_path in md_files:
        # Compute output path
        relative_path = source_path.relative_to(source_dir)
        output_path = output_dir / relative_path

        await translate_file(source_path, output_path, model)

    print(f"\nTranslation complete! {len(md_files)} files translated.")


if __name__ == "__main__":
    asyncio.run(main())
