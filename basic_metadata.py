# import glob
# import os               


# # basic_metadata.py
# import fitz  # PyMuPDF
# import re
# import requests
# from typing import Dict, Optional

# def extract_basic_metadata(pdf_path: str, use_grobid: bool = True, grobid_url: str = None) -> Dict:
#     """Extract title, authors, affiliations, year, venue"""
    
#     # Try GROBID first if available
#     if use_grobid and grobid_url:
#         try:
#             grobid_data = extract_with_grobid(pdf_path, grobid_url)
#             if grobid_data:
#                 return grobid_data
#         except Exception as e:
#             print(f"GROBID failed: {e}, falling back to PyMuPDF")
    
#     # Fallback to PyMuPDF extraction
#     return extract_with_pymupdf(pdf_path)

# def extract_with_grobid(pdf_path: str, grobid_url: str) -> Optional[Dict]:
#     """Use GROBID API for structured metadata."""
#     url = f"{grobid_url}/api/processHeaderDocument"

#     try:
#         with open(pdf_path, 'rb') as f:
#             files = {'input': f}
#             response = requests.post(url, files=files, timeout=30)
#     except requests.exceptions.RequestException as e:
#         print(f"[Warning] Could not connect to GROBID at {url}: {e}")
#         return None  # fallback to PyMuPDF

#     if response.status_code != 200:
#         print(f"[Warning] GROBID responded with {response.status_code}")
#         return None

#     from bs4 import BeautifulSoup
#     soup = BeautifulSoup(response.text, 'xml')

#     # Extract fields
#     title = soup.find('title')
#     title_text = title.get_text(strip=True) if title else None

#     authors = []
#     affiliations = []
#     for author in soup.find_all('author'):
#         name_parts = []
#         if author.find('forename'):
#             name_parts.append(author.find('forename').get_text(strip=True))
#         if author.find('surname'):
#             name_parts.append(author.find('surname').get_text(strip=True))
#         if name_parts:
#             authors.append(' '.join(name_parts))

#         aff = author.find('affiliation')
#         if aff and aff.find('orgName'):
#             affiliations.append(aff.find('orgName').get_text(strip=True))

#     year = soup.find('date', {'type': 'published'})
#     year_text = year.get('when', '')[:4] if year else None

#     venue = soup.find('meeting')
#     venue_text = venue.get_text(strip=True) if venue else None

#     return {
#         'title': title_text,
#         'authors': authors,
#         'affiliations': list(set(affiliations)),
#         'year': year_text,
#         'venue': venue_text,
#         'extraction_method': 'grobid'
#     }


# def extract_with_pymupdf(pdf_path: str) -> dict:
#     """Enhanced extraction with layout, header info, and folder-based hints."""
#     doc = fitz.open(pdf_path)
#     first_page = doc[0]
#     blocks = first_page.get_text("dict")["blocks"]
#     full_text = first_page.get_text("text")

#     # Get folder name (as context)
#     folder_name = os.path.basename(os.path.dirname(pdf_path))

#     # --------------------------
#     # 1️⃣ Extract header/footer info (publisher, journal, DOI, arXiv)
#     # --------------------------
#     header_text = ""
#     footer_text = ""

#     for b in blocks:
#         bbox = b["bbox"]
#         text = " ".join(span["text"] for line in b.get("lines", []) for span in line.get("spans", []))
#         if not text.strip():
#             continue

#         if bbox[1] < 100:  # near top
#             header_text += " " + text.strip()
#         elif bbox[1] > first_page.rect.height - 100:  # near bottom
#             footer_text += " " + text.strip()

#     header_footer = (header_text + " " + footer_text).strip()
#     venue = extract_publication_info(header_footer)

#     # --------------------------
#     # 2️⃣ Title detection (largest font size)
#     # --------------------------
#     title, max_font = None, 0
#     for block in blocks:
#         for line in block.get("lines", []):
#             for span in line.get("spans", []):
#                 if span["size"] > max_font and 10 < len(span["text"]) < 200:
#                     max_font = span["size"]
#                     title = span["text"].strip()

#     # --------------------------
#     # 3️⃣ Author / affiliation extraction
#     # --------------------------
#     authors, affiliations = [], []
#     after_title = False
#     for block in blocks:
#         block_text = " ".join(span["text"] for line in block.get("lines", []) for span in line.get("spans", []))
#         block_text = block_text.strip()

#         if not block_text:
#             continue
#         if title and title in block_text:
#             after_title = True
#             continue

#         if after_title:
#             if re.search(r"(university|institute|college|lab|centre|school|department)", block_text, re.I):
#                 affiliations.append(block_text)
#             elif re.search(r"[A-Z][a-z]+ [A-Z][a-z]+", block_text):
#                 authors.append(block_text)
#             if re.search(r"abstract", block_text, re.I):
#                 break

#     # Add folder name as backup author
#     if folder_name and not authors:
#         authors.append(folder_name)

#     # --------------------------
#     # 4️⃣ Abstract extraction
#     # --------------------------
#     abstract_match = re.search(r"(?i)abstract\s*[:\-]?\s*(.*?)\n(?:keywords?|introduction)", full_text, re.S)
#     abstract = abstract_match.group(1).strip() if abstract_match else None

