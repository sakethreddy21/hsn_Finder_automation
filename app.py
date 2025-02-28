import streamlit as st
from main import search_hsn, generate_reasoning

# Streamlit UI setup
st.set_page_config(page_title="HSN Code Finder", layout="centered")

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔒 Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "milind" and password == "admin11":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")

if not st.session_state.logged_in:
    login()
else:
    st.title("🔍 HSN Code Search Assistant")

    # Session state for storing chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # User input
    query_text = st.text_input("Enter a query about HSN codes:")
    if st.button("Search") and query_text:
        with st.spinner("Searching..."):
            results = search_hsn(query_text)

            if results:
                reasoning = generate_reasoning(results)
                best_match = results[0]  # Top result
                response = f"**HSN Code:** {best_match['metadata']['hsn_code']}\n\n**Description:** {best_match['metadata']['description']}\n\n**Reasoning:** {reasoning}"
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

    # Logout button
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
