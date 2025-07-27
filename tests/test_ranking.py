import unittest
from unittest.mock import patch
import numpy as np

from app.ranking.engine import RankingEngine

class TestRankingEngine(unittest.TestCase):

    def setUp(self):
        """Set up reusable sample data for tests."""
        self.sample_extracted_data = [
            {
                'filename': 'doc1.pdf', 'page_number': 1, 'section_title': 'About Apples',
                'text': 'This text is about apples.', 'subsections': []
            },
            {
                'filename': 'doc2.pdf', 'page_number': 5, 'section_title': 'About GNN',
                'text': 'This text is about graph neural networks.',
                'subsections': [
                    {'text': 'GNN performance benchmarks are key.', 'page_number': 5},
                    {'text': 'Irrelevant subsection about bananas.', 'page_number': 5}
                ]
            }
        ]
        self.sample_query = "performance benchmarks for graph neural networks"

    @patch('app.ranking.engine.EmbeddingModel')
    def test_rank_sorts_correctly(self, MockEmbeddingModel):
        """Tests if the rank method correctly sorts based on mock similarity scores."""
        # --- Arrange ---
        mock_model_instance = MockEmbeddingModel.return_value
        query_embedding = np.array([[1, 0, 0]])
        section_embeddings = np.array([[0, 1, 0], [1, 0, 0]])
        subsection_embeddings = np.array([[1, 0, 0], [0, 0, 1]])

        mock_model_instance.get_embeddings.side_effect = [
            query_embedding, section_embeddings, subsection_embeddings
        ]
        
        # --- Act ---
        ranking_engine = RankingEngine(model_path="/fake/path")
        ranked_sections, ranked_subsections = ranking_engine.rank(self.sample_query, self.sample_extracted_data)

        # --- Assert ---
        self.assertEqual(len(ranked_sections), 2)
        self.assertEqual(len(ranked_subsections), 2)

        # Check section ranking
        self.assertEqual(ranked_sections[0]['section_title'], 'About GNN')
        self.assertEqual(ranked_sections[0]['importance_rank'], 1)
        self.assertAlmostEqual(ranked_sections[0]['similarity'], 1.0)

        # Check subsection ranking
        self.assertEqual(ranked_subsections[0]['refined_text'], 'GNN performance benchmarks are key.')
        self.assertEqual(ranked_subsections[0]['importance_rank'], 1)

    @patch('app.ranking.engine.EmbeddingModel')
    def test_rank_with_empty_input(self, MockEmbeddingModel):
        """Tests if the rank method handles empty input gracefully."""
        ranking_engine = RankingEngine(model_path="/fake/path")
        ranked_sections, ranked_subsections = ranking_engine.rank(self.sample_query, [])
        self.assertEqual(ranked_sections, [])
        self.assertEqual(ranked_subsections, [])

if __name__ == '__main__':
    unittest.main()