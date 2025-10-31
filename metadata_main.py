# """
# Main Metadata Pipeline
# ----------------------
# Processes research PDFs organized by author folders:
#   base_folder/
#     ├── Author_1/
#     │    ├── paper1.pdf
#     │    ├── paper2.pdf
#     ├── Author_2/
#          ├── paperA.pdf

# For each author:
# - Extracts PDF metadata
# - Extracts keywords (RAKE, KeyBERT)
# - Extracts topics (LDA, NMF)
# - Extracts named entities & domain terms (NER)
# - Stores structured JSON results in Redis
# """

# import os
# import json
# import redis
# import traceback
# from datetime import datetime
# from typing import Dict, List

# #  Import existing extraction functions
# from basic_metadata import extract_with_pymupdf
# from keywords_metadata import extract_keywords_all_methods
# from topic_metadata import extract_topics
# from ner_metadata import extract_ner_metadata


# # =============================
# # Redis Connection Setup
# # =============================
# def connect_redis(host='localhost', port=6379, db=0, decode_responses=True):
#     """Initialize Redis connection with error handling."""
#     try:
#         r = redis.Redis(host=host, port=port, db=db, decode_responses=decode_responses)
#         r.ping()
#         print(" Connected to Redis successfully.")
#         return r
#     except redis.ConnectionError as e:
#         print(f" Redis connection failed: {e}")
#         return None


# # =============================
# # PDF + Author Processing
# # =============================
# def process_pdf(pdf_path: str) -> Dict:
#     """Extracts metadata, keywords, topics, and entities for one PDF."""
#     try:
#         # Step 1: Extract basic metadata
#         metadata = extract_with_pymupdf(pdf_path)

#         # Step 2: Read text content
#         import fitz
#         doc = fitz.open(pdf_path)
#         text = ""
#         for page in doc:
#             text += page.get_text("text")
#             if len(text) > 200000:  # prevent memory issues
#                 break
#         doc.close()

#         # Step 3: Extract keywords
#         keywords = extract_keywords_all_methods(text)

#         # Step 4: Extract topics
#         topics = extract_topics(text)

#         # Step 5: Extract NER metadata
#         ner = extract_ner_metadata(text)

#         # Step 6: Combine results
#         return {
#             "pdf_name": os.path.basename(pdf_path),
#             "metadata": metadata,
#             "keywords": keywords,
#             "topics": topics,
#             "ner": ner,
#             "processed_at": datetime.now().isoformat()
#         }

#     except Exception as e:
#         print(f"[ERROR] Failed to process {pdf_path}: {e}")
#         traceback.print_exc()
#         return {
#             "pdf_name": os.path.basename(pdf_path),
#             "error": str(e)
#         }


# def process_author_folder(author_folder: str) -> Dict:
#     """Processes all PDFs in one author’s folder."""
#     author_name = os.path.basename(author_folder)
#     pdfs = [os.path.join(author_folder, f)
#             for f in os.listdir(author_folder)
#             if f.lower().endswith(".pdf")]

#     if not pdfs:
#         print(f"[WARNING] No PDFs found in folder: {author_folder}")
#         return {"author": author_name, "papers": []}

#     author_results = []
#     for pdf_path in pdfs:
#         print(f" Processing {pdf_path} ...")
#         author_results.append(process_pdf(pdf_path))

#     return {
#         "author": author_name,
#         "paper_count": len(author_results),
#         "papers": author_results,
#         "processed_at": datetime.now().isoformat()
#     }


# # =============================
# # Main Function
# # =============================
# def main(base_folder: str, redis_client=None, redis_prefix="author_metadata"):
#     """
#     Processes all authors under base_folder and stores results in Redis.
#     Key format in Redis:
#         author_metadata:<author_name>
#     """
#     if not redis_client:
#         redis_client = connect_redis()
#         if not redis_client:
#             raise RuntimeError("Cannot proceed without Redis connection.")

#     if not os.path.isdir(base_folder):
#         raise ValueError(f"Invalid base folder: {base_folder}")

#     print(f" Scanning author folders in: {base_folder}")

#     all_authors_data = {}
#     author_folders = [os.path.join(base_folder, d)
#                       for d in os.listdir(base_folder)
#                       if os.path.isdir(os.path.join(base_folder, d))]

#     for author_folder in author_folders:
#         author_data = process_author_folder(author_folder)
#         author_name = author_data.get("author", "unknown_author")
#         key = f"{redis_prefix}:{author_name}"

#         # Save in Redis
#         try:
#             redis_client.set(key, json.dumps(author_data, indent=2))
#             print(f"Stored {author_name} → Redis key: {key}")
#         except Exception as e:
#             print(f"[ERROR] Redis store failed for {author_name}: {e}")

#         all_authors_data[author_name] = author_data

#     # Store combined dataset
#     combined_key = f"{redis_prefix}:_combined_all"
#     redis_client.set(combined_key, json.dumps(all_authors_data, indent=2))
#     print(f" Combined metadata stored in Redis key: {combined_key}")

#     return all_authors_data


