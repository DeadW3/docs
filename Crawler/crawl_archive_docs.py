#!/usr/bin/env python3
"""
Internet Archive Developer Docs Crawler

This script crawls all pages from https://archive.org/developers/ and
saves them as formatted markdown files using Firecrawl API.
"""

import asyncio
import os
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse
import time
from dotenv import load_dotenv

try:
    from firecrawl import FirecrawlApp
except ImportError:
    print("Error: firecrawl-py package not installed.")
    print("Please run: pip install firecrawl-py")
    exit(1)


class ArchiveDocsCrawler:
    """Crawler for Internet Archive developer documentation using Firecrawl."""
    
    def __init__(
        self,
        base_url: str = "https://archive.org/developers/",
        output_dir: str = "archive_docs",
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
        """
        Save markdown content to a file.
        
        Args:
            url: Source URL
            content: Markdown content
            metadata: Optional metadata dictionary
            
        Returns:
            True if successful, False otherwise
        """
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
                    # Escape any newlines in description
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
    
    def crawl_all(self) -> None:
        """
        Crawl all pages from the developer docs site using Firecrawl.
        """
        print(f"Starting crawl of {self.base_url}...")
        print(f"Using Firecrawl API...")
        if self.limit:
            print(f"Limit: {self.limit} pages")
        print()
        
        try:
            # Use Firecrawl's crawl_url_and_watch method
            # It will automatically discover and crawl all subpages
            crawl_params = {}
            if self.limit:
                crawl_params['limit'] = self.limit
            
            print("Submitting crawl job and waiting for completion...")
            print("(This may take a few minutes depending on the site size)")
            
            # Retry with exponential backoff for rate limits
            max_retries = 3
            retry_delay = 30  # Start with 30 seconds
            result = None
            
            for attempt in range(max_retries):
                try:
                    # Use crawl_url which polls automatically and returns results
                    print("Starting crawl (this will poll automatically)...")
                    result = self.firecrawl.crawl_url(
                        url=self.base_url,
                        params=crawl_params,
                        poll_interval=5  # Poll every 5 seconds
                    )
                    break  # Success, exit retry loop
                except Exception as e:
                    error_msg = str(e)
                    if ("Rate limit" in error_msg or "429" in error_msg) and attempt < max_retries - 1:
                        print(f"Rate limit exceeded. Waiting {retry_delay} seconds before retry {attempt + 2}/{max_retries}...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        print(f"Error during crawl: {error_msg}")
                        return
            
            if not result:
                print("Failed to crawl after all retries.")
                return
            
            # Parse the result
            # The result might be a dict with 'data' key, or a list directly
            if isinstance(result, dict):
                pages = result.get('data', [])
                if not pages and 'success' in result and not result.get('success'):
                    print(f"Crawl failed: {result.get('message', 'Unknown error')}")
                    return
            elif isinstance(result, list):
                pages = result
            else:
                print(f"Unexpected result type: {type(result)}")
                print(f"Result preview: {str(result)[:200]}")
                return
            
            if not pages:
                print("No pages returned from Firecrawl.")
                print(f"Result structure: {type(result)}")
                if isinstance(result, dict):
                    print(f"Result keys: {list(result.keys())}")
                return
            
            print(f"\nCrawl completed! Received {len(pages)} pages\n")
            
            successful = 0
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
                else:
                    self.failed_urls.append(url)
            
            print(f"\n{'='*60}")
            print(f"Crawling complete!")
            print(f"Successfully saved: {successful}/{len(pages)}")
            print(f"Failed: {len(self.failed_urls)}")
            
            if self.failed_urls:
                print(f"\nFailed URLs:")
                for url in self.failed_urls:
                    print(f"  - {url}")
            
            # Create index file
            self.create_index([p.get('metadata', {}).get('sourceURL', '') or p.get('url', '') 
                              for p in pages if p.get('markdown')])
            
        except Exception as e:
            print(f"Error during crawl: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def create_index(self, urls: List[str]) -> None:
        """Create an index markdown file listing all crawled pages."""
        # Filter out empty URLs
        urls = [u for u in urls if u]
        
        index_content = """# Internet Archive Developer Documentation

This directory contains the crawled markdown files from https://archive.org/developers/

## Pages

"""
        for url in sorted(urls):
            filename = self._url_to_filename(url)
            # Get a readable title from the filename
            title = filename.replace('.md', '').replace('_', ' ').title()
            index_content += f"- [{title}]({filename}) - `{url}`\n"
        
        index_content += f"\n---\n\nTotal pages: {len(urls)}\n"
        index_content += f"Crawled at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        index_path = self.output_dir / "INDEX.md"
        index_path.write_text(index_content, encoding='utf-8')
        print(f"\nCreated index: {index_path}")


def main():
    """Main entry point."""
    import argparse
    
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="Crawl Internet Archive developer documentation and save as markdown using Firecrawl"
    )
    parser.add_argument(
        '--output-dir',
        default='archive_docs',
        help='Output directory for markdown files (default: archive_docs)'
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
    
    args = parser.parse_args()
    
    # Get API key from argument, environment variable, or .env file
    api_key = args.api_key or os.getenv('FIRECRAWL_API_KEY')
    
    if not api_key:
        print("Error: Firecrawl API key not found.")
        print("Please either:")
        print("  1. Set FIRECRAWL_API_KEY in your .env file")
        print("  2. Pass --api-key argument")
        print("  3. Set FIRECRAWL_API_KEY environment variable")
        exit(1)
    
    crawler = ArchiveDocsCrawler(
        output_dir=args.output_dir,
        api_key=api_key,
        limit=args.limit,
    )
    
    crawler.crawl_all()


if __name__ == "__main__":
    main()

