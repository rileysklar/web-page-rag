"""
Streamlit app for chat-based RAG interactions.
"""
import streamlit as st
from rag_query import RAGQueryEngine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

def initialize_rag_engine():
    """Initialize the RAG engine with Pinecone."""
    return RAGQueryEngine(
        index_name="web-page-rag",
        model_name="gpt-3.5-turbo",
        temperature=0.7
    )

# App title and description
st.title("💬 Website Chat Assistant")
st.caption("Ask questions about the content from sanantonesklars.com")

# Initialize RAG engine
rag_engine = initialize_rag_engine()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("View Sources"):
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(f"{i}. {source}")

# Chat input
if prompt := st.chat_input("Ask a question about the website..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = rag_engine.query(prompt)
            answer = response["answer"]
            sources = [doc.metadata.get('source', 'Unknown source') 
                      for doc in response["source_documents"]]
            
            # Display response
            st.markdown(answer)
            if sources:
                with st.expander("View Sources"):
                    for i, source in enumerate(sources, 1):
                        st.markdown(f"{i}. {source}")
            
            # Add assistant message to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            }) 