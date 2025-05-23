from qdrant_client import QdrantClient
from dotenv import load_dotenv
import chainlit as cl
import openai
import requests
import json
import fitz
import os
from functions import univ_functions

load_dotenv()

embedding_model = "text-embedding-3-small"
assistant_model = "gpt-3.5-turbo"

openai_client = openai.Client()

qdrant_host = os.getenv('QDRANT_HOST')
qdrant_api_key = os.getenv('QDRANT_API_KEY')

client = QdrantClient(
    qdrant_host,
    api_key= qdrant_api_key,
)

collection_name = "university_collection"

assistant_name = "Univ Assistant"

def convert_embedding(texts):
    result = openai_client.embeddings.create(input=texts, model=embedding_model)
    return result

def find_threshold(embedded_query,collection_name,vector_name):
    query_results = client.search(
        collection_name=collection_name,
        query_vector=(vector_name, embedded_query),
        limit=10, 
        query_filter=None,
    )
    sum = 0
    for i, article in enumerate(query_results):
        if(i==0):
            sum += article.score*3
        sum += article.score
        #print(article.score)
    mean = sum / 13
    cnt = 0
    print(mean)
    for i, article in enumerate(query_results):
        if(article.score>=mean):
            cnt+=1
    print(cnt)
    return cnt

def query_qdrant(query, collection_name, vector_name='content'):
    embedded_query = convert_embedding(query).data[0].embedding
    top_k = find_threshold(embedded_query,collection_name,vector_name)
    query_results = client.search(
        collection_name=collection_name,
        query_vector=(vector_name, embedded_query),
        limit=top_k, 
        query_filter=None,
    )
    return query_results

def recommend_qdrant(query, collection_name, not_relevant, vector_name='content' ):
    embedded_query = convert_embedding(query).data[0].embedding
    top_k = find_threshold(embedded_query,collection_name,vector_name)
    query_results = client.recommend(
        collection_name=collection_name,
        query_vector=(vector_name, embedded_query),
        negative = not_relevant, 
        limit=top_k, 
        query_filter=None,
    )
    return query_results

def check_completion(text_input):
    completion = openai_client.chat.completions.create(
        model=assistant_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that help university student answer their query."},
            {"role": "user", "content": text_input},
        ],
        tools=univ_functions,
        tool_choice="auto"
    )
    output = completion.choices[0].message.tool_calls[0].function.arguments
    output = eval(output)
    return output['main_idea']

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
            #print(result.payload['title'],result.payload['start_page'])

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

def get_weblink(results):
    weblink = ''
    duplicate = []
    for result in results:
        if(result.payload['type']=='web') and (result.payload['title'] not in duplicate):
            weblink += result.payload['title']
            weblink +='\n'
            duplicate.append(result.payload['title'])
            #print(result.payload['title'],result.payload['start_page'])
    return weblink
    
def strapi_search(query):
    query_results = query_qdrant(query, "QNA_collection" , 'Answer')
    list_str = ""
    for article in query_results:
        list_str += f'{article.payload["Answer"]}\n'
    return list_str 


@cl.action_callback("helpful_response")
async def give_another_action(action):

    initial_message = {
        "role": "system",
        "content": "You are a helpful assistant that helps university students answer their queries. You read a lot of sources about universities and those are: "
    }
    cl.user_session.set("messages", [initial_message])
    not_relevant_arr = cl.user_session.get("not_relevant")
    #recommend_qdrant(query, collection_name, not_relevant_arr, vector_name='content' )

    cl.user_session.set("not_relevant", not_relevant_arr)
    
    await action.remove()
    # Remove both action buttons from the chatbot user interface

# Define individual callbacks that use the combined handler





# Chainlit App start
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("openai_model", "gpt-3.5-turbo")
    initial_message = {
        "role": "system",
        "content": "You are a helpful assistant that help university student answer their query. You read a lot of source about university and those are " 
    }
    cl.user_session.set("messages", [initial_message])
    cl.user_session.set("AI_doc", [])
    cl.user_session.set("not_relevant", [])

    await cl.Message(content="Hello,I am here to help you with university stuff").send()
    #


@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="GPT-3.5",
            markdown_description="The underlying LLM model is **GPT-3.5**.",
            icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="GPT-4",
            markdown_description="The underlying LLM model is **GPT-4**.",
            icon="https://picsum.photos/250",
        ),
    ]


@cl.on_message
async def main(user_message: cl.message):

    user_input = user_message.content
    messages = cl.user_session.get("messages")
    messages.append({"role": "user", "content": user_input})

    title = cl.user_session.get("AI_doc")

    #get from strapi

    context = strapi_search(user_input)
    messages[0]['content'] += context


    #get from  qdrant database
    content, title = get_top_search(user_input, title)
    if content not in messages[0]['content']:
        messages[0]['content'] += content
    cl.user_session.set("AI_doc", title)
        
    print(messages[0]['content'])
    try:
        completion = openai_client.chat.completions.create(
            model=cl.user_session.get("openai_model"),
            messages=messages,
            temperature=0.2,
        )
        response = completion.choices[0].message.content
    except:
        await cl.Message(content="this response reach its max capicity or there is some issue with the conversation, please start a new conversation", author=assistant_name).send()  #message reach token

        #reset chat
        initial_message = {
            "role": "system",
            "content": "You are a helpful assistant that help university student answer their query. You read a lot of source about university and those are " 
        }
        cl.user_session.set("messages", [initial_message])
    #message append
    messages.append({"role": "assistant", "content": response})
    cl.user_session.set("messages", messages )

    elements = []
    try:

        #get the top result 
        result = query_qdrant(user_input, collection_name, 'content')
        new_pdf_path = extract_relevant_pages(result) # get pdf path
        link = get_weblink(result) # get web link

        if(new_pdf_path): #insert pdf if any
            elements.append(cl.Pdf(name="Relevant PDF", display="inline", path=new_pdf_path))
        if(link): #insert weblink if any
            elements.append(cl.Text(name="link that might be helpful", content=link, display="inline"))

        actions = [
            cl.Action(name="helpful_response", value="recom_value", label = "Find another article for this question"),
        ]
        await cl.Message(content=response, elements=elements,actions =actions, author=assistant_name).send()  

    except:
        await cl.Message(content="this response reach its max capicity or there is some issue with the conversation, please start a new conversation", author=assistant_name).send()  #message reach token

        #reset chat
        initial_message = {
            "role": "system",
            "content": "You are a helpful assistant that help university student answer their query. You read a lot of source about university and those are " 
        }
        cl.user_session.set("messages", [initial_message])


    #checking if this message is usefull
    #await cl.Message(content=response, elements=elements).send()    
    
    
    # await cl.Message(content=response).send()\