# # =============================
# # Entry Point
# # =============================
# if __name__ == "__main__":
#     BASE_FOLDER = "D:/Gomathi_ai"  # Update this path as needed
#     redis_client = connect_redis()
#     results = main(BASE_FOLDER, redis_client)
#     print("\n Processing complete. Example keys in Redis:")
#     for key in redis_client.keys("author_metadata:*"):
#         print(" -", key)


"""
Research PDF Metadata Pipeline
------------------------------
Folder format expected:

D:/Gomathi_ai/
    └── Dataset/
          ├── Author1/
          │     ├── paper1.pdf
          │     └── paper2.pdf
          └── Author2/
                └── paperA.pdf
"""

import os
import json
import redis
import traceback
from datetime import datetime
from typing import Dict

# Force UTF-8 console output (Windows safe)
import sys, io
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception:
    pass

# Import your extraction functions
from basic_metadata import extract_with_pymupdf
from keywords_metadata import extract_keywords_all_methods
from topic_metadata import extract_topics
from ner_metadata import extract_ner_metadata


# -----------------------------------
# Redis Connection
# -----------------------------------
def connect_redis(host="localhost", port=6379, db=0, decode_responses=True):
    try:
        r = redis.Redis(host=host, port=port, db=db, decode_responses=decode_responses)
        r.ping()
        print("[INFO] Connected to Redis successfully.")
        return r
    except Exception as e:
        print(f"[ERROR] Redis connection failed: {e}")
        return None


# -----------------------------------
# Process One PDF
# -----------------------------------
def process_pdf(pdf_path: str) -> Dict:
    try:
        # 1. Basic metadata
        metadata = extract_with_pymupdf(pdf_path)

        # 2. Extract text
        import fitz
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text")
            if len(text) > 200000:
                break
        doc.close()

        # 3. NLP extractors
        keywords = extract_keywords_all_methods(text)
        topics = extract_topics(text)
        ner = extract_ner_metadata(text)

        return {
            "pdf_name": os.path.basename(pdf_path),
            "metadata": metadata,
            "keywords": keywords,
            "topics": topics,
            "ner": ner,
            "processed_at": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"[ERROR] Failed to process PDF {pdf_path}: {e}")
        traceback.print_exc()
        return {"pdf_name": os.path.basename(pdf_path), "error": str(e)}


# -----------------------------------
# Process Author Folder
# -----------------------------------
def process_author_folder(author_folder: str) -> Dict:
    author_name = os.path.basename(author_folder)

    pdfs = [
        os.path.join(author_folder, f)
        for f in os.listdir(author_folder)
        if f.lower().endswith(".pdf")
    ]

    if not pdfs:
        print(f"[WARNING] No PDFs found for author: {author_name}")
        return {"author": author_name, "papers": []}

    results = []
    for pdf in pdfs:
        print(f"[INFO] Processing PDF: {pdf}")
        results.append(process_pdf(pdf))

    return {
        "author": author_name,
        "paper_count": len(results),
        "papers": results,
        "processed_at": datetime.now().isoformat()
    }


# -----------------------------------
# Main Pipeline
# -----------------------------------
def main(base_folder: str, redis_client=None, redis_prefix="author_metadata"):

    # Normalize path (Windows safe)
    base_folder = os.path.normpath(base_folder)

    if not redis_client:
        redis_client = connect_redis()
        if not redis_client:
            raise RuntimeError("Cannot continue without Redis")

    if not os.path.isdir(base_folder):
        raise ValueError(f"Invalid folder: {base_folder}")

    # Auto-enter Dataset folder
    dataset_path = os.path.join(base_folder, "Dataset")
    if os.path.isdir(dataset_path):
        print(f"[INFO] Found Dataset folder. Using: {dataset_path}")
        base_folder = dataset_path

    print(f"[INFO] Scanning author folders in: {base_folder}")

    ignore = {"__pycache__", "venv", "env", "dataset"}

    author_folders = [
        os.path.join(base_folder, d)
        for d in os.listdir(base_folder)
        if os.path.isdir(os.path.join(base_folder, d))
        and d.lower() not in ignore
    ]

    all_data = {}

    for folder in author_folders:
        author_data = process_author_folder(folder)
        author_name = author_data.get("author", "unknown")

        key = f"{redis_prefix}:{author_name}"
        try:
            redis_client.set(key, json.dumps(author_data, indent=2))
            print(f"[INFO] Stored author '{author_name}' -> key: {key}")
        except Exception as e:
            print(f"[ERROR] Redis store failed for {author_name}: {e}")

        all_data[author_name] = author_data

    # Store combined metadata
    combined_key = f"{redis_prefix}:_combined_all"
    redis_client.set(combined_key, json.dumps(all_data, indent=2))
    print(f"[SUCCESS] Stored combined metadata -> key: {combined_key}")

    return all_data


# -----------------------------------
# Run Script
# -----------------------------------
if __name__ == "__main__":
    BASE_FOLDER = r"D:/Gomathi_ai/Dataset"  # <- IMPORTANT: base only, script finds Dataset/
    redis_client = connect_redis()
    results = main(BASE_FOLDER, redis_client)

    print("\n[INFO] Redis keys created:")
    for key in redis_client.keys("author_metadata:*"):
        print(" -", key)
