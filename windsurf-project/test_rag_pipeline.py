"""
Test suite for RAG pipeline with mocked Gemini API.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from pdf_processor import PDFProcessor
from rag_pipeline import RAGPipeline


class TestPDFProcessor:
    """Tests for PDF text extraction."""
    
    def test_extract_pdf_text_preserves_page_numbers(self):
        """Test that PDF extraction preserves page numbers."""
        processor = PDFProcessor()
        
        # Create a mock PDF structure
        pages = [
            {"page_number": 1, "text": "This is page 1 content."},
            {"page_number": 2, "text": "This is page 2 content."},
            {"page_number": 3, "text": "This is page 3 content."}
        ]
        
        processor.pages = pages
        
        assert processor.get_page_count() == 3
        assert processor.pages[0]["page_number"] == 1
        assert processor.pages[1]["page_number"] == 2
        assert processor.pages[2]["page_number"] == 3
    
    def test_get_text_preview(self):
        """Test text preview generation."""
        processor = PDFProcessor()
        processor.pages = [
            {"page_number": 1, "text": "A" * 1000}
        ]
        
        preview = processor.get_text_preview(max_chars=100)
        assert len(preview) <= 103  # 100 + "..."
        assert "..." in preview


class TestRAGPipeline:
    """Tests for RAG pipeline."""
    
    @patch('rag_pipeline.SentenceTransformer')
    def test_split_into_chunks_creates_valid_chunks(self, mock_transformer):
        """Test that text chunking creates valid chunks with metadata."""
        pipeline = RAGPipeline()
        
        pages = [
            {"page_number": 1, "text": "This is a test. " * 100},
            {"page_number": 2, "text": "More content here. " * 100}
        ]
        
        chunks = pipeline.split_into_chunks(pages, chunk_size=200, overlap=50)
        
        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)
        assert all('page_numbers' in chunk for chunk in chunks)
        assert all(len(chunk['text']) > 0 for chunk in chunks)
        assert all(len(chunk['page_numbers']) > 0 for chunk in chunks)
    
    @patch('rag_pipeline.SentenceTransformer')
    def test_create_vector_index(self, mock_transformer):
        """Test vector index creation."""
        pipeline = RAGPipeline()
        
        # Mock the embedding model
        mock_model = Mock()
        mock_model.encode.return_value = np.random.rand(5, 384).astype('float32')
        mock_transformer.return_value = mock_model
        
        chunk_data = [
            {"text": "Test chunk 1", "page_numbers": [1]},
            {"text": "Test chunk 2", "page_numbers": [2]},
            {"text": "Test chunk 3", "page_numbers": [3]},
            {"text": "Test chunk 4", "page_numbers": [4]},
            {"text": "Test chunk 5", "page_numbers": [5]}
        ]
        
        error = pipeline.create_vector_index(chunk_data)
        
        assert error == ""
        assert pipeline.index is not None
        assert len(pipeline.chunks) == 5
        assert len(pipeline.chunk_metadata) == 5
    
    @patch('rag_pipeline.SentenceTransformer')
    def test_retrieve_relevant_chunks(self, mock_transformer):
        """Test that retrieval returns relevant chunks."""
        pipeline = RAGPipeline()
        
        # Mock the embedding model
        mock_model = Mock()
        mock_model.encode.return_value = np.random.rand(5, 384).astype('float32')
        mock_transformer.return_value = mock_model
        
        chunk_data = [
            {"text": "Machine learning is a subset of AI", "page_numbers": [1]},
            {"text": "Deep learning uses neural networks", "page_numbers": [2]},
            {"text": "Natural language processing deals with text", "page_numbers": [3]},
            {"text": "Computer vision processes images", "page_numbers": [4]},
            {"text": "Reinforcement learning learns through rewards", "page_numbers": [5]}
        ]
        
        pipeline.create_vector_index(chunk_data)
        
        results = pipeline.retrieve_relevant_chunks("What is machine learning?", top_k=3)
        
        assert len(results) <= 3
        assert all('text' in result for result in results)
        assert all('page_numbers' in result for result in results)
        assert all('score' in result for result in results)
    
    @patch('rag_pipeline.genai')
    def test_classify_question_ambiguous(self, mock_genai):
        """Test that ambiguous questions produce clarifying questions."""
        pipeline = RAGPipeline()
        
        # Mock Gemini response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "CLASSIFICATION: NEEDS_CLARIFICATION\nCLARIFICATION: Which accuracy are you asking about: the proposed model's accuracy, a baseline model's accuracy, or accuracy on a specific dataset?"
        mock_client.models.generate_content.return_value = mock_response
        pipeline.gemini_model = mock_client
        
        retrieved_chunks = [
            {"text": "The model achieved 95% accuracy", "page_numbers": [1]},
            {"text": "The baseline had 90% accuracy", "page_numbers": [2]}
        ]
        
        classification, clarification = pipeline.classify_question("What is its accuracy?", retrieved_chunks)
        
        assert classification == "NEEDS_CLARIFICATION"
        assert len(clarification) > 0
        assert "accuracy" in clarification.lower()
    
    @patch('rag_pipeline.genai')
    def test_classify_question_clear(self, mock_genai):
        """Test that clear questions are classified correctly."""
        pipeline = RAGPipeline()
        
        # Mock Gemini response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "CLASSIFICATION: CLEAR\nCLARIFICATION: N/A"
        mock_client.models.generate_content.return_value = mock_response
        pipeline.gemini_model = mock_client
        
        retrieved_chunks = [
            {"text": "The abstract discusses machine learning applications", "page_numbers": [1]}
        ]
        
        classification, clarification = pipeline.classify_question("What is the abstract about?", retrieved_chunks)
        
        assert classification == "CLEAR"
    
    @patch('rag_pipeline.genai')
    def test_insufficient_evidence_no_hallucination(self, mock_genai):
        """Test that questions with insufficient evidence don't produce unsupported answers."""
        pipeline = RAGPipeline()
        
        # Mock Gemini response for classification
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "CLASSIFICATION: INSUFFICIENT_EVIDENCE\nCLARIFICATION: The paper does not contain information about quantum computing applications."
        mock_client.models.generate_content.return_value = mock_response
        pipeline.gemini_model = mock_client
        
        retrieved_chunks = [
            {"text": "This paper discusses classical machine learning", "page_numbers": [1]}
        ]
        
        classification, clarification = pipeline.classify_question(
            "What quantum computing applications are mentioned?", 
            retrieved_chunks
        )
        
        assert classification == "INSUFFICIENT_EVIDENCE"
        assert "quantum" in clarification.lower()
    
    @patch('rag_pipeline.SentenceTransformer')
    def test_new_document_clears_previous_index(self, mock_transformer):
        """Test that a new document does not reuse the previous document's index."""
        pipeline = RAGPipeline()
        
        # Mock the embedding model
        mock_model = Mock()
        mock_model.encode.return_value = np.random.rand(3, 384).astype('float32')
        mock_transformer.return_value = mock_model
        
        # Create first index
        chunk_data_1 = [
            {"text": "Document 1 chunk 1", "page_numbers": [1]},
            {"text": "Document 1 chunk 2", "page_numbers": [2]},
            {"text": "Document 1 chunk 3", "page_numbers": [3]}
        ]
        pipeline.create_vector_index(chunk_data_1)
        
        first_chunk_count = len(pipeline.chunks)
        
        # Clear and create new index
        pipeline.clear_index()
        
        chunk_data_2 = [
            {"text": "Document 2 chunk 1", "page_numbers": [1]},
            {"text": "Document 2 chunk 2", "page_numbers": [2]}
        ]
        pipeline.create_vector_index(chunk_data_2)
        
        assert len(pipeline.chunks) == 2
        assert len(pipeline.chunks) != first_chunk_count
        assert "Document 2" in pipeline.chunks[0]
    
    def test_invalid_pdf_handling(self):
        """Test that invalid PDFs are handled gracefully."""
        processor = PDFProcessor()
        
        # Test with non-existent file
        pages, error = processor.extract_pdf_text("nonexistent.pdf")
        
        assert len(pages) == 0
        assert len(error) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
