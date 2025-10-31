# import os
# import fitz  # PyMuPDF
# import re
# import logging
# import numpy as np
# from typing import Dict, List
# from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
# from sklearn.decomposition import LatentDirichletAllocation, NMF

# # ------------------------- #
# # Logging setup
# # ------------------------- #
# logging.basicConfig(
#     filename='topic_extraction.log',
#     filemode='a',
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

# # ------------------------- #
# # Utility Functions
# # ------------------------- #

# def extract_text_from_pdf(pdf_path: str) -> str:
#     """Extract plain text from a PDF file using PyMuPDF."""
#     try:
#         text = ""
#         with fitz.open(pdf_path) as doc:
#             for page in doc:
#                 text += page.get_text("text")
#         text = re.sub(r'\s+', ' ', text).strip()
#         return text
#     except Exception as e:
#         logging.error(f"Failed to extract text from {pdf_path}: {e}")
#         return ""


# def load_author_corpus(base_folder: str) -> Dict[str, List[str]]:
#     """
#     Load all PDFs for each author in the dataset.
#     Each folder inside base_folder corresponds to an author name.
#     Returns {author_name: [concatenated_text_of_papers]}.
#     """
#     author_corpus = {}
#     for author_name in os.listdir(base_folder):
#         author_path = os.path.join(base_folder, author_name)
#         if not os.path.isdir(author_path):
#             continue
        
#         author_texts = []
#         for file in os.listdir(author_path):
#             if file.lower().endswith('.pdf'):
#                 pdf_path = os.path.join(author_path, file)
#                 text = extract_text_from_pdf(pdf_path)
#                 if len(text.split()) > 50:  # ensure non-trivial doc
#                     author_texts.append(text)
#                 else:
#                     logging.warning(f"File too short or empty: {pdf_path}")

#         # Combine all texts if multiple, handle single-doc case
#         if author_texts:
#             combined_text = " ".join(author_texts)
#             author_corpus[author_name] = combined_text
#         else:
#             logging.warning(f"No valid documents found for {author_name}")

#     if not author_corpus:
#         logging.error("No valid author documents found in dataset folder.")
#     return author_corpus


# def preprocess_text(text: str) -> str:
#     """Basic preprocessing for reliability."""
#     text = text.lower()
#     text = re.sub(r'[^a-z0-9\s]', ' ', text)
#     text = re.sub(r'\s+', ' ', text).strip()
#     return text


# # ------------------------- #
# # Topic Extraction Functions
# # ------------------------- #

# def extract_topics(text: str, n_topics: int = 10, n_words: int = 10) -> Dict:
#     """Extract topics using LDA and NMF with reliability and error handling."""
#     if not text or len(text.split()) < 30:
#         logging.warning("Text too short for topic modeling.")
#         return {'lda': [], 'nmf': []}

#     text = preprocess_text(text)
#     topics = {}

#     try:
#         topics['lda'] = extract_lda_topics(text, n_topics, n_words)
#     except Exception as e:
#         logging.error(f"LDA extraction failed: {e}")
#         topics['lda'] = []

#     try:
#         topics['nmf'] = extract_nmf_topics(text, n_topics, n_words)
#     except Exception as e:
#         logging.error(f"NMF extraction failed: {e}")
#         topics['nmf'] = []

#     return topics


# def extract_lda_topics(text: str, n_topics: int = 10, n_words: int = 10) -> List[Dict]:
#     """Latent Dirichlet Allocation topic modeling with safety checks."""
#     vectorizer = CountVectorizer(
#         max_features=2000,
#         stop_words='english',
#         min_df=2,
#         max_df=0.95
#     )

#     docs = [text]
#     doc_term_matrix = vectorizer.fit_transform(docs)
#     if doc_term_matrix.shape[1] < 10:
#         logging.warning("Too few unique terms for LDA.")
#         return []

#     lda = LatentDirichletAllocation(
#         n_components=min(n_topics, doc_term_matrix.shape[1]),
#         random_state=42,
#         max_iter=30
#     )
#     lda.fit(doc_term_matrix)

#     feature_names = vectorizer.get_feature_names_out()
#     topics = []
#     doc_topic_dist = lda.transform(doc_term_matrix)[0]

#     for topic_idx, topic in enumerate(lda.components_):
#         top_indices = topic.argsort()[-n_words:][::-1]
#         top_words = [feature_names[i] for i in top_indices]
#         top_scores = [float(topic[i]) for i in top_indices]
#         topics.append({
#             'topic_id': topic_idx,
#             'words': top_words,
#             'scores': top_scores,
#             'document_weight': float(doc_topic_dist[topic_idx])
#         })

#     return topics


# def extract_nmf_topics(text: str, n_topics: int = 10, n_words: int = 10) -> List[Dict]:
#     """Non-negative Matrix Factorization topic modeling with reliability."""
#     vectorizer = TfidfVectorizer(
#         max_features=2000,
#         stop_words='english',
#         min_df=2,
#         max_df=0.95
#     )

