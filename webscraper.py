import sys # Import sys
from typing import Any, Optional, List
import mcp.types as types
import asyncio
import httpx
import os
from youtube_transcript_api import YouTubeTranscriptApi
import re
from urllib.parse import urlparse
import trafilatura
from trafilatura.settings import use_config
from concurrent.futures import ThreadPoolExecutor
from mcp.server.fastmcp import FastMCP
from utils.pdf_scraper import download_pdf_from_url
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

import marker

# Constants for configuration
TIMEOUT_SECONDS = int(os.environ.get("REQUEST_TIMEOUT", "30"))  # Default 30 seconds
MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", str(10 * 1024 * 1024)))  # Default 10MB

class WebScraperError(Exception):
    """Base exception for webscraper errors"""
    pass

class InvalidURLError(WebScraperError):
    """Raised when URL is invalid"""
    pass

class ContentExtractionError(WebScraperError):
    """Raised when content extraction fails"""
    pass

def validate_url(url: str) -> bool:
    """
    Validate if the provided URL is well-formed.
    
    Args:
        url: URL string to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

async def fetch_url(url: str, timeout: int) -> str:
    """
    Fetch URL content asynchronously with timeout.
    
    Args:
        url: URL to fetch
        timeout: Timeout in seconds
        
    Returns:
        str: HTML content
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=timeout, follow_redirects=True)
        response.raise_for_status()
        return response.text

# Create the FastMCP instance with a descriptive name
server = FastMCP("Web Scraper")
print("[webscraper.py] FastMCP instance created", file=sys.stderr, flush=True)

@server.tool()
async def get_webpage_content(url: str) -> List[types.TextContent]:
    '''
    Returns the text content on a webpage based on the link provided.
    Uses trafilatura for efficient text extraction with good handling of boilerplate content.
    
    Args:
        url: The url from which to extract text.
        
    Raises:
        InvalidURLError: If URL is malformed
        ContentExtractionError: If content extraction fails
    '''
    print(f"[webscraper.py] get_webpage_content called with URL: {url}", file=sys.stderr, flush=True)
    if not validate_url(url):
        raise InvalidURLError(f"Invalid URL provided: {url}")
        
    try:
        # Fetch HTML content
        html_content = await fetch_url(url, TIMEOUT_SECONDS)
        
        # Use ThreadPoolExecutor for CPU-bound text extraction
        with ThreadPoolExecutor() as executor:
            extracted_text = await asyncio.get_event_loop().run_in_executor(
                executor,
                lambda: trafilatura.extract(html_content, include_comments=False, include_tables=True, 
                                          include_images=False, include_links=False, no_fallback=False)
            )
            
        if not extracted_text:
            raise ContentExtractionError("No content could be extracted from the webpage")
            
        # Extract metadata using a separate executor call to avoid ConfigParser encoding issues
        with ThreadPoolExecutor() as executor:
            metadata_dict = await asyncio.get_event_loop().run_in_executor(
                executor,
                lambda: trafilatura.metadata.extract_metadata(html_content)
            )
        
        # Combine metadata with content
        output = []
        if metadata_dict:
            if hasattr(metadata_dict, 'title') and metadata_dict.title:
                output.append(f"# {metadata_dict.title}\n")
            if hasattr(metadata_dict, 'author') and metadata_dict.author:
                output.append(f"Author: {metadata_dict.author}\n")
            if hasattr(metadata_dict, 'date') and metadata_dict.date:
                output.append(f"Date: {metadata_dict.date}\n")
            output.append("\n---\n\n")
            
        output.append(extracted_text)
        
        return [types.TextContent(type="text", text="\n".join(output))]
            
    except httpx.TimeoutException:
        raise ContentExtractionError(f"Request timed out after {TIMEOUT_SECONDS} seconds")
    except httpx.HTTPError as e:
        raise ContentExtractionError(f"HTTP error occurred: {str(e)}")
    except Exception as e:
        print(f"Error in get_webpage_content tool: {e}", file=sys.stderr, flush=True)
        raise ContentExtractionError(f"Failed to extract content: {str(e)}")

