# # main.py
# from keywords_metadata import UnifiedKeywordExtractor as KeywordExtractor
# import json
# from grobid_metadata import GrobidExtractor
# import json
# from ner_metadata import NerExtractor

# def main():
#     # extractor = KeywordExtractor()
#     folder = r"D:\\Gomathi_ai\\Dataset\\Dataset\\Amit Saxena"

#     print(" Reading and extracting keywords from PDFs...")
#     # result = extractor.extract_from_pdf_folder(folder)

#     # # Save JSON output
#     # out_file = "amit_saxena_results.json"
#     # with open(out_file, "w", encoding="utf-8") as f:
#     #     json.dump(result, f, indent=2, ensure_ascii=False)

#     # print(f" Extraction complete. Results saved to {out_file}")

#     extractor = GrobidExtractor()
#     folder = r"D:\Gomathi_ai\Dataset\Dataset\Amit Saxena"
#     result2 = extractor.extract_pdfs_in_folder(folder)


#     # Save JSON output
#     with open("amit_saxena_results_grobid.json", "w", encoding="utf-8") as f:
#         json.dump(result2, f, indent=2, ensure_ascii=False)
#     print(" Extraction complete. Results saved to amit_saxena_results.json")

#         # Save NER/domain terms to JSON
#     extractor3 = GrobidExtractor()
#     ner_result = extractor3.extract_ner_for_folder(folder)
#     ner_out_file = "amit_saxena_ner.json"
#     with open(ner_out_file, "w", encoding="utf-8") as f:
#         json.dump(ner_result, f, indent=2, ensure_ascii=False)
#     print(f"NER extraction complete. Results saved to {ner_out_file}")

# if __name__ == "__main__":
#     main()



import os
import json
import numpy as np
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import PyPDF2
from collections import Counter
import re
from typing import Optional, List, Tuple, Dict


