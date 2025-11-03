#!/usr/bin/env python3
"""
Clanker Documentation Crawler

This script crawls all pages from https://clanker.gitbook.io/clanker-documentation
and saves them as formatted markdown files using Firecrawl API, then combines
them into 2 organized documents.
"""

import os
import time
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse
from dotenv import load_dotenv

try:
    from firecrawl import FirecrawlApp
except ImportError:
    print("Error: firecrawl-py package not installed.")
    print("Please run: pip install firecrawl-py")
    exit(1)


class ClankerDocsCrawler:
    """Crawler for Clanker documentation using Firecrawl."""
    
    def __init__(
        self,
        base_url: str = "https://clanker.gitbook.io/clanker-documentation",
        output_dir: str = "clanker_docs",
        api_key: Optional[str] = None,
        limit: Optional[int] = None,
    ):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.limit = limit
        self.failed_urls: List[str] = []
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Firecrawl client
        if not api_key:
            raise ValueError("Firecrawl API key is required. Set FIRECRAWL_API_KEY in .env file or pass as argument.")
        
        self.firecrawl = FirecrawlApp(api_key=api_key)
        
    def _url_to_filename(self, url: str) -> str:
        """Convert URL to a safe filename."""
        parsed = urlparse(url)
        path = parsed.path.strip('/').replace('/', '_')
        if not path:
            path = 'index'
        # Remove or replace invalid filename characters
        path = path.replace('?', '_').replace('&', '_').replace('=', '_')
        # Remove file extensions like .html
        if path.endswith('.html'):
            path = path[:-5]
        if len(path) > 200:  # Limit filename length
            path = path[:200]
        return f"{path}.md"
    
    def save_markdown(self, url: str, content: str, metadata: Optional[dict] = None) -> bool:
        """Save markdown content to a file."""
        filename = self._url_to_filename(url)
        filepath = self.output_dir / filename
        
        try:
            # Build frontmatter with source URL and metadata
            frontmatter_lines = [
                "---",
                f"source_url: {url}",
                f"crawled_at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            ]
            
            if metadata:
                if metadata.get('title'):
                    frontmatter_lines.append(f"title: {metadata.get('title')}")
                if metadata.get('description'):
                    desc = metadata.get('description', '').replace('\n', ' ')
                    frontmatter_lines.append(f"description: {desc}")
            
            frontmatter_lines.append("---")
            frontmatter = "\n".join(frontmatter_lines) + "\n\n"
            
            filepath.write_text(frontmatter + content, encoding='utf-8')
            print(f"  ✓ Saved: {filepath.name}")
            return True
        except Exception as e:
            print(f"  ✗ Error saving {filepath}: {str(e)}")
            return False
    
    def crawl_all(self) -> List[dict]:
        """Crawl all pages from the Clanker docs site using Firecrawl."""
        print(f"Starting crawl of {self.base_url}...")
        print(f"Using Firecrawl API...")
        if self.limit:
            print(f"Limit: {self.limit} pages")
        print()
        
        try:
            crawl_params = {}
            if self.limit:
                crawl_params['limit'] = self.limit
            
            print("Submitting crawl job and waiting for completion...")
            print("(This may take a few minutes depending on the site size)")
            
            # Retry with exponential backoff for rate limits
            max_retries = 3
            retry_delay = 30
            result = None
            
            for attempt in range(max_retries):
                try:
                    print("Starting crawl (this will poll automatically)...")
                    result = self.firecrawl.crawl_url(
                        url=self.base_url,
                        params=crawl_params,
                        poll_interval=5
                    )
                    break
                except Exception as e:
                    error_msg = str(e)
                    if ("Rate limit" in error_msg or "429" in error_msg) and attempt < max_retries - 1:
                        print(f"Rate limit exceeded. Waiting {retry_delay} seconds before retry {attempt + 2}/{max_retries}...")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        print(f"Error during crawl: {error_msg}")
                        return []
            
            if not result:
                print("Failed to crawl after all retries.")
                return []
            
            # Parse the result
            if isinstance(result, dict):
                pages = result.get('data', [])
                if not pages and 'success' in result and not result.get('success'):
                    print(f"Crawl failed: {result.get('message', 'Unknown error')}")
                    return []
            elif isinstance(result, list):
                pages = result
            else:
                print(f"Unexpected result type: {type(result)}")
                return []
            
            if not pages:
                print("No pages returned from Firecrawl.")
                return []
            
            print(f"\nCrawl completed! Received {len(pages)} pages\n")
            
            successful = 0
            all_pages = []
            
            for i, page in enumerate(pages, 1):
                url = page.get('metadata', {}).get('sourceURL', '') or page.get('url', '')
                markdown = page.get('markdown', '')
                metadata = page.get('metadata', {})
                
                if not url:
                    print(f"  ✗ Page {i}: No URL found, skipping")
                    continue
                
                if not markdown:
                    print(f"  ✗ Page {i} ({url}): No markdown content")
                    self.failed_urls.append(url)
                    continue
                
                print(f"  [{i}/{len(pages)}] Processing: {url}")
                if self.save_markdown(url, markdown, metadata):
                    successful += 1
                    all_pages.append({
                        'url': url,
                        'markdown': markdown,
                        'metadata': metadata
                    })
                else:
                    self.failed_urls.append(url)
            
            print(f"\n{'='*60}")
            print(f"Crawling complete!")
            print(f"Successfully saved: {successful}/{len(pages)}")
            print(f"Failed: {len(self.failed_urls)}")
            
            return all_pages
            
        except Exception as e:
            print(f"Error during crawl: {str(e)}")
            import traceback
            traceback.print_exc()
            return []


def categorize_page(url: str, content: str, metadata: dict) -> str:
    """Categorize a page into one of two groups."""
    url_lower = url.lower()
    content_lower = content.lower()
    title_lower = metadata.get('title', '').lower()
    
    # Category 1: Getting Started & General (Introduction, FAQ, Quick Start, General info)
    if any(keyword in url_lower or keyword in title_lower or keyword in content_lower[:500] for keyword in [
        'introduction', 'quick-start', 'quickstart', 'getting-started', 'getting started',
        'faq', 'general', 'overview', 'getting started', 'welcome', 'index',
        'creator rewards', 'fees', 'warning tags', 'token deployments', 'changelog'
    ]):
        return 'getting_started'
    
    # Category 2: SDK & API Reference (Technical docs, SDK, API, CLI)
    return 'technical_reference'


def combine_into_documents(pages: List[dict], output_dir: Path):
    """Combine pages into 2 organized documents."""
    categorized = {
        'getting_started': [],
        'technical_reference': []
    }
    
    for page in pages:
        category = categorize_page(page['url'], page['markdown'], page['metadata'])
        categorized[category].append(page)
    
    print(f"\nCategorization:")
    print(f"  Getting Started & General: {len(categorized['getting_started'])} pages")
    print(f"  SDK & API Reference: {len(categorized['technical_reference'])} pages")
    print()
    
    # Create combined output directory
    combined_dir = output_dir / 'combined'
    combined_dir.mkdir(exist_ok=True)
    
    # Combine Getting Started
    if categorized['getting_started']:
        create_combined_doc(
            categorized['getting_started'],
            combined_dir / '01_getting_started_and_general.md',
            "Clanker Documentation - Getting Started & General",
            "This document contains introduction guides, quick start tutorials, FAQs, general information, and non-technical documentation for Clanker."
        )
    
    # Combine Technical Reference
    if categorized['technical_reference']:
        create_combined_doc(
            categorized['technical_reference'],
            combined_dir / '02_sdk_and_api_reference.md',
            "Clanker Documentation - SDK & API Reference",
            "This document contains SDK documentation, API references, CLI guides, and all technical specifications for developers using Clanker."
        )
    
    print(f"\n✅ Combined documents created in: {combined_dir}")


def create_combined_doc(pages: List[dict], output_path: Path, title: str, description: str):
    """Create a combined markdown document from multiple pages."""
    lines = [
        f"# {title}",
        "",
        description,
        "",
        "---",
        "",
        ""
    ]
    
    for i, page in enumerate(pages, 1):
        url = page['url']
        content = page['markdown']
        metadata = page['metadata']
        
        # Extract title
        title_text = metadata.get('title', '')
        if not title_text:
            # Try to get from content
            import re
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                title_text = title_match.group(1)
            else:
                # Use URL as fallback
                parsed = urlparse(url)
                title_text = parsed.path.strip('/').replace('/', ' ').replace('-', ' ').title()
        
        lines.append(f"## {title_text}")
        lines.append("")
        lines.append(f"*Source: {url}*")
        lines.append("")
        
        # Remove the first heading if it matches our section title
        content_lines = content.split('\n')
        if content_lines and content_lines[0].startswith('#') and content_lines[0].replace('#', '').strip().lower() == title_text.lower():
            content = '\n'.join(content_lines[1:]).strip()
        
        lines.append(content)
        lines.append("")
        lines.append("---")
        lines.append("")
    
    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"✓ Created {output_path.name} with {len(pages)} sections")


