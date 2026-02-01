import streamlit as st
import uuid
# import functions from your backend file
from final_agenticbot import agentic_bot, run_agentic_chat 

# helper function

def get_session_id():
    """Create or retrieve a unique ID for the current chat session."""
    if "thread_id" not in st.session_state:
        st.session_state["thread_id"] = str(uuid.uuid4())
    return st.session_state["thread_id"]

# page setup

st.set_page_config(page_title="Ebook Assistant", page_icon="📖")

# initialize the chat history list if it doesn't exist
if "display_history" not in st.session_state:
    st.session_state["display_history"] = []

# getting the thread ID for the current user
user_thread = get_session_id()

# making sidebar

with st.sidebar:
    st.header("App Settings")
    st.write(f"Session ID: {user_thread}")
    
    if st.button("Clear Chat"):
        # Reset everything
        st.session_state["thread_id"] = str(uuid.uuid4())
        st.session_state["display_history"] = []
        st.rerun()

# main chatbot

st.title("Agentic AI Ebook Bot")
st.write("Ask me questions about the Agentic AI document.")

# Show existing chat messages
for chat in st.session_state["display_history"]:
    with st.chat_message(chat["role"]):
        st.write(chat["content"])
        
        # If the bot found sources, show them in an expander
        if chat["role"] == "assistant" and chat.get("sources"):
            with st.expander("View PDF Sources"):
                for i, text in enumerate(chat["sources"]):
                    st.write(f"**Source {i+1}:**")
                    st.write(text)

# new user input
user_query = st.chat_input("Type your question here...")

if user_query:
    # add user question to the history
    st.session_state["display_history"].append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    # book loading indicator
    loading_text = st.text("loading... checking the ebook...")

    # get the response from the backend
    answer, context, confidence, tool_used = run_agentic_chat(
        user_query, 
        user_thread
    )
    
    # remove the loading text once done
    loading_text.empty()

    # save the bot's response to history
    bot_data = {
        "role": "assistant",
        "content": answer,
        "sources": context if tool_used else None,
        "conf": confidence
    }
    st.session_state["display_history"].append(bot_data)
    
    # rerun the app to update the UI
    st.rerun()