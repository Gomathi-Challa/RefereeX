# # # ner_metadata.py
# # import os
# # import re
# # from collections import Counter
# # from typing import Dict, List

# # import spacy

# # # Global model instance
# # nlp = None


# # def load_ner_model(model_name: str = "en_core_sci_sm", fallback: str = "en_core_web_sm"):
# #     """
# #     Load SciSpaCy model for scientific domain.
# #     Falls back to standard spaCy if unavailable.
# #     """
# #     global nlp
# #     try:
# #         import scispacy  # type: ignore
# #         nlp = spacy.load(model_name)
# #         print(f" Loaded SciSpaCy model: {model_name}")
# #     except Exception:
# #         print(f" SciSpaCy model '{model_name}' not found. Falling back to {fallback}.")
# #         try:
# #             nlp = spacy.load(fallback)
# #         except Exception as e:
# #             print(f"[ERROR] Failed to load spaCy fallback model: {e}")
# #             nlp = None


# # def preprocess_text(text: str) -> str:
# #     """Clean and normalize text for robust NER extraction."""
# #     if not text or not isinstance(text, str):
# #         return ""

# #     # Basic text normalization
# #     text = text.replace("\n", " ")
# #     text = re.sub(r"-\s+", "", text)  # Remove line break hyphenation
# #     text = re.sub(r"\s+", " ", text)
# #     text = text.strip().lower()

# #     # Remove citations, references, numbers, and equations
# #     text = re.sub(r"\[[0-9,\s]+\]", " ", text)  # remove [1], [2,3]
# #     text = re.sub(r"\(.*?et al\.,?\s*\d{4}\)", " ", text)  # remove (Smith et al., 2020)
# #     text = re.sub(r"\d+", " ", text)
# #     text = re.sub(r"[^a-zA-Z\s]", " ", text)

# #     # Remove common academic filler words
# #     text = re.sub(
# #         r"\b(et al|figure|table|dataset|results?|algorithm|model|section|appendix|"
# #         r"references?|experiment|paper|study|method|approach|data|analysis|work)\b",
# #         " ",
# #         text,
# #         flags=re.I,
# #     )

# #     # Normalize spacing
# #     text = re.sub(r"\s+", " ", text)
# #     return text.strip()


# # def split_text(text: str, max_chars: int = 100000) -> List[str]:
# #     """Split text into manageable chunks for large documents."""
# #     if not text:
# #         return []
# #     return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]


# # def extract_domain_terms(doc) -> List[Dict]:
# #     """Extract domain-specific terms (noun phrases, scientific entities)."""
# #     terms = []
# #     try:
# #         for chunk in doc.noun_chunks:
# #             if len(chunk.text) > 3 and not chunk.root.is_stop:
# #                 terms.append(chunk.text.lower())
# #     except Exception as e:
# #         print(f"[ERROR] Noun chunk extraction failed: {e}")

# #     term_counts = Counter(terms)
# #     return [
# #         {'term': k, 'count': v}
# #         for k, v in term_counts.most_common(50)
# #         if v > 1
# #     ]


# # def extract_ner_metadata(text: str, log_errors: bool = True) -> Dict:
# #     """
# #     Extract named entities and domain terms from text.
# #     Uses preprocessing, chunking, and error handling.
# #     """
# #     if nlp is None:
# #         load_ner_model()

# #     if not text or not isinstance(text, str):
# #         if log_errors:
# #             print("[WARNING] Empty or invalid text passed to NER extractor.")
# #         return {'entities': {}, 'domain_terms': []}

# #     # Preprocess
# #     clean_text = preprocess_text(text)
# #     if not clean_text:
# #         if log_errors:
# #             print("[WARNING] Cleaned text is empty after preprocessing.")
# #         return {'entities': {}, 'domain_terms': []}

# #     # Chunk large text
# #     chunks = split_text(clean_text, max_chars=80000)

# #     # Only keep useful academic entity types
# #     useful_entity_labels = ['PERSON', 'ORG', 'GPE', 'WORK_OF_ART']
# #     all_entities = {label: [] for label in useful_entity_labels}
# #     all_terms = []