@server.tool()
async def get_youtube_transcript(url: str) -> List[types.TextContent]:
    '''
    Extract transcript from YouTube videos.
    
    Args:
        url: YouTube video URL
        
    Raises:
        InvalidURLError: If URL is not a valid YouTube URL
        ContentExtractionError: If transcript extraction fails
    '''
    print(f"[webscraper.py] get_youtube_transcript called with URL: {url}", file=sys.stderr, flush=True)
    
    youtube_re = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})"

    if not validate_url(url):
        raise InvalidURLError(f"Invalid URL provided: {url}")

    match = re.search(youtube_re, url)
    if not match:
        raise InvalidURLError("Invalid YouTube URL format")
        
    video_id = match.group(1)
    
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        output = " ".join(item['text'] for item in transcript_list)
        
        if not output.strip():
            raise ContentExtractionError("Empty transcript received")
            
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        raise ContentExtractionError(f"No transcript available: {str(e)}")
    except Exception as e:
        print(f"Error extracting YouTube transcript: {e}", file=sys.stderr, flush=True)
        raise ContentExtractionError(f"Failed to extract transcript: {str(e)}")
        
    return [types.TextContent(type="text", text=output)]

@server.tool()
async def get_pdf(url: str) -> List[types.TextContent]:
    """
    Convert a URL that leads to a PDF file to markdown text.
    
    Args:
        url: URL of the PDF file
        
    Raises:
        InvalidURLError: If URL is invalid
        ContentExtractionError: If PDF processing fails
    """
    print(f"[webscraper.py] get_pdf called with URL: {url}", file=sys.stderr, flush=True)
    
    if not validate_url(url):
        raise InvalidURLError(f"Invalid URL provided: {url}")
        
    try:
        filename = download_pdf_from_url(url)
        
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            raise ContentExtractionError("PDF download failed or file is empty")
            
        if os.path.getsize(filename) > MAX_CONTENT_LENGTH:
            raise ContentExtractionError(f"PDF file too large (max {MAX_CONTENT_LENGTH/1024/1024}MB)")
        
        # Convert PDF to markdown using marker
        output = marker.convert(filename)
        
        if not output.strip():
            raise ContentExtractionError("No text content extracted from PDF")
            
    except Exception as e:
        print(f"Error processing PDF: {e}", file=sys.stderr, flush=True)
        raise ContentExtractionError(f"Failed to process PDF: {str(e)}")
    finally:
        # Clean up temporary file
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)
            
    return [types.TextContent(type="text", text=output)]

if __name__ == "__main__":
    from typing import List  # Fix missing import
    
    debug_mode = os.environ.get("MCP_DEBUG", "0") == "1"
    client_running = os.environ.get("MCP_CLIENT_RUNNING", "0") == "1"
    
    # Print debug information on stderr to not interfere with stdio transport
    if debug_mode:
        print(f"[webscraper.py DEBUG] Debug mode enabled", file=sys.stderr, flush=True)
        print(f"[webscraper.py DEBUG] Python version: {sys.version}", file=sys.stderr, flush=True)
        print(f"[webscraper.py DEBUG] PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}", file=sys.stderr, flush=True)
        print(f"[webscraper.py DEBUG] Running from MCP client: {client_running}", file=sys.stderr, flush=True)
        print(f"[webscraper.py DEBUG] stdin/stdout isatty: {sys.stdin.isatty()}/{sys.stdout.isatty()}", file=sys.stderr, flush=True)
    
    try:
        print("[webscraper.py] Starting MCP server with stdio transport...", file=sys.stderr, flush=True)
        
        # Following the MCP documentation pattern for server initialization
        if debug_mode:
            # In debug mode, use the async version with explicit asyncio.run
            print("[webscraper.py DEBUG] Running server in asyncio debug mode", file=sys.stderr, flush=True)
            asyncio.run(server.run_stdio_async())
        else:
            # Standard mode - use the synchronous run method
            print("[webscraper.py] Running server.run(transport='stdio')", file=sys.stderr, flush=True)
            server.run(transport='stdio')
            
    except KeyboardInterrupt:
        print("[webscraper.py] Server interrupted by user", file=sys.stderr, flush=True)
        sys.exit(130)
    except Exception as e:
        print(f"[webscraper.py] Server error: {type(e).__name__} - {e}", file=sys.stderr, flush=True)
        if debug_mode:
            import traceback
            traceback.print_exc(file=sys.stderr)
        sys.exit(1)