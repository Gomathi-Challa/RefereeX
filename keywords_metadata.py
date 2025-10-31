# # # # keyword_metadata.py
# # # import os
# # # import re
# # # from typing import Dict, List
# # # import numpy as np

# # # # ============================================================
# # # # 🔧 Unified Keyword Extraction Controller
# # # # ============================================================

# # # def extract_keywords_all_methods(text: str, top_n: int = 20, log_errors: bool = True) -> Dict:
# # #     """
# # #     Extracts keywords using multiple methods (RAKE, KeyBERT),
# # #     with preprocessing, logging, and reliability handling.
# # #     """
# # #     results = {}
# # #     text = preprocess_text(text)  # Unified preprocessing

# # #     methods = {
# # #         'rake': extract_rake_keywords,
# # #         'keybert': extract_keybert_keywords
# # #     }

# # #     for method, func in methods.items():
# # #         try:
# # #             results[method] = func(text, top_n)
# # #         except Exception as e:
# # #             if log_errors:
# # #                 print(f"[ERROR] {method} failed: {e}")
# # #             results[method] = []
# # #     return results


# # # # ============================================================
# # # # ⚙️ RAKE Keyword Extraction
# # # # ============================================================

# # # def extract_rake_keywords(text: str, top_n: int = 20) -> List[Dict]:
# # #     """Extract keywords using RAKE (Rapid Automatic Keyword Extraction)."""
# # #     try:
# # #         from rake_nltk import Rake
# # #         domain_stopwords = [
# # #             'et', 'al', 'figure', 'table', 'dataset', 'result', 'results',
# # #             'data', 'experiment', 'paper', 'section', 'algorithm', 'model',
# # #             'introduction', 'conclusion', 'method', 'approach', 'based'
# # #         ]
# # #         rake = Rake(stopwords=domain_stopwords)
# # #         rake.extract_keywords_from_text(text)
# # #         ranked = rake.get_ranked_phrases_with_scores()

# # #         return [{'keyword': phrase, 'score': float(score)}
# # #                 for score, phrase in ranked[:top_n]]

# # #     except ImportError:
# # #         print(" RAKE not installed. Install it via: pip install rake-nltk")
# # #         return []
# # #     except Exception as e:
# # #         print(f"[ERROR] RAKE extraction failed: {e}")
# # #         return []


# # # # ============================================================
# # # # 💡 KeyBERT Keyword Extraction
# # # # ============================================================

# # # def extract_keybert_keywords(text: str, top_n: int = 20) -> List[Dict]:
# # #     """Extract keywords using KeyBERT with semantic embeddings."""
# # #     try:
# # #         from keybert import KeyBERT
# # #         kw_model = KeyBERT(model='all-MiniLM-L6-v2')

# # #         # Handle long text by chunking
# # #         chunks = split_text(text, max_words=512)
# # #         keywords = []

# # #         for chunk in chunks:
# # #             chunk_keywords = kw_model.extract_keywords(
# # #                 chunk,
# # #                 keyphrase_ngram_range=(1, 3),
# # #                 stop_words='english',
# # #                 top_n=top_n
# # #             )
# # #             keywords.extend(chunk_keywords)

# # #         # Deduplicate and average scores
# # #         keyword_scores = {}
# # #         for kw, score in keywords:
# # #             if kw not in keyword_scores:
# # #                 keyword_scores[kw] = []
# # #             keyword_scores[kw].append(score)

# # #         avg_keywords = [
# # #             {'keyword': kw, 'score': float(np.mean(scores))}
# # #             for kw, scores in keyword_scores.items()
# # #         ]

# # #         avg_keywords.sort(key=lambda x: x['score'], reverse=True)
# # #         return avg_keywords[:top_n]

# # #     except ImportError:
# # #         print(" KeyBERT not installed. Install it via: pip install keybert")
# # #         return []
# # #     except Exception as e:
# # #         print(f"[ERROR] KeyBERT extraction failed: {e}")
# # #         return []


# # # # ============================================================
# # # # 🧹 Academic Text Preprocessing
# # # # ============================================================

# # # def preprocess_text(text: str) -> str:
# # #     """Clean and normalize academic text for keyword extraction."""
# # #     if not text or not isinstance(text, str):
# # #         return ""

# # #     # --- Text extraction cleaning ---
# # #     text = text.replace('\n', ' ')
# # #     text = re.sub(r'-\s+', '', text)  # remove hyphenation
# # #     text = re.sub(r'\s+', ' ', text)
# # #     text = text.encode('utf-8', 'ignore').decode('utf-8', 'ignore')