class ReviewerRecommendationSystem:
    """
    Hybrid scoring system combining:
    1. TF-IDF + Cosine Similarity (Lexical matching)
    2. Sentence-BERT embeddings (Semantic similarity)
    """
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.authors_data = {}
        self.semantic_model = None
        print("Initializing Reviewer Recommendation System...")
        
    def load_semantic_model(self):
        """Load sentence transformer model for semantic similarity"""
        if self.semantic_model is None:
            print("Loading Sentence-BERT model...")
            self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("     Model loaded successfully")
    
    def load_authors_data(self) -> Dict:
        """Load all author metadata and analysis results"""
        print(f"\nLoading authors data from {self.output_dir}...")
        
        files = os.listdir(self.output_dir)
        grobid_files = [f for f in files if f.endswith('_grobid_metadata.json')]
        analysis_files = [f for f in files if f.endswith('_analysis.json')]
        
        for grobid_file in grobid_files:
            author_name = grobid_file.replace('_grobid_metadata.json', '')
            analysis_file = f"{author_name}_analysis.json"
            
            try:
                # Load GROBID metadata
                with open(os.path.join(self.output_dir, grobid_file), 'r', encoding='utf-8') as f:
                    grobid_data = json.load(f)
                
                # Load analysis data
                analysis_data = {}
                if analysis_file in analysis_files:
                    with open(os.path.join(self.output_dir, analysis_file), 'r', encoding='utf-8') as f:
                        analysis_data = json.load(f)
                
                # Combine into author profile
                self.authors_data[author_name] = {
                    'grobid': grobid_data,
                    'ner': analysis_data.get('ner', {}),
                    'keywords': analysis_data.get('keywords', {}),
                    'topics': analysis_data.get('topics', {}),
                    'combined_text': self._build_author_text(grobid_data, analysis_data)
                }
                
                print(f"       Loaded: {author_name}")
            except Exception as e:
                print(f"      Failed to load {author_name}: {e}")
        
        print(f"\n     Loaded {len(self.authors_data)} authors")
        return self.authors_data
    
    def _build_author_text(self, grobid_data: Dict, analysis_data: Dict) -> str:
        """Build comprehensive text representation of author's work"""
        text_parts = []
        
        # Extract titles and abstracts from papers
        for paper_data in grobid_data.values():
            if paper_data.get('title'):
                text_parts.append(paper_data['title'])
            if paper_data.get('abstract'):
                text_parts.append(paper_data['abstract'])
            if paper_data.get('keywords'):
                text_parts.extend(paper_data['keywords'])
        
        # Add extracted keywords
        keywords = analysis_data.get('keywords', {})
        if isinstance(keywords, dict):
            if 'yake_keywords' in keywords:
                text_parts.extend([kw[0] for kw in keywords['yake_keywords']])
            if 'tfidf_keywords' in keywords:
                text_parts.extend([kw[0] for kw in keywords['tfidf_keywords']])
        
        # Add NER entities
        ner = analysis_data.get('ner', {})
        if isinstance(ner, dict):
            for entity_list in ner.values():
                if isinstance(entity_list, list):
                    text_parts.extend(entity_list)
        
        # Add topics
        topics = analysis_data.get('topics', {})
        if isinstance(topics, dict) and 'lda_topics' in topics:
            for topic in topics['lda_topics']:
                if isinstance(topic, dict) and 'words' in topic:
                    text_parts.extend(topic['words'])
        
        return ' '.join(text_parts)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from candidate PDF"""
        print(f"\nExtracting text from candidate paper: {pdf_path}")
        text = ""
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            
            # Clean text
            text = re.sub(r'\s+', ' ', text).strip()
            print(f"     Extracted {len(text)} characters")
            return text
        except Exception as e:
            print(f"     Error extracting text: {e}")
            return ""
    
    def compute_tfidf_similarity(self, candidate_text: str, authors_texts: Dict[str, str]) -> Dict[str, float]:
        """Compute TF-IDF cosine similarity scores"""
        print("\nComputing TF-IDF similarity scores...")
        
        # Prepare documents
        author_names = list(authors_texts.keys())
        documents = [candidate_text] + [authors_texts[name] for name in author_names]
        
        # Compute TF-IDF
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(documents)
            
            # Compute cosine similarity
            candidate_vector = tfidf_matrix[0:1]
            author_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(candidate_vector, author_vectors)[0]
            
            scores = {author_names[i]: float(similarities[i]) for i in range(len(author_names))}
            print(f"     Computed TF-IDF scores for {len(scores)} authors")
            return scores
        except Exception as e:
            print(f"    TF-IDF computation failed: {e}")
            return {name: 0.0 for name in author_names}
    
    def compute_semantic_similarity(self, candidate_text: str, authors_texts: Dict[str, str]) -> Dict[str, float]:
        """Compute semantic similarity using Sentence-BERT"""
        print("\nComputing semantic similarity scores...")
        
        if self.semantic_model is None:
            self.load_semantic_model()
        
        try:
            # Encode candidate paper
            candidate_embedding = self.semantic_model.encode(candidate_text, convert_to_tensor=False)
            
            # Encode author texts
            author_names = list(authors_texts.keys())
            author_texts = [authors_texts[name] for name in author_names]
            author_embeddings = self.semantic_model.encode(author_texts, convert_to_tensor=False)
            
            # Compute cosine similarity
            similarities = cosine_similarity([candidate_embedding], author_embeddings)[0]
            
            scores = {author_names[i]: float(similarities[i]) for i in range(len(author_names))}
            print(f"     Computed semantic scores for {len(scores)} authors")
            return scores
        except Exception as e:
            print(f"    Semantic similarity computation failed: {e}")
            return {name: 0.0 for name in author_names}
    
    def compute_hybrid_scores(
        self,
        candidate_text: str,
        tfidf_weight: float = 0.4,
        semantic_weight: float = 0.6
    ) -> List[Tuple[str, Dict]]:
        """
        Compute weighted hybrid scores combining lexical and semantic similarity
        
        Args:
            candidate_text: Text from candidate paper
            tfidf_weight: Weight for TF-IDF scores (lexical)
            semantic_weight: Weight for semantic scores
        
        Returns:
            List of (author_name, scores_dict) sorted by hybrid score
        """
        print(f"\n{'='*60}")
        print("Computing Hybrid Reviewer Scores")
        print(f"TF-IDF weight: {tfidf_weight}, Semantic weight: {semantic_weight}")
        print(f"{'='*60}")
        
        # Build author text representations
        authors_texts = {
            name: data['combined_text']
            for name, data in self.authors_data.items()
        }
        
        # Compute both similarity scores
        tfidf_scores = self.compute_tfidf_similarity(candidate_text, authors_texts)
        semantic_scores = self.compute_semantic_similarity(candidate_text, authors_texts)
        
        # Combine scores
        print("\nComputing weighted hybrid scores...")
        hybrid_results = []
        
        for author_name in self.authors_data.keys():
            tfidf_score = tfidf_scores.get(author_name, 0.0)
            semantic_score = semantic_scores.get(author_name, 0.0)
            
            # Weighted combination
            hybrid_score = (tfidf_weight * tfidf_score) + (semantic_weight * semantic_score)
            
            hybrid_results.append((
                author_name,
                {
                    'tfidf_score': round(tfidf_score, 4),
                    'semantic_score': round(semantic_score, 4),
                    'hybrid_score': round(hybrid_score, 4),
                    'paper_count': len(self.authors_data[author_name]['grobid']),
                    'keywords': self._get_top_keywords(author_name, n=5)
                }
            ))
        
        # Sort by hybrid score
        hybrid_results.sort(key=lambda x: x[1]['hybrid_score'], reverse=True)
        
        print(f"     Computed hybrid scores for {len(hybrid_results)} authors")
        return hybrid_results
    
    def _get_top_keywords(self, author_name: str, n: int = 5) -> List[str]:
        """Extract top keywords for an author"""
        keywords_data = self.authors_data[author_name].get('keywords', {})
        keywords = []
        
        if isinstance(keywords_data, dict):
            if 'yake_keywords' in keywords_data:
                keywords.extend([kw[0] for kw in keywords_data['yake_keywords'][:n]])
            elif 'tfidf_keywords' in keywords_data:
                keywords.extend([kw[0] for kw in keywords_data['tfidf_keywords'][:n]])
        
        return keywords[:n]
    
    def get_top_reviewers(
            self,
            candidate_pdf: Optional[str] = None,
            candidate_text: Optional[str] = None,
            k: int = 10,
            tfidf_weight: float = 0.4,
            semantic_weight: float = 0.6
        ) -> List[Tuple[str, Dict]]:
        """
        Get top-k reviewer recommendations for a candidate paper

        Either candidate_pdf or candidate_text must be provided.
        """
        if candidate_text is None:
            if candidate_pdf is None:
                raise ValueError("Either candidate_pdf or candidate_text must be provided")
            candidate_text = self.extract_text_from_pdf(candidate_pdf)

        if not candidate_text:
            print("     Failed to extract text from candidate paper")
            return []

        # Compute hybrid scores
        all_scores = self.compute_hybrid_scores(
            candidate_text,
            tfidf_weight=tfidf_weight,
            semantic_weight=semantic_weight
        )

        # Return top-k
        top_k = all_scores[:k]

        print(f"\n{'='*60}")
        print(f"Top {k} Recommended Reviewers")
        print(f"{'='*60}")
        for i, (author, scores) in enumerate(top_k, 1):
            print(f"{i}. {author}")
            print(f"   Hybrid Score: {scores['hybrid_score']:.4f}")
            print(f"   TF-IDF: {scores['tfidf_score']:.4f} | Semantic: {scores['semantic_score']:.4f}")
            print(f"   Papers: {scores['paper_count']} | Keywords: {', '.join(scores['keywords'])}")
            print()

        return top_k

    
    def save_recommendations(self, recommendations: List[Tuple[str, Dict]], output_file: str):
        """Save recommendations to JSON file"""
        output_data = {
            'recommendations': [
                {
                    'rank': i + 1,
                    'author': author,
                    'scores': scores
                }
                for i, (author, scores) in enumerate(recommendations)
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"     Recommendations saved to {output_file}")


def main():
    """Main function for reviewer recommendation"""
    # Initialize system
    recommender = ReviewerRecommendationSystem(output_dir="output")
    
    # Load authors data
    recommender.load_authors_data()
    
    # Get recommendations for candidate paper
    candidate_pdf = "candidate_paper.pdf"  # Replace with actual path
    
    if os.path.exists(candidate_pdf):
        top_reviewers = recommender.get_top_reviewers(
            candidate_pdf=candidate_pdf,
            k=10,
            tfidf_weight=0.4,
            semantic_weight=0.6
        )
        
        # Save recommendations
        recommender.save_recommendations(
            top_reviewers,
            output_file="reviewer_recommendations.json"
        )
    else:
        print(f"     Candidate paper not found: {candidate_pdf}")


if __name__ == "__main__":
    main()

