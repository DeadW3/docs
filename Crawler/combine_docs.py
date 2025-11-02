#!/usr/bin/env python3
"""
Combine Internet Archive developer docs into 3 organized documents for GPT instructions.
"""

from pathlib import Path
import re
from typing import List, Tuple


def read_markdown_file(filepath: Path) -> Tuple[str, str]:
    """Read a markdown file and extract content (removing frontmatter)."""
    content = filepath.read_text(encoding='utf-8')
    
    # Remove frontmatter if present
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            # Extract source URL from frontmatter for reference
            frontmatter = parts[1]
            source_url = ''
            for line in frontmatter.split('\n'):
                if line.startswith('source_url:'):
                    source_url = line.split(':', 1)[1].strip()
                    break
            content = parts[2].strip()
        else:
            content = parts[1] if len(parts) > 1 else content
    else:
        source_url = str(filepath)
    
    return content.strip(), source_url


def categorize_file(filename: str, content: str) -> str:
    """Categorize a file into one of three groups."""
    filename_lower = filename.lower()
    content_lower = content.lower()
    
    # Category 1: Getting Started & Quick Start
    if any(keyword in filename_lower for keyword in [
        'quick-start', 'installation', 'setup', 'getting-started',
        'index', 'developers.md', 'introduction'
    ]) or filename_lower == 'developers.md':
        return 'getting_started'
    
    # Category 2: Tutorials & How-To Guides
    if any(keyword in filename_lower for keyword in [
        'tutorial', 'how-to', 'guide', 'example', 'walkthrough'
    ]):
        return 'tutorials'
    
    # Category 3: API Reference & Advanced Topics
    # Everything else (APIs, metadata, advanced features, reference)
    return 'api_reference'


def create_combined_document(
    files: List[Tuple[Path, str]],
    output_path: Path,
    title: str,
    description: str
) -> None:
    """Combine multiple markdown files into a single document."""
    lines = [
        f"# {title}",
        "",
        description,
        "",
        "---",
        "",
        ""
    ]
    
    for i, (filepath, category) in enumerate(files, 1):
        try:
            content, source_url = read_markdown_file(filepath)
            
            # Extract a title from the filename or content
            filename = filepath.stem.replace('developers_', '').replace('__sources_', '').replace('_', ' ').title()
            
            # Try to get the actual title from content
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                doc_title = title_match.group(1)
            else:
                doc_title = filename
            
            lines.append(f"## {doc_title}")
            lines.append("")
            if source_url and source_url.startswith('http'):
                lines.append(f"*Source: {source_url}*")
                lines.append("")
            lines.append(content)
            lines.append("")
            lines.append("---")
            lines.append("")
            
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            continue
    
    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"✓ Created {output_path.name} with {len(files)} sections")


def main():
    """Main function to combine all docs."""
    archive_docs_dir = Path('archive_docs')
    
    if not archive_docs_dir.exists():
        print(f"Error: {archive_docs_dir} directory not found")
        return
    
    # Get all markdown files except INDEX.md
    all_files = [
        f for f in archive_docs_dir.glob('*.md')
        if f.name != 'INDEX.md' and not f.name.startswith('combined_')
    ]
    
    print(f"Found {len(all_files)} markdown files to combine\n")
    
    # Read and categorize all files
    categorized = {
        'getting_started': [],
        'tutorials': [],
        'api_reference': []
    }
    
    for filepath in all_files:
        try:
            content, _ = read_markdown_file(filepath)
            category = categorize_file(filepath.name, content)
            categorized[category].append((filepath, category))
        except Exception as e:
            print(f"Warning: Could not categorize {filepath}: {e}")
    
    # Also handle files that might need manual categorization
    # Move internetarchive library docs to getting_started
    for filepath in categorized['api_reference']:
        if 'internetarchive' in filepath[0].name.lower() and 'api' not in filepath[0].name.lower():
            # Move non-API internetarchive docs to getting_started
            categorized['getting_started'].append(filepath)
            categorized['api_reference'].remove(filepath)
    
    # Print categorization summary
    print("Categorization:")
    print(f"  Getting Started: {len(categorized['getting_started'])} files")
    print(f"  Tutorials: {len(categorized['tutorials'])} files")
    print(f"  API Reference: {len(categorized['api_reference'])} files")
    print()
    
    # Create output directory
    output_dir = Path('combined_docs')
    output_dir.mkdir(exist_ok=True)
    
    # Combine files
    create_combined_document(
        categorized['getting_started'],
        output_dir / '01_getting_started.md',
        "Internet Archive Developer Documentation - Getting Started",
        "This document contains all getting started guides, quick start tutorials, installation instructions, and basic setup information for the Internet Archive Developer APIs."
    )
    
    create_combined_document(
        categorized['tutorials'],
        output_dir / '02_tutorials.md',
        "Internet Archive Developer Documentation - Tutorials",
        "This document contains step-by-step tutorials and how-to guides for common tasks using the Internet Archive APIs."
    )
    
    create_combined_document(
        categorized['api_reference'],
        output_dir / '03_api_reference.md',
        "Internet Archive Developer Documentation - API Reference",
        "This document contains complete API reference documentation, advanced topics, metadata schemas, and detailed technical specifications for the Internet Archive Developer APIs."
    )
    
    print(f"\n✅ All documents combined successfully!")
    print(f"Output directory: {output_dir}")
    print(f"\nCreated files:")
    print(f"  - 01_getting_started.md ({len(categorized['getting_started'])} sections)")
    print(f"  - 02_tutorials.md ({len(categorized['tutorials'])} sections)")
    print(f"  - 03_api_reference.md ({len(categorized['api_reference'])} sections)")


if __name__ == "__main__":
    main()