# # #     # --- Remove citations, equations, and numbers ---
# # #     text = re.sub(r'\[[0-9,\s]+\]', ' ', text)                 # [1], [2,3]
# # #     text = re.sub(r'\(.*?et al\.,?\s*\d{4}\)', ' ', text)      # (Smith et al., 2020)
# # #     text = re.sub(r'\d+', ' ', text)                           # numbers
# # #     text = re.sub(r'[^a-zA-Z\s]', ' ', text)                   # math symbols

# # #     # --- Remove structural & academic noise ---
# # #     text = re.sub(
# # #         r'\b(et al|figure|table|dataset|results?|section|appendix|references?|'
# # #         r'experiment|paper|methodology|approach|data|model|algorithm|conclusion)\b',
# # #         ' ', text, flags=re.I
# # #     )

# # #     # --- Normalize spacing and case ---
# # #     text = re.sub(r'\s+', ' ', text)
# # #     text = text.strip().lower()

# # #     return text


# # # # ============================================================
# # # # ✂️ Text Chunking for Long Documents
# # # # ============================================================

# # # def split_text(text: str, max_words: int = 512) -> List[str]:
# # #     """Split text into smaller chunks for large document processing."""
# # #     words = text.split()
# # #     if not words:
# # #         return []
# # #     return [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]


# # # # ============================================================
# # # # 👩‍🔬 Per-Author Keyword Extraction
# # # # ============================================================

# # # def extract_keywords_for_authors(base_folder: str, top_n: int = 20) -> Dict[str, Dict]:
# # #     """
# # #     Traverse a folder structure where each folder represents an author
# # #     containing one or more PDFs of their work.
    
# # #     Extracts aggregated keywords per author, with preprocessing and logging.
# # #     """
# # #     from PyPDF2 import PdfReader

# # #     author_keywords = {}

# # #     for author_name in os.listdir(base_folder):
# # #         author_path = os.path.join(base_folder, author_name)
# # #         if not os.path.isdir(author_path):
# # #             continue

# # #         author_texts = []

# # #         for file in os.listdir(author_path):
# # #             if file.lower().endswith(".pdf"):
# # #                 pdf_path = os.path.join(author_path, file)
# # #                 try:
# # #                     reader = PdfReader(pdf_path)
# # #                     text = " ".join(page.extract_text() or "" for page in reader.pages)
# # #                     author_texts.append(text)
# # #                 except Exception as e:
# # #                     print(f"[ERROR] Failed to read PDF {file} for {author_name}: {e}")

# # #         if not author_texts:
# # #             print(f"[WARNING] No valid documents found for {author_name}")
# # #             author_keywords[author_name] = {}
# # #             continue

# # #         if len(author_texts) == 1:
# # #             print(f" Only one paper found for {author_name} — results may be less representative.")

# # #         full_text = " ".join(author_texts)
# # #         preprocessed_text = preprocess_text(full_text)

# # #         if not preprocessed_text.strip():
# # #             print(f"[WARNING] Empty combined text after preprocessing for {author_name}")
# # #             author_keywords[author_name] = {}
# # #             continue

# # #         author_keywords[author_name] = extract_keywords_all_methods(preprocessed_text, top_n)

# # #     return author_keywords


# # import os
# # import re
# # import numpy as np
# # from typing import Dict, List, Optional

# # class UnifiedKeywordExtractor:
# #     def __init__(
# #         self, 
# #         keybert_model: str = "all-MiniLM-L6-v2",
# #         chunk_max_words: int = 512,
# #         chunk_overlap: int = 60,  # overlap so phrases aren't split
# #         min_score: float = 0.0
# #     ):
# #         self.keybert_model_name = keybert_model
# #         self.chunk_max_words = chunk_max_words
# #         self.chunk_overlap = chunk_overlap
# #         self.min_score = min_score

# #         self.domain_stopwords = {
# #             'et', 'al', 'figure', 'table', 'dataset', 'result', 'results',
# #             'data', 'experiment', 'paper', 'section', 'algorithm', 'model',
# #             'introduction', 'conclusion', 'method', 'approach', 'based'
# #         }

# #     # ============================================================
# #     # 🔧 Main Entry
# #     # ============================================================
# #     def extract_text_keywords(self, text: str, top_n: int = 20) -> Dict:
        


