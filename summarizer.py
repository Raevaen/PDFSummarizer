import os
import sys
import argparse

try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_ollama import ChatOllama
    from langchain_core.prompts import ChatPromptTemplate
except ImportError as e:
    missing = str(e).split()[-1].strip("'\n")
    print("Missing Python dependency:", missing)
    print("Install required packages with:")
    print("python -m pip install -r requirements.txt")
    print("If you already have a virtualenv, activate it first.")
    sys.exit(1)

def summarize_single_pdf(file_path, model_name="llama3.2"):
    """
    Summarize a single PDF file and return the summary as a string.
    
    Args:
        file_path (str): Path to the PDF file.
        model_name (str): Name of the Ollama model to use.
    
    Returns:
        str: The summarized text.
    """
    # 1. Initialize the Local Model (Optimized for CPU)
    llm = ChatOllama(model=model_name, temperature=0.1)

    # 2. Configure the Chunker
    # We use 3000 chars with 300 overlap to maintain 'contextual entanglement'
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000, 
        chunk_overlap=300
    )

    # Define custom prompt to ensure high-quality output
    prompt_template = """Write a concise summary of the following text.
Do not use bullet points or numbered lists. Emphasize the most relevant topics by making them bold (use **bold**). 
Follow the 20/80 rule: prioritize the top ~20% of information that conveys ~80% of the value. 
Keep the summary short, focused, and easy to read/scan.

Text:
"{text}"

CONCISE SUMMARY:"""
    ADAPTIVE_PROMPT = ChatPromptTemplate.from_template(prompt_template)

    # Load and Split PDF
    loader = PyPDFLoader(file_path)
    docs = loader.load_and_split(text_splitter=text_splitter)
    
    # 3. Manual Map-Reduce Summarization
    # Summarize each chunk
    chunk_summaries = []
    for doc in docs:
        messages = ADAPTIVE_PROMPT.format_messages(text=doc.page_content)
        summary = llm.invoke(messages)
        chunk_summaries.append(summary.content)
    
    # Combine and summarize the chunk summaries
    combined_text = "\n".join(chunk_summaries)
    final_messages = ADAPTIVE_PROMPT.format_messages(text=combined_text)
    final_summary = llm.invoke(final_messages)

    return final_summary.content


def summarize_pdf_folder(folder_path, model_name="llama3.2", callback=None):
    """
    Summarize all PDFs in a folder and optionally call a callback for each.
    
    Args:
        folder_path (str): Path to the folder containing PDF files.
        model_name (str): Name of the Ollama model to use.
        callback (callable): Optional function to call with (filename, summary) after each PDF.
    """
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            print(f"--- Processing: {filename} ---")
            file_path = os.path.join(folder_path, filename)
            
            summary = summarize_single_pdf(file_path, model_name)
            
            if callback:
                callback(filename, summary)
            print(f"Summary for {filename}:\n{summary}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize PDFs in a folder using Ollama")
    parser.add_argument(
        "pdf_folder",
        nargs="?",
        default="./",
        help="Path to the folder containing PDF files (default current directory)"
    )
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_folder):
        os.makedirs(args.pdf_folder)
        print(f"Please put PDFs in {args.pdf_folder}")
    else:
        summarize_pdf_folder(args.pdf_folder)