def main():
    """Main entry point."""
    import argparse
    
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="Crawl Clanker documentation and combine into 2 markdown files"
    )
    parser.add_argument(
        '--output-dir',
        default='clanker_docs',
        help='Output directory for files (default: clanker_docs)'
    )
    parser.add_argument(
        '--api-key',
        default=None,
        help='Firecrawl API key (or set FIRECRAWL_API_KEY in .env file)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit the number of pages to crawl (default: no limit)'
    )
    parser.add_argument(
        '--skip-crawl',
        action='store_true',
        help='Skip crawling and only combine existing files'
    )
    
    args = parser.parse_args()
    
    api_key = args.api_key or os.getenv('FIRECRAWL_API_KEY')
    
    if not args.skip_crawl:
        if not api_key:
            print("Error: Firecrawl API key not found.")
            print("Please either:")
            print("  1. Set FIRECRAWL_API_KEY in your .env file")
            print("  2. Pass --api-key argument")
            exit(1)
        
        crawler = ClankerDocsCrawler(
            output_dir=args.output_dir,
            api_key=api_key,
            limit=args.limit,
        )
        
        pages = crawler.crawl_all()
        
        if pages:
            combine_into_documents(pages, Path(args.output_dir))
        else:
            print("No pages to combine.")
    else:
        # Just combine existing files
        print("Skipping crawl, combining existing files...")
        output_dir = Path(args.output_dir)
        pages = []
        
        for md_file in output_dir.glob('*.md'):
            if md_file.name.startswith('combined_') or md_file.name.startswith('0'):
                continue
            try:
                content = md_file.read_text(encoding='utf-8')
                # Parse frontmatter
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    frontmatter = parts[1]
                    source_url = ''
                    title = ''
                    for line in frontmatter.split('\n'):
                        if line.startswith('source_url:'):
                            source_url = line.split(':', 1)[1].strip()
                        elif line.startswith('title:'):
                            title = line.split(':', 1)[1].strip()
                    content = parts[2] if len(parts) > 2 else ''
                else:
                    source_url = str(md_file)
                    title = ''
                
                pages.append({
                    'url': source_url,
                    'markdown': content.strip(),
                    'metadata': {'title': title}
                })
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
        
        if pages:
            combine_into_documents(pages, output_dir)
        else:
            print("No existing files found to combine.")


if __name__ == "__main__":
    main()

