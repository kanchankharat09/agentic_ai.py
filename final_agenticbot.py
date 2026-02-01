import os
import sqlite3
import json
from typing import Annotated, TypedDict, List
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import tool
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

# using pdf loader
SOURCE_PDF = "Ebook-Agentic-AI.pdf"
FAISS_INDEX_DIR = "vectorstore/db_faiss"


#  vector Store
embedding_model=HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    cache_folder="./model_cache"
)

if os.path.exists(FAISS_INDEX_DIR):
    # print(vectore store is done)
    vector_db = FAISS.load_local(
        FAISS_INDEX_DIR, embedding_model, allow_dangerous_deserialization=True
    )
else:

    if not os.path.exists(SOURCE_PDF):
        raise FileNotFoundError(f"PDF source not found: {SOURCE_PDF}")

    os.makedirs(os.path.dirname(FAISS_INDEX_DIR), exist_ok=True)
    loader=PyPDFLoader(SOURCE_PDF)
    pages=loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    text_chunks = splitter.split_documents(pages)

    vector_db = FAISS.from_documents(text_chunks, embedding_model)
    vector_db.save_local(FAISS_INDEX_DIR)

#  LLM setup
llm = ChatGroq(model="qwen/qwen3-32b", temperature=0)

# defining tool
@tool
def rag_tool(query: str) -> str:
    """
    Search and retrieve technical content from the Agentic AI ebook.
    MANDATORY: Use this tool for any questions regarding Agentic AI.
    """
    matches = vector_db.similarity_search_with_score(query, k=5)

    segments = []
    scores = []

    for doc, dist in matches:
        segments.append(doc.page_content)
        # converting L2 distnace with similarity score
        val = float(1 / (1 + dist))
        scores.append(val)

    avg_conf = sum(scores) / len(scores) if scores else 0.0
    
    return json.dumps({
        "context": segments, 
        "confidence": float(round(avg_conf, 2)), 
        "tool_called": True
    })

tools_list = [rag_tool]
llm_with_tools = llm.bind_tools(tools_list)

#  using langgraph
class WorkflowState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

def core_logic_node(state: WorkflowState):
    """Primary processing node."""
    system_instruction = SystemMessage(
        content=(
            "You are a specialized Agentic AI consultant. "
            "You have NO internal knowledge and must strictly use 'agentic_ai_rag_tool' to answer.\n\n"
            "RULES:\n"
            "1. You MUST call the tool for every question.\n"
            "2. Answer ONLY using the retrieved context.\n"
            "3. If the context is empty, say: 'I cannot find this information in the ebook.'"
        )
    )
    # cleans the history from privious promt
    user_msgs = [m for m in state["messages"] if not isinstance(m, SystemMessage)]
    response = llm_with_tools.invoke([system_instruction] + user_msgs)
    return {"messages": [response]}

# building graph
workflow = StateGraph(WorkflowState)
workflow.add_node("agent", core_logic_node)
workflow.add_node("tools", ToolNode(tools_list))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

# memory saver
brain_memory = InMemorySaver()
agentic_bot = workflow.compile(checkpointer=brain_memory)

# function for ui
def run_agentic_chat(user_query: str, thread_id: str):
    """
    Executes the graph and extracts source metadata.
    """
    output = agentic_bot.invoke(
        {"messages":[HumanMessage(content=user_query)]},
        config={"configurable": {"thread_id": thread_id}},
    )

    final_text = output["messages"][-1].content
    
    # metadata extraction
    sources, confidence, used_tool = [], 0.0, False

    for msg in reversed(output["messages"]):
        if isinstance(msg, ToolMessage):
            try:
                data = json.loads(msg.content)
                sources = data.get("context", [])
                confidence = data.get("confidence", 0.0)
                used_tool = True
                break
            except: continue

    return final_text, sources, confidence, used_tool


print('don')