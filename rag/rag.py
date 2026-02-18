import os
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory


MAIN_MODEL="gemma3:1b"  # Smaller, optimized for CPU, text-only


class ChatLogic:
    def __init__(self):
        # 1. Hardware-optimized Models (Great for i5 + 16GB RAM)
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.llm = ChatOllama(model=MAIN_MODEL, temperature=0)
        
        # 2. Local Database (Persistence)
        self.db = Chroma(persist_directory="./rag/chroma_db", embedding_function=self.embeddings)
        
        # 3. Simple Memory Store
        self.history_store = {}

        # 4. Build the modern RAG Chain
        self.chain = self._setup_chain()

    def _setup_chain(self):
        
        system_prompt = (
            "You are an expert assistant. Use the provided context to answer the question. "
            "If you don't know the answer, say so. Keep it concise.\n\n"
            "Context: {context}"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])

        combine_docs_chain = create_stuff_documents_chain(self.llm, prompt)
        
        retrieval_chain = create_retrieval_chain(
            self.db.as_retriever(search_kwargs={"k": 3}), 
            combine_docs_chain
        )

        return RunnableWithMessageHistory(
            retrieval_chain,
            lambda session_id: self.history_store.setdefault(session_id, InMemoryChatMessageHistory()),
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

    def ingest_pdf(self, file_path):
        """Loads PDF, splits it, and saves vectors to disk."""
        loader = PyPDFLoader(file_path)
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = loader.load_and_split(splitter)
        self.db.add_documents(docs)
        return f"Successfully vectorized: {os.path.basename(file_path)}"

    def ask(self, query):
        """Standard query method for the GUI."""
        config = {"configurable": {"session_id": "gui_session"}}
        result = self.chain.invoke({"input": query}, config=config)
        return result["answer"]