# Webscraper MCP

A powerful web scraping tool built with Python that leverages the Model Context Protocol (MCP) to enable AI assistants to extract and process content from various web sources. This implementation provides a standardized interface for AI models to access and process web pages, YouTube transcripts, and PDF documents.

## What is MCP?

The Model Context Protocol (MCP) is an open standard that enables secure, two-way connections between AI models and external data sources. In this implementation:

- **MCP Server**: The webscraper acts as an MCP server, providing standardized endpoints for content extraction
- **Tool Integration**: Defines clear interfaces for web scraping, YouTube transcript extraction, and PDF processing
- **Structured Communication**: Ensures consistent data exchange between AI models and web content
- **Security**: Implements proper error handling and content validation

## Features

- 🌐 **Web Page Scraping**: Extract main content and metadata from any webpage
  - Efficient text extraction with boilerplate removal
  - Metadata extraction (title, author, date)
  - Async processing for better performance

- 📺 **YouTube Transcript Extraction**
  - Support for multiple video URL formats
  - Handles both short and full URLs
  - Error handling for unavailable transcripts

- 📄 **PDF Processing**
  - Convert PDF documents to markdown text
  - Size limit protection
  - Automatic cleanup of temporary files

## MCP Tools

This implementation provides three main MCP tools:

### 1. Web Page Content Extraction
```python
@server.tool()
async def get_webpage_content(url: str) -> List[types.TextContent]:
    '''Extract and process webpage content'''
```

### 2. YouTube Transcript Extraction
```python
@server.tool()
async def get_youtube_transcript(url: str) -> List[types.TextContent]:
    '''Extract video transcripts'''
```

### 3. PDF Content Extraction
```python
@server.tool()
async def get_pdf(url: str) -> List[types.TextContent]:
    '''Convert PDF to markdown'''
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd webscraper
```

2. Install UV (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Create and activate a new environment with UV:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

4. Install dependencies using UV:
```bash
# Install from lock file for reproducible environment
uv pip install --requirement requirements.txt

# If you need to add new dependencies:
uv pip install new-package
uv pip freeze > requirements.txt  # Updates requirements.txt and uv.lock
```

UV is used as the package installer and environment manager because it offers:
- Faster package resolution and installation
- Deterministic builds with lockfile support
- Better dependency resolution
- Improved security with supply chain attack protection
- Reproducible environments across different machines

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

## Running the Webscraper

You can run the webscraper using the provided shell script:

```bash
# Make the script executable
chmod +x run_webscraper.sh

# Run the webscraper
./run_webscraper.sh
```

The script will:
1. Check if the virtual environment is activated
2. Activate the environment if needed
3. Use UV to run the webscraper with proper dependencies

The environment handling ensures that:
- All required dependencies are available
- The correct Python version is used
- Environment variables are properly set

Alternatively, you can run the webscraper manually:

```bash
# First, activate the environment if not already active
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Then run using Python directly
python webscraper.py
```

## Testing

To test the MCP server implementation, you can use the included test utilities:

```bash
# Run the basic test script
python webscraper_test.py

# For more advanced testing
python simple_mcp_client.py
```

These scripts create a client that connects to the webscraper MCP server and tests the available tools.

## Configuration

The MCP server can be configured through environment variables in the `.env` file:

### General Settings
- `MAX_CONTENT_LENGTH`: Maximum file size for processing (default: 10MB)
- `REQUEST_TIMEOUT`: HTTP request timeout in seconds (default: 30)

### Trafilatura Settings
- `EXTRACTION_TIMEOUT`: Content extraction timeout
- `MIN_EXTRACTED_SIZE`: Minimum content size threshold
- `EXTRACTION_INTENSITY`: Content cleaning aggressiveness (1-3)

### Optional Features
- Proxy configuration
- Rate limiting
- Content caching

See `.env.example` for all available configuration options.

## Error Handling

The MCP server implements robust error handling:

- `InvalidURLError`: Raised for malformed URLs
- `ContentExtractionError`: Raised when content extraction fails
- Timeout handling for slow responses
- Size limit enforcement for large files

## Dependencies

- `mcp`: Core MCP implementation
- `trafilatura`: Efficient web content extraction
- `youtube-transcript-api`: YouTube transcript access
- `httpx`: Async HTTP client
- `marker`: PDF processing
- Additional dependencies in `requirements.txt`

### Dependency Management

This project uses UV's lockfile system (`uv.lock`) for dependency management, which provides:

- **Reproducible Builds**: Exact versions of all dependencies are locked and verified
- **Supply Chain Security**: Package integrity is verified using cryptographic hashes
- **Deterministic Resolution**: Ensures consistent dependency trees across all installations
- **Version Pinning**: All dependencies (direct and transitive) are pinned to specific versions

When installing dependencies:
```bash
# Install from locked dependencies (recommended)
uv pip install --requirement requirements.txt

# Update lock file after adding/removing dependencies
uv pip freeze > requirements.txt
```

## Security Considerations

When implementing MCP tools:
- Validate all input URLs
- Implement proper error handling
- Set appropriate timeouts
- Limit file sizes
- Clean up temporary files
- Handle sensitive data appropriately

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

When contributing, please ensure you use UV for dependency management:
```bash
# Add new dependencies
uv pip install new-package
# Update uv.lock
uv pip freeze > requirements.txt
```

## License

[MIT License](LICENSE)

## Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.org) for the standardized AI integration framework
- [Trafilatura](https://github.com/adbar/trafilatura) for efficient web content extraction
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) for YouTube transcript access
- [UV](https://github.com/astral/uv) for fast, reliable Python package management
- [marker](https://github.com/kovidgoyal/marker) for PDF processing