# #         text = self.preprocess_text(text)
# #         return {
# #             "rake": self.extract_rake(text, top_n),
# #             "keybert": self.extract_keybert(text, top_n)
# #         }

# #     # ============================================================
# #     # 📂 Folder → keywords per PDF
# #     # ============================================================
# #     def extract_from_pdf_folder(self, folder: str, top_n: int = 20) -> Dict:
# #         """
# #         Return JSON-like {filename: {rake:[], keybert:[]}}
# #         """
# #         from PyPDF2 import PdfReader

# #         results = {}
# #         for f in os.listdir(folder):
# #             if not f.lower().endswith(".pdf"):
# #                 continue

# #             try:
# #                 pdf_path = os.path.join(folder, f)
# #                 reader = PdfReader(pdf_path)
# #                 text = " ".join((page.extract_text() or "") for page in reader.pages)
# #                 results[f] = self.extract_text_keywords(text, top_n)
# #             except Exception as e:
# #                 print(f"[ERROR] PDF {f}: {e}")
# #                 results[f] = {"rake": [], "keybert": []}

# #         return results

# #     # ============================================================
# #     # 🧠 KeyBERT
# #     # ============================================================
# #     def extract_keybert(self, text: str, top_n: int = 20) -> List[Dict]:
# #         try:
# #             from keybert import KeyBERT
# #             kw_model = KeyBERT(model=self.keybert_model_name)
# #         except ImportError:
# #             print("Install KeyBERT: pip install keybert")
# #             return []

# #         chunks = self._chunk(text)

# #         all_kws = []
# #         for c in chunks:
# #             kws = kw_model.extract_keywords(
# #                 c,
# #                 keyphrase_ngram_range=(1, 3),
# #                 stop_words="english",  # ✅ user can override if needed
# #                 top_n=top_n
# #             )
# #             all_kws.extend(kws)

# #         # dedupe + mean score
# #         kw_scores = {}
# #         for kw, score in all_kws:
# #             if score < self.min_score:
# #                 continue
# #             kw_scores.setdefault(kw, []).append(score)

# #         averaged = [
# #             {"keyword": k, "score": float(np.mean(scores))}
# #             for k, scores in kw_scores.items()
# #         ]

# #         averaged.sort(key=lambda x: x["score"], reverse=True)
# #         return averaged[:top_n]

# #     # ============================================================
# #     # 🚀 RAKE
# #     # ============================================================
# #     def extract_rake(self, text: str, top_n: int = 20) -> List[Dict]:
# #         try:
# #             from rake_nltk import Rake
# #             from nltk.corpus import stopwords
# #         except ImportError:
# #             print("Install: pip install rake-nltk nltk")
# #             return []

# #         # combine RAKE + domain stopwords
# #         try:
# #             nltk_stop = set(stopwords.words("english"))
# #         except:
# #             nltk_stop = set()

# #         combined = list(nltk_stop.union(self.domain_stopwords))

# #         rake = Rake(
# #             stopwords=combined,
# #             min_length=1,   # avoid empty phrases
# #             max_length=4    # ✅ prevent very long RAKE phrases
# #         )
# #         rake.extract_keywords_from_text(text)
# #         ranked = rake.get_ranked_phrases_with_scores()

# #         return [
# #             {"keyword": p, "score": float(s)}
# #             for s, p in ranked[:top_n]
# #         ]

# #     # ============================================================
# #     # 🧹 Preprocess Academic Text
# #     # ============================================================
# #     def preprocess_text(self, text: str) -> str:
# #         if not isinstance(text, str):
# #             return ""

# #         text = text.replace('\n', ' ')
# #         text = re.sub(r'-\s+', '', text)
# #         text = re.sub(r'\s+', ' ', text)

# #         text = re.sub(r'\[[0-9,\s]+\]', ' ', text)
# #         text = re.sub(r'\(.*?et al\.,?\s*\d{4}\)', ' ', text)
# #         text = re.sub(r'\d+', ' ', text)
# #         text = re.sub(r'[^a-zA-Z\s]', ' ', text)

# #         text = re.sub(
# #             r'\b(et al|figure|table|dataset|results?|section|appendix|references?|'
# #             r'experiment|paper|methodology|approach|data|model|algorithm|conclusion)\b',
# #             ' ', text, flags=re.I
# #         )
# #         return re.sub(r'\s+', ' ', text).strip().lower()

