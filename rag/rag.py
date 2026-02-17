import os
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


DB_PATH = "chroma_db"
embeddings = OllamaEmbeddings(model="nomic-embed-text")
llm = ChatOllama(model="gemma3:1b", temperature=0) # gemma3:1b is smaller but can process only text, llama3.2 can process text and images but is larger and a bit slower

db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)


def process_new_pdf(file_path):
    """
    Ingest a PDF into the vector database and generate a short summary.

    This function loads the PDF at `file_path`, splits it into text chunks, 
    adds those chunks to the configured Chroma vector store, 
    then generates a concise summary (using only the first few chunks for speed) 
    and stores that summary in the same vector store as aseparate document 
    with metadata `{"source": file_path, "type": "summary"}`.

    Args:
        file_path (str): Path to the PDF file to process.

    Returns:
        str: The generated concise summary text.
    """
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=250)
    chunks = splitter.split_documents(docs)
    
    db.add_documents(chunks)
    
    summary_prompt = ChatPromptTemplate.from_template("Provide a concise summary of this text: {context}")
    context_text = "\n".join([c.page_content for c in chunks[:10]]) # up to 20k characters
    # | = pipe the output of the left-hand component into the input of the next component
    summary_chain = summary_prompt | llm | StrOutputParser()
    summary = summary_chain.invoke({"context": context_text})
    
    db.add_documents([Document(page_content=summary, metadata={"source": file_path, "type": "summary"})])
    return summary


qa_prompt = ChatPromptTemplate.from_template("""
Use the context below to answer. If you don't know, say you don't know.
Context: {context}
Question: {question}
""")

rag_chain = (
    {"context": db.as_retriever(search_kwargs={"k": 3}) 
    | (lambda docs: "\n\n".join(d.page_content for d in docs)), 
        "question": RunnablePassthrough()}
    | qa_prompt 
    | llm 
    | StrOutputParser()
)


if __name__ == "__main__":
    pdf_path = "/Users/ciccio/Documents/document.pdf" 
    summary = process_new_pdf(pdf_path)
    print("Ready")

    while True:
        try:
            question = input("Ask a question (/bye to quit): ").strip()
        except EOFError:
            break

        if question == "/bye":
            break
        if not question:
            continue

        answer = rag_chain.invoke(question)
        print("Answer:", answer)
