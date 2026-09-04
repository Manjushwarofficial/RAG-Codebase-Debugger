import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INDEX_PATH = BASE_DIR.parent / "faiss_index"
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", str(DEFAULT_INDEX_PATH))

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

# llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.2, max_output_tokens=1024)
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.1:8b", temperature=0.2)
retriever = db.as_retriever(search_kwargs={"k": 3})

SYSTEM_PROMPT = """You are a helpful assistant that answers questions about the codebase.
You are given a question and a set of context documents. Use the context to answer the question.
If you cannot find the answer in the context, say "I don't know" and do not make up an answer.
If the question is not related to the codebase, politely inform them that.
Context : {context}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
])

combine_docs_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

origins = ["*"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str


@app.get("/")
def home():
    return {"message": "Welcome to the RAG Codebase Debugger API!"}


import time
import traceback

@app.post("/query")
async def query(request: QueryRequest):
    try:
        start = time.time()
        result = rag_chain.invoke({"input": request.query})
        elapsed = time.time() - start
        print(f"=== rag_chain.invoke took {elapsed:.2f}s ===")
        answer = result["answer"]
        sources = result.get("context", [])
        return {"answer": answer, "sources": [doc.metadata for doc in sources]}
    except Exception as e:
        print("=== ERROR IN /query ===")
        traceback.print_exc()
        return {"error": str(e)}