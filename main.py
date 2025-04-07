# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 15:18:20 2025

@author: Aleks
"""

"""
Main entry point for the PDF Processor application.
This file imports and runs the application from run.py
"""

import sys
import os
from run import main

if __name__ == "__main__":
    # Pass any command line arguments to the main function
    # This allows us to forward arguments from main.py to run.py
    print("PDF Processor with Google Gemini AI")
    print("===================================")
    print("Running PDF processor application...")
    print("")
    
    # Forward command line arguments to run.py
    # This allows users to run either "python main.py <url> <prompt>" 
    # or "python run.py <url> <prompt>"
    main()
