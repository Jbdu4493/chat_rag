from openai import OpenAI
import streamlit as st
import os
from utils import DoccumentChat
from langchain_openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.llms.ollama import Ollama

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")


MODEL_NAME = "gpt-3.5-turbo"
MODEL_NAME = "gemma"
EMBED_MODEL_NAME = "text-embedding-3-large"

st.session_state["llm"] = Ollama(model=MODEL_NAME, base_url=OLLAMA_URL)

st.title("ChatGPT-like clone")

with st.sidebar:
    apikey = st.text_input(label="OPENAI_API_KEY")
    apikey_button = st.button(label='OK')
    if apikey_button and apikey:
        if "openai_api_key" not in st.session_state:
            st.session_state["openai_api_key"] = apikey
            st.session_state["embedding"] = OpenAIEmbeddings(
                api_key=apikey, model=EMBED_MODEL_NAME)
            doc_chat = DoccumentChat(embedding=st.session_state['embedding'],
                                     llm=st.session_state['llm'])
            if "doccument_chat" not in st.session_state:
                st.session_state["doccument_chat"] = doc_chat
        elif st.session_state["openai_api_key"] != apikey:
            st.session_state["openai_api_key"] != apikey

    uploaded_file = st.file_uploader(
        "Choose a PDF file", accept_multiple_files=False)
    if uploaded_file is not None:
        file_name = uploaded_file.name
        bytes_data = uploaded_file.getvalue()
        with open(file_name, "wb") as file:
            file.write(bytes_data)
        if "doccument_chat" in st.session_state:
            index = st.session_state["doccument_chat"].loead_pdf_in_es(
                file_name)
            st.session_state["index"] = index

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Poser une question lié au doccument charger..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = st.session_state["doccument_chat"].document_question_stream(
            prompt, st.session_state["index"])
        response = st.write_stream(stream)
        st.session_state.messages.append(
            {"role": "assistant", "content": response})
