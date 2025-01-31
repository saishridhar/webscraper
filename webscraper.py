import requests 
from dotenv import load_dotenv
import os
import logging
import sys
from google import genai
from typing import Any
import mcp.types as types
import asyncio
from openai import OpenAI
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("websrcaper")

load_dotenv()

api_key = os.getenv('OPENROUTER_API_KEY')
client = OpenAI(base_url="https://openrouter.ai/api/v1",api_key=api_key)


@mcp.tool()
async def get_webpage_content(url: str) -> str:
    '''
    Returns the text content on a webpage based on the url provided. 
    When the user provides a url and asks questions based on that, this function should be called.
    Args:
        url: The url from which you want to text to be extracted. 

    '''
    
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        webpage_content = response.text  # Get the HTML content of the page
        logging.error("Webpage Recieved!")
    
    else:
        logging.error(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        
    
    logging.error("Thinking...")


    completion = client.chat.completions.create(
            model="google/gemini-pro-1.5",
            max_tokens = 8000,
            messages=[
                {
                "role": "user",
                "content": f"{webpage_content}\n\nExtract only the text that would display on the main page. No links and other things. Just the text that would appear at the center of the page. Think about what the reader would actually be reading when he opened this page and display that. Return the complete, rendered text of the main page, including all sections, subsections, paragraphs, code blocks with syntax highlighting, and the textual representations of the diagrams, as it would be visible to a user, without any extraneous HTML or metadata. Ensure that the output preserves the original structure and formatting of the text."
                }
            ]
            )
    
    logging.error("Processed Webpage Recieved")
    output = completion.choices[0].message.content
    
    return [types.TextContent(type="text", text=output)]


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')


