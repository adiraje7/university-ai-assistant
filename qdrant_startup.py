from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.models import PointStruct

import openai
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

qdrant_host = os.getenv('QDRANT_HOST')
qdrant_api_key = os.getenv('QDRANT_API_KEY')

client = QdrantClient(
    qdrant_host,
    api_key= qdrant_api_key,
)

vector_size = 1536
client.create_collection(
    collection_name='QNA_collection',
    vectors_config={
        'Answer': VectorParams(
            distance=Distance.COSINE,
            size=vector_size,
        ),
        # 'content': VectorParams(
        #     distance=Distance.COSINE,
        #     size=vector_size,
        # ),
    }
)