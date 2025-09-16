import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
os.environ["LANGCHAIN_PROJECT"]=os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["HF_API_KEY"]=os.getenv("HF_API_KEY")

from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader,TextLoader
from langchain_community.document_loaders.image import UnstructuredImageLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_chroma import Chroma


#function to create Vector DB:
def create_db(file):
    extension = os.path.splitext(file.name)[1].lower()

    if extension == ".pdf":
        file_path = os.path.join("Resources", file.name)
        with open(file_path, "wb") as f:
            f.write(path.read())
        loader = PyPDFLoader(file_path)
        docs = loader.load()

    elif extension ==".txt":
        path.seek(0)
        text_content = path.read().decode("utf-8")
        docs = [{"page_content": text_content}]
    else:
        return -1
    
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=100)
    splitted_docs = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model="all-MiniLM-L6-v2")
    db =Chroma.from_documents(embedding=embeddings,documents=splitted_docs)
    return db
    
st.title("RAG Document Q&A")
uploaded_docs = st.file_uploader("Upload file:")
if(uploaded_docs is not None):
    vectordb = create_db(uploaded_docs)
    if vectordb !=-1:
        retriever = vectordb.as_retriever()
        st.write("Ask Me a Query")
        input_text =st.text_input("Enter your Query:")
        #LLM:
        llm = ChatGroq(model="llama-3.3-70b-versatile")
        #Prompt template:
        prompts =ChatPromptTemplate.from_template(
        '''
            Hey You are Intelligent ChatBot answer the Users Query on the basic of given context.

            {context}

            question:{input}
        '''
        )
        document_chain =create_stuff_documents_chain(llm=llm,prompt=prompts)
        retrieval_chain = create_retrieval_chain(retriever,document_chain)
    
        if input_text:
            response = retrieval_chain.invoke({"input": input_text})
            st.write(response["answer"])
    else:
        st.write("Ops File Format is not supported")