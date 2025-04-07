# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 15:18:30 2025

@author: Aleks
"""

import os
import logging
import tempfile
from urllib.parse import urlparse, unquote
import requests
import PyPDF2
import google.generativeai as genai
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def download_pdf(url):
    """
    Download a PDF file from the provided URL.
    
    Args:
        url (str): URL of the PDF file to download
        
    Returns:
        tuple: (local_path, filename) - Path to the downloaded file and its filename
    
    Raises:
        Exception: If download fails or response is not a PDF
    """
    logger.info(f"Downloading PDF from: {url}")
    
    try:
        # Parse URL to extract filename
        parsed_url = urlparse(url)
        filename = os.path.basename(unquote(parsed_url.path))
        
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'  # Ensure filename has PDF extension
        
        # Create a temporary file
        temp_dir = tempfile.gettempdir()
        local_path = os.path.join(temp_dir, filename)
        
        # Download the file with a timeout
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Check Content-Type header if available
        content_type = response.headers.get('Content-Type', '').lower()
        if content_type and 'application/pdf' not in content_type:
            logger.warning(f"Content-Type is not PDF: {content_type}")
            # Continue anyway as some servers might not set correct Content-Type
        
        # Save the file
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"PDF successfully downloaded to: {local_path}")
        return local_path, filename
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading PDF: {str(e)}")
        raise Exception(f"Failed to download PDF: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error downloading PDF: {str(e)}")
        raise Exception(f"Failed to download PDF: {str(e)}")

def validate_pdf(file_path):
    """
    Validate that the downloaded file is a valid PDF.
    
    Args:
        file_path (str): Path to the file to validate
        
    Returns:
        tuple: (is_valid, message) - Boolean indicating validity and a message
    """
    logger.info(f"Validating PDF: {file_path}")
    
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    if os.path.getsize(file_path) == 0:
        return False, "File is empty"
    
    try:
        # Try to open the file with PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            num_pages = len(reader.pages)
            
            if num_pages == 0:
                return False, "PDF has no pages"
            
            # Try to read the first page to further validate
            _ = reader.pages[0].extract_text()
            
            logger.info(f"PDF is valid with {num_pages} pages")
            return True, f"Valid PDF with {num_pages} pages"
    
    except PyPDF2.errors.PdfReadError as e:
        logger.error(f"Invalid PDF format: {str(e)}")
        return False, f"Invalid PDF format: {str(e)}"
    except Exception as e:
        logger.error(f"Error validating PDF: {str(e)}")
        return False, f"Error validating PDF: {str(e)}"

def process_with_gemini(pdf_path, prompt, api_key):
    """
    Process the PDF with Google Gemini AI.
    
    Args:
        pdf_path (str): Path to the PDF file
        prompt (str): User prompt for Gemini
        api_key (str): Google Gemini API key
        
    Returns:
        str: Response from Gemini
    """
    logger.info(f"Processing PDF with Gemini: {pdf_path}")
    
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Initialize the Gemini model - use the recommended model instead of deprecated one
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Read the PDF file
        pdf_content = extract_text_from_pdf(pdf_path)
        
        # Create the prompt with PDF content
        full_prompt = f"{prompt}\n\nPDF Content:\n{pdf_content}"
        
        # Generate content with Gemini
        response = model.generate_content(full_prompt)
        
        response_text = response.text
        logger.info("Successfully processed PDF with Gemini")
        return response_text
    
    except Exception as e:
        logger.error(f"Error processing with Gemini: {str(e)}")
        raise Exception(f"Error processing with Gemini: {str(e)}")

def extract_text_from_pdf(pdf_path):
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text content
    """
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n\n"
            
            return text
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Error extracting text from PDF: {str(e)}")
