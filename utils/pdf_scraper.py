import os
import requests
import tempfile
from urllib.parse import urlparse

def download_pdf_from_url(url, output_path=None):
    """
    Download a PDF file from a URL.
    
    Args:
        url (str): URL of the PDF to download
        output_path (str): Optional path to save the PDF. If None, saves to a temporary file.
        
    Returns:
        str: Path to the downloaded PDF file
    """
    # Parse the URL to get the filename
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    
    # If no filename was found or it doesn't end with .pdf, use a default name
    if not filename or not filename.endswith('.pdf'):
        filename = 'downloaded_document.pdf'
    
    # Determine where to save the file
    if output_path is None:
        # Create a temporary file
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, filename)
    
    print("Downloading PDF...")
    # Download the PDF
    response = requests.get(url, stream=True)
    response.raise_for_status() 
    
    print("Saving PDF...")
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    
    print(f"Downloaded PDF to: {output_path}")
    return output_path