#     # --------------------------
#     # 5️⃣ Keywords extraction
#     # --------------------------
#     keywords_match = re.search(r"(?i)(keywords?|index terms)\s*[:\-]?\s*(.*?)\n", full_text)
#     keywords = [k.strip() for k in re.split(r"[;,]", keywords_match.group(2))] if keywords_match else []

#     # --------------------------
#     # 6️⃣ Year extraction
#     # --------------------------
#     year_match = re.search(r"\b(19|20)\d{2}\b", full_text[:1000])
#     year = year_match.group(0) if year_match else None

#     doc.close()

#     return {
#         "title": title,
#         "authors": list(set(authors))[:10],
#         "affiliations": list(set(affiliations))[:5],
#         "abstract": abstract,
#         "keywords": keywords,
#         "year": year,
#         "venue": venue,
#         "folder_context": folder_name,
#         "extraction_method": "pymupdf-extended"
#     }

# def extract_publication_info(header_text: str) -> str:
#     """Detect venue, publisher, or DOI from header/footer text."""
#     if not header_text:
#         return None
#     header_text = header_text.lower()

#     # Common patterns
#     if "ieee" in header_text:
#         return "IEEE Publication"
#     if "springer" in header_text:
#         return "Springer"
#     if "elsevier" in header_text:
#         return "Elsevier"
#     if "acm" in header_text:
#         return "ACM Digital Library"
#     if "arxiv" in header_text:
#         return "arXiv Preprint"
#     if "nature" in header_text:
#         return "Nature Publishing"
#     if "wiley" in header_text:
#         return "Wiley"
#     if "sciencedirect" in header_text:
#         return "ScienceDirect"

#     # DOI extraction
#     doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", header_text, re.I)
#     if doi_match:
#         return f"DOI: {doi_match.group(0)}"

#     return None

# # def extract_title(text: str, metadata_title: Optional[str]) -> Optional[str]:
# #     """Extract paper title"""
# #     if metadata_title and len(metadata_title) > 10:
# #         return metadata_title.strip()
    
# #     lines = text.split('\n')[:10]
# #     for line in lines:
# #         line = line.strip()
# #         if len(line) > 20 and len(line) < 300 and not line.isupper():
# #             return line
# #     return None

# # def extract_authors(text: str) -> list:
# #     """Extract author names"""
# #     # Look for common patterns
# #     patterns = [
# #         r'(?:by|By)\s+((?:[A-Z][a-z]+\s+[A-Z][a-z]+(?:,\s+)?)+)',
# #         r'([A-Z][a-z]+\s+[A-Z][a-z]+(?:,\s+[A-Z][a-z]+\s+[A-Z][a-z]+)*)'
# #     ]
    
# #     lines = text.split('\n')[:20]
# #     authors = []
    
# #     for line in lines:
# #         if 'abstract' in line.lower():
# #             break
# #         for pattern in patterns:
# #             matches = re.findall(pattern, line)
# #             if matches:
# #                 authors.extend([a.strip() for a in matches[0].split(',')])
    
# #     return list(set(authors))[:10]  # Max 10 authors

# # def extract_year(text: str, creation_date: str) -> Optional[str]:
# #     """Extract publication year"""
# #     # Try creation date first
# #     year_match = re.search(r'(19|20)\d{2}', creation_date)
# #     if year_match:
# #         return year_match.group()
    
# #     # Search in first page
# #     year_match = re.search(r'\b(19|20)\d{2}\b', text[:500])
# #     return year_match.group() if year_match else None

# # def extract_affiliations(text: str) -> list:
# #     """Extract institutional affiliations"""
# #     patterns = [
# #         r'(University[^,\n]+)',
# #         r'(Institute[^,\n]+)',
# #         r'(College[^,\n]+)',
# #         r'(Laboratory[^,\n]+)',
# #         r'([A-Z][a-z]+\s+University)'
# #     ]
    
# #     affiliations = []
# #     for pattern in patterns:
# #         matches = re.findall(pattern, text[:1000])
# #         affiliations.extend(matches)
    
# #     return list(set(affiliations))[:5]

# import os
# import glob

# def pdf_extraction(folder_path: str, grobid_url: str = None, use_grobid: bool = True):
#     """
#     Process all PDFs in a folder and extract metadata.
#     Can optionally disable GROBID and only use PyMuPDF.
#     """
#     results = {}

#     pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))

#     if not pdf_files:
#         print(f"No PDF files found in folder: {folder_path}")
#         return {}

#     print(f"Found {len(pdf_files)} PDF files. Starting extraction...\n")

#     for pdf_path in pdf_files:
#         file_name = os.path.basename(pdf_path)
#         print(f"\n===== Processing: {file_name} =====")

#         # ---------------------------
#         # Option 1: Use GROBID if enabled
#         # ---------------------------
#         if use_grobid and grobid_url:
#             try:
#                 grobid_metadata = extract_with_grobid(pdf_path, grobid_url)
#                 if grobid_metadata:
#                     print(f" GROBID extraction succeeded for {file_name}")
#                     metadata = grobid_metadata
#                 else:
#                     print(f" GROBID failed for {file_name}, using PyMuPDF...")
#                     metadata = extract_basic_metadata(pdf_path, use_grobid=False)
#             except Exception as e:
#                 print(f" GROBID error for {file_name}: {e}. Using PyMuPDF fallback.")
#                 metadata = extract_basic_metadata(pdf_path, use_grobid=False)
        
