# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 13:12:24 2018
Reading Us Tax Code for text order and section
@author: abhaddad
"""

#importing packages
import os
from bs4 import BeautifulSoup, Tag
import pandas as pd
import requests
import numpy as np
import re

#reads the tax code file from local
def read_htm_file(Directory, Name_of_File):
    os.chdir(Directory)
    f = open(Name_of_File)  
    soup = BeautifulSoup(f, "lxml")
    f.close()
    return(soup)

#parses the tax code soup file into a dataframe by section   
def take_soup_return_sections_and_text(soup):
   dict_of_headers_and_text={}
   for header in soup.find_all('h3'):
        if "§" in header.text:
        #if header.text=="CHAPTER 1—NORMAL TAXES AND SURTAXES":
            text_of_code=""
            nextNode = header
            while True:
                nextNode = nextNode.nextSibling
                if nextNode is None:
                    break
                if isinstance(nextNode, Tag):
                    if (nextNode.name == "h3") or (nextNode.name == "h2") or (nextNode.name == "h1"):
                        break
                    text_of_code= text_of_code+ " " + (nextNode.get_text(strip=True).strip())
            dict_of_headers_and_text[header.text] = text_of_code
   df=pd.DataFrame.from_dict(dict_of_headers_and_text, orient='index')
   df.columns=["Text"]
   return(df)

#get relevant links from tax reg page
def get_links_from_URL_with_keywords(url, keywords=[""], leave_outs=["this is a phrase that will not come up"]):
    response = requests.get(url)
    data = response.text
    soup = BeautifulSoup(data, 'lxml')
    tags = soup.find_all('a')
    all_links=[]
    for tag in tags:
        try:
            all_links.append(tag.get('href'))
        except TypeError: 
            0
    links=[i for i in all_links if type(i)==str]
    for keyword in keywords:
        links=[i for i in links if keyword in i]
    for leave_out in leave_outs:
        links=[i for i in links if leave_out not in i] 
    return(links)

#get all the text from the tax reg links
def get_text_from_links_into_str(links):
    text=""
    for link in links:
        response = requests.get(link)
        data = response.text
        soup = BeautifulSoup(data, 'lxml')
        text=text+soup.text
    #text_cleaned= text.replace('\n',' ')    
    #return(text_cleaned)
    return(text)

#get section header and section numbers from tax code df
def clean_tax_code(df):
    df=df.reset_index()
    df['Section Header']=df['index'].str.split(' ', n=1, expand=True)[1]
    df["Section Number"]=df['index'].str.split('.', n=1, expand=True)[0].str.replace('§','').str.replace('[','')
    return(df)

#parse tax reg doc into sections dict
def parse_text_of_tax_reg_into_section_dict(text):
    section_start="\n\n\n\nSec."
    places=[m.start() for m in re.finditer(section_start, text)]
    dictionary_of_sections={}
    for number in range(0, len(places)-1):
        key=text[places[number]+4:places[number]+20]
        value=text[places[number]+4:places[number+1]]
        dictionary_of_sections[key]=value
    for number in [len(places)-1]:
        key=text[places[number]+4:places[number]+20]
        value=text[places[number]+4:len(text)]
        dictionary_of_sections[key]=value
    return(dictionary_of_sections)

#this takes the text and puts out the df for the tax reg
def make_text_dict_df(text):
    dict_of_sections=parse_text_of_tax_reg_into_section_dict(text)
    df_of_tax_reg=pd.DataFrame.from_dict(dict_of_sections, orient='index')
    df_of_tax_reg=df_of_tax_reg.reset_index()
    df_of_tax_reg.columns=["index", "Text"]
    df_of_tax_reg['Actual Section']=df_of_tax_reg['index'].apply(get_section_number_from_tax_reg_index)
    df_of_tax_reg['Section Title Text']=df_of_tax_reg['Text'].apply(split_on_two_ns_and_spaces)
    return(df_of_tax_reg)    
  
#gets the section number of the tax reg    
def get_section_number_from_tax_reg_index(string):
    return(string.split(".")[2].split("-")[0].split("(")[0].split(" ")[0])

#gets length of a string
def string_length(string):
    return(len(string)) 

#returns intersection of Tax Code section numbers and Tax Reg section numbers    
def first_stage_screen(df, df_of_sections):
    Tax_Sections=list(df['Section Number'].unique())
    Reg_Sections=list(df_of_sections['Actual Section'].unique())
    intersection=[i for i in Tax_Sections if i in Reg_Sections]
    return(intersection, Tax_Sections)

#gets intersection of Tax Code section numbers and modified Tax Reg section numbers
def second_stage_screen(df, df_of_sections):
    df_of_sections["Section_Version_2"]=df_of_sections["Actual Section"].apply(keep_just_digits)
    Tax_Sections=list(df['Section Number'].unique())
    Reg_Sections_2=list(df_of_sections['Actual Section'].unique())
    intersection_2=[i for i in Tax_Sections if i in Reg_Sections_2]
    return(df_of_sections, intersection_2)

#Called 'looks for [Reserved] in beginning of string function
def third_stage_screen(df_of_sections):
    df_of_sections["Reserved"]=df_of_sections["Text"].apply(reserved_value)
    return(df_of_sections)

#Looks for [Reserved] in beginning of string            
def reserved_value(string):
    if "[Reserved]" in string[0:70]:
        return("Reserved")
    else:
        return("Not Reserved")

#keeps just digits
def keep_just_digits(string):
    return(re.sub("[^0-9]", "", string))

#determines correct value to merge on for the Tax Reg and drops non-matching [Reserved] values
def all_screening(df, df_of_sections):
    intersection, Tax_Sections=first_stage_screen(df, df_of_sections)
    df_of_sections, intersection_2=second_stage_screen(df, df_of_sections)
    df_of_sections=third_stage_screen(df_of_sections)
    #condition 1: if Section number is in intersection, true merge value is section number
    conditions = [
    (df_of_sections['Actual Section'].isin(intersection)),
    (~df_of_sections['Actual Section'].isin(intersection)) & (df_of_sections["Section_Version_2"].isin(intersection_2)),
    (~df_of_sections['Actual Section'].isin(intersection)) & (~df_of_sections["Section_Version_2"].isin(intersection_2)) & (df_of_sections["Reserved"]=="Reserved")]
    choices = [df_of_sections['Actual Section'],df_of_sections["Section_Version_2"], "Reserved"]
    df_of_sections['Merge Value'] = np.select(conditions, choices, default=df_of_sections['Actual Section'])
    #this drops the Reserved that are not being found
    df_of_sections=df_of_sections.loc[df_of_sections['Merge Value']!="Reserved"]
    df_of_sections=df_of_sections[['index', 'Text', 'Merge Value', 'Section Title Text']]
    return(df_of_sections)

#cleans out line breaks - to use on the text of the tax code df
def clean_out_line_breaks(string):
    try:
        text_cleaned=string.replace('\n',' ')   
        return(text_cleaned)
    except:
        return(string)

#puts together the merging functions, aggregates the df_tax_reg functions by section, does merge, gets metrics for merge
def merge_and_metrics(df_tax_code, df_tax_reg):
    df_tax_code=df_tax_code[['Section Number', 'Section Header','Text']]
    df_tax_reg=df_tax_reg[['Merge Value', 'Text', 'Section Title Text']]
    df_section_titles_by_merge_value=df_tax_reg.groupby(['Merge Value'])['Section Title Text'].apply(lambda x: ','.join(x)).reset_index() 
    df_section_text_by_merge_value=df_tax_reg.groupby(['Merge Value'])['Text'].apply(lambda x: ','.join(x)).reset_index() 
    df_reg_by_merge_value=df_section_titles_by_merge_value.merge(df_section_text_by_merge_value, left_on='Merge Value', right_on='Merge Value')
    df_reg_by_merge_value['Text Length']= df_reg_by_merge_value['Text'].str.len()
    right_merge_agg=df_tax_code.merge(df_reg_by_merge_value, left_on="Section Number", right_on='Merge Value', how="right")
    inner_merge_agg=df_tax_code.merge(df_reg_by_merge_value, left_on="Section Number", right_on='Merge Value', how="inner")
    print(f'The proportion of the aggregated reg rows that merged in was {round(100*len(inner_merge_agg)/len(right_merge_agg),1)}%')
    length_merged=inner_merge_agg['Text Length'].sum()
    total_length=right_merge_agg['Text Length'].sum()
    print(f'The proportion of the reg text that merged in was {round(100*length_merged/ total_length,1)}%')
    left_merge_agg=df_tax_code.merge(df_reg_by_merge_value, left_on="Section Number", right_on='Merge Value', how="outer")
    left_merge_agg.columns=['Tax Code Section Number', 'Tax Code Section Header', 'Tax Code Text','Merge Value', 'Tax Reg Section Titles', 'Tax Reg Text',  'Text Length']
    left_merge_agg=left_merge_agg[['Tax Code Section Number', 'Tax Code Section Header', 'Tax Reg Section Titles' ,'Tax Code Text', 'Tax Reg Text']]
    left_merge_agg['Tax Code Text']=left_merge_agg['Tax Code Text'].apply(clean_out_line_breaks)
    left_merge_agg['Tax Reg Text']=left_merge_agg['Tax Reg Text'].apply(clean_out_line_breaks)
    print(f'The proportion of the tax rows that merged in was {round(100*len(inner_merge_agg)/len(left_merge_agg),1)}%')  
    return(left_merge_agg)    

#this gets just the text of the title of the tax reg sections so we can spot check whether they relate to the tax code sections of the merge    
def split_on_two_ns_and_spaces(string):
    return(string.split("\n\n")[0].split("    ")[0])
    
#This is where I read the tax code file, put it into df, and pickle/read pickle 
Directory=r"C:\Users\abhaddad\Documents\IRS RAAS\Generic Code\Tax Code Files"
Name_of_File='PRELIMusc26.htm'

#soup=read_htm_file(Directory, Name_of_File)
#df_tax_code=take_soup_return_sections_and_text(soup)
#df_tax_code.to_pickle("TaxCode.pkl")

os.chdir(Directory)
df_tax_code=pd.read_pickle("TaxCode.pkl")
df_tax_code=clean_tax_code(df_tax_code)
    
keywords=["CFR-2018-title26", ".htm"]
url="https://www.gpo.gov/fdsys/search/pagedetails.action?collectionCode=CFR&searchPath=Title+26%2FChapter+I%2FSubchapter+A%2FPart+1%2FSubjgrp&granuleId=&packageId=CFR-2018-title24-vol5&oldPath=Title+26%2FChapter+I%2FSubchapter+A%2FPart+1&fromPageDetails=true&collapse=true&ycord=1342.6666259765625"
#this is where I get the CFR links from the url
links=get_links_from_URL_with_keywords(url, keywords)
#this is where I aggregate them into a big string
text=get_text_from_links_into_str(links)
#this is where I put that into a dict and then df
df_tax_reg= make_text_dict_df(text)

#this cleans the values of the df tax reg for merging based on what's succesfully hitting the tax code
df_tax_reg=all_screening(df_tax_code, df_tax_reg)
#this does the merge and generates values
merged_reg_and_tax=merge_and_metrics(df_tax_code, df_tax_reg)

#this outputs the result to Excel
writer = pd.ExcelWriter('Merged Text Data.xlsx')
merged_reg_and_tax.to_excel(writer,'Merged Text Data')
writer.save()

#testing some results
import random
df_to_test= merged_reg_and_tax.dropna()
random.seed(77)
list_to_test=[]
for x in range(10):
  list_to_test.append(random.randint(0,len(df_to_test)))

for i in list_to_test:
    print("Tax Code: ", df_to_test['Tax Code Section Header'].iloc[i])
    print("Tax Reg: ",df_to_test['Tax Reg Section Titles'].iloc[i])
    print("")
    
merged_reg_and_tax.to_pickle("Tax and Reg Code.pkl")    
"""


