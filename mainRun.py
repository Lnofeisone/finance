# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 15:19:06 2025

@author: Aleks
"""
#!pip install PyPDF2
#!pip install google.generativeai

#another bank URL - https://www.minneapolisfed.org/~/media/Y6Reports/2023/y6report_1126484_JOHNSON-BSHRS_2023.pdf

from app import process_pdf_with_gemini
#!pip install pypdf
import pypdf




#FUTURE FEATURE: RUN ONCE WITH INCREMENTAL DELTA
#recursively analysze all files or build RAG
#for now, read in community bank handbook


#HandbookSection = pypdf.PdfReader("C:/Users/Aleks/OCC Data Files/OCC Handbook/www.occ.treas.gov/publications-and-resources/publications/comptrollers-handbook/files/community-bank-supervision/pub-ch-community-bank-supervision.pdf")

'''
ObjectiveResult = process_pdf_with_gemini(

    pdf_url = "https://www.occ.gov/publications-and-resources/publications/comptrollers-handbook/files/community-bank-supervision/pub-ch-community-bank-supervision.pdf",
    prompt = "Extract every numbered objective and organize in a table",
    api_key="NEED API"
)
   
print(ObjectiveResult['response'])
'''

#this can also be used to read in ana analyze all the objectives
ObjectiveResult = process_pdf_with_gemini(

    pdf_url = "https://www.occ.gov/publications-and-resources/publications/comptrollers-handbook/files/community-bank-supervision/pub-ch-community-bank-supervision.pdf",
    prompt = "What are capital computations and risk-based capital computations I should be focusing on for a community bank. Augment this information with information from the HandbookSection. Use the handbook and general knowledge to provide formulas.",
    api_key="AIzaSyBD_x_EWX6jJLc2hywjv7ACnsG4ihVXz7g"
)
   
print(ObjectiveResult['response'])


'''
#this works and is complete
result = process_pdf_with_gemini(
    
    #pdf_url="https://www.minneapolisfed.org/~/media/Y6Reports/2023/y6report_3802858_AMERICAN-FED-CORP_2023.pdf",
    #pdf_url="https://www.minneapolisfed.org/~/media/Y6Reports/2023/y6report_1126484_JOHNSON-BSHRS_2023.pdf",
    #pdf_url="https://www.minneapolisfed.org/~/media/Y6Reports/2023/y6report_1246805_CENTRAL-BC_2023.pdf",
    prompt="Look at this PDF and print a table of all owners with larger than 5% ownership in a table",
    api_key="NEED API"
)
print(result['response'])
'''