#         # ---------------------------
#         # Option 2: Skip GROBID entirely
#         # ---------------------------
#         else:
#             print(f" Skipping GROBID. Extracting {file_name} with PyMuPDF...")
#             metadata = extract_basic_metadata(pdf_path, use_grobid=False)

#         # Store results
#         results[file_name] = metadata

#     print("\n Extraction completed for folder:", folder_path)
#     return results



# folder = "D:\\Gomathi_ai\\Dataset\\Dataset\\Amit Saxena"
# grobid = "http://localhost:8070"  # your GROBID server URL

# data = pdf_extraction(folder, grobid, False)

# # Save JSON
# import json
# with open("author_metadata.json", "w") as f:
#     json.dump(data, f, indent=4)

# print("Saved author_metadata.json")





# # # Provide the path to your PDF and GROBID URL (if you have it)
# # pdf_path = "D:/Gomathi_ai/Dataset/Dataset/Amit Saxena/A Review of Clustering Techniques.pdf"

# # grobid_url = "http://localhost:8070"  # Example: Update with your own GROBID instance URL

# # # Run the test
# # if os.path.exists(pdf_path):
# #     test_pdf_extraction(pdf_path, grobid_url)
# # else:
# #     print(f"PDF file not found: {pdf_path}")


# # import os
# # import re
# # import json
# # import fitz  # PyMuPDF
# # import requests
# # import logging
# # from datetime import datetime
# # from typing import Dict, Optional, List

# # # ---------------- Logging Setup ---------------- #
# # logging.basicConfig(
# #     filename='metadata_extraction.log',
# #     level=logging.INFO,
# #     format='%(asctime)s [%(levelname)s] %(message)s'
# # )


# # # ---------------- Main Extraction Functions ---------------- #
# # def extract_basic_metadata(pdf_path: str, use_grobid: bool = True, grobid_url: str = None) -> Dict:
# #     """Extract title, authors, affiliations, year, venue from a PDF."""
# #     if use_grobid and grobid_url:
# #         try:
# #             data = extract_with_grobid(pdf_path, grobid_url)
# #             if data:
# #                 return data
# #         except Exception as e:
# #             logging.warning(f"GROBID failed for {pdf_path}: {e}")

# #     try:
# #         return extract_with_pymupdf(pdf_path)
# #     except Exception as e:
# #         logging.error(f"PyMuPDF extraction failed for {pdf_path}: {e}")
# #         return {"error": str(e), "file": pdf_path}


# # def extract_with_grobid(pdf_path: str, grobid_url: str) -> Optional[Dict]:
# #     """Use GROBID API for structured metadata."""
# #     url = f"{grobid_url}/api/processHeaderDocument"

# #     try:
# #         with open(pdf_path, 'rb') as f:
# #             files = {'input': f}
# #             response = requests.post(url, files=files, timeout=30)
# #     except requests.exceptions.RequestException as e:
# #         logging.warning(f"[Warning] Could not connect to GROBID: {e}")
# #         return None

# #     if response.status_code != 200:
# #         logging.warning(f"GROBID error {response.status_code} for {pdf_path}")
# #         return None

# #     from bs4 import BeautifulSoup
# #     soup = BeautifulSoup(response.text, 'xml')

# #     title = soup.find('title')
# #     authors = []
# #     affiliations = []
# #     for author in soup.find_all('author'):
# #         name_parts = []
# #         if author.find('forename'):
# #             name_parts.append(author.find('forename').get_text(strip=True))
# #         if author.find('surname'):
# #             name_parts.append(author.find('surname').get_text(strip=True))
# #         if name_parts:
# #             authors.append(' '.join(name_parts))
# #         aff = author.find('affiliation')
# #         if aff and aff.find('orgName'):
# #             affiliations.append(aff.find('orgName').get_text(strip=True))

# #     year = soup.find('date', {'type': 'published'})
# #     year_text = year.get('when', '')[:4] if year else None
# #     venue = soup.find('monogr')
# #     venue_text = venue.find('title').get_text(strip=True) if venue and venue.find('title') else None

# #     return {
# #         "title": title.get_text(strip=True) if title else None,
# #         "authors": authors,
# #         "affiliations": affiliations,
# #         "year": year_text,
# #         "venue": venue_text,
# #         "source": "GROBID"
# #     }


# # def extract_with_pymupdf(pdf_path: str) -> Dict:
# #     """Fallback metadata extraction using PyMuPDF."""
# #     doc = fitz.open(pdf_path)
# #     text = ""
# #     for page in doc:
# #         text += page.get_text("text")
# #         if len(text) > 10000:  # limit
# #             break
# #     doc.close()

# #     title_match = re.search(r'(?i)title[:\s]+(.+)', text)
# #     title = title_match.group(1).strip() if title_match else None

# #     author_match = re.findall(r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)', text)
# #     year_match = re.search(r'\b(19|20)\d{2}\b', text)

