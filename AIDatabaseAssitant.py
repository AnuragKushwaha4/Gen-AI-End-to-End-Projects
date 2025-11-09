import os
from dotenv import load_dotenv
load_dotenv()
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
os.environ["LANGCHAIN_PROJECT"]=os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_TRACING_V2"]="true"
from pathlib import Path



import streamlit as st
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.sql_database import SQLDatabase
from sqlalchemy import create_engine
from langchain_groq import ChatGroq
import sqlite3

llm = ChatGroq(model="llama-3.3-70b-versatile")

st.title("AI Database Assistant Agent")

LOCAL_DB ="use_localDB"
MYSQL = "use_MYSQL"

radioOpt = ["Use SQLLITE 3 DB student.db","Connect to your SQL DB"]
selectedOpt = st.sidebar.radio(label="Choose DB",options=radioOpt)

if(radioOpt.index(selectedOpt)==1):
    db_uri=MYSQL
    mysqlHost = st.sidebar.text_input("Enter mysql host name")
    mysqluser = st.sidebar.text_input("Enter username")
    mysqlPassword = st.sidebar.text_input("Enter password")
    mysqlDB = st.sidebar.text_input("Enter Database")
else:
    db_uri=LOCAL_DB


if not db_uri:
    st.info("Please enter The DataBase URI")


@st.cache_resource(ttl='2h')
def configureDB(dburi,mysqlHost = None,mysqluser = None, mysqlPassword = None,mysqlDB = None):
    if dburi == LOCAL_DB:
        dbfile = "D:/Langchain/Database Manager AI/student.db"
        creator = lambda: sqlite3.connect(f"file:{dbfile}?mode=ro",uri=True)
        return SQLDatabase(create_engine("sqlite:///",creator=creator))
    else:
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysqluser}:{mysqlPassword}@{mysqlHost}/{mysqlDB}"))

if db_uri==MYSQL:
    db = configureDB(db_uri,mysqlHost,mysqluser,mysqlPassword,mysqlDB)
else:
    db = configureDB(db_uri)


toolkit = SQLDatabaseToolkit(llm=llm,db=db)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

query=st.chat_input("Enter your Query")
res= agent.invoke(query)
st.write(res)
