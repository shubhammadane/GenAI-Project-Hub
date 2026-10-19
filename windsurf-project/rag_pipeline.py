"""
RAG pipeline: chunking, embeddings, FAISS retrieval, and answer generation.
"""

import os
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from langchain_text_splitters import RecursiveCharacterTextSplitter

from google import genai

load_dotenv()


class RAGPipeline:
    """Manages the complete RAG pipeline for question answering."""
    
    def __init__(self):
        self.embedding_model = None
        self.index = None
        self.chunks = []
        self.chunk_metadata = []  # Stores page numbers for each chunk
        self.gemini_model = None
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        
        # Initialize Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            client = genai.Client(api_key=api_key)
            self.gemini_model = client
    
    def initialize_embedding_model(self):
        """Initialize the sentence transformer model."""
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def split_into_chunks(self, pages: List[Dict], chunk_size: int = 800, overlap: int = 150) -> List[Dict]:
        """
        Split text into chunks while preserving page metadata.
        
        Args:
            pages: List of page dicts with 'text' and 'page_number'
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks in characters
            
        Returns:
            List of chunk dicts with 'text' and 'page_numbers'
        """
        # Combine all text with page markers
        full_text = ""
        for page in pages:
            full_text += f"[PAGE {page['page_number']}]\n{page['text']}\n\n"
        
        # Split using LangChain
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = text_splitter.split_text(full_text)
        
        # Extract page numbers from each chunk
        chunk_data = []
        for chunk in chunks:
            # Find all page markers in the chunk
            page_numbers = []
            lines = chunk.split('\n')
            for line in lines:
                if line.startswith('[PAGE ') and line.endswith(']'):
                    try:
                        page_num = int(line.replace('[PAGE ', '').replace(']', ''))
                        page_numbers.append(page_num)
                    except ValueError:
                        pass
            
            # If no page markers found, use the first page as default
            if not page_numbers:
                page_numbers = [pages[0]['page_number']]
            
            # Remove page markers from the chunk text
            clean_chunk = chunk
            for line in lines:
                if line.startswith('[PAGE ') and line.endswith(']'):
                    clean_chunk = clean_chunk.replace(line, '', 1)
            
            # Only add if chunk has content after cleaning
            clean_text = clean_chunk.strip()
            if clean_text:
                chunk_data.append({
                    'text': clean_text,
                    'page_numbers': sorted(list(set(page_numbers)))
                })
        
        return chunk_data
    
    def create_vector_index(self, chunk_data: List[Dict]) -> str:
        """
        Create FAISS index from chunks.
        
        Args:
            chunk_data: List of chunk dicts with 'text' and 'page_numbers'
            
        Returns:
            Error message if any, empty string on success
        """
        try:
            self.initialize_embedding_model()
            
            # Extract chunk texts
            self.chunks = [chunk['text'] for chunk in chunk_data]
            self.chunk_metadata = [chunk['page_numbers'] for chunk in chunk_data]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(self.chunks, show_progress_bar=True)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings.astype('float32'))
            
            return ""
            
        except Exception as e:
            return f"Error creating vector index: {str(e)}"
    
    def retrieve_relevant_chunks(self, question: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve the most relevant chunks for a question.
        
        Args:
            question: User's question
            top_k: Number of chunks to retrieve
            
        Returns:
            List of dicts with 'text', 'page_numbers', and 'score'
        """
        if self.index is None or self.embedding_model is None:
            return []
        
        try:
            # Generate question embedding
            question_embedding = self.embedding_model.encode([question])
            
            # Search index
            distances, indices = self.index.search(question_embedding.astype('float32'), top_k)
            
            # Format results
            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.chunks):
                    results.append({
                        'text': self.chunks[idx],
                        'page_numbers': self.chunk_metadata[idx],
                        'score': float(dist)
                    })
            
            return results
            
        except Exception as e:
            print(f"Error during retrieval: {str(e)}")
            return []
    
    def classify_question(self, question: str, retrieved_chunks: List[Dict]) -> Tuple[str, str]:
        """
        Classify question as CLEAR, NEEDS_CLARIFICATION, or INSUFFICIENT_EVIDENCE.
        
        Args:
            question: User's question
            retrieved_chunks: Retrieved context chunks
            
        Returns:
            Tuple of (classification, clarifying_question_or_reason)
        """
        if not self.gemini_model:
            return "CLEAR", ""
        
        # Prepare context
        context = "\n\n".join([f"[Page {chunk['page_numbers'][0]}] {chunk['text']}" 
                              for chunk in retrieved_chunks[:3]])
        
        prompt = f"""You are analyzing a question about a research paper. 

Question: "{question}"

Context from the paper:
{context}

Classify the question as exactly one of:
- CLEAR: The question is specific and the context provides enough information to answer it
- NEEDS_CLARIFICATION: The question is ambiguous or could refer to multiple things
- INSUFFICIENT_EVIDENCE: The paper does not contain enough information to answer the question

If classification is NEEDS_CLARIFICATION, provide ONE short, specific follow-up question to clarify.
If classification is INSUFFICIENT_EVIDENCE, briefly explain what information is missing.

Respond in this exact format:
CLASSIFICATION: [classification]
CLARIFICATION: [your follow-up question or explanation, or "N/A" if CLEAR]"""
        
        try:
            response = self.gemini_model.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            response_text = response.text
            
            # Parse response
            classification = "CLEAR"
            clarification = ""
            
            for line in response_text.split('\n'):
                if line.startswith("CLASSIFICATION:"):
                    classification = line.replace("CLASSIFICATION:", "").strip().upper()
                elif line.startswith("CLARIFICATION:"):
                    clarification = line.replace("CLARIFICATION:", "").strip()
            
            # Ensure valid classification
            if classification not in ["CLEAR", "NEEDS_CLARIFICATION", "INSUFFICIENT_EVIDENCE"]:
                classification = "CLEAR"
            
            return classification, clarification
            
        except Exception as e:
            print(f"Error classifying question: {str(e)}")
            return "CLEAR", ""
    
    def generate_grounded_answer(self, question: str, retrieved_chunks: List[Dict], 
                                 clarification: str = "") -> Tuple[str, List[str]]:
        """
        Generate a grounded answer with citations.
        
        Args:
            question: User's question
            retrieved_chunks: Retrieved context chunks
            clarification: User's clarification if provided
            
        Returns:
            Tuple of (answer, list of cited page numbers)
        """
        if not self.gemini_model:
            return "Gemini model not initialized. Please check your API key.", []
        
        # Prepare context with page numbers
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            pages = chunk['page_numbers']
            if len(pages) == 1:
                page_ref = f"[Page {pages[0]}]"
            else:
                page_ref = f"[Pages {pages[0]}-{pages[-1]}]"
            context_parts.append(f"{page_ref}\n{chunk['text']}")
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Build prompt
        if clarification:
            prompt = f"""Answer the following question based ONLY on the provided research paper excerpts.

Original Question: "{question}"
User's Clarification: "{clarification}"

Paper Excerpts:
{context}

Instructions:
1. Answer using ONLY the information in the excerpts above
2. If the answer cannot be found in the excerpts, state that clearly
3. Do not invent facts or make claims not supported by the text
4. Use simple, clear English
5. Include citations in the format [Page X] or [Pages X-Y] when referring to specific information
6. Provide short supporting excerpts when useful
7. Be concise but thorough"""
        else:
            prompt = f"""Answer the following question based ONLY on the provided research paper excerpts.

Question: "{question}"

Paper Excerpts:
{context}

Instructions:
1. Answer using ONLY the information in the excerpts above
2. If the answer cannot be found in the excerpts, state that clearly
3. Do not invent facts or make claims not supported by the text
4. Use simple, clear English
5. Include citations in the format [Page X] or [Pages X-Y] when referring to specific information
6. Provide short supporting excerpts when useful
7. Be concise but thorough"""
        
        try:
            response = self.gemini_model.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            answer = response.text
            
            # Extract unique page numbers from retrieved chunks
            all_pages = []
            for chunk in retrieved_chunks:
                all_pages.extend(chunk['page_numbers'])
            cited_pages = sorted(list(set(all_pages)))
            
            return answer, cited_pages
            
        except Exception as e:
            error_msg = f"Error generating answer: {str(e)}"
            return error_msg, []
    
    def clear_index(self):
        """Clear the current index and chunks."""
        self.index = None
        self.chunks = []
        self.chunk_metadata = []