# #     # ============================================================
# #     # ✂️ Chunk w/ overlap
# #     # ============================================================
# #     def _chunk(self, text: str) -> List[str]:
# #         words = text.split()
# #         if not words:
# #             return []

# #         step = self.chunk_max_words - self.chunk_overlap
# #         return [
# #             " ".join(words[i:i + self.chunk_max_words])
# #             for i in range(0, len(words), max(step, 1))
# #         ]

# import os
# import re
# import json
# import numpy as np
# from typing import Dict, List, Optional


# class UnifiedKeywordExtractor:
#     def __init__(
#         self,
#         keybert_model: str = "all-MiniLM-L6-v2",
#         chunk_max_words: int = 512,
#         chunk_overlap: int = 60,
#         min_score: float = 0.0,
#         log_file: Optional[str] = None
#     ):
#         self.keybert_model_name = keybert_model
#         self.chunk_max_words = chunk_max_words
#         self.chunk_overlap = chunk_overlap
#         self.min_score = min_score
#         self.log_file = log_file

#         self.domain_stopwords = {
#             'et', 'al', 'figure', 'table', 'dataset', 'result', 'results',
#             'data', 'experiment', 'paper', 'section', 'algorithm', 'model',
#             'introduction', 'conclusion', 'method', 'approach', 'based'
#         }

#     # -------------------------------------------------------------
#     # Helper logging function
#     # -------------------------------------------------------------
#     def log(self, message: str):
#         print(message)
#         if self.log_file:
#             with open(self.log_file, "a", encoding="utf-8") as f:
#                 f.write(message + "\n")

#     # -------------------------------------------------------------
#     # Main Entry
#     # -------------------------------------------------------------
#     def extract_text_keywords(self, text: str, top_n: int = 20) -> Dict:
#         self.log(f"Preprocessing text ({len(text)} chars)...")
#         text = self.preprocess_text(text)
#         self.log(f"Cleaned text length: {len(text)}")

#         result = {
#             "rake": self.extract_rake(text, top_n),
#             "keybert": self.extract_keybert(text, top_n)
#         }
#         self.log(f"Extraction done. RAKE: {len(result['rake'])} | KeyBERT: {len(result['keybert'])}")
#         return result

#     # -------------------------------------------------------------
#     # Folder → keywords per PDF
#     # -------------------------------------------------------------
#     def extract_from_pdf_folder(self, folder: str, top_n: int = 20) -> Dict:
#         """
#         Return JSON-like {filename: {rake:[], keybert:[]}}
#         """
#         from PyPDF2 import PdfReader

#         results = {}
#         self.log(f"Scanning folder: {folder}")

#         for f in os.listdir(folder):
#             if not f.lower().endswith(".pdf"):
#                 continue

#             pdf_path = os.path.join(folder, f)
#             self.log(f"Processing PDF: {f}")

#             try:
#                 reader = PdfReader(pdf_path)
#                 text = " ".join((page.extract_text() or "") for page in reader.pages)
#                 if not text.strip():
#                     self.log(f"Empty or unreadable PDF: {f}")
#                     results[f] = {"rake": [], "keybert": []}
#                     continue

#                 result = self.extract_text_keywords(text, top_n)
#                 results[f] = result
#                 self.log(f"Completed {f}\n")

#             except Exception as e:
#                 err_msg = f"[ERROR] PDF {f}: {e}"
#                 self.log(err_msg)
#                 results[f] = {"rake": [], "keybert": []}

#         json_result = json.dumps(results, indent=2, ensure_ascii=False)
#         self.log("Extraction complete for all PDFs.")
#         return json_result

#     # -------------------------------------------------------------
#     # KeyBERT
#     # -------------------------------------------------------------
#     def extract_keybert(self, text: str, top_n: int = 20) -> List[Dict]:
#         try:
#             from keybert import KeyBERT
#             kw_model = KeyBERT(model=self.keybert_model_name)
#             self.log("KeyBERT model loaded.")
#         except ImportError:
#             self.log("Install KeyBERT: pip install keybert")
#             return []

#         chunks = self._chunk(text)
#         self.log(f"Split text into {len(chunks)} chunks.")

#         all_kws = []
#         for i, c in enumerate(chunks):
#             try:
#                 self.log(f"Extracting KeyBERT keywords for chunk {i+1}/{len(chunks)}...")
#                 kws = kw_model.extract_keywords(
#                     c,
#                     keyphrase_ngram_range=(1, 3),
#                     stop_words="english",
#                     top_n=top_n
#                 )
#                 all_kws.extend(kws)
#             except Exception as e:
#                 self.log(f"[ERROR] KeyBERT chunk {i+1}: {e}")

