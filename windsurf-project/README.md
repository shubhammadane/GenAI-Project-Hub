# Research Paper QA System

A simple, functional web application that allows users to upload research papers in PDF format, ask questions about their contents, and receive accurate, context-based answers using Retrieval-Augmented Generation (RAG).

## Features

- **PDF Upload**: Upload research papers with automatic text extraction
- **RAG Pipeline**: Uses embeddings and vector search to retrieve relevant passages
- **Clarifying Questions**: Identifies ambiguous questions and asks for clarification
- **Grounded Answers**: All answers are based on the uploaded paper with page citations
- **Conversation History**: Maintains chat context for follow-up questions
- **Error Handling**: Gracefully handles corrupted PDFs, missing text, and API errors

## How RAG Works in This Project

1. **Text Extraction**: PyMuPDF extracts text from the PDF page by page, preserving page numbers
2. **Chunking**: LangChain splits the text into overlapping chunks (~800 characters with 150 overlap)
3. **Embeddings**: Sentence-transformers generates vector embeddings for each chunk using `all-MiniLM-L6-v2`
4. **Vector Index**: FAISS stores and indexes the embeddings for fast similarity search
5. **Retrieval**: When you ask a question, the system retrieves the 5 most relevant chunks
6. **Classification**: Gemini classifies your question as CLEAR, NEEDS_CLARIFICATION, or INSUFFICIENT_EVIDENCE
7. **Answer Generation**: If clear, Gemini generates an answer using only the retrieved content with page citations

## Architecture and Data Flow

```
PDF Upload → Text Extraction → Chunking → Embeddings → FAISS Index
                                                              ↓
User Question → Question Embedding → FAISS Search → Retrieved Chunks
                                                              ↓
                                      Gemini Classification → Clarification (if needed)
                                                              ↓
                                      Gemini Answer Generation → Grounded Answer with Citations
```

### File Structure

```
research-paper-qa/
├── app.py                 # Streamlit interface and session state
├── pdf_processor.py       # PDF extraction and page metadata
├── rag_pipeline.py        # Chunking, embeddings, FAISS, and answer generation
├── test_rag_pipeline.py   # Pytest test suite
├── requirements.txt       # Project dependencies
├── .env.example          # Environment configuration template
├── .gitignore            # Git exclusions
└── README.md             # This file
```

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **PDF Extraction**: PyMuPDF (`pymupdf`)
- **Text Splitting**: LangChain text splitters
- **Embeddings**: `sentence-transformers` with `all-MiniLM-L6-v2`
- **Vector Database**: FAISS (`faiss-cpu`)
- **LLM**: Google Gemini API using `google-genai` SDK
- **Configuration**: `.env` file for API keys

## Installation

### Prerequisites

- Python 3.11 or 3.12
- Windows PowerShell (or your preferred terminal)
- A Google Gemini API key (get one at https://ai.google.dev/)

### Step 1: Create a Virtual Environment

Open PowerShell in the project directory and run:

```powershell
python -m venv venv
```

### Step 2: Activate the Virtual Environment

```powershell
.\venv\Scripts\Activate
```

You should see `(venv)` in your command prompt indicating the virtual environment is active.

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Configure the Gemini API Key

1. Copy the example environment file:
```powershell
Copy-Item .env.example .env
```

2. Open the `.env` file in a text editor
3. Replace `your_gemini_api_key_here` with your actual Gemini API key
4. Save the file

Your `.env` file should look like:
```
GOOGLE_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-1.5-pro
```

## Running the Application

Start the Streamlit application:

```powershell
streamlit run app.py
```

The application will open in your web browser at `http://localhost:8501`

## Running the Tests

Run the test suite with pytest:

```powershell
pytest test_rag_pipeline.py -v
```

The tests use mocked Gemini API calls, so they don't require a real API key or paid requests.

## Usage

1. **Upload a PDF**: Click "Browse files" to select a research paper PDF
2. **Process**: Click "Process Document" to extract text and create the vector index
3. **Ask Questions**: Type your question in the input field and click "Ask Question"
4. **Clarify if Needed**: If the system asks for clarification, provide your response
5. **View Answers**: Read the grounded answer with page citations
6. **Continue**: Ask more questions about the same paper
7. **Upload New**: Click "Upload New Document" to start with a different paper

## Example Questions to Try

- "What is the main contribution of this paper?"
- "What methods does the paper propose?"
- "What are the experimental results?"
- "How does this compare to previous work?"
- "What are the limitations mentioned?"

## Known Limitations

- OCR is not supported - scanned PDFs without extractable text cannot be processed
- Password-protected PDFs are not supported
- Clarification is limited to one round per question
- The system uses a single embedding model and may not capture all semantic nuances
- Gemini API rate limits may apply for heavy usage

## Error Handling

The application handles the following cases gracefully:

- No PDF uploaded
- Unsupported file formats
- Corrupted or empty PDFs
- Scanned PDFs without extractable text
- Missing or invalid Gemini API key
- Gemini API errors and rate limits
- Empty questions
- No relevant retrieval results
- Questions unrelated to the uploaded paper
- Failures during embedding generation or FAISS indexing

## Troubleshooting

**Issue**: "Gemini API key not configured"
- **Solution**: Ensure you've created a `.env` file with a valid `GOOGLE_API_KEY`

**Issue**: "No extractable text found"
- **Solution**: The PDF may be scanned. Try a PDF with selectable text.

**Issue**: Application is slow during processing
- **Solution**: This is normal for the first time as the embedding model downloads. Subsequent runs will be faster.

**Issue**: Import errors
- **Solution**: Ensure you've activated the virtual environment and installed all dependencies.

## Security Notes

- Never commit your `.env` file to version control
- Never share your API key publicly
- The `.gitignore` file is configured to exclude `.env` and other sensitive files

## License

This is a student portfolio project. Feel free to use it for learning purposes.
