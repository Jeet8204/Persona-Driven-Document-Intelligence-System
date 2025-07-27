
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .embedding import EmbeddingModel

class RankingEngine:
    """
    Ranks text using a weighted score and then re-ranks using Maximal Marginal Relevance (MMR)
    to ensure relevance and diversity in the final output.
    """
    def __init__(self, model_path: str):
        self.embedding_model = EmbeddingModel(model_path)

    def _apply_mmr(self, query_embedding, doc_embeddings, docs, top_k=5, lambda_val=0.7):
        """
        Applies Maximal Marginal Relevance to a list of documents.

        Args:
            query_embedding: The embedding of the user's query.
            doc_embeddings: Embeddings of the candidate documents.
            docs: The list of candidate document dictionaries.
            top_k: The number of documents to return.
            lambda_val: Controls diversity (0.0) vs. relevance (1.0).

        Returns:
            A re-ranked list of documents based on MMR.
        """
        if not docs or len(docs) <= top_k:
            return docs

        # Calculate initial relevance scores
        relevance_scores = cosine_similarity(query_embedding, doc_embeddings)[0]
        
        selected_indices = []
        remaining_indices = list(range(len(docs)))

        # Select the most relevant document first
        first_selection_idx = np.argmax(relevance_scores)
        selected_indices.append(first_selection_idx)
        remaining_indices.remove(first_selection_idx)

        # Iteratively select the rest based on MMR
        while len(selected_indices) < top_k and remaining_indices:
            mmr_scores = {}
            selected_embeddings = doc_embeddings[selected_indices]

            for idx in remaining_indices:
                relevance = relevance_scores[idx]
                # Calculate max similarity to already selected items
                similarity_to_selected = cosine_similarity(doc_embeddings[idx].reshape(1, -1), selected_embeddings)
                max_sim = np.max(similarity_to_selected) if similarity_to_selected.size > 0 else 0
                
                # MMR Formula
                mmr_score = lambda_val * relevance - (1 - lambda_val) * max_sim
                mmr_scores[idx] = mmr_score
            
            # Select the best candidate
            best_idx = max(mmr_scores, key=mmr_scores.get)
            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)
            
        return [docs[i] for i in selected_indices]


    def rank(self, query: str, extracted_data: list):
        if not extracted_data:
            return [], []

        query_embedding = self.embedding_model.get_embeddings(query)

        sections = [d for d in extracted_data if d.get('text')]
        subsections = [sub for d in extracted_data for sub in d.get('subsections', []) if sub.get('text')]

        # --- Initial Ranking (Weighted for Sections) ---
        # This part remains the same to get a good candidate pool.
        if sections:
            title_weight, content_weight = 0.6, 0.4
            section_titles = [s.get('section_title', '') for s in sections]
            section_contents = [s['text'] for s in sections]
            title_embeddings = self.embedding_model.get_embeddings(section_titles)
            content_embeddings = self.embedding_model.get_embeddings(section_contents)
            title_sims = cosine_similarity(query_embedding, title_embeddings)[0]
            content_sims = cosine_similarity(query_embedding, content_embeddings)[0]
            for i, section in enumerate(sections):
                section['score'] = (title_sims[i] * title_weight) + (content_sims[i] * content_weight)
                section['embedding'] = content_embeddings[i] # Store embedding for MMR
            ranked_sections_sorted = sorted(sections, key=lambda x: x['score'], reverse=True)
        else:
            ranked_sections_sorted = []
        
        # --- Subsection Initial Ranking ---
        if subsections:
            subsection_texts = [s['text'] for s in subsections]
            subsection_embeddings = self.embedding_model.get_embeddings(subsection_texts)
            subsection_sims = cosine_similarity(query_embedding, subsection_embeddings)[0]
            for i, sub in enumerate(subsections):
                sub['similarity'] = subsection_sims[i]
                sub['embedding'] = subsection_embeddings[i] # Store embedding for MMR
            ranked_subsections_sorted = sorted(subsections, key=lambda x: x['similarity'], reverse=True)
        else:
            ranked_subsections_sorted = []
        
        # --- NEW: Re-rank the top candidates using MMR for diversity ---
        # We take a larger pool of candidates (e.g., top 25) for MMR to choose from.
        candidate_sections = ranked_sections_sorted[:25]
        candidate_subsections = ranked_subsections_sorted[:25]

        # Apply MMR to sections
        if candidate_sections:
            section_embeddings_pool = np.array([s['embedding'] for s in candidate_sections])
            diversified_sections = self._apply_mmr(query_embedding, section_embeddings_pool, candidate_sections)
        else:
            diversified_sections = []

        # Apply MMR to subsections
        if candidate_subsections:
            subsection_embeddings_pool = np.array([s['embedding'] for s in candidate_subsections])
            diversified_subsections = self._apply_mmr(query_embedding, subsection_embeddings_pool, candidate_subsections)
        else:
            diversified_subsections = []

        # Format final output with the diversified lists
        final_ranked_sections = [
            {
                "document": s['filename'],
                "page_number": s['page_number'],
                "section_title": s['section_title'],
                "importance_rank": i + 1,
            } for i, s in enumerate(diversified_sections)
        ]

        final_ranked_subsections = [
            {
                "document": sub.get('filename'),
                "refined_text": sub['text'],
                "page_number_constraints": [sub['page_number']],
            } for i, sub in enumerate(diversified_subsections)
        ]
        
        return final_ranked_sections, final_ranked_subsections