# #     return {
# #         "title": title or os.path.basename(pdf_path),
# #         "authors": list(set(author_match[:5])) if author_match else [],
# #         "year": year_match.group(0) if year_match else None,
# #         "venue": None,
# #         "source": "PyMuPDF"
# #     }


# # # ---------------- Folder Handling ---------------- #
# # def process_author_folder(author_folder: str, grobid_url: Optional[str] = None) -> Dict:
# #     """Process all PDFs for one author folder."""
# #     results = {"author": os.path.basename(author_folder), "papers": []}
# #     pdf_files = [f for f in os.listdir(author_folder) if f.lower().endswith('.pdf')]

# #     if not pdf_files:
# #         logging.warning(f"No PDFs found in {author_folder}")
# #         results["error"] = "No PDF files found"
# #         return results

# #     for pdf in pdf_files:
# #         pdf_path = os.path.join(author_folder, pdf)
# #         try:
# #             meta = extract_basic_metadata(pdf_path, use_grobid=bool(grobid_url), grobid_url=grobid_url)
# #             results["papers"].append(meta)
# #         except Exception as e:
# #             logging.error(f"Error processing {pdf_path}: {e}")
# #             results["papers"].append({"file": pdf, "error": str(e)})

# #     return results


# # # ---------------- Main Function ---------------- #
# # def main(base_folder: str, grobid_url: Optional[str] = None, save_path: Optional[str] = None) -> Dict:
# #     """
# #     Processes all author folders under a base directory.
# #     Returns a combined JSON dictionary of all metadata.
# #     """
# #     all_metadata = []
# #     logging.info(f"Starting metadata extraction in {base_folder}")

# #     author_folders = [
# #         os.path.join(base_folder, d)
# #         for d in os.listdir(base_folder)
# #         if os.path.isdir(os.path.join(base_folder, d))
# #     ]

# #     if not author_folders:
# #         logging.warning(f"No author folders found in {base_folder}")
# #         return {"error": "No author folders found"}

# #     for folder in author_folders:
# #         try:
# #             author_data = process_author_folder(folder, grobid_url=grobid_url)
# #             all_metadata.append(author_data)
# #         except Exception as e:
# #             logging.error(f"Failed to process {folder}: {e}")
# #             all_metadata.append({"author": os.path.basename(folder), "error": str(e)})

# #     combined_json = {
# #         "timestamp": datetime.now().isoformat(),
# #         "base_folder": base_folder,
# #         "authors_processed": len(all_metadata),
# #         "data": all_metadata
# #     }

# #     if save_path:
# #         try:
# #             with open(save_path, 'w', encoding='utf-8') as f:
# #                 json.dump(combined_json, f, indent=2)
# #             logging.info(f"Saved combined JSON to {save_path}")
# #         except Exception as e:
# #             logging.error(f"Failed to save combined JSON: {e}")

# #     return combined_json


# # # ---------------- Run (example) ---------------- #
# # if __name__ == "__main__":
# #     BASE_DIR = "authors_papers"  # folder containing subfolders of author names
# #     OUTPUT_JSON = "combined_metadata.json"

# #     result = main(base_folder=BASE_DIR, grobid_url=None, save_path=OUTPUT_JSON)
# #     print(json.dumps(result, indent=2))


import fitz
import re
import os
from typing import Dict, List, Tuple, Optional, Set
from collections import Counter, defaultdict
import warnings
import glob
import spacy
from sentence_transformers import SentenceTransformer, util