#Stuff I'm Not Using
df['Section From Code']=np.empty((len(df), 0)).tolist()

present_in_text=[]
for i in df['Section Header']:
    if i.lower() in text:
        present_in_text.append(i)
        
            else:
        return("No")
        
#crosstab
pd.crosstab(df['Repealed'], df['Present'])
#the biggest source of not found in the section heads in that they're repealed, but it's not all of them 
df.loc[(df['Repealed'] =="No") & (df['Present'] == "no")]

we_found_it=[word for word in possible_section_heads if "Small aircraft on nonestablished lines".lower() in word.lower()]


count=0
for row in range(0, len(df)):
    if count==0:
        for item_in_list in possible_section_heads:
            if df['Section From Code'][row] in present_in_text:
                if df['Section Header'][row].lower() in item_in_list:
                    df['Section From Code'][row].append(item_in_list)
                    print(item_in_list)
                count=count+1

df['Possible Matches']=df['Section From Code'].apply(len)
promising_df=df.loc[df['Possible Matches']==1]
#tomorrow I will pickle these earlier objects so I can stop running this stuff
promising_df.to_excel("Do We See A Pattern.xlsx")

def repealed (words):
    if "Repealed" in words:
        return("Yes")

df.loc[df["Section Number"]=="280G"]

len(df["Section Number"])

