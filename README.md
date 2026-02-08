 AI Documentation Assistant (PoC)

This project is a proof-of-concept AI assistant designed to answer user questions based on technical PDF documentation (e.g. service manuals, instructions, safety documents).

It uses OpenAI models for embeddings and text generation, combined with in-memory vector search and basic safety guardrails.

---

## How to Run the Project

### 1. Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate    # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root directory with the following content:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Run the application

```bash
python app/cli/main.py
```

---

## Requirements

- Python 3.10 or newer
- OpenAI API key
- Internet connection
- PDF documentation placed in the `material/` directory

---

## How It Works

### Document Processing
- PDF files from the `material/` directory are loaded
- Text is extracted and split into smaller chunks
- Metadata such as section titles, severity levels, and page numbers are attached

### Vector Indexing
- Each text chunk is converted into an embedding using an OpenAI embedding model
- Embeddings are stored in an in-memory vector store
- No persistent storage is used (index is rebuilt on each run)

### Question Answering
- The user question is embedded
- The most relevant documentation chunks are retrieved
- A confidence score is calculated based on similarity

### Answer Generation
- A prompt is built using the retrieved context
- An OpenAI language model generates the answer
- Safety guardrails verify that required warnings and safety instructions are not omitted

### Output
- Final formatted answer
- Safety warnings if applicable
- Confidence score
- All interactions are logged to `audit.log` for traceability

---

## Project Status and Limitations

- Proof-of-concept / experimental
- In-memory vector store only
- No persistence of embeddings
- Designed for technical and safety-critical documentation
