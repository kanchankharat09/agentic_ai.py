



Agentic AI Ebook Assistant
A specialized Retrieval-Augmented Generation (RAG) chatbot built using an agentic workflow. This system is designed to provide highly accurate, document-grounded answers from the "Agentic AI" technical ebook.
Project Overview
This project goes beyond simple search by using an Agentic Loop. Instead of a direct query-response, the system uses a reasoning agent that must decide to use a retrieval tool before answering. This ensures the model doesn't hallucinate and only uses the provided PDF as its "Source of Truth."

Key Technical Features:
Stateful Agent: Built with LangGraph to manage complex logic and maintain conversation memory (thread_id).

Vector Search: Implements FAISS for efficient similarity searching of PDF content.

Context-Aware Splitting: Uses RecursiveCharacterTextSplitter to maintain semantic meaning across document chunks.

Source Verification: Displays retrieved PDF excerpts and a Confidence Score for every response.

Technical Stack
Orchestration: LangChain & LangGraph

LLM: Qwen-3-32b (via Groq Cloud)

Vector Store: FAISS (Local)

Embeddings: HuggingFace (all-mpnet-base-v2)

Frontend: Streamlit

📂 Project Structure
Plaintext

├── final_agenticbot.py   # Backend: PDF Processing, Vector Store, & LangGraph Logic
├── app.py                # Frontend: Streamlit Interface & Session Management
├── Ebook-Agentic-AI.pdf  # The source knowledge base
├── vectorstore/          # Locally saved FAISS index
└── model_cache/          # Cache for the HuggingFace embedding model
⚙️ How It Works
Ingestion: On the first run, the PDF is parsed and stored in a local vector database.

Logic Gate: When a user asks a question, the Core Logic Node (Agent) receives the query.

Tool Call: The Agent is strictly programmed to call the rag_tool.

Retrieval: The tool searches the FAISS index for the 5 most relevant chunks from the ebook.

Synthesis: The Agent combines these chunks into a natural language answer.

Setup & Installation
Clone the Repository

Install Dependencies:

Bash

pip install -r requirements.txt
Set Environment Variables: Create a .env file and add your API key:

Code snippet

GROQ_API_KEY=your_api_key_here
Run the Application:

Bash

streamlit run app.py
I developed this project to demonstrate my ability to:

Handle unstructured data (PDFs) and turn it into a searchable knowledge base.

Implement state-of-the-art Agentic Workflows rather than simple linear chains.

Create a clean, user-friendly UI that handles asynchronous "loading" states and session history.
