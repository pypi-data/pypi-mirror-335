# import os
# import asyncio
# from lightrag import LightRAG, QueryParam
# from lightrag.utils import EmbeddingFunc
# from lightrag.kg.shared_storage import initialize_pipeline_status
# from lightrag.llm.ollama import ollama_embed, ollama_model_complete
# import time

# model_name = "deepseek-r1:7b"

# sample_text = '''
# We’re super excited to make this jump!
# Sameer and Evelien with open source contributors at the Hackathon in February 2025
# Sameer and Evelien with open source contributors at the Hackathon in February 2025
 
# Ever since Dembrane’s founding over two years ago, we have been thinking about ways to share our tools more broadly, not only with the communities and organisations benefitting from using them, but also with a worldwide network of passionate co-strivers that want to help push the field of democratic technologies forward.
# “Our open source journey is about more than releasing code—it’s a commitment to transparency, community, and long-term innovation.”  
# - Jorim, Founder
# Set in motion by collaborations on open civic participation tools with the The Association of Dutch Municipalities (VNG) and the OECD, we now see a clear path forward. Going open source can improve the quality of our tool, while we can also benefit from developments in the open source movement more broadly, such as in infrastructure, knowledge sharing and a sense of community. We believe this can amplify Dembrane's impact in strengthening democratic participation globally.
# "I fundamentally believe transparency is the way forward. We're all in this together, so let's share our knowledge." - Bram, Operations Lead
# Going open source aligns with our belief that the tools shaping our democratic future should be transparent, accountable, and community-driven. By making our code public, we invite universities, public sector organisations, and civic tech enthusiasts to verify our privacy practices, contribute security improvements, and help make ECHO more accessible for everyone. 
# notion image
 
# What does this mean concretely?
# As of today, Dembrane ECHO is open source under the AGPL v3 license. This means anyone can inspect, modify, and self-host our software, and any contributions feed back into the community and are useable by everyone. In February, our team participated in a hackathon hosted by the VNG and the province of south holland where government technologists and civic servants worked directly with our codebase to create new features. These early collaborations have already led to valuable improvements in ECHO's accessibility and feature set! This a wonderful start to building our open source community and we are eager to expand the scope of contributions over the coming weeks. 
 
# notion image
# "Dembrane's core belief is that people know how. Open source is our way of showing that we want to bring this thinking into the very process of building and maintaining our software. I am excited to see how ECHO will evolve from here." - Lukas, Impact Lead 
# ECHO's code is open source, but we provide enterprise-grade hosting and support for organisations who want a hassle-free experience - for current clients: that means the only thing that changes is that you have a bigger community working to make the ECHO better. To those contributing to Dembrane financially: Your subscription and sponsorship helps us continuously improve the platform while making democratic tools accessible to all - whether you use our hosted solution or run ECHO yourself. 
# Please note:
# If you modify ECHO and provide it to users over a network (like a web application), you must make the source code of your modified version available to those users.
# Any derivative works you create must also be licensed under AGPL.
# You must provide access to the complete source code, including your modifications, to anyone who receives the software.
# We’re just getting started
# This is only the beginning of our open source journey. Even more so, today is an exciting day in Dembrane’s story and we look forward to sharing further progress updates with you soon. 
# In the meantime we hope to collaborate with many of you on making ECHO better together - and to bring it to even more people so that they can start using it with as much joy as we do.
# "Dembrane has always been a mission-driven company, and we've said from the start we want to contribute to bringing the field of democratic technologies forward in any way we can. Our tool is something anyone who wants to organise communities should be able to work and interact with." - Evelien, Co-Founder
 
# The Dembrane Team
# Built with Care in Europe
# Published February 14th, 2025
# '''

# # WorkingDir
# ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# WORKING_DIR = os.path.join(ROOT_DIR, "myKG")
# if not os.path.exists(WORKING_DIR):
#     os.mkdir(WORKING_DIR)
# print(f"WorkingDir: {WORKING_DIR}")

# os.environ["NEO4J_USERNAME"] = "neo4j"
# os.environ["NEO4J_PASSWORD"] = "admin@dembrane"
# os.environ["NEO4J_URI"] = "bolt://localhost:7687"
# os.environ["POSTGRES_HOST"] = "localhost"
# os.environ["POSTGRES_PORT"] = "5432"
# os.environ["POSTGRES_USER"] = "dembrane"
# os.environ["POSTGRES_PASSWORD"] =  "dembrane"
# os.environ["POSTGRES_DATABASE"] = "dembrane"
# os.environ["VERBOSE"] = "true"

# async def initialize_rag():
#     rag = LightRAG(
#         working_dir=WORKING_DIR,
#         llm_model_func=ollama_model_complete,
#         llm_model_name=model_name,
#         llm_model_max_async=4,
#         llm_model_max_token_size=8192,
#         llm_model_kwargs={
#             "host": "http://host.docker.internal:11434",  # Changed: include protocol and port in host URL
#             "options": {"num_ctx": 8192},
#         },
#         embedding_func=EmbeddingFunc(
#             embedding_dim=768,
#             max_token_size=8192,
#             func=lambda texts: ollama_embed(
#                 texts, 
#                 embed_model="nomic-embed-text", 
#                 host="http://host.docker.internal:11434"  # Changed: use host.docker.internal
#             ),
#         ),
#         graph_storage="Neo4JStorage",
#         kv_storage="PGKVStorage",
#         doc_status_storage="PGDocStatusStorage",
#         vector_storage="PGVectorStorage",
#     )

# #     # Add initialization code
#     await rag.initialize_storages()
#     await initialize_pipeline_status()

#     return rag


# loop = asyncio.get_event_loop()
# rag = loop.run_until_complete(initialize_rag())

# print('******Insert******')
# rag.insert(input = sample_text, 
#            ids=[f"{model_name}_{int(time.time())}"])
# print('******Insert******')


# # print('******Query******')
# # print(rag.query(query="Why is echo relevant?", 
# #                 param = QueryParam(mode = "mix", 
# #                                    ids = ["deepseek-r1:7b_1742030617"])))
# # print('******Query******')



# print('******Query******')
# print(rag.query(query="Whats dembrane and Echo?", 
#                 param = QueryParam(mode = "mix", 
#                                 #    ids = ["deepseek-r1:7b_1742211087"]
#                                 )))
# print('******Query******')