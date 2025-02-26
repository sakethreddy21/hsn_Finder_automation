import openai
import os
from pinecone import Pinecone
from dotenv import load_dotenv
import os
# Initialize Pinecone

load_dotenv()

# ✅ Correct way to initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# ✅ Ensure index exists before using it
index_name = "hsn-vector-db"

if index_name not in pc.list_indexes().names():
    print(f"Index '{index_name}' not found. Please create it first.")
    exit()

# ✅ Connect to the Pinecone index
index = pc.Index(index_name)


# Function to generate text embeddings using OpenAI
def get_embedding(text):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=[text]
    )
    return response.data[0].embedding 

# **Step 1: Search Pinecone for Relevant Data**
def search_pinecone(query_text, top_k=5):
    # Generate embedding for search query
    query_vector = get_embedding(query_text)

    # Query Pinecone index
    search_results = index.query(
        vector=query_vector, 
        top_k=top_k, 
        include_metadata=True
    )

    return search_results['matches']

# **Step 2: Format Retrieved Data as a Prompt**
def format_prompt(results):
    context = "\n".join(
        f"HSN Code: {match['metadata']['hsn_code']}\nDescription: {match['metadata']['description']}" 
        for match in results
    )
    prompt = f"Given the following HSN Codes:\n\n{context}\n\nProvide a summary or insights."
    return prompt

# **Step 3: Get Response from OpenAI**
def get_openai_response(prompt):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(  
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an assistant that provides information about HSN codes."},
                  {"role": "user", "content": prompt}],
        max_tokens=100
    )
    return response.choices[0].message.content.strip()

# **Step 4: Full Process**
def main(query):
    results = search_pinecone(query)
    if not results:
        return "No relevant HSN data found."
    
    prompt = format_prompt(results)
    response = get_openai_response(prompt)

    return response

# **Example Query**
query_text = "Find information about electrical appliances"
response = main(query_text)
print(response)
