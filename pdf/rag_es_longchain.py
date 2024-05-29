from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from elasticsearch import Elasticsearch
from langchain_elasticsearch import ElasticsearchStore
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
import os
from typing import List


ES_URI = os.environ.get('ELASTICSEARCH_URI')
PROMPT_TEMPLATE = """
"Utilise ces données de contexte: 

{context}.

Réponds à cette question:{question}

Si les informations ne sont pas presentent dit 'Je ne sait pas'. sans rien en plus
Reponds en francais bein sûr.
"""

# Load the PDF
loader = PyPDFLoader("./pdf/1-CONDITIONS-GENERALES.pdf")


es = Elasticsearch(ES_URI)

# Nom de l'index
index_name = "openai"


embedding = OllamaEmbeddings(model="gemma")

embedding = OpenAIEmbeddings()
# Suppression de tous les documents
query = {
    "query": {
        "match_all": {}
    }
}
try:
    response = es.delete_by_query(index=index_name, body=query)
except Exception as e:
    print(f"Petit souci a la suppression de doc: {e}")


data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=150)
docs = text_splitter.split_documents(data)
# for doc in docs:
#     embedding_vector = embedding.embed_query(doc.page_content)
#     # Affiche une partie des embeddings pour vérifier
#     print(f"Embedding pour le document: {len(embedding_vector)}...")

db = ElasticsearchStore.from_documents(
    docs,
    embedding,
    es_url=ES_URI,
    index_name=index_name,
)

db.client.indices.refresh(index=index_name)

query = "que se passe-il en cas de défaillance du contructeur?"
results = db.similarity_search(query, fetch_k=500, k=5)

context_text = "\n\n---\n\n".join([doc.page_content for doc in results])
prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
prompt = prompt_template.format(context=context_text, question=query)

model = Ollama(model="llama3")
print(prompt)
for chunk in model.stream(prompt):
    print(chunk, end='', flush=True)

