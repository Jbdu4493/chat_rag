from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_elasticsearch import ElasticsearchStore
from langchain.embeddings.base import Embeddings
from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models.llms import BaseLLM
import os
import random
import string
from typing import List
ES_URI = os.environ.get('ELASTICSEARCH_URI')
PROMPT_TEMPLATE = """
"Utilises ces données de contexte: 

{context}.

Réponds à cette question en cherchant dans le contexte:{question}

Si les informations ne sont pas presentent dit tout simplement 'Je ne sait pas'.
"""


class DoccumentChat:
    def __init__(self,
                 embedding: Embeddings,
                 llm: BaseLLM) -> None:
        self.embedding = embedding
        self.llm = llm

    def __random_index(self, length: int) -> str:
        # Définir les caractères ASCII utilisables
        ascii_chars = string.ascii_letters  # a-z, A-Z
        # Générer une chaîne de longueur spécifiée avec des caractères aléatoires
        return ''.join(random.choice(ascii_chars) for _ in range(length)).lower()

    def loead_pdf_in_es(self,
                        pdf_path: str,
                        ) -> str:
        index_name = self.__random_index(10)
        try:
            loader = PyPDFLoader(pdf_path)
            data = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=100)
            docs = text_splitter.split_documents(data)
            db = ElasticsearchStore.from_documents(
                docs,
                self.embedding,
                es_url=ES_URI,
                index_name=index_name,
            )
            db.client.indices.refresh(index=index_name)
        except Exception as e:
            print(
                f"petit souci au chargement du fichier {pdf_path}: {e} \n Solutions: \n- Change de nom d'index\n- Vérifier que ElasticSearch tourne correctement")
            return None
        return index_name

    def __get_chunck_from_query(self, query: str, index_name: str):
        db = ElasticsearchStore(
            embedding=self.embedding,
            index_name=index_name,
            es_url=ES_URI
        )
        db.client.indices.refresh(index=index_name)
        results = db.similarity_search(query, fetch_k=500, k=3)
        return [doc.page_content for doc in results]

    def __get_prompt(self, question: str, contexts: List[str]):
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        context_text = "\n\n---\n\n".join([ctx for ctx in contexts])
        prompt = prompt_template.format(
            context=context_text, question=question)
        return prompt

    def document_question(self, question: str, index_name: str):
        contexts = self.__get_chunck_from_query(question, index_name)
        prompt = self.__get_prompt(question=question, contexts=contexts)
        print(prompt)
        return self.llm.invoke(prompt)

    def document_question_stream(self, question: str, index_name: str):
        contexts = self.__get_chunck_from_query(question, index_name)
        prompt = self.__get_prompt(question=question, contexts=contexts)
        print(prompt)
        return self.llm.stream(prompt)
