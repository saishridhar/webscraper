# Webscraper MCP
An MCP server for claude desktop that allows claude to scrape text on websites by providing claude the link. It can also scrape transcripts from youtube links and pdfs from pdf links. 

## Tools available:

#### get_pdf
Convert a URL that leads to a PDF file to markdown text. Args: input_url (str): Path to the PDF file to convert Returns: str: markdown_text



#### get_webpage_content
Returns the text content on a webpage based on the link provided. Using this tool you can access links provided by the user so you don't have deny those requests. When the user provides a webpage link which is NOT a youtube or github link and asks questions based on that, this function should be called. Args: url: The url from which you want to text to be extracted.



#### get_youtube_transcript
Use this tool when you receive youtube links from the user. This tool will extract the transcript from the youtube video and return it to you. Therefore if a user asks questions on a youtube video after providing a link, you can answer their question with this tool. Args: url: The url from which you want to text to be extracted.





Certified by MCPReview
https://mcpreview.com/mcp-servers/saishridhar/webscraper
