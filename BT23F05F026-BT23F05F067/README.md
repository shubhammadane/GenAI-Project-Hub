# AI Research Paper Analysis Chatbot

An AI-powered web application that helps users understand academic research papers. Upload a research paper in PDF format to extract its content, identify its sections, generate section-wise summaries, and ask questions about the paper through an interactive chatbot.

## Project Team

| Name | Roll Number |
|---|---|
| Aditya Gujarkar | BT23F05F026 |
| Gangaprasad Urekar | BT23F05F067 |

## Features

- **PDF Upload:** Upload a research paper in PDF format through the web interface.
- **Text Extraction:** Extract text and content from the uploaded research paper.
- **Section Detection:** Identify and organize the paper's sections using an LLM-assisted processing workflow.
- **Section-wise Summaries:** Generate structured summaries for selected sections, including key points and simplified explanations.
- **Interactive Question Answering:** Ask questions about the uploaded paper and receive answers grounded in its retrieved content.
- **Semantic Retrieval:** Split the paper into smaller text chunks, generate vector embeddings, and retrieve relevant chunks for question answering.

## Technology Stack

- **Programming Language:** Python
- **Backend:** Flask
- **Frontend:** HTML, CSS, JavaScript
- **LLM Integration:** Groq API through LangChain
- **Embeddings:** Hugging Face sentence-transformer models
- **Vector Database:** FAISS
- **AI Framework:** LangChain
- **PDF Processing:** PyMuPDF (fitz)

## How It Works

1. **Upload a PDF:** The user uploads a research paper using the web interface.
2. **Extract Text:** The application extracts the text from the PDF.
3. **Detect Sections:** The extracted text is processed to identify the paper's sections and headings.
4. **Generate Summaries:** When a user selects a section, the LLM generates a structured summary of its content.
5. **Prepare the Vector Store:** The paper text is divided into overlapping chunks. An embedding model converts these chunks into vectors, which are indexed using FAISS.
6. **Ask Questions:** The user's question is passed to the retrieval-based question-answering chain. Relevant text chunks are retrieved and supplied to the LLM as context.
7. **Return an Answer:** The chatbot generates an answer based on the retrieved content. If the required information is not available in the context, the configured prompt instructs it to respond with "I don't know."

## Project Structure

```text
AI-Research-Paper-Analysis-chatbot/
│
├── app.py
├── requirements.txt
├── .env
│
├── src/
│   ├── load_and_extract_text.py
│   ├── detect_and_split_sections.py
│   ├── get_summary.py
│   ├── create_vector_db.py
│   └── RAG_retrival_chain.py
│
├── templates/
│   └── index.html
│
├── static/
│   └── images and frontend assets
│
└── uploads/
    └── uploaded PDF files
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI-Research-Paper-Analysis-chatbot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate
```

** macOS / Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project's root directory and add the following variables:

```env
GROQ_API_KEY=your_groq_api_key
LLM_MODEL=your_supported_groq_model
EMBEDDING_MODEL=your_huggingface_embedding_model
```

Replace the placeholder values with your actual API key and model names. Do not commit the `.env` file or expose your API key publicly.

### 5. Run the Application

```bash
python app.py
```

Open the local URL displayed in the terminal (typically `http://127.0.0.1:5000`) in your browser.

## Usage

1. Start the Flask application.
2. Open the application in your browser.
3. Upload a research paper in PDF format.
4. Select a detected section to generate its summary.
5. Open the question-answering interface and ask questions about the uploaded paper.
6. Review the responses generated from the paper's retrieved content.

## Notes

- A valid Groq API key is required for LLM-based section processing, summaries, and question answering.
- The Hugging Face embedding model is configured through the `EMBEDDING_MODEL` environment variable.
- The current application keeps the active paper text and vector database in application-level variables. It is designed as a project prototype; production deployment would require stronger session isolation, persistent storage, upload validation, and additional security controls.
- The question-answering workflow uses Retrieval-Augmented Generation (RAG) with FAISS-based dense vector retrieval. This repository does **not** currently implement BM25-based lexical retrieval or a BM25-plus-dense hybrid search pipeline.

## Future Enhancements

- Add BM25 retrieval and combine it with dense retrieval using Reciprocal Rank Fusion (RRF) or weighted score fusion.
- Support multiple research papers and persistent user sessions.
- Add citation and source-chunk display for generated answers.
- Improve PDF validation, error handling, and deployment security.
- Add research-paper comparison and cross-paper question answering.

---

**Developed by Aditya Gujarkar and Gangaprasad Urekar.**
