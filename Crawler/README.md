# Internet Archive Developer Docs Crawler

A Python script to crawl all pages from [https://archive.org/developers/](https://archive.org/developers/) and convert them to formatted markdown files using the [Firecrawl API](https://docs.firecrawl.dev/introduction).

## Features

- 🔥 Uses Firecrawl for intelligent web crawling and markdown conversion
- 📝 Converts pages to clean markdown format automatically
- 🚀 Handles all URL discovery and crawling automatically
- 📁 Organizes output into nicely named markdown files
- 📋 Generates an index file listing all crawled pages
- ⚙️ Configurable page limits and output directories

## Prerequisites

You need a Firecrawl API key:
1. Sign up at [https://firecrawl.dev](https://firecrawl.dev)
2. Get your API key from the dashboard
3. Add it to your `.env` file (see Setup below)

## Installation

```bash
pip install -r requirements.txt
```

## Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your Firecrawl API key:
```
FIRECRAWL_API_KEY=fc-your-actual-api-key-here
```

## Usage

### Basic Usage

Crawl all pages from the Internet Archive developer docs:

```bash
python3 crawl_archive_docs.py
```

### Advanced Options

```bash
# Specify custom output directory
python3 crawl_archive_docs.py --output-dir my_docs

# Limit the number of pages to crawl (useful for testing)
python3 crawl_archive_docs.py --limit 10

# Pass API key directly (alternative to .env file)
python3 crawl_archive_docs.py --api-key fc-your-api-key

# Combine options
python3 crawl_archive_docs.py --output-dir archive_docs --limit 50
```

### Command Line Arguments

- `--output-dir`: Output directory for markdown files (default: `archive_docs`)
- `--api-key`: Firecrawl API key (alternative to .env file)
- `--limit`: Limit the number of pages to crawl (default: no limit)

## Output Structure

The script creates:

```
archive_docs/
├── INDEX.md              # Index of all crawled pages
├── index.md              # Main page
├── quick_start_cli.md    # Quick start pages
├── tutorials.md          # Tutorial pages
└── ...                   # Other pages
```

Each markdown file includes frontmatter with:
- Source URL
- Crawl timestamp
- Page title and description (if available)

## How It Works

1. **Firecrawl Integration**: The script uses Firecrawl's `crawl()` method which automatically:
   - Discovers all accessible pages on the site
   - Converts each page to clean markdown
   - Handles JavaScript-rendered content
   - Manages rate limiting and retries

2. **File Organization**: Markdown files are saved with descriptive filenames based on the URL path

3. **Index Generation**: An index file is created listing all crawled pages with links

## About Firecrawl

Firecrawl is an API service that:
- Crawls entire websites automatically (no sitemap required)
- Converts pages to LLM-ready markdown
- Handles dynamic content, anti-bot mechanisms, and proxies
- Provides structured data extraction capabilities

For more information, visit [https://docs.firecrawl.dev](https://docs.firecrawl.dev)

## Notes

- Firecrawl automatically handles rate limiting and retries
- The API key is required for all operations
- Large sites may take some time to crawl completely
- Failed URLs are tracked and reported at the end

## Troubleshooting

If some pages fail to crawl:
- Check your Firecrawl API key is correct
- Verify your API key has sufficient credits
- Check the Firecrawl dashboard for any errors
- Try reducing `--limit` if you're testing

For Firecrawl-specific issues, see the [Firecrawl documentation](https://docs.firecrawl.dev).