# Optional imports with fallbacks
try:
    import spacy
    SPACY_AVAILABLE = True
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("Downloading spaCy model 'en_core_web_sm'...")
        os.system("python -m spacy download en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
except ImportError:
    SPACY_AVAILABLE = False
    nlp = None
    warnings.warn("spaCy not available. Install with: pip install spacy && python -m spacy download en_core_web_sm")

try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    semantic_model = None
    warnings.warn("sentence-transformers not available. Install with: pip install sentence-transformers")


class PDFMetadataExtractor:
    """Enhanced PDF metadata extraction with NLP and semantic understanding."""
    
    def __init__(self, top_n_words: int = 3000, use_semantic: bool = True, use_spacy: bool = True):
        """
        Initialize extractor.
        
        Args:
            top_n_words: Number of words to extract from start of document
            use_semantic: Whether to use semantic similarity for classification
            use_spacy: Whether to use spaCy NER for entity extraction
        """
        self.top_n_words = top_n_words
        self.use_semantic = use_semantic 
        self.use_spacy = use_spacy 
        
        # Patterns for line classification
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'url': r'https?://[^\s]+',
            'doi': r'10\.\d{4,9}/[-._;()/:A-Z0-9]+',
            'year': r'\b(19|20)\d{2}\b',
            'arxiv': r'arXiv:\d+\.\d+',
            'issn': r'ISSN\s*:?\s*\d{4}-?\d{3}[\dX]',
            'university': r'\b(university|institute|college|school|department|lab|laboratory|centre|center)\b',
            'publisher': r'\b(ieee|springer|elsevier|acm|nature|wiley|science|plos|oxford|cambridge|sage|taylor|francis)\b',
            'name_pattern': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            'boilerplate': r'\b(copyright|rights reserved|downloaded from|view the article|see discussions|citation received|accepted|published|see terms|open access)\b',
        }
        
        # Semantic reference texts for classification
        if self.use_semantic:
            self.semantic_references = {
                'title': [
                    "main title of the research paper",
                    "article title heading",
                    "study title and topic"
                ],
                'author': [
                    "author names and contributors",
                    "list of researchers who wrote this",
                    "paper authors"
                ],
                'affiliation': [
                    "university and institution affiliations",
                    "department and research center",
                    "academic institution address"
                ],
                'abstract': [
                    "abstract summary of the research",
                    "brief overview of the study methods and results",
                    "paper summary and conclusions"
                ],
                'keywords': [
                    "index terms and keywords",
                    "subject area topics",
                    "research field tags"
                ],
                'publication': [
                    "journal name and conference proceedings",
                    "publisher and publication venue",
                    "where this was published"
                ],
                'boilerplate': [
                    "copyright notice and legal terms",
                    "downloaded from website",
                    "view article online"
                ]
            }
            
            # Pre-compute embeddings for reference texts
            self.semantic_embeddings = {}
            for category, texts in self.semantic_references.items():
                self.semantic_embeddings[category] = semantic_model.encode(texts, convert_to_tensor=True)
    
    def extract_top_words(self, doc: fitz.Document) -> Tuple[str, List[Dict]]:
        """Extract first N words from document with position info."""
        words_collected = 0
        text_blocks = []
        full_text = ""
        
        for page_num, page in enumerate(doc):
            if words_collected >= self.top_n_words:
                break
            
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" not in block:
                    continue
                
                block_text = ""
                block_bbox = block["bbox"]
                max_font = 0
                
                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        line_text += span["text"]
                        max_font = max(max_font, span.get("size", 0))
                    
                    block_text += line_text.strip() + " "
                
                block_text = block_text.strip()
                if not block_text:
                    continue
                
                words_in_block = len(block_text.split())
                words_collected += words_in_block
                
                text_blocks.append({
                    "text": block_text,
                    "bbox": block_bbox,
                    "page": page_num,
                    "font_size": max_font,
                    "position": "header" if block_bbox[1] < 100 else "footer" if block_bbox[3] > page.rect.height - 100 else "body"
                })
                
                full_text += block_text + "\n"
                
                if words_collected >= self.top_n_words:
                    break
        
        return full_text, text_blocks
    
    def extract_entities_with_spacy(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities using spaCy NER."""
        if not self.use_spacy or not text:
            return {}
        
        doc = nlp(text[:100000])  # Limit to avoid memory issues
        
        entities = defaultdict(list)
        for ent in doc.ents:
            entities[ent.label_].append(ent.text)
        
        return {
            'persons': entities.get('PERSON', []),
            'organizations': entities.get('ORG', []),
            'locations': entities.get('GPE', []),
            'dates': entities.get('DATE', []),
            'all_entities': dict(entities)
        }
    
    def get_semantic_similarity(self, text: str, category: str) -> float:
        """
        Calculate semantic similarity between text and category reference texts.
        
        Args:
            text: Text to classify
            category: Category to compare against
            
        Returns:
            Similarity score (0-1)
        """
        if not self.use_semantic or category not in self.semantic_embeddings:
            return 0.0
        
        # Encode the input text
        text_embedding = semantic_model.encode(text, convert_to_tensor=True)
        
        # Calculate cosine similarity with reference embeddings
        similarities = util.cos_sim(text_embedding, self.semantic_embeddings[category])
        
        # Return max similarity
        return float(similarities.max())
    
    def classify_line(self, text: str, position: str = "body", font_size: float = 10.0) -> Dict[str, any]:
        """
        Classify a line of text using regex, heuristics, and semantic analysis.
        
        Args:
            text: Text to classify
            position: Position in page (header/body/footer)
            font_size: Font size of text
            
        Returns:
            Dictionary with classification results
        """
        text_lower = text.lower()
        
        # Basic regex classification
        classification = {
            'is_email': bool(re.search(self.patterns['email'], text)),
            'is_url': bool(re.search(self.patterns['url'], text)),
            'is_doi': bool(re.search(self.patterns['doi'], text, re.I)),
            'is_arxiv': bool(re.search(self.patterns['arxiv'], text)),
            'has_year': bool(re.search(self.patterns['year'], text)),
            'is_institution': bool(re.search(self.patterns['university'], text_lower)),
            'is_publisher': bool(re.search(self.patterns['publisher'], text_lower)),
            'is_boilerplate': bool(re.search(self.patterns['boilerplate'], text_lower)),
            'has_names': len(re.findall(self.patterns['name_pattern'], text)),
            'word_count': len(text.split()),
            'position': position,
            'font_size': font_size,
        }
        
        # SpaCy NER analysis (only for longer text)
        if self.use_spacy and 3 <= classification['word_count'] <= 100:
            entities = self.extract_entities_with_spacy(text)
            classification['spacy_persons'] = len(entities.get('persons', []))
            classification['spacy_orgs'] = len(entities.get('organizations', []))
            classification['spacy_entities'] = entities
        else:
            classification['spacy_persons'] = 0
            classification['spacy_orgs'] = 0
            classification['spacy_entities'] = {}
        
        # Semantic similarity scores
        if self.use_semantic and classification['word_count'] >= 3:
            semantic_scores = {}
            for category in ['title', 'author', 'affiliation', 'abstract', 'keywords', 'publication', 'boilerplate']:
                semantic_scores[category] = self.get_semantic_similarity(text, category)
            
            classification['semantic_scores'] = semantic_scores
            classification['semantic_best_match'] = max(semantic_scores.items(), key=lambda x: x[1])
        else:
            classification['semantic_scores'] = {}
            classification['semantic_best_match'] = (None, 0.0)
        
        # Combined classification logic
        classification['likely_type'] = self._determine_likely_type(classification)
        classification['confidence'] = self._calculate_confidence(classification)
        
        return classification
    
    def _determine_likely_type(self, classification: Dict) -> str:
        """Determine the most likely type using all available information."""
        
        # Strong signals override everything
        if classification['is_boilerplate']:
            return 'boilerplate'
        
        if classification['is_email'] or classification['is_url']:
            return 'contact_info'
        
        # Semantic analysis (if available)
        if self.use_semantic and classification['semantic_best_match'][1] > 0.5:
            semantic_type = classification['semantic_best_match'][0]
            
            # Validate with other signals
            if semantic_type == 'author' and classification['has_names'] >= 1:
                return 'authors'
            elif semantic_type == 'affiliation' and classification['is_institution']:
                return 'affiliation'
            elif semantic_type == 'abstract' and 50 <= classification['word_count'] <= 500:
                return 'abstract'
            elif semantic_type == 'title' and 5 <= classification['word_count'] <= 50:
                return 'title'
            elif semantic_type in ['keywords', 'publication']:
                return semantic_type
        
        # SpaCy NER signals
        if self.use_spacy:
            if classification['spacy_persons'] >= 2 and classification['word_count'] < 50:
                return 'authors'
            if classification['spacy_orgs'] >= 1 and classification['is_institution']:
                return 'affiliation'
        
        # Fallback to heuristics
        if classification['is_institution']:
            return 'affiliation'
        elif classification['is_publisher'] or classification['is_doi']:
            return 'publication_info'
        elif classification['has_names'] >= 2 and classification['word_count'] < 50:
            return 'authors'
        elif 50 <= classification['word_count'] <= 500:
            return 'content'
        elif classification['word_count'] < 3:
            return 'noise'
        else:
            return 'unknown'
    
    def _calculate_confidence(self, classification: Dict) -> float:
        """Calculate confidence score for classification."""
        confidence = 0.5  # Base confidence
        
        # Boost for strong signals
        if classification['is_boilerplate']:
            confidence = 0.95
        elif classification['is_email'] or classification['is_url']:
            confidence = 0.95
        elif classification['is_doi']:
            confidence = 0.9
        
        # Boost from semantic similarity
        if self.use_semantic and classification['semantic_best_match'][1] > 0.6:
            confidence = max(confidence, classification['semantic_best_match'][1])
        
        # Boost from spaCy NER
        if self.use_spacy:
            if classification['spacy_persons'] >= 2 and classification['likely_type'] == 'authors':
                confidence = max(confidence, 0.8)
            if classification['spacy_orgs'] >= 1 and classification['likely_type'] == 'affiliation':
                confidence = max(confidence, 0.75)
        
        return min(confidence, 1.0)
    
    def preprocess_blocks(self, text_blocks: List[Dict]) -> List[Dict]:
        """
        Preprocess and classify all text blocks.
        
        Returns:
            Enriched text blocks with classification info
        """
        enriched_blocks = []
        
        for block in text_blocks:
            # Skip very short blocks
            if len(block['text'].split()) < 2:
                continue
            
            # Classify the block
            classification = self.classify_line(
                block['text'],
                block['position'],
                block['font_size']
            )
            
            # Merge classification into block
            enriched_block = {**block, **classification}
            enriched_blocks.append(enriched_block)
        
        return enriched_blocks
    
    def extract_title(self, blocks: List[Dict]) -> Optional[str]:
        """Extract title using semantic understanding."""
        
        # Filter candidates
        candidates = []
        
        for block in blocks[:20]:
            if block['page'] > 0:
                break
            
            # Skip boilerplate
            if block.get('likely_type') in ['boilerplate', 'contact_info', 'noise']:
                continue
            
            # Title criteria
            if (5 <= block['word_count'] <= 50 and 
                block['position'] == 'body' and
                block['font_size'] > 10):
                
                score = block['font_size']
                
                # Boost for semantic match
                if self.use_semantic and 'semantic_scores' in block:
                    score += block['semantic_scores'].get('title', 0) * 50
                
                # Penalty for too many names
                if block['has_names'] > 3:
                    score *= 0.5
                
                candidates.append({
                    'text': block['text'],
                    'score': score,
                    'confidence': block.get('confidence', 0.5)
                })
        
        if not candidates:
            return None
        
        # Sort by score
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        return candidates[0]['text'] if candidates[0]['confidence'] > 0.4 else None
    
    def extract_authors(self, blocks: List[Dict], title: Optional[str]) -> List[str]:
        """Extract authors using NLP and semantic analysis."""
        authors = []
        seen = set()
        
        title_found = False
        
        for block in blocks[:30]:
            if block['page'] > 0:
                break
            
            # Check if past title
            if title and title in block['text']:
                title_found = True
                continue
            
            if not title_found:
                continue
            
            # Stop at abstract
            if block.get('likely_type') == 'abstract' or re.search(r'\babstract\b', block['text'], re.I):
                break
            
            # Stop at affiliations
            if block.get('likely_type') == 'affiliation' and block['word_count'] > 10:
                break
            
            # Look for author blocks
            if block.get('likely_type') == 'authors' or (
                block['has_names'] >= 1 and 
                block['word_count'] < 50 and
                block.get('spacy_persons', 0) >= 1
            ):
                # Use spaCy to extract names
                if self.use_spacy and 'spacy_entities' in block:
                    persons = block['spacy_entities'].get('persons', [])
                    for person in persons:
                        clean_name = re.sub(r'\d+', '', person).strip()
                        if clean_name and len(clean_name) > 3 and clean_name not in seen:
                            authors.append(clean_name)
                            seen.add(clean_name)
                
                # Fallback to regex
                if not authors or len(authors) < 3:
                    names = re.findall(self.patterns['name_pattern'], block['text'])
                    for name in names:
                        if name not in seen:
                            authors.append(name)
                            seen.add(name)
        
        return authors[:10]
    
    def extract_affiliations(self, blocks: List[Dict]) -> List[str]:
        """Extract affiliations using NLP."""
        affiliations = []
        seen = set()
        
        for block in blocks[:40]:
            if block['page'] > 0:
                break
            
            if re.search(r'\babstract\b', block['text'], re.I):
                break
            
            # Look for affiliation blocks
            if block.get('likely_type') == 'affiliation' or (
                block['is_institution'] and 
                5 <= block['word_count'] <= 50
            ):
                # Use spaCy organizations
                if self.use_spacy and 'spacy_entities' in block:
                    orgs = block['spacy_entities'].get('organizations', [])
                    for org in orgs:
                        if org not in seen and len(org) > 5:
                            affiliations.append(org)
                            seen.add(org)
                
                # Also add full text if it looks good
                clean_text = re.sub(r'^\d+\s*', '', block['text']).strip()
                if clean_text not in seen and len(clean_text) > 10:
                    affiliations.append(clean_text)
                    seen.add(clean_text)
        
        return affiliations[:10]
    
    def extract_abstract(self, blocks: List[Dict], full_text: str) -> Optional[str]:
        """Extract abstract using semantic similarity."""
        
        # Try semantic approach first
        if self.use_semantic:
            for block in blocks[:50]:
                if (block.get('likely_type') == 'abstract' or 
                    (50 <= block['word_count'] <= 500 and 
                     block.get('semantic_scores', {}).get('abstract', 0) > 0.5)):
                    
                    return block['text']
        
        # Fallback to regex
        patterns = [
            r'(?i)abstract\s*[:\-]?\s*(.*?)\n\s*(?:keywords?|introduction|1\.|i\.|background)',
            r'(?i)abstract\s*[:\-]?\s*(.*?)\n\s*\n',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, full_text, re.S)
            if match:
                abstract = match.group(1).strip()
                abstract = re.sub(r'\s+', ' ', abstract)
                word_count = len(abstract.split())
                if 50 <= word_count <= 1000:
                    return abstract
        
        return None
    
    def extract_keywords(self, blocks: List[Dict], full_text: str) -> List[str]:
        """Extract keywords."""
        
        # Try semantic approach
        if self.use_semantic:
            for block in blocks[:50]:
                if (block.get('semantic_scores', {}).get('keywords', 0) > 0.5 and
                    3 <= block['word_count'] <= 50):
                    keywords = re.split(r'[;,•\n]', block['text'])
                    keywords = [k.strip() for k in keywords if k.strip()]
                    if len(keywords) >= 3:
                        return keywords[:15]
        
        # Fallback to regex
        patterns = [
            r'(?i)keywords?\s*[:\-]?\s*(.*?)(?:\n\s*\n|introduction|1\.)',
            r'(?i)index terms\s*[:\-]?\s*(.*?)(?:\n\s*\n|introduction)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, full_text, re.S)
            if match:
                keywords_text = match.group(1).strip()
                keywords = re.split(r'[;,•\n]', keywords_text)
                keywords = [k.strip() for k in keywords if k.strip()]
                keywords = [k for k in keywords if 2 <= len(k.split()) <= 8]
                return keywords[:15]
        
        return []
    
    def extract_year(self, full_text: str, blocks: List[Dict]) -> Optional[str]:
        """Extract publication year."""
        
        # Check header/footer
        for block in blocks[:10] + blocks[-5:]:
            if block['position'] in ['header', 'footer']:
                years = re.findall(self.patterns['year'], block['text'])
                if years:
                    years = [int(y) for y in years if 1950 <= int(y) <= 2030]
                    if years:
                        return str(max(years))
        
        # Use spaCy DATE entities
        if self.use_spacy:
            entities = self.extract_entities_with_spacy(full_text[:2000])
            for date in entities.get('dates', []):
                years = re.findall(self.patterns['year'], date)
                if years:
                    years = [int(y) for y in years if 1950 <= int(y) <= 2030]
                    if years:
                        return str(max(years))
        
        # Fallback
        years = re.findall(self.patterns['year'], full_text[:1000])
        if years:
            years = [int(y) for y in years if 1950 <= int(y) <= 2030]
            if years:
                return str(max(years))
        
        return None
    
    def extract_publication_info(self, full_text: str, blocks: List[Dict]) -> Optional[str]:
        """Extract publication venue."""
        
        # Check semantic classification
        if self.use_semantic:
            for block in blocks[:20]:
                if (block.get('semantic_scores', {}).get('publication', 0) > 0.5 or
                    block.get('is_publisher') or block.get('is_doi')):
                    
                    # Extract publisher name
                    text_lower = block['text'].lower()
                    for pattern, name in [
                        ('ieee', 'IEEE Publication'),
                        ('springer', 'Springer'),
                        ('elsevier', 'Elsevier'),
                        ('acm', 'ACM Digital Library'),
                        ('arxiv', 'arXiv Preprint'),
                        ('nature', 'Nature Publishing'),
                        ('wiley', 'Wiley'),
                    ]:
                        if pattern in text_lower:
                            return name
                    
                    # Check for DOI
                    doi_match = re.search(self.patterns['doi'], block['text'], re.I)
                    if doi_match:
                        return f"DOI: {doi_match.group(0)}"
        
        # Fallback to regex search
        header_footer = " ".join([b['text'] for b in blocks[:10] + blocks[-5:] if b['position'] in ['header', 'footer']])
        text_to_search = (header_footer + " " + full_text[:2000]).lower()
        
        publishers = {
            'ieee': 'IEEE Publication',
            'springer': 'Springer',
            'elsevier': 'Elsevier',
            'acm': 'ACM Digital Library',
            'arxiv': 'arXiv Preprint',
            'nature': 'Nature Publishing',
            'wiley': 'Wiley',
        }
        
        for key, value in publishers.items():
            if key in text_to_search:
                return value
        
        doi_match = re.search(self.patterns['doi'], text_to_search, re.I)
        if doi_match:
            return f"DOI: {doi_match.group(0)}"
        
        return None
    
    def extract_with_pymupdf(self, pdf_path: str) -> Dict:
        """
        Main extraction method with NLP and semantic analysis.
        """
        doc = fitz.open(pdf_path)
        folder_name = os.path.basename(os.path.dirname(pdf_path))
        
        # Extract text
        full_text, text_blocks = self.extract_top_words(doc)
        
        # Preprocess and classify blocks
        enriched_blocks = self.preprocess_blocks(text_blocks)
        
        # Extract metadata using enriched blocks
        title = self.extract_title(enriched_blocks)
        authors = self.extract_authors(enriched_blocks, title)
        affiliations = self.extract_affiliations(enriched_blocks)
        abstract = self.extract_abstract(enriched_blocks, full_text)
        keywords = self.extract_keywords(enriched_blocks, full_text)
        year = self.extract_year(full_text, enriched_blocks)
        venue = self.extract_publication_info(full_text, enriched_blocks)
        
        doc.close()
        
        result = {
            "title": title,
            "authors": authors,
            "affiliations": affiliations,
            "abstract": abstract,
            "keywords": keywords,
            "year": year,
            "venue": venue,
            "folder_context": folder_name,
            "extraction_method": "pymupdf-nlp-semantic-v3",
            "nlp_features_used": {
                "spacy_ner": self.use_spacy,
                "semantic_similarity": self.use_semantic
            }
        }
        
        return result
    
    
    def extract_pdfs_in_folder(self, folder_path: str) -> Dict:
        """
        Process all PDFs in a folder using the PyMuPDF extractor.
        """
        results = {}
        pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))

        if not pdf_files:
            print(f"No PDF files found in: {folder_path}")
            return {}

        print(f"Found {len(pdf_files)} PDFs in folder. Starting extraction...\n")

        for pdf_path in pdf_files:
            file_name = os.path.basename(pdf_path)
            print(f"\n===Processing {file_name} =====")

            try:
                metadata = self.extract_with_pymupdf(pdf_path)
                print(f" Successfully extracted metadata for {file_name}")
            except Exception as e:
                print(f" Error processing {file_name}: {e}")
                metadata = {"error": str(e)}

            results[file_name] = metadata

        print("\n Folder extraction completed.")
        return results

# Example usage
if __name__ == "__main__":
    # Initialize with NLP features
    extractor = PDFMetadataExtractor(
        top_n_words=3000,
        use_semantic=True,
        use_spacy=True
    )
    
    # Process single PDF
    result = extractor.extract_pdfs_in_folder("D:\\Gomathi_ai\\Dataset\\Dataset\\Amit Saxena")
    
    import json
    print(json.dumps(result, indent=2))
    
    # Batch processing
    import glob
    results = {}
    for pdf_file in glob.glob("papers/**/*.pdf", recursive=True):
        try:
            results[os.path.basename(pdf_file)] = extractor.extract_with_pymupdf(pdf_file)
            print(f" Processed: {pdf_file}")
        except Exception as e:
            print(f" Error processing {pdf_file}: {e}")
    
    # Save results
    with open("extracted_metadata.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)