# #     try:
# #         for chunk in chunks:
# #             doc = nlp(chunk)
# #             for ent in doc.ents:
# #                 if ent.label_ in useful_entity_labels:
# #                     all_entities[ent.label_].append(ent.text)
# #             all_terms.extend(extract_domain_terms(doc))
# #     except Exception as e:
# #         if log_errors:
# #             print(f"[ERROR] spaCy NER failed: {e}")
# #         return {'entities': {}, 'domain_terms': []}

# #     # Count & deduplicate entities
# #     for key in all_entities:
# #         counter = Counter(all_entities[key])
# #         all_entities[key] = [
# #             {'entity': k, 'count': v} for k, v in counter.most_common(20)
# #         ]

# #     # Merge domain terms across chunks
# #     term_counts = Counter([t['term'] for t in all_terms])
# #     aggregated_terms = [
# #         {'term': k, 'count': v} for k, v in term_counts.most_common(50) if v > 1
# #     ]

# #     return {'entities': all_entities, 'domain_terms': aggregated_terms}


# # def extract_ner_for_authors(base_folder: str) -> Dict[str, Dict]:
# #     """
# #     Traverse author folders. Each author folder contains one or more PDFs.
# #     Extract aggregated NER + domain terms per author.
# #     """
# #     from PyPDF2 import PdfReader

# #     if nlp is None:
# #         load_ner_model()

# #     author_entities = {}

# #     for author_name in os.listdir(base_folder):
# #         author_path = os.path.join(base_folder, author_name)
# #         if not os.path.isdir(author_path):
# #             continue

# #         all_texts = []

# #         for file in os.listdir(author_path):
# #             if file.lower().endswith(".pdf"):
# #                 pdf_path = os.path.join(author_path, file)
# #                 try:
# #                     reader = PdfReader(pdf_path)
# #                     text = " ".join(page.extract_text() or "" for page in reader.pages)
# #                     all_texts.append(text)
# #                 except Exception as e:
# #                     print(f"[ERROR] Failed to read {file} for {author_name}: {e}")

# #         if not all_texts:
# #             print(f"[WARNING] No valid documents found for {author_name}")
# #             author_entities[author_name] = {}
# #             continue

# #         if len(all_texts) == 1:
# #             print(f" Only one paper found for {author_name} — results may be limited.")

# #         combined_text = " ".join(all_texts)
# #         processed = extract_ner_metadata(combined_text)
# #         author_entities[author_name] = processed

# #     return author_entities


# # ner_metadata.py
# import os
# import re
# from collections import Counter
# from typing import Dict, List

# import spacy

# # Global language model
# nlp = None

# class NerExtractor:
#     """NER and Domain Term Extractor using spaCy/SciSpaCy."""
    
#     def load_ner_model(model_name: str = "en_core_sci_sm", fallback="en_core_web_sm"):
#         """Load SciSpaCy model, fallback to spaCy small model."""
#         global nlp
#         try:
#             import scispacy  # noqa
#             nlp = spacy.load(model_name)
#             print(f"Loaded SciSpaCy model: {model_name}")
#         except Exception:
#             print(f"SciSpaCy model '{model_name}' not found. Falling back to {fallback}")
#             try:
#                 nlp = spacy.load(fallback)
#             except Exception as e:
#                 print(f"Failed to load spaCy model: {e}")
#                 nlp = None


#     def preprocess_text(text: str) -> str:
#         """Clean text for domain term extraction (NOT for NER!)."""
#         if not text:
#             return ""

#         text = text.replace("\n", " ")
#         text = re.sub(r"-\s+", "", text)
#         text = re.sub(r"\s+", " ", text)

#         # Lowercase only for term extraction
#         text = text.lower()

#         # Remove citations, numbers, punctuation
#         text = re.sub(r"\[[0-9,\s]+\]", " ", text)
#         text = re.sub(r"\(.*?et al\.,?\s*\d{4}\)", " ", text)
#         text = re.sub(r"\d+", " ", text)
#         text = re.sub(r"[^a-zA-Z\s]", " ", text)

#         # Remove common academic filler words
#         stop_academic = (
#             r"\b(et al|figure|table|dataset|results?|algorithm|model|section|appendix|"
#             r"references?|experiment|paper|study|method|approach|data|analysis|work)\b"
#         )
#         text = re.sub(stop_academic, " ", text)