#         kw_scores = {}
#         for kw, score in all_kws:
#             if score < self.min_score:
#                 continue
#             kw_scores.setdefault(kw, []).append(score)

#         averaged = [
#             {"keyword": k, "score": float(np.mean(scores))}
#             for k, scores in kw_scores.items()
#         ]

#         averaged.sort(key=lambda x: x["score"], reverse=True)
#         return averaged[:top_n]

#     # -------------------------------------------------------------
#     # RAKE
#     # -------------------------------------------------------------
#     def extract_rake(self, text: str, top_n: int = 20) -> List[Dict]:
#         try:
#             from rake_nltk import Rake
#             from nltk.corpus import stopwords
#             import nltk
#             nltk.download("stopwords", quiet=True)
#             self.log("RAKE + NLTK stopwords loaded.")
#         except ImportError:
#             self.log("Install: pip install rake-nltk nltk")
#             return []

#         try:
#             nltk_stop = set(stopwords.words("english"))
#         except:
#             nltk_stop = set()

#         combined = list(nltk_stop.union(self.domain_stopwords))

#         rake = Rake(
#             stopwords=combined,
#             min_length=1,
#             max_length=4
#         )
#         self.log("Extracting RAKE keywords...")
#         rake.extract_keywords_from_text(text)
#         ranked = rake.get_ranked_phrases_with_scores()

#         return [
#             {"keyword": p, "score": float(s)}
#             for s, p in ranked[:top_n]
#         ]

#     # -------------------------------------------------------------
#     # Preprocess Academic Text
#     # -------------------------------------------------------------
#     def preprocess_text(self, text: str) -> str:
#         if not isinstance(text, str):
#             return ""

#         text = text.replace('\n', ' ')
#         text = re.sub(r'-\s+', '', text)
#         text = re.sub(r'\s+', ' ', text)
#         text = re.sub(r'\[[0-9,\s]+\]', ' ', text)
#         text = re.sub(r'\(.*?et al\.,?\s*\d{4}\)', ' ', text)
#         text = re.sub(r'\d+', ' ', text)
#         text = re.sub(r'[^a-zA-Z\s]', ' ', text)
#         text = re.sub(
#             r'\b(et al|figure|table|dataset|results?|section|appendix|references?|'
#             r'experiment|paper|methodology|approach|data|model|algorithm|conclusion)\b',
#             ' ', text, flags=re.I
#         )
#         cleaned = re.sub(r'\s+', ' ', text).strip().lower()
#         return cleaned

#     # -------------------------------------------------------------
#     # Chunk w/ overlap
#     # -------------------------------------------------------------
#     def _chunk(self, text: str) -> List[str]:
#         words = text.split()
#         if not words:
#             return []

#         step = self.chunk_max_words - self.chunk_overlap
#         return [
#             " ".join(words[i:i + self.chunk_max_words])
#             for i in range(0, len(words), max(step, 1))
#         ]


# # -------------------------------------------------------------
# # Example Usage
# # -------------------------------------------------------------
# if __name__ == "__main__":
#     extractor = UnifiedKeywordExtractor(log_file="keyword_extraction.log")
#     folder_path = r"D:\Gomathi_ai\Dataset\Dataset\Amit Saxena"
#     output_json = extractor.extract_from_pdf_folder(folder_path, top_n=10)

#     print("\nFinal JSON output:")
#     print(output_json)

# keyword_extractor.py
import re
import numpy as np
from typing import Dict, List, Optional


