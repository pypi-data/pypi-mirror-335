import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.kg.shared_storage import initialize_pipeline_status


from typing import Any, Optional
from litellm import embedding
from litellm import completion
from pydantic import BaseModel
import time
import numpy as np
AZURE_OPENAI_LIGHTRAGLLM_NAME = os.getenv("AZURE_OPENAI_LIGHTRAGLLM_NAME")
AZURE_OPENAI_LIGHTRAGLLM_API_KEY = os.getenv("AZURE_OPENAI_LIGHTRAGLLM_API_KEY")
AZURE_OPENAI_LIGHTRAGLLM_ENDPOINT = os.getenv("AZURE_OPENAI_LIGHTRAGLLM_ENDPOINT")
AZURE_OPENAI_LIGHTRAGLLM_API_VERSION = os.getenv("AZURE_OPENAI_LIGHTRAGLLM_API_VERSION")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")
AZURE_EMBEDDING_API_KEY = os.getenv("AZURE_EMBEDDING_API_KEY")
AZURE_EMBEDDING_ENDPOINT = os.getenv("AZURE_EMBEDDING_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

class Transctiptions(BaseModel):
    TRANSCRIPTS: list[str]
    CONTEXTUAL_TRANSCRIPT: str

async def llm_model_func(
    prompt: str, 
    system_prompt: Optional[str] = None, 
    history_messages: Optional[list[dict]] = None, 
    **kwargs: Any
) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history_messages:
        messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    chat_completion = completion(
        model=f"azure/{AZURE_OPENAI_LIGHTRAGLLM_NAME}",  # litellm format for Azure models
        messages=messages,
        temperature=kwargs.get("temperature", 0.2),
        api_key=AZURE_OPENAI_LIGHTRAGLLM_API_KEY,
        api_version=AZURE_OPENAI_LIGHTRAGLLM_API_VERSION,
        api_base=AZURE_OPENAI_LIGHTRAGLLM_ENDPOINT
    )
    return chat_completion.choices[0].message.content


async def embedding_func(texts: list[str]) -> np.ndarray:
    response = embedding(
        model=f"azure/{AZURE_EMBEDDING_DEPLOYMENT}",
        input=texts,
        api_key=str(AZURE_EMBEDDING_API_KEY),
        api_base=str(AZURE_EMBEDDING_ENDPOINT),
        api_version=str(AZURE_OPENAI_API_VERSION),
        dimensions=1536
    )
    
    embeddings = [item['embedding'] for item in response.data]
    return np.array(embeddings)



model_name = "deepseek-r1:7b"

sample_text = '''
Google was founded on September 4, 1998, by American computer scientists Larry Page and Sergey Brin while they were PhD students at Stanford University in California. Together, they own about 14% of its publicly listed shares and control 56% of its stockholder voting power through super-voting stock. The company went public via an initial public offering (IPO) in 2004. In 2015, Google was reorganized as a wholly owned subsidiary of Alphabet Inc. Google is Alphabet's largest subsidiary and is a holding company for Alphabet's internet properties and interests. Sundar Pichai was appointed CEO of Google on October 24, 2015, replacing Larry Page, who became the CEO of Alphabet. On December 3, 2019, Pichai also became the CEO of Alphabet.[14]

 of products and services beyond Google Search, many of which hold dominant market positions. These products address a wide range of use cases, including email (Gmail), navigation and mapping (Waze, Maps and Earth), cloud computing (Cloud), web navigation (Chrome), video sharing (YouTube), productivity (Workspace), operating systems (Android), cloud storage (Drive), language translation (Translate), photo storage (Photos), videotelephony (Meet), smart home (Nest), smartphones (Pixel), wearable technology (Pixel Watch and Fitbit), music streaming (YouTube Music), video on demand (YouTube TV), AI (Google Assistant and Gemini), machine learning APIs (TensorFlow), AI chips (TPU), and more. Discontinued Google products include gaming (Stadia),[15] Glass, Google+, Reader, Play Music, Nexus, Hangouts, and Inbox by Gmail.[16][17] Google's other ventures outside of internet services and consumer electronics include quantum computing (Sycamore), self-driving cars (Waymo, formerly the Google Self-Driving Car Project), smart cities (Sidewalk Labs), and transformer models (Google DeepMind).[18]
'''

# sample_text = '''Russia
# On October 31, 2024, the Russian government imposed a "symbolic" fine of $20 decillion on Google for blocking pro-Russian YouTube channels. In 2022, during the invasion of Ukraine, a Russian court had ordered Google to restore the channels, with penalties doubling every week according to TASS.[413] This comes alongside other large fines against social media companies accused of hosting content critical of the Kremlin or supportive of Ukraine.[414]

# Geolocation
# Google has been criticized for continuing to collect location data from users who had turned off location-sharing settings.[415] In 2020, the FBI used a geofence warrant to request data from Google about Android devices near the Seattle Police Officers Guild building following an arson attempt during Black Lives Matter protests. Google provided anonymized location data from devices in the area, which raised privacy concerns due to the potential inclusion of unrelated protesters.[416]'''
# # WorkingDir
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKING_DIR = os.path.join(ROOT_DIR, "myKG")
if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)
print(f"WorkingDir: {WORKING_DIR}")

os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "admin@dembrane"
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["POSTGRES_USER"] = "dembrane"
os.environ["POSTGRES_PASSWORD"] =  "dembrane"
os.environ["POSTGRES_DATABASE"] = "dembrane"
os.environ["VERBOSE"] = "true"

async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=llm_model_func,
        embedding_func=embedding_func,
        llm_model_name=model_name,
        llm_model_max_async=4,
        llm_model_max_token_size=8192,
        graph_storage="Neo4JStorage",
        kv_storage="PGKVStorage",
        doc_status_storage="PGDocStatusStorage",
        vector_storage="PGVectorStorage",
    )
    await rag.initialize_storages()
    await initialize_pipeline_status()
    return rag


loop = asyncio.get_event_loop()
rag = loop.run_until_complete(initialize_rag())

print('******Insert******')
rag.insert(input = sample_text, 
           ids=[f"2"])
print('******Insert******')


# print('******Query******')
# print(rag.query(query="When was google founded?", 
#                 param = QueryParam(mode = "mix", 
#                                    ids = ["deepseek-r1:7b_1742211087", 
#                                           "deepseek-r1:7b_1742631817", 
#                                           "deepseek-r1:7b_1742631833"
#                                           ],
#                                     stream = True
#                                 )))
# print('******Query******')



print('******Query******')
print(rag.query(query="When was google founded?", 
                param = QueryParam(mode = "mix", 
                                   ids = ["1"],
                                    stream = True
                                )))
print('******Query******')