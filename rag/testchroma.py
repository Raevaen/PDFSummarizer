import os
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings

DB_PATH = "chroma_db"
embeddings = OllamaEmbeddings(model="nomic-embed-text")
#llm = ChatOllama(model="gemma3:1b", temperature=0) # gemma3:1b is smaller but can process only text, llama3.2 can process text and images but is larger and a bit slower

db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

# 3. Add a test "vectorized summary"
test_doc = Document(
    page_content="The project is about local PDF summarization on an i5 CPU.",
    metadata={"source": "manual_test", "type": "summary"}
)

print("--- Step 2: Saving document to disk ---")
db.add_documents([test_doc])

# 4. Verify Retrieval (The "Acid Test")
print("--- Step 3: Testing Retrieval ---")
# We search for something semantically similar but not identical
query = "Tell me about the i5 hardware project."
results = db.similarity_search(query, k=1)

if len(results) > 0:
    print(f"SUCCESS! Found: {results[0].page_content}")
    print(f"Metadata: {results[0].metadata}")
else:
    print("FAILED: No documents found.")

# 5. Check if the folder was created
if os.path.exists(DB_PATH):
    print(f"\n--- Persistence Check ---")
    print(f"Directory '{DB_PATH}' exists and contains: {os.listdir(DB_PATH)}")