#     docs = [text]
#     tfidf_matrix = vectorizer.fit_transform(docs)
#     if tfidf_matrix.shape[1] < 10:
#         logging.warning("Too few unique terms for NMF.")
#         return []

#     nmf = NMF(
#         n_components=min(n_topics, tfidf_matrix.shape[1]),
#         random_state=42,
#         max_iter=300
#     )
#     W = nmf.fit_transform(tfidf_matrix)

#     feature_names = vectorizer.get_feature_names_out()
#     topics = []

#     for topic_idx, topic in enumerate(nmf.components_):
#         top_indices = topic.argsort()[-n_words:][::-1]
#         top_words = [feature_names[i] for i in top_indices]
#         top_scores = [float(topic[i]) for i in top_indices]
#         topics.append({
#             'topic_id': topic_idx,
#             'words': top_words,
#             'scores': top_scores,
#             'document_weight': float(W[0][topic_idx])
#         })

#     return topics

# topic_extractor.py
import re
import logging
from typing import Dict, List
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF

# Logging setup
logging.basicConfig(
    filename='topic_extraction.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def preprocess_text(text: str) -> str:
    """Basic preprocessing for topic modeling."""
    if not text:
        return ""
    
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_topics(text: str, n_topics: int = 10, n_words: int = 10) -> Dict:
    """
    Extract topics using LDA and NMF.
    Works with pre-extracted text from GROBID pipeline.
    """
    if not text or len(text.split()) < 30:
        logging.warning("Text too short for topic modeling")
        return {'lda': [], 'nmf': []}

    text = preprocess_text(text)
    topics = {}

    try:
        topics['lda'] = extract_lda_topics(text, n_topics, n_words)
        logging.info(f" LDA extraction complete: {len(topics['lda'])} topics")
    except Exception as e:
        logging.error(f"LDA extraction failed: {e}")
        topics['lda'] = []

    try:
        topics['nmf'] = extract_nmf_topics(text, n_topics, n_words)
        logging.info(f" NMF extraction complete: {len(topics['nmf'])} topics")
    except Exception as e:
        logging.error(f"NMF extraction failed: {e}")
        topics['nmf'] = []

    return topics


def extract_lda_topics(text: str, n_topics: int = 10, n_words: int = 10) -> List[Dict]:
    """Latent Dirichlet Allocation topic modeling."""
    vectorizer = CountVectorizer(
        max_features=2000,
        stop_words='english',
        min_df=2,
        max_df=0.95
    )

    docs = [text]
    doc_term_matrix = vectorizer.fit_transform(docs)
    
    if doc_term_matrix.shape[1] < 10:
        logging.warning("Too few unique terms for LDA")
        return []

    # Adjust n_topics to not exceed vocabulary size
    actual_n_topics = min(n_topics, doc_term_matrix.shape[1])
    
    lda = LatentDirichletAllocation(
        n_components=actual_n_topics,
        random_state=42,
        max_iter=30
    )
    lda.fit(doc_term_matrix)

    feature_names = vectorizer.get_feature_names_out()
    topics = []
    doc_topic_dist = lda.transform(doc_term_matrix)[0]

    for topic_idx, topic in enumerate(lda.components_):
        top_indices = topic.argsort()[-n_words:][::-1]
        top_words = [feature_names[i] for i in top_indices]
        top_scores = [float(topic[i]) for i in top_indices]
        
        topics.append({
            'topic_id': topic_idx,
            'words': top_words,
            'scores': top_scores,
            'document_weight': float(doc_topic_dist[topic_idx])
        })

    return topics


def extract_nmf_topics(text: str, n_topics: int = 10, n_words: int = 10) -> List[Dict]:
    """Non-negative Matrix Factorization topic modeling."""
    vectorizer = TfidfVectorizer(
        max_features=2000,
        stop_words='english',
        min_df=2,
        max_df=0.95
    )

    docs = [text]
    tfidf_matrix = vectorizer.fit_transform(docs)
    
    if tfidf_matrix.shape[1] < 10:
        logging.warning("Too few unique terms for NMF")
        return []

    # Adjust n_topics to not exceed vocabulary size
    actual_n_topics = min(n_topics, tfidf_matrix.shape[1])
    
    nmf = NMF(
        n_components=actual_n_topics,
        random_state=42,
        max_iter=300
    )
    W = nmf.fit_transform(tfidf_matrix)

    feature_names = vectorizer.get_feature_names_out()
    topics = []

    for topic_idx, topic in enumerate(nmf.components_):
        top_indices = topic.argsort()[-n_words:][::-1]
        top_words = [feature_names[i] for i in top_indices]
        top_scores = [float(topic[i]) for i in top_indices]
        
        topics.append({
            'topic_id': topic_idx,
            'words': top_words,
            'scores': top_scores,
            'document_weight': float(W[0][topic_idx])
        })

    return topics