#         return re.sub(r"\s+", " ", text).strip()


#     def split_text(text: str, max_chars: int = 80000) -> List[str]:
#         """Chunk text safely for spaCy."""
#         return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]


#     def extract_domain_terms(doc) -> List[Dict]:
#         """Extract top domain noun phrases."""
#         terms = []
#         try:
#             for chunk in doc.noun_chunks:
#                 if len(chunk.text) > 3 and not chunk.root.is_stop:
#                     terms.append(chunk.text.lower())
#         except Exception as e:
#             print(f"Noun chunk error: {e}")

#         counter = Counter(terms)
#         return [{'term': k, 'count': v} for k, v in counter.most_common(50) if v > 1]


#     def extract_ner_metadata(text: str, log_errors=True) -> Dict:
#         """Run NER on raw text, domain terms on cleaned text."""
#         if nlp is None:
#             load_ner_model()

#         if not text:
#             return {'entities': {}, 'domain_terms': []}

#         # RAW text for NER
#         raw_text = text

#         # CLEAN text for term extraction only
#         clean_text = preprocess_text(text)
#         if not clean_text:
#             return {'entities': {}, 'domain_terms': []}

#         # Chunking
#         raw_chunks = split_text(raw_text)
#         clean_chunks = split_text(clean_text)

#         useful_labels = ['PERSON', 'ORG', 'GPE', 'LOC', 'PRODUCT', 'NORP']
#         entity_store = {label: [] for label in useful_labels}
#         all_terms = []

#         try:
#             for chunk, clean_chunk in zip(raw_chunks, clean_chunks):
#                 doc_raw = nlp(chunk)
#                 doc_clean = nlp(clean_chunk)

#                 for ent in doc_raw.ents:
#                     if ent.label_ in useful_labels:
#                         entity_store[ent.label_].append(ent.text)

#                 all_terms.extend(extract_domain_terms(doc_clean))

#         except Exception as e:
#             if log_errors:
#                 print(f"spaCy processing error: {e}")
#             return {'entities': {}, 'domain_terms': []}

#         # Aggregate entities
#         for label in entity_store:
#             c = Counter(entity_store[label])
#             entity_store[label] = [{'entity': k, 'count': v} for k, v in c.most_common(20)]

#         # Aggregate terms across chunks
#         term_counts = Counter([t['term'] for t in all_terms])
#         domain_terms = [{'term': k, 'count': v} for k, v in term_counts.most_common(50) if v > 1]

#         return {'entities': entity_store, 'domain_terms': domain_terms}


#     def extract_ner_for_folder(folder_path: str) -> Dict:
#         """
#         Process all PDFs inside a given folder and run NER + domain term extraction.
#         Returns a single dictionary of entities and domain terms for that folder.
#         """
#         from PyPDF2 import PdfReader

#         if nlp is None:
#             load_ner_model()

#         texts = []
#         for file in os.listdir(folder_path):
#             if file.lower().endswith(".pdf"):
#                 pdf_path = os.path.join(folder_path, file)
#                 text = ""

#                 # Try PyMuPDF first (more accurate)
#                 try:
#                     import fitz
#                     with fitz.open(pdf_path) as pdf:
#                         text = " ".join(page.get_text() for page in pdf)
#                 except Exception:
#                     # fallback to PyPDF2
#                     try:
#                         reader = PdfReader(pdf_path)
#                         text = " ".join(page.extract_text() or "" for page in reader.pages)
#                     except Exception as e:
#                         print(f"Cannot read PDF {file}: {e}")

#                 if text:
#                     texts.append(text)

#         if not texts:
#             print(f"No readable PDFs in folder {folder_path}")
#             return {}

#         combined_text = " ".join(texts)
#         return extract_ner_metadata(combined_text)

# ner_metadata.py
import re
from collections import Counter
from typing import Dict, List
import spacy

# Global language model
nlp = None


