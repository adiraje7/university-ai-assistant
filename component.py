import PyPDF2
from dotenv import load_dotenv
import openai
import os
import requests
from bs4 import BeautifulSoup


from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.models import PointStruct

from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
#load OPEN_API
load_dotenv()

qdrant_host = os.getenv('QDRANT_HOST')
qdrant_api_key = os.getenv('QDRANT_API_KEY')

qdrantclient = QdrantClient(
    qdrant_host,
    api_key= qdrant_api_key,
)

class PDFProcessor:
    def __init__(self, collection_name, embedding_model="text-embedding-ada-002", assistant_model="gpt-3.5-turbo"):
        self.embedding_model = embedding_model
        self.assistant_model = assistant_model
        self.collection_name = collection_name
        self.openai_client = openai.Client()
        self.qdrant_client = qdrantclient

    def convert_embedding(self, texts):
        result = self.openai_client.embeddings.create(input=texts, model=self.embedding_model)
        return result

    def read_pdf(self, file_path):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            chunks = ""

            for page_num in range(total_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                if text:
                    chunks += text + "\n\n"
        return chunks

    def qdrant_embedding(self, chunk_content, title, x):
        payload_data = []
        cnt = 0
        for chunk in chunk_content:
            payload_data.append({
                'title': self.convert_embedding(f'{title}__{cnt}').data[0].embedding,
                'body': self.convert_embedding(chunk[0]).data[0].embedding,
            })
            cnt += 1
        
        points = []
        for idx, (data, text) in enumerate(zip(payload_data, chunk_content)):
            num = x + idx
            num = self.get_next_index(num)
            point = PointStruct(
                id=num,
                vector={
                    'title': data['title'], 
                    'content': data['body']
                },
                payload={
                    'title': f'{title}__{idx}',
                    'content': text[0],
                    'start_page': text[1],
                    'end_page': text[2],
                    'type': 'pdf',
                    'file_name': title
                }
            )
            points.append(point)
        
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        return x + 1

    def get_next_index(self,x):
        while(True):
            try:
                response = self.qdrant_client.retrieve(
                    collection_name=self.collection_name,
                    ids=[x]
                )
                response[0].id
                x+=1
            except:
                break
        return x


    def semantic_chunking(self, file_path, content):
        text_splitter = SemanticChunker(OpenAIEmbeddings(), breakpoint_threshold_type="interquartile")
        docs = text_splitter.create_documents([content])

        docs_with_pages = []
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)

            doc_length = 0
            text_length = 0
            start_page = 0
            end_page = 0
            for i in range(len(docs)):
                doc_length += len(docs[i].page_content)
                pdf_content = ''
                for page_num in range(start_page, total_pages):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    
                    text_length += len(text)
                    pdf_content += text

                    if text_length < doc_length:
                        end_page += 1
                    else:
                        docs_with_pages.append([docs[i].page_content, start_page, end_page])
                        start_page = end_page + 1
                        end_page = start_page
                        break
                docs_with_pages.append([docs[i].page_content, start_page, end_page])
        
        return docs_with_pages 

    def recursive_chunking(self, file_path, file):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=256,
            chunk_overlap=20
        )

        docs = text_splitter.create_documents([file])
        return docs

    def process_file(self, file_path,file_name):
        count1 = self.get_next_index(0)
        pdf = self.read_pdf(file_path)
        docs = self.semantic_chunking(file_path, pdf)
        embed = self.qdrant_embedding(docs, file_name, count1)

class PDFDelete:
    def __init__(self, collection_name, embedding_model="text-embedding-ada-002", assistant_model="gpt-3.5-turbo"):
        self.embedding_model = embedding_model
        self.assistant_model = assistant_model
        self.collection_name = collection_name
        self.openai_client = openai.Client()
        self.qdrant_client = qdrantclient

    def delete_pdf(self, file_name):
        self.qdrant_client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="file_name",
                            match=models.MatchValue(value=file_name),
                        ),
                    ],
                )
            ),
        )
        return 0

class WebScraping:
    def __init__(self, collection_name, qdrantclient = qdrantclient, embedding_model="text-embedding-ada-002", assistant_model="gpt-3.5-turbo"):
        self.embedding_model = embedding_model
        self.assistant_model = assistant_model
        self.collection_name = collection_name
        self.openai_client = openai.Client()
        self.qdrant_client = qdrantclient
        
    def convert_embedding(self, texts):
        result = self.openai_client.embeddings.create(input=texts, model=self.embedding_model)
        return result

    def qdrant_embedding(self, chunk_content,url, x):
        payload_data = []
        web_url_embed = self.convert_embedding(url).data[0].embedding
        for chunk in chunk_content:
            payload_data.append({
                'title': web_url_embed,
                'body': self.convert_embedding(chunk.page_content).data[0].embedding,
            })

        points = []
        for idx, (data, text) in enumerate(zip(payload_data, chunk_content)):
            num = x + idx
            num = self.get_next_index(num)
            point = PointStruct(
                id=num,
                vector={
                    'title': data['title'], 
                    'content': data['body']
                },
                payload={
                    'title': url,
                    'content': text.page_content,
                    'type': 'web',
                }
            )
            points.append(point)
        
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        return x + 1

    def get_next_index(self,x):
        while(True):
            try:
                response = self.qdrant_client.retrieve(
                    collection_name=self.collection_name,
                    ids=[x]
                )
                response[0].id
                x+=1
            except:
                break
        return x

    def recursive_chunking(self, file):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2048,
            chunk_overlap=20
        )

        docs = text_splitter.create_documents([file])
        return docs

    def scrape_text_from_page(self,text,url):
        # Send a GET request to the web page
        x = self.get_next_index(0)
        chunk = self.recursive_chunking(text)
        self.qdrant_embedding(chunk,url,x)
    
    def search_data(self,collection_name,data_type,web_url):
        find1 = self.qdrant_client.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="title",
                        match=models.MatchValue(value=web_url),
                    ),
                ]
            ),
        )
        return find1

class WebDelete:
    def __init__(self, collection_name, url, qdrantclient = qdrantclient, ):
        self.collection_name = collection_name
        self.qdrant_client = qdrantclient
        self.url = url
        
    def delete_web(self):
        self.qdrant_client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="title",
                            match=models.MatchValue(value=self.url),
                        ),
                        models.FieldCondition(
                            key="type",
                            match=models.MatchValue(value='web'),
                        ),
                    ],
                )
            ),
        )
        return 0
    
    def search_data(self,collection_name,data_type,web_url):
        find1 = self.qdrant_client.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="title",
                        match=models.MatchValue(value=web_url),
                    ),
                ]
            ),
        )
        return find1

class MyDatabase:
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.qdrant_client = qdrantclient

    def search_collection(self):
        arr = []
        l = len(self.qdrant_client.get_collection().collections)
        for i in range(l):
            arr.append(self.qdrant_client.get_collection().collections[i].name)
        return arr

    def get_count(self,collection_name):
        num = client.count(
            collection_name=collection_name,
            exact=True,
        )
        return num

    def search_data(self,collection_name,data_type,data_name):
        find1 = client.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(
                should=[
                    models.FieldCondition(
                        key="file_name",
                        match=models.MatchValue(value=data_name),
                    ),
                    models.FieldCondition(
                        key="type",
                        match=models.MatchValue(value=data_type),
                    ),
                ]
            ),
        )
        return find1


    