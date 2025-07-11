# rag

This repository implements a basic local Retrieval Augmented Generation (RAG) system.
Documents are read from `pdf_docs/`, processed into text files in `processed_docs/` and
indexed in a local Qdrant vector store. You can then ask questions and receive answers
referencing the exact document and page numbers.

## Usage

1. **Ingest PDFs**

   Place your PDF files in `pdf_docs/` and run:

   ```bash
   python -m rag_local.ingest
   ```

2. **Index processed pages**

   ```bash
   python -m rag_local.index
   ```

   A local Qdrant database is created in `qdrant_data/`.

3. **Ask questions**

   ```bash
   python -m rag_local.query "¿Cuál es el objetivo del proyecto?"
   ```

   The script searches the most relevant pages and sends them to the LLM
   defined in `rag_local.llm.call_llm`. By default it uses the OpenAI API,
   but you can set `provider='gemini-cli'` or extend it as needed.

## Requirements

- Python 3.10+
- The libraries listed in `requirements.txt`
- A running Qdrant instance (the scripts create a local one by default)

Install them with pip:

```bash
pip install -r requirements.txt
```

Or create the conda environment:

```bash
conda env create -f environment.yml
conda activate xe-alejandria-rag
```

To run everything inside Docker:

```bash
docker build -t rag-local .
docker run -it rag-local
```

