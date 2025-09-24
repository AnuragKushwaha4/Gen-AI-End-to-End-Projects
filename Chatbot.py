from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import openai
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
os.environ["LANGCHAIN_PROJECT"]=os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_TRACING_V2"]="true"

prompt =ChatPromptTemplate.from_messages(
    [
        ("system","You are super intelligent model and you have to answer users query politly and to the point and when needed explain in brief use emojies when required etc."),
        ("user","question:{question}")

    ]
)

def generateResponseOPENAI(question,api,maxtoken,temperature,model):
    llm=ChatOpenAI(
        model=model,
        api_key=api,
        temperature=temperature,
        max_tokens=maxtoken,
    )
    outputparser = StrOutputParser()
    chain = prompt|llm|outputparser
    response = chain.invoke({"question",question})
    return response

def generateResponseOPENSOURCE(question,maxtoken,temperature,model):
    llm = ChatGroq(
        model=model,
        temperature=temperature,
        max_tokens=maxtoken,
    )
    outputparser = StrOutputParser()
    chain = prompt|llm|outputparser
    response = chain.invoke({"question",question})
    return response

st.title("Q&A AI CHATBOT")
st.sidebar.title("Settings")

modeltype = st.sidebar.selectbox("Select Model type:",["Open Source","OpenAI"])

if modeltype=="OpenAI":
    api = st.sidebar.text_input("Enter api key:",type="password")
    llm = st.sidebar.selectbox("Choose model: ",["gpt-4o","gpt-4o-mini","gpt-3.5-turbo"])
    temperature= st.sidebar.slider("Temperature",max_value=1.0,min_value=0.0,value=0.7,step=0.1)
    maxtoken = st.sidebar.slider("Max Tokens",min_value=50,max_value=500,value=200)
    st.write("How Can I Help You...🤞")
    input_text = st.chat_input(placeholder="You")
    if input_text:
        response = generateResponseOPENAI(input_text,api,maxtoken,temperature,llm)
        st.write(response)
else:
    llm = st.sidebar.selectbox("Choose model: ",["llama-3.1-8b-instant","llama-3.3-70b-versatile","meta-llama/llama-guard-4-12b"])
    temperature= st.sidebar.slider("Temperature",max_value=1.0,min_value=0.0,value=0.7,step=0.1)
    maxtoken = st.sidebar.slider("Max Tokens",min_value=50,max_value=500,value=200)
    st.write("How Can I Help You...🤞")
    input_text = st.chat_input(placeholder="You")
    if input_text:
        response = generateResponseOPENSOURCE(input_text,maxtoken,temperature,llm)
        st.write(response)

