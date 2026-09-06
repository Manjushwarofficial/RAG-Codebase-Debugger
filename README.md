# RAG Codebase Debugger

RAG Codebase Debugger lets you ask natural-language questions about a codebase and receive answers grounded in the code itself. It combines structure-aware document chunking, Hugging Face embeddings, a local FAISS vector index, and a Groq-powered language model.

The included knowledge base is the C++ [**Wolfenstein3D Clone**](https://github.com/vaibhav-yerkar/Wolfenstein3D_Clone) project. The application is intended to make unfamiliar codebases easier to explore, debug, and understand.

## UI (Streamlit)
![alt text](<Screenshot 2026-09-05 at 10.40.08 PM.png>)

## Features

- Ingests C++, text, and PDF files from `knowledge_base/`.
- Splits C++ by symbols such as classes, namespaces, functions, templates, and enums when Tree-sitter is available.
- Stores embeddings in a local FAISS index for fast retrieval.
- Uses retrieved code context to answer questions and avoid unsupported guesses.
- Provides a Streamlit chat interface backed by a FastAPI API.

## Project Structure

```text
backend/
	app.py          # Builds the FAISS index from knowledge_base/
	main.py         # FastAPI retrieval and question-answering API
frontend/
	app.py          # Streamlit chat interface
faiss_index/      # Generated or checked-in FAISS vector index
knowledge_base/   # Source material used for retrieval
requirements.txt
```

## UML and Sequence Diagram
<img width="1672" height="941" alt="ChatGPT Image Sep 6, 2026 at 06_12_35 PM" src="https://github.com/user-attachments/assets/420ea111-2a0c-413d-90f3-1d594f4b0005" />
<img width="1672" height="941" alt="ChatGPT Image Sep 6, 2026 at 06_16_21 PM" src="https://github.com/user-attachments/assets/d5606df6-623b-4793-bb16-6a53bad04b6d" />


## Requirements

- Python 3.10 or newer
- A Groq API key

## Setup

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env` and add your API key:

```env
GROQ_API_KEY=your_groq_api_key
```

The application uses the existing `faiss_index/` directory by default. To rebuild it after changing the files in `knowledge_base/`, run:

```bash
python backend/app.py
```

## Run the Application

Start the API in one terminal:

```bash
uvicorn backend.main:app --reload
```

Start the Streamlit interface in another terminal:

```bash
streamlit run frontend/app.py
```

Then open the local URL printed by Streamlit and ask questions about the indexed codebase.

The API also exposes:

```text
GET  /
POST /query
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/query \
	-H "Content-Type: application/json" \
	-d '{"query":"Where is player movement implemented?"}'
```

## Attribution

This project works with the **Wolfenstein3D Clone** codebase by Vaibhav Yerkar. The source code used in the knowledge base comes from:

- Repository: [vaibhav-yerkar/Wolfenstein3D_Clone](https://github.com/vaibhav-yerkar/Wolfenstein3D_Clone)
- GitHub account: [@vaibhav-yerkar](https://github.com/vaibhav-yerkar)

All credit for the original Wolfenstein3D Clone codebase belongs to Vaibhav Yerkar and the contributors acknowledged in that repository. This project adds the retrieval, indexing, API, and chat interface used to explore that codebase.

Please review and follow the original repository's license and usage terms before redistributing or building on its source code.
