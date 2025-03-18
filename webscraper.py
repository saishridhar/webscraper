import sys # Import sys
from typing import Any
import mcp.types as types
import asyncio
import httpx
import os
from youtube_transcript_api import YouTubeTranscriptApi
import re
from crawl4ai import *
from mcp.server.fastmcp import FastMCP
from utils.pdf_scraper import download_pdf_from_url


from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

mcp = FastMCP("websrcaper")

@mcp.tool()
async def get_webpage_content(url_input: str) -> str:
    '''
    Returns the text content on a webpage based on the link provided. Using this tool you can access links provided by the user so you don't have deny those requests.
    When the user provides a webpage link which is NOT a youtube or github link and asks questions based on that, this function should be called.
    Args:
        url: The url from which you want to text to be extracted.

    '''
    async with AsyncWebCrawler() as crawler:
        try:
            result = await crawler.arun(
                url=url_input,
            )
        except Exception as e:
            print(f"Error in get_webpage_content tool: {e}", file=sys.stderr) # PRINT TO STDERR!
            raise e
    #print(result.markdown)
    output = result.markdown
    return [types.TextContent(type="text", text=output)]


@mcp.tool()
async def get_youtube_transcript(url_input: str) -> str:
    '''
    Use this tool when you receive youtube links from the user. This tool will extract the transcript from the youtube video and return it to you. Therefore if a user asks questions on a youtube video after providing a link, you can answer their question with this tool.
    Args:
        url: The url from which you want to text to be extracted.

    '''
    youtube_re = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})"

    match = re.search(youtube_re, url_input)
    if match:
        video_id = match.group(1)
    else:
        print("Invalid youtube url")
        exit()
    dic = YouTubeTranscriptApi.get_transcript(video_id)
    output = ""
    for i in dic:
        output += i['text'] + " "
    return [types.TextContent(type="text", text=output)]

@mcp.tool()
async def get_pdf(url_input: str) -> str:
  
    """
    Convert a URL that leads to a PDF file to markdown text.
    
    Args:
        input_url (str): Path to the PDF file to convert
        
        
    Returns:
        str: markdown_text
    """
    
    
    
     # Extract filename without extension
    filename = download_pdf_from_url(url_input)
    
    converter = PdfConverter(
    artifact_dict=create_model_dict(),
    )
    rendered = converter(filename)
    output, _, _ = text_from_rendered(rendered)
    os.remove(filename)
    return [types.TextContent(type="text", text=output)]



if __name__ == "__main__":
    try:
        # Initialize and run the server
        mcp.run(transport='stdio')
    except Exception as e:
        print(f"Error initializing or running MCP server: {e}", file=sys.stderr) # PRINT TO STDERR!
        sys.exit(1)  # Exit with a non-zero code to indicate an error