class NerExtractor:
    """NER and Domain Term Extractor using spaCy/SciSpaCy."""
    
    @staticmethod
    def load_ner_model(model_name: str = "en_core_sci_sm", fallback="en_core_web_sm"):
        """Load SciSpaCy model, fallback to spaCy small model."""
        global nlp
        if nlp is not None:
            return  # Already loaded
            
        try:
            import scispacy  # noqa
            nlp = spacy.load(model_name)
            print(f" Loaded SciSpaCy model: {model_name}")
        except Exception:
            print(f" SciSpaCy model '{model_name}' not found. Falling back to {fallback}")
            try:
                nlp = spacy.load(fallback)
                print(f" Loaded spaCy model: {fallback}")
            except Exception as e:
                print(f" Failed to load spaCy model: {e}")
                nlp = None

    @staticmethod
    def preprocess_text_for_terms(text: str) -> str:
        """
        Clean text for domain term extraction ONLY (NOT for NER!).
        This is used only for noun phrase extraction.
        """
        if not text:
            return ""

        text = text.replace("\n", " ")
        text = re.sub(r"-\s+", "", text)
        text = re.sub(r"\s+", " ", text)
        text = text.lower()

        # Remove citations, numbers, punctuation
        text = re.sub(r"\[[0-9,\s]+\]", " ", text)
        text = re.sub(r"\(.*?et al\.,?\s*\d{4}\)", " ", text)
        text = re.sub(r"\d+", " ", text)
        text = re.sub(r"[^a-zA-Z\s]", " ", text)

        # Remove common academic filler words
        stop_academic = (
            r"\b(et al|figure|table|dataset|results?|algorithm|model|section|appendix|"
            r"references?|experiment|paper|study|method|approach|data|analysis|work)\b"
        )
        text = re.sub(stop_academic, " ", text, flags=re.I)

        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def split_text(text: str, max_chars: int = 80000) -> List[str]:
        """Chunk text safely for spaCy."""
        if not text:
            return []
        return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]

    @staticmethod
    def extract_domain_terms(doc) -> List[str]:
        """Extract domain noun phrases from spaCy doc."""
        terms = []
        try:
            for chunk in doc.noun_chunks:
                if len(chunk.text) > 3 and not chunk.root.is_stop:
                    terms.append(chunk.text.lower())
        except Exception as e:
            print(f" Noun chunk error: {e}")
        return terms

    @staticmethod
    def extract_ner_metadata(text: str, log_errors=True) -> Dict:
        """
        Run NER on raw text (case-preserved), domain terms on cleaned text.
        This function processes combined text from multiple PDFs.
        """
        global nlp
        
        if nlp is None:
            NerExtractor.load_ner_model()
        
        if nlp is None or not text:
            return {'entities': {}, 'domain_terms': []}

        # Use RAW text for NER (preserves entities like person names)
        raw_text = text

        # Use CLEANED text only for term extraction
        clean_text = NerExtractor.preprocess_text_for_terms(text)
        if not clean_text:
            return {'entities': {}, 'domain_terms': []}

        # Chunk both versions
        raw_chunks = NerExtractor.split_text(raw_text)
        clean_chunks = NerExtractor.split_text(clean_text)

        useful_labels = ['PERSON', 'ORG', 'GPE', 'LOC', 'PRODUCT', 'NORP']
        entity_store = {label: [] for label in useful_labels}
        all_terms = []

        try:
            # Process chunks in parallel-ish fashion
            for raw_chunk, clean_chunk in zip(raw_chunks, clean_chunks):
                # Extract entities from RAW text
                doc_raw = nlp(raw_chunk)
                for ent in doc_raw.ents:
                    if ent.label_ in useful_labels:
                        entity_store[ent.label_].append(ent.text)

                # Extract domain terms from CLEAN text
                doc_clean = nlp(clean_chunk)
                all_terms.extend(NerExtractor.extract_domain_terms(doc_clean))

        except Exception as e:
            if log_errors:
                print(f" spaCy processing error: {e}")
            return {'entities': {}, 'domain_terms': []}

        # Aggregate entities by label
        for label in entity_store:
            c = Counter(entity_store[label])
            entity_store[label] = [
                {'entity': k, 'count': v}
                for k, v in c.most_common(20)
            ]

        # Aggregate domain terms
        term_counts = Counter(all_terms)
        domain_terms = [
            {'term': k, 'count': v}
            for k, v in term_counts.most_common(50)
            if v > 1
        ]

        return {
            'entities': entity_store,
            'domain_terms': domain_terms
        }