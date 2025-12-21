# PDF Summarizer

Automatically summarize PDF documents using Ollama and LangChain.

## Requirements:

- Ollama
- llama3.2

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Ollama is running with the llama3.2 model:
```bash
ollama serve
```

## UI usage
```bash
python ui.py
```

### Basic usage (default: current folder):
```bash
python ui.py
python summarizer.py
```

### With custom PDF folder:
```bash
python summarizer.py /path/to/pdf/folder
```

### Examples:
```bash
python summarizer.py ./papers
python summarizer.py "C:\Users\<YourName>\Documents\PDFs"
python summarizer.py ../research_papers
```

The script will:
1. Create the folder if it doesn't exist
2. Process all PDF files in the specified folder
3. Generate a concise summary for each PDF using the local llama3.2 model