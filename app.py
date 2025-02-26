import streamlit as st
import openai
from pinecone import Pinecone
from dotenv import load_dotenv
import os
# Initialize Pinecone

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "hsn-vector-db"

if index_name not in pc.list_indexes().names():
    st.error(f"Index '{index_name}' not found. Please create it first.")
    st.stop()

index = pc.Index(index_name)

# OpenAI API Key
openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)

# Function to generate embeddings
def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=[text]
    )
    return response.data[0].embedding

# Function to search Pinecone
def search_pinecone(query_text, top_k=5):
    query_vector = get_embedding(query_text)
    search_results = index.query(
        vector=query_vector, 
        top_k=top_k, 
        include_metadata=True
    )
    return search_results['matches']

# Function to format results
def format_prompt(results):
    context = "\n".join(
        f"HSN Code: {match['metadata']['hsn_code']}\nDescription: {match['metadata']['description']}"
        for match in results
    )
    return f"Given the following HSN Codes:\n\n{context}\n\nProvide a summary or insights."

# Function to get OpenAI response
def get_openai_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an assistant that provides information about HSN codes."},
                  {"role": "user", "content": prompt}],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

# Streamlit UI
st.set_page_config(page_title="HSN Code Finder", layout="centered")
st.title("🔍 HSN Code Search Assistant")

# Session state for storing chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
query_text = st.text_input("Enter a query about HSN codes:")
if st.button("Search") and query_text:
    with st.spinner("Searching..."):
        results = search_pinecone(query_text)
        if results:
            prompt = format_prompt(results)
            response = get_openai_response(prompt)
            st.session_state.chat_history.append((query_text, response))
        else:
            response = "No relevant HSN data found."
            st.session_state.chat_history.append((query_text, response))

# Display chat history
st.subheader("📜 Previous Searches")
for query, response in st.session_state.chat_history[::-1]:
    st.markdown(f"**📝 Query:** {query}")
    st.markdown(f"**💡 Response:** {response}")
    st.divider()

# Clear session button
if st.button("Clear History"):
    st.session_state.chat_history = []
    st.experimental_user()