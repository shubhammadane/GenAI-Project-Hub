"""
Streamlit interface for Research Paper QA System.
"""

import os
import streamlit as st
from dotenv import load_dotenv

from pdf_processor import PDFProcessor
from rag_pipeline import RAGPipeline

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="ResearchPaper QA",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if 'pdf_processor' not in st.session_state:
    st.session_state.pdf_processor = PDFProcessor()
if 'rag_pipeline' not in st.session_state:
    st.session_state.rag_pipeline = RAGPipeline()
if 'pages' not in st.session_state:
    st.session_state.pages = []
if 'indexed' not in st.session_state:
    st.session_state.indexed = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'clarification_needed' not in st.session_state:
    st.session_state.clarification_needed = False
if 'original_question' not in st.session_state:
    st.session_state.original_question = ""
if 'clarification_question' not in st.session_state:
    st.session_state.clarification_question = ""
if 'filename' not in st.session_state:
    st.session_state.filename = ""


def check_api_key():
    """Check if Gemini API key is configured."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        st.error("⚠️ Gemini API key not configured. Please set GOOGLE_API_KEY in your .env file.")
        return False
    return True


def clear_chat():
    """Clear chat history."""
    st.session_state.chat_history = []
    st.session_state.clarification_needed = False
    st.session_state.original_question = ""
    st.session_state.clarification_question = ""


def clear_document():
    """Clear uploaded document and all state."""
    st.session_state.pages = []
    st.session_state.indexed = False
    st.session_state.chat_history = []
    st.session_state.clarification_needed = False
    st.session_state.original_question = ""
    st.session_state.clarification_question = ""
    st.session_state.filename = ""
    st.session_state.rag_pipeline.clear_index()


def main():
    """Main application."""
    
    # Sidebar
    with st.sidebar:
        st.title("📄 ResearchPaper QA")
        st.markdown("---")
        
        # Document info
        if st.session_state.filename:
            st.subheader("Document Info")
            st.text(f"File: {st.session_state.filename}")
            st.text(f"Pages: {len(st.session_state.pages)}")
            st.text(f"Status: {'✅ Indexed' if st.session_state.indexed else '⏳ Not indexed'}")
            st.markdown("---")
        
        # Action buttons
        if st.session_state.indexed:
            if st.button("Clear Chat"):
                clear_chat()
                st.rerun()
        
        if st.session_state.filename:
            if st.button("Upload New Document"):
                clear_document()
                st.rerun()
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This application uses RAG (Retrieval-Augmented Generation) to answer questions about uploaded research papers.
        
        **Features:**
        - Upload PDF research papers
        - Ask questions with page citations
        - Clarifying questions for ambiguity
        - Conversation history
        """)
    
    # Main content
    st.title("Research Paper Question-Answering System")
    st.markdown("""
    Upload a research paper in PDF format, ask questions about its contents, and receive accurate, context-based answers with page citations.
    """)
    
    # Check API key
    if not check_api_key():
        st.stop()
    
    # PDF Upload section
    st.markdown("## 1. Upload Research Paper")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        key="pdf_uploader"
    )
    
    if uploaded_file is not None:
        # Clear previous document if new one uploaded
        if st.session_state.filename != uploaded_file.name:
            clear_document()
        
        # Display file info
        file_size = uploaded_file.size / 1024  # KB
        st.info(f"📁 **Filename:** {uploaded_file.name} | **Size:** {file_size:.2f} KB")
        
        # Process button
        if st.button("Process Document", key="process_btn"):
            with st.spinner("Extracting text from PDF..."):
                # Save uploaded file temporarily
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Extract text
                pages, error = st.session_state.pdf_processor.extract_pdf_text(temp_path)
                
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                if error:
                    st.error(f"❌ Error: {error}")
                else:
                    st.session_state.pages = pages
                    st.session_state.filename = uploaded_file.name
                    
                    # Display preview
                    st.success(f"✅ Successfully extracted text from {len(pages)} pages")
                    
                    with st.expander("Preview extracted text"):
                        preview = st.session_state.pdf_processor.get_text_preview(1000)
                        st.text(preview)
                    
                    # Create vector index
                    with st.spinner("Creating vector index (this may take a moment)..."):
                        chunk_data = st.session_state.rag_pipeline.split_into_chunks(pages)
                        index_error = st.session_state.rag_pipeline.create_vector_index(chunk_data)
                        
                        if index_error:
                            st.error(f"❌ Error creating index: {index_error}")
                        else:
                            st.session_state.indexed = True
                            st.success(f"✅ Document indexed successfully with {len(chunk_data)} chunks")
                    
                    st.rerun()
    
    # Question-Answering section (only show if document is indexed)
    if st.session_state.indexed:
        st.markdown("## 2. Ask Questions")
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("### Conversation History")
            for i, exchange in enumerate(st.session_state.chat_history):
                with st.chat_message("user"):
                    st.write(exchange['question'])
                with st.chat_message("assistant"):
                    st.write(exchange['answer'])
                    if exchange.get('sources'):
                        st.markdown(f"**Sources:** {', '.join(exchange['sources'])}")
        
        # Clarification input
        if st.session_state.clarification_needed:
            st.info(f"**Clarification needed:** {st.session_state.clarification_question}")
            
            clarification = st.text_input(
                "Your response:",
                key="clarification_input"
            )
            
            if st.button("Submit Clarification", key="submit_clarification"):
                if clarification.strip():
                    with st.spinner("Generating answer..."):
                        # Retrieve chunks again
                        retrieved_chunks = st.session_state.rag_pipeline.retrieve_relevant_chunks(
                            st.session_state.original_question
                        )
                        
                        # Generate answer with clarification
                        answer, cited_pages = st.session_state.rag_pipeline.generate_grounded_answer(
                            st.session_state.original_question,
                            retrieved_chunks,
                            clarification=clarification
                        )
                        
                        # Format sources
                        sources = [f"Page {p}" for p in cited_pages]
                        
                        # Add to chat history
                        st.session_state.chat_history.append({
                            'question': st.session_state.original_question,
                            'answer': answer,
                            'sources': sources
                        })
                        
                        # Clear clarification state
                        st.session_state.clarification_needed = False
                        st.session_state.original_question = ""
                        st.session_state.clarification_question = ""
                        
                        st.rerun()
        
        # Regular question input
        question = st.text_input(
            "Ask a question about the paper:",
            key="question_input",
            disabled=st.session_state.clarification_needed
        )
        
        if st.button("Ask Question", key="ask_btn", disabled=st.session_state.clarification_needed):
            if question.strip():
                with st.spinner("Analyzing question and retrieving relevant passages..."):
                    # Retrieve relevant chunks
                    retrieved_chunks = st.session_state.rag_pipeline.retrieve_relevant_chunks(question)
                    
                    if not retrieved_chunks:
                        st.warning("⚠️ No relevant information found in the document. Try rephrasing your question.")
                    else:
                        # Classify question
                        classification, clarification = st.session_state.rag_pipeline.classify_question(
                            question, retrieved_chunks
                        )
                        
                        if classification == "NEEDS_CLARIFICATION":
                            # Ask for clarification
                            st.session_state.clarification_needed = True
                            st.session_state.original_question = question
                            st.session_state.clarification_question = clarification
                            st.rerun()
                        
                        elif classification == "INSUFFICIENT_EVIDENCE":
                            # Inform user about insufficient evidence
                            answer = f"Based on the retrieved content, {clarification}"
                            
                            cited_pages = sorted(list(set(
                                [p for chunk in retrieved_chunks for p in chunk['page_numbers']]
                            )))
                            sources = [f"Page {p}" for p in cited_pages]
                            
                            st.session_state.chat_history.append({
                                'question': question,
                                'answer': answer,
                                'sources': sources
                            })
                            st.rerun()
                        
                        else:
                            # Generate answer directly
                            answer, cited_pages = st.session_state.rag_pipeline.generate_grounded_answer(
                                question, retrieved_chunks
                            )
                            
                            sources = [f"Page {p}" for p in cited_pages]
                            
                            st.session_state.chat_history.append({
                                'question': question,
                                'answer': answer,
                                'sources': sources
                            })
                            st.rerun()
            else:
                st.warning("⚠️ Please enter a question.")
    
    else:
        st.info("👆 Please upload and process a research paper before asking questions.")


if __name__ == "__main__":
    main()