#nope
df['Present']="unclear"
#for number in range(0,len(df["Section Number"])):
for number in range(0,len(df["Section Number"])):
    if df["Section Number"][number] in text:
        df['Present'][number]="yes"
    else: 
        df['Present'][number]="no"
        
#do I want a 95% solution???
for number in range(0,len(df["Section Number"])):
    if df['Present'][number]=="no":
        just_number=re.sub("[^0-9]", "", df["Section Number"][number])
        #print(just_number)
        if len([s for s in possible_section_heads if str(just_number) in s])>0:
            df['Present'][number]="partially"
#let's focus on parsing the text into sections, this is gonna be hard
sub="Review of overpayments exceeding"

[s for s in possible_section_heads  if sub in s]

place=[m.start() for m in re.finditer(sub, text)][-1]
text[place-100:place+100]

stuff_going_on=[text[m+4:m+20] for m in places]

def possible_section_heads(text):
    tokens = [word for word in nltk.word_tokenize(text)]
    possible_section_heads=[]
    count=0
    for number_of_token in range(0, len(tokens)):
        if tokens[number_of_token]=="Sec":
        #possible_section_heads.append(tokens[number_of_token+2])
            possible_section_text=' '.join(tokens[number_of_token:number_of_token+20])
            possible_section_heads.append(possible_section_text)
            count=count+1
    return(possible_section_heads)
    
