
import pandas as pd
from pinecone import Pinecone, ServerlessSpec
import openai
import time
from dotenv import load_dotenv
import os
# Initialize Pinecone

load_dotenv()

# Load the Excel file
file_path = "HSN_Muthu_Db.xlsx"  # Replace with your actual file path
df = pd.read_excel(file_path)

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment="us-west1-gcp")
index_name = "hsn-vector-db"

# Create an index if it doesn't exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,  # Must match your embedding model's output
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")  # Adjust region as needed
    )

# Connect to the Pinecone index
index = pc.Index(index_name)

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")


# Function to generate text embeddings in batches
def get_embeddings(texts, batch_size=50):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY")
)
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=batch
        )

        # Collect embeddings from the response
        batch_embeddings = [r.embedding for r in response.data]
        embeddings.extend(batch_embeddings)

        # Avoid hitting rate limits
        time.sleep(1)  # Adjust based on API rate limits

    return embeddings

# Prepare and insert data into Pinecone in batches
batch_size = 100  # Adjust based on your dataset size
descriptions = df["Description"].astype(str).tolist()
hsn_codes = df["HSN CODES"].astype(str).tolist()

# Generate embeddings in batches
print("Generating embeddings in batches...")
embeddings = get_embeddings(descriptions, batch_size=50)

# Prepare vectors for Pinecone
vectors = [
    (hsn_codes[i], embeddings[i], {"hsn_code": hsn_codes[i], "description": descriptions[i]})
    for i in range(len(hsn_codes))
]

# Upsert data into Pinecone in batches
print("Uploading vectors to Pinecone...")
for i in range(0, len(vectors), batch_size):
    index.upsert(vectors[i : i + batch_size])
    print(f"Uploaded batch {i // batch_size + 1}")

print("HSN Codes and Descriptions uploaded successfully!")
