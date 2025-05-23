from qdrant_client import QdrantClient
from dotenv import load_dotenv
import chainlit as cl
import openai
import requests
import json
import fitz
from functions import univ_functions
from component import PDFProcessor, PDFDelete, WebScraping, WebDelete, MyDatabase

def query_qdrant(query, collection_name, vector_name='content', top_k=10):
    query_results = client.search(
        collection_name=collection_name,
        query_vector=(vector_name, query),
        limit=top_k, 
        query_filter=None,
        score_threshold = 0.36,
    )
    return query_results

def get_top_search(query, title):
    query_results = query_qdrant(query, collection_name, 'content')
    list_str = ""
    for article in query_results:
        if article.payload["title"] in title:
            continue
        title.append(article.payload["title"])
        list_str += f'{article.payload["title"]}, this movie review: {article.payload["content"]}\n'
    return list_str, title

def get_element(search_result):
    pass
    # element = []
    # for result in search_result:
    #     if(result.payload['type']=='pdf'):
            

def extract_relevant_pages(results):
    
    relevant_pages = []

    for result in results:
        if(result.payload['type']=='pdf'):
            relevant_pages.append([result.payload['file_name'],result.payload['start_page'],result.payload['end_page']])
            print(result.payload['title'],result.payload['start_page'])
    print(len(relevant_pages))
    #print(relevant_pages)
    # Create a new PDF with relevant pages
    if relevant_pages:
        new_pdf_path = '../Project_AI_assistant/pdf/relevant_pages.pdf'
        new_doc = fitz.open()
        for filename, start, end in relevant_pages:
            pdf_path = f'../Project_AI_assistant/pdf/{filename}.pdf' 
            doc = fitz.open(pdf_path)
            new_doc.insert_pdf(doc, from_page=start, to_page=end)
            print(new_doc)
        new_doc.save(new_pdf_path)
        new_doc.close()
        return new_pdf_path
    else:
        return None

def get_next_index():
    response = client.scroll(
        collection_name=collection_name,
        limit=1,
        with_payload=False,
    )
    # if response and response.points:
    #     return response.points[0].id + 1
    return response

    def recursive_chunking(file):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=20
        )

        docs = text_splitter.create_documents([file])
        return docs

#client = QdrantClient(host="localhost", port=6333)
collection_name = "university_collection"
# test = query_qdrant(embed_example, 'university_collection', 'content')
# new_pdf_path = extract_relevant_pages(test)


response = requests.get("https://www.spjain.ae/global-campus/singapore")
print(response)

scrapingweb = WebScraping(collection_name=collection_name)
deleteWeb = WebDelete(collection_name=collection_name, url="https://www.spjain.ae/")
print(deleteWeb.search_data(collection_name,"web","https://www.spjain.ae/")[0])
#print(scrapingweb.search_data(collection_name,"web","https://www.spjain.ae/")[0])
#print(scrapingweb.search_data(collection_name,"web","https://www.spjain.ae/global-campus/singapore/")[0])