df_of_sections["Split Part"]=df_of_sections["Text"].apply(split_by_possible_part)


def split_by_possible_part(string):
    try:
        new_string=re.split(r'\n{2,}\s+\bpart\b', string)[1]
        return(new_string)
    except IndexError:
        "nothing"
pattern = r'\n{2,}\s+\bpart\b'

stuff=[i for i in df_of_sections['Text'] if re.search(pattern, i.lower())]


right_df=df.merge(df_of_sections, left_on="Section Number", right_on='Merge Value', how="right")

just_in_reg=[i for i in df_of_sections['Merge Value'].unique() if i not in df['Section Number'].unique()]
leftovers=df_of_sections.loc[df_of_sections['Merge Value'].isin(just_in_reg)]
 
     
df_of_sections.loc[df_of_sections['Merge Value']=='9000']
for entry in df_of_sections.loc[df_of_sections['Merge Value']=='9000']['Text']:
    print("")
    print("NEW")
    print(entry[0:50])

in_900=[i for i in df['index'].unique() if "900" in i]

#do_we_see_stuff

[i for i in df['index'].unique() if "gross income requirement" in i.lower()]
writer = pd.ExcelWriter('output.xlsx')
leftovers.to_excel(writer,'Sheet1')
writer.save()

leftovers['Section Name Text']=leftovers['Text'].apply(get_section_text)

found_leftovers=[i for i in leftovers['Section Name Text'] if i.lower() in df['Section Header'].str.lower().unique()]
renumbered=[i for i in leftovers['Section Name Text'] if "introduction" in i.lower()]

#df_of_sections['After Four Line Breaks_1']=df_of_sections['Text'].apply(get_stuff_after_four_line_breaks)
#two pieces: cleaning the section headers for merging on
#and cleanign the actual text    

def get_stuff_after_line_break_and_part(string):
    return(string.split("\n\n\n\n")[1])

def get_section_text(string):
    try:
        return(string.split(" ", 2)[2].split("\n", 1)[0])
    except:
        return("")

"""