class UnifiedKeywordExtractor:
    """
    Keyword extraction using RAKE and KeyBERT.
    Works with pre-extracted text from GROBID pipeline.
    """
    
    def __init__(
        self,
        keybert_model: str = "all-MiniLM-L6-v2",
        chunk_max_words: int = 512,
        chunk_overlap: int = 60,
        min_score: float = 0.0,
        log_file: Optional[str] = None
    ):
        self.keybert_model_name = keybert_model
        self.chunk_max_words = chunk_max_words
        self.chunk_overlap = chunk_overlap
        self.min_score = min_score
        self.log_file = log_file

        self.domain_stopwords = {
            'et', 'al', 'figure', 'table', 'dataset', 'result', 'results',
            'data', 'experiment', 'paper', 'section', 'algorithm', 'model',
            'introduction', 'conclusion', 'method', 'approach', 'based'
        }

    def log(self, message: str):
        """Log messages to console and optionally to file."""
        print(message)
        if self.log_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(message + "\n")

    def extract_text_keywords(self, text: str, top_n: int = 20) -> Dict:
        """
        Main entry point: extract keywords using RAKE and KeyBERT.
        Expects pre-processed text from GROBID pipeline.
        """
        if not text or len(text.split()) < 30:
            self.log(" Text too short for keyword extraction")
            return {"rake": [], "keybert": []}
        
        self.log(f"Preprocessing text ({len(text)} chars)...")
        text = self.preprocess_text(text)
        self.log(f"Cleaned text length: {len(text)}")

        result = {
            "rake": self.extract_rake(text, top_n),
            "keybert": self.extract_keybert(text, top_n)
        }
        
        self.log(f" Extraction done. RAKE: {len(result['rake'])} | KeyBERT: {len(result['keybert'])}")
        return result

    def extract_keybert(self, text: str, top_n: int = 20) -> List[Dict]:
        """Extract keywords using KeyBERT with chunking."""
        try:
            from keybert import KeyBERT
            kw_model = KeyBERT(model=self.keybert_model_name)
            self.log("  KeyBERT model loaded")
        except ImportError:
            self.log("   KeyBERT not installed: pip install keybert")
            return []
        except Exception as e:
            self.log(f"   KeyBERT error: {e}")
            return []

        chunks = self._chunk(text)
        self.log(f"  Split text into {len(chunks)} chunks")

        all_kws = []
        for i, c in enumerate(chunks):
            try:
                kws = kw_model.extract_keywords(
                    c,
                    keyphrase_ngram_range=(1, 3),
                    stop_words="english",
                    top_n=top_n
                )
                all_kws.extend(kws)
            except Exception as e:
                self.log(f"   KeyBERT chunk {i+1} error: {e}")

        # Aggregate scores across chunks
        kw_scores = {}
        for kw, score in all_kws:
            if score < self.min_score:
                continue
            kw_scores.setdefault(kw, []).append(score)

        averaged = [
            {"keyword": k, "score": float(np.mean(scores))}
            for k, scores in kw_scores.items()
        ]

        averaged.sort(key=lambda x: x["score"], reverse=True)
        return averaged[:top_n]

    def extract_rake(self, text: str, top_n: int = 20) -> List[Dict]:
        """Extract keywords using RAKE algorithm."""
        try:
            from rake_nltk import Rake
            from nltk.corpus import stopwords
            import nltk
            
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download("stopwords", quiet=True)
            
            self.log("  RAKE + NLTK stopwords loaded")
        except ImportError:
            self.log("   RAKE not installed: pip install rake-nltk nltk")
            return []
        except Exception as e:
            self.log(f"   RAKE error: {e}")
            return []

        try:
            nltk_stop = set(stopwords.words("english"))
        except:
            nltk_stop = set()

        combined = list(nltk_stop.union(self.domain_stopwords))

        rake = Rake(
            stopwords=combined,
            min_length=1,
            max_length=4
        )
        
        self.log("  Extracting RAKE keywords...")
        rake.extract_keywords_from_text(text)
        ranked = rake.get_ranked_phrases_with_scores()

        return [
            {"keyword": p, "score": float(s)}
            for s, p in ranked[:top_n]
        ]

    def preprocess_text(self, text: str) -> str:
        """Preprocess academic text for keyword extraction."""
        if not isinstance(text, str):
            return ""

        text = text.replace('\n', ' ')
        text = re.sub(r'-\s+', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\[[0-9,\s]+\]', ' ', text)
        text = re.sub(r'\(.*?et al\.,?\s*\d{4}\)', ' ', text)
        text = re.sub(r'\d+', ' ', text)
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        text = re.sub(
            r'\b(et al|figure|table|dataset|results?|section|appendix|references?|'
            r'experiment|paper|methodology|approach|data|model|algorithm|conclusion)\b',
            ' ', text, flags=re.I
        )
        cleaned = re.sub(r'\s+', ' ', text).strip().lower()
        return cleaned

    def _chunk(self, text: str) -> List[str]:
        """Chunk text with overlap for better keyword extraction."""
        words = text.split()
        if not words:
            return []

        step = self.chunk_max_words - self.chunk_overlap
        return [
            " ".join(words[i:i + self.chunk_max_words])
            for i in range(0, len(words), max(step, 1))
        ]