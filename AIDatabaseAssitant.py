import os
from dotenv import load_dotenv
from pathlib import Path
import streamlit as st
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.sql_database import SQLDatabase
from sqlalchemy import create_engine
from langchain_groq import ChatGroq
import sqlite3

# Load API keys
load_dotenv()
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_TRACING_V2"] = "true"

# LLM
llm = ChatGroq(model="llama-3.3-70b-versatile")

st.title("AI Database Assistant Agent")

LOCAL_DB = "use_localDB"
MYSQL = "use_MYSQL"

radioOpt = ["Use SQLLITE 3 DB student.db", "Connect to your SQL DB"]
selectedOpt = st.sidebar.radio("Choose DB", options=radioOpt)

@st.cache_resource(ttl=7200)
def configureDB(dburi, mysqlHost=None, mysqluser=None, mysqlPassword=None, mysqlDB=None):
    if dburi == LOCAL_DB:
        dbfile = Path("D:/Langchain/Database Manager AI/student.db")
        creator = lambda: sqlite3.connect(f"file:{dbfile}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    else:
        # safer driver
        return SQLDatabase(create_engine(f"mysql+pymysql://{mysqluser}:{mysqlPassword}@{mysqlHost}/{mysqlDB}"))

# --- Main logic ---

db = None

if radioOpt.index(selectedOpt) == 1:
    # MySQL mode
    mysqlHost = st.sidebar.text_input("MySQL Host")
    mysqluser = st.sidebar.text_input("Username")
    mysqlPassword = st.sidebar.text_input("Password", type="password")
    mysqlDB = st.sidebar.text_input("Database Name")

    if st.sidebar.button("Connect to MySQL"):
        if mysqlHost and mysqluser and mysqlDB:
            try:
                db = configureDB(MYSQL, mysqlHost, mysqluser, mysqlPassword, mysqlDB)
                st.success("✅ Connected to MySQL successfully!")
            except Exception as e:
                st.error(f"Connection failed: {e}")
        else:
            st.warning("Please fill all required fields before connecting.")
else:
    # Local SQLite mode
    db = configureDB(LOCAL_DB)
    st.success("✅ Connected to local SQLite database.")

if db:
    toolkit = SQLDatabaseToolkit(llm=llm, db=db)
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
    )

    query = st.chat_input("Enter your SQL Query")
    if query:
        res = agent.invoke(query)
        st.write(res)
