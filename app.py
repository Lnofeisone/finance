# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 15:17:56 2025

@author: Aleks
"""

import os
import logging
from pdf_processor import download_pdf, validate_pdf, process_with_gemini

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_pdf_with_gemini(pdf_url, prompt, api_key=None):
    """
    Process a PDF from a URL with Gemini AI.
    
    Args:
        pdf_url (str): URL of the PDF to process
        prompt (str): Prompt for Gemini AI
        api_key (str, optional): Gemini API key. Defaults to environment variable.
        
    Returns:
        dict: Results with filename, prompt, and AI response
        
    Raises:
        Exception: If processing fails at any step
    """
    try:
        # Step 1: Download PDF
        logger.info(f"Starting to process PDF from URL: {pdf_url}")
        pdf_path, pdf_filename = download_pdf(pdf_url)
        
        # Step 2: Validate PDF
        is_valid, validation_msg = validate_pdf(pdf_path)
        if not is_valid:
            error_msg = f'Invalid PDF: {validation_msg}'
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # Step 3: Process with Gemini
        gemini_api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not gemini_api_key:
            error_msg = 'Gemini API key is not provided and not found in environment variables'
            logger.error(error_msg)
            raise Exception(error_msg)
        
        gemini_response = process_with_gemini(pdf_path, prompt, gemini_api_key)
        
        # Return the result
        result = {
            'filename': pdf_filename,
            'prompt': prompt,
            'response': gemini_response
        }
        
        logger.info(f"Successfully processed PDF: {pdf_filename}")
        return result
    
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        raise
