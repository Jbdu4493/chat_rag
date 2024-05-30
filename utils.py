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

# Récupération de l'URI d'Elasticsearch à partir des variables d'environnement
ES_URI = os.environ.get('ELASTICSEARCH_URI')

# Modèle de prompt pour les questions
PROMPT_TEMPLATE = """
Utilises ces données de contexte: 

{context}.

Réponds à cette question en cherchant dans le contexte: {question}

Si les informations ne sont pas présentes, dis tout simplement 'Je ne sais pas'.
"""


class DoccumentChat:
    """
    Classe pour gérer les interactions avec des documents PDF et un modèle de langage.

    Attributs:
    embedding (Embeddings): Objet pour les embeddings.
    llm (BaseLLM): Modèle de langage pour générer des réponses.

    Méthodes:
    __init__(embedding, llm): Initialise les attributs de la classe.
    __random_index(length): Génère un index aléatoire de longueur spécifiée.
    loead_pdf_in_es(pdf_path, index_name): Charge un fichier PDF dans Elasticsearch.
    get_context_from_question(question, index_name): Récupère le contexte pertinent pour une question donnée.
    get_prompt(question, contexts): Génère un prompt à partir d'une question et de contextes.
    document_question(question, index_name): Répond à une question en utilisant les documents indexés.
    document_question_stream(question, index_name): Répond à une question en flux continu en utilisant les documents indexés.
    """

    def __init__(self, embedding: Embeddings, llm: BaseLLM) -> None:
        """
        Initialise les attributs de la classe DoccumentChat.

        Args:
        embedding (Embeddings): Objet pour les embeddings.
        llm (BaseLLM): Modèle de langage pour générer des réponses.
        """
        self.embedding = embedding
        self.llm = llm

    def __random_index(self, length: int) -> str:
        """
        Génère un index aléatoire de longueur spécifiée.

        Args:
        length (int): Longueur de l'index à générer.

        Returns:
        str: Index aléatoire généré.
        """
        ascii_chars = string.ascii_letters  # a-z, A-Z
        return ''.join(random.choice(ascii_chars) for _ in range(length)).lower()

    def loead_pdf_in_es(self, pdf_path: str, index_name=None) -> str:
        """
        Charge un fichier PDF dans Elasticsearch.

        Args:
        pdf_path (str): Chemin vers le fichier PDF.
        index_name (str, optionnel): Nom de l'index Elasticsearch. Si non spécifié, un nom aléatoire est généré.

        Returns:
        str: Nom de l'index Elasticsearch utilisé.
        """
        if index_name is None:
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

    def get_context_from_question(self, question: str, index_name: str) -> List[str]:
        """
        Récupère le contexte pertinent pour une question donnée.

        Args:
        question (str): Question à poser.
        index_name (str): Nom de l'index Elasticsearch.

        Returns:
        List[str]: Liste de contextes pertinents.
        """
        db = ElasticsearchStore(
            embedding=self.embedding,
            index_name=index_name,
            es_url=ES_URI
        )
        db.client.indices.refresh(index=index_name)
        results = db.similarity_search(question, fetch_k=500, k=3)
        return [doc.page_content for doc in results]

    def get_prompt(self, question: str, contexts: List[str]) -> str:
        """
        Génère un prompt à partir d'une question et de contextes.

        Args:
        question (str): Question à poser.
        contexts (List[str]): Liste de contextes pertinents.

        Returns:
        str: Prompt généré.
        """
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        context_text = "\n\n---\n\n".join([ctx for ctx in contexts])
        prompt = prompt_template.format(
            context=context_text, question=question)
        return prompt

    def document_question(self, question: str, index_name: str):
        """
        Répond à une question en utilisant les documents indexés.

        Args:
        question (str): Question à poser.
        index_name (str): Nom de l'index Elasticsearch.

        Returns:
        Réponse générée par le modèle de langage.
        """
        contexts = self.get_context_from_question(question, index_name)
        prompt = self.get_prompt(question=question, contexts=contexts)
        print(prompt)
        return self.llm.invoke(prompt)

    def document_question_stream(self, question: str, index_name: str):
        """
        Répond à une question en flux continu en utilisant les documents indexés.

        Args:
        question (str): Question à poser.
        index_name (str): Nom de l'index Elasticsearch.

        Returns:
        Réponse générée par le modèle de langage en flux continu.
        """
        contexts = self.get_context_from_question(question, index_name)
        prompt = self.get_prompt(question=question, contexts=contexts)
        print(prompt)
        return self.llm.stream(prompt)
