import math
import fitz
import re
import os
from typing import Dict, List, Tuple, Optional, Set
from collections import Counter, defaultdict
import warnings
import glob

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
    warnings.warn("spaCy not available.")

try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    semantic_model = None
    warnings.warn("sentence-transformers not available.")


class PDFMetadataExtractor:
    """Enhanced PDF metadata extraction with comprehensive fixes."""
    
    def __init__(self, top_n_words: int = 4000, use_semantic: bool = True, use_spacy: bool = True):
        self.top_n_words = top_n_words
        self.use_semantic = use_semantic and SENTENCE_TRANSFORMERS_AVAILABLE
        self.use_spacy = use_spacy and SPACY_AVAILABLE
        
        # Enhanced patterns
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'url': r'https?://[^\s]+',
            'doi': r'10\.\d{4,9}/[-._;()/:A-Z0-9]+',
            'year': r'\b(19|20)\d{2}\b',
            'arxiv': r'arXiv:\d+\.\d+',
            'issn': r'ISSN\s*:?\s*\d{4}-?\d{3}[\dX]',
            'university': r'\b(university|institute|college|school|department|lab|laboratory|centre|center|hospital|medical)\b',
            'publisher': r'\b(ieee|springer|elsevier|acm|nature|wiley|science|plos|oxford|cambridge|sage|taylor|francis|pnas|circulation|arthritis)\b',
            'name_pattern': r'\b[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]+)?\b',
            
            # Enhanced boilerplate detection
            'boilerplate': r'\b(copyright|rights reserved|downloaded from|view the article|see discussions|citation|received|accepted|published|see terms|open access|editorial see|clinical perspective|study highlights|article in|correspondence to|address for|to cite this article|all content following|permissions|license|creative commons)\b',
            
            # Superscript patterns
            'superscript': r'[¹²³⁴⁵⁶⁷⁸⁹⁰†‡§¶*#]+|\d+[,;†‡§¶*]',
            
            # ResearchGate/download page patterns
            'researchgate': r'researchgate\.net|see discussions.*author profiles|publications.*citations|reads|see profile',
            
            # Journal header patterns
            'journal_header': r'\b(vol\.|volume|no\.|number|pp\.|pages|doi:|issn)\b',
            
            # Multi-author separator patterns
            'author_separators': r'[,;](?:\s*and\s*)?',
        }
        
        # Semantic references
        if self.use_semantic:
            self.semantic_references = {
                'title': [
                    "main research title of academic paper",
                    "article title scientific study",
                    "paper title research topic"
                ],
                'author': [
                    "list of author names with affiliations numbers",
                    "researcher contributors comma separated",
                    "scientists who wrote paper"
                ],
                'affiliation': [
                    "university department institution address",
                    "research center laboratory location",
                    "academic institution affiliation"
                ],
                'abstract': [
                    "abstract summary research findings methods results",
                    "study overview background methodology conclusions",
                    "paper summary scientific abstract"
                ],
                'keywords': [
                    "keywords index terms subject tags",
                    "research topics classification terms",
                    "subject headings key phrases"
                ],
                'publication': [
                    "journal name conference proceedings",
                    "publisher venue publication",
                    "where published journal title"
                ],
                'boilerplate': [
                    "copyright notice legal disclaimer",
                    "downloaded from website URL",
                    "view article online permissions"
                ]
            }
            
            self.semantic_embeddings = {}
            for category, texts in self.semantic_references.items():
                self.semantic_embeddings[category] = semantic_model.encode(texts, convert_to_tensor=True)
    
    def clean_text(self, text: str) -> str:
        """Remove superscripts, artifacts, and normalize text."""
        # Remove superscript markers
        text = re.sub(r'[¹²³⁴⁵⁶⁷⁸⁹⁰†‡§¶*#]+', '', text)
        # Remove numbered affiliations (1, 2,)
        text = re.sub(r'(?<=[A-Za-z])\s*\d+\s*[,;]\s*', ' ', text)
        # Remove standalone affiliation numbers
        text = re.sub(r'\b\d+\s*(?=[A-Z][a-z])', '', text)
        # Fix unicode artifacts
        text = text.replace('\ufb01', 'fi').replace('\ufb02', 'fl')
        text = text.replace('\u00ad', '').replace('\u2013', '-').replace('\u2014', '-')
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def is_researchgate_page(self, text: str) -> bool:
        """Detect ResearchGate or download pages."""
        return bool(re.search(self.patterns['researchgate'], text, re.I))
    
    def has_author_list_pattern(self, text: str) -> bool:
        """Detect author list patterns."""
        # Many commas (author lists have lots of commas)
        if text.count(',') >= 4:
            return True
        
        # Has superscript markers
        if re.search(r'[¹²³⁴⁵⁶⁷⁸⁹⁰†‡§¶*]|\d+[,;†]', text):
            return True
        
        # Contains "and" with commas (typical author list)
        if ', and ' in text.lower() or '; and ' in text.lower():
            return True
        
        # Multiple short capitalized sequences
        cap_sequences = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z]\.)*\s+[A-Z][a-z]+', text)
        if len(cap_sequences) >= 3:
            return True
        
        return False
    
    def is_journal_header(self, text: str) -> bool:
        """Detect journal header lines."""
        return bool(re.search(self.patterns['journal_header'], text, re.I))
    
    def extract_top_words(self, doc: fitz.Document) -> Tuple[str, List[Dict]]:
        """Extract first N words with structure detection."""
        words_collected = 0
        text_blocks = []
        full_text = ""
        
        # Skip ResearchGate pages
        start_page = 0
        if doc.page_count > 0:
            first_page_text = doc[0].get_text("text")[:800]
            if self.is_researchgate_page(first_page_text):
                print("   ️  Detected ResearchGate page, skipping to page 2")
                start_page = 1
        
        for page_num in range(start_page, min(doc.page_count, 3)):  # Check first 3 pages
            if words_collected >= self.top_n_words:
                break
            
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            page_height = page.rect.height
            
            for block in blocks:
                if "lines" not in block:
                    continue
                
                block_text = ""
                block_bbox = block["bbox"]
                max_font = 0
                font_sizes = []
                
                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        line_text += span["text"]
                        font_size = span.get("size", 0)
                        max_font = max(max_font, font_size)
                        font_sizes.append(font_size)
                    
                    block_text += line_text.strip() + " "
                
                block_text = block_text.strip()
                if not block_text:
                    continue
                
                words_in_block = len(block_text.split())
                words_collected += words_in_block
                
                # Determine position (more granular)
                y_top = block_bbox[1]
                y_bottom = block_bbox[3]
                
                if y_top < 80:
                    position = "header"
                elif y_bottom > page_height - 80:
                    position = "footer"
                elif y_top < page_height * 0.2:
                    position = "top"
                elif y_top > page_height * 0.8:
                    position = "bottom"
                else:
                    position = "body"
                
                text_blocks.append({
                    "text": block_text,
                    "text_clean": self.clean_text(block_text),
                    "bbox": block_bbox,
                    "page": page_num,
                    "font_size": max_font,
                    "avg_font_size": sum(font_sizes) / len(font_sizes) if font_sizes else 10,
                    "position": position,
                })
                
                full_text += block_text + "\n"
                
                if words_collected >= self.top_n_words:
                    break
        
        return full_text, text_blocks
    
    def extract_entities_with_spacy(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities using spaCy."""
        if not self.use_spacy or not text:
            return {}
        
        doc = nlp(text[:100000])
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
        """Calculate semantic similarity."""
        if not self.use_semantic or category not in self.semantic_embeddings:
            return 0.0
        
        text_embedding = semantic_model.encode(text, convert_to_tensor=True)
        similarities = util.cos_sim(text_embedding, self.semantic_embeddings[category])
        return float(similarities.max())
    
    def classify_line(self, text: str, text_clean: str, position: str, font_size: float, avg_font: float) -> Dict:
        """Comprehensive line classification."""
        text_lower = text.lower()
        
        classification = {
            'is_email': bool(re.search(self.patterns['email'], text)),
            'is_url': bool(re.search(self.patterns['url'], text)),
            'is_doi': bool(re.search(self.patterns['doi'], text, re.I)),
            'is_arxiv': bool(re.search(self.patterns['arxiv'], text)),
            'has_year': bool(re.search(self.patterns['year'], text)),
            'is_institution': bool(re.search(self.patterns['university'], text_lower)),
            'is_publisher': bool(re.search(self.patterns['publisher'], text_lower)),
            'is_boilerplate': bool(re.search(self.patterns['boilerplate'], text_lower)),
            'is_journal_header': self.is_journal_header(text),
            'has_superscript': bool(re.search(self.patterns['superscript'], text)),
            'has_author_pattern': self.has_author_list_pattern(text),
            'has_names': len(re.findall(self.patterns['name_pattern'], text)),
            'word_count': len(text.split()),
            'comma_count': text.count(','),
            'semicolon_count': text.count(';'),
            'position': position,
            'font_size': font_size,
            'avg_font_size': avg_font,
        }
        
        # SpaCy NER
        if self.use_spacy and 3 <= classification['word_count'] <= 150:
            entities = self.extract_entities_with_spacy(text_clean)
            classification['spacy_persons'] = len(entities.get('persons', []))
            classification['spacy_orgs'] = len(entities.get('organizations', []))
            classification['spacy_entities'] = entities
        else:
            classification['spacy_persons'] = 0
            classification['spacy_orgs'] = 0
            classification['spacy_entities'] = {}
        
        # Semantic scores
        if self.use_semantic and classification['word_count'] >= 3:
            semantic_scores = {}
            for category in ['title', 'author', 'affiliation', 'abstract', 'keywords', 'publication', 'boilerplate']:
                semantic_scores[category] = self.get_semantic_similarity(text_clean, category)
            
            classification['semantic_scores'] = semantic_scores
            classification['semantic_best_match'] = max(semantic_scores.items(), key=lambda x: x[1])
        else:
            classification['semantic_scores'] = {}
            classification['semantic_best_match'] = (None, 0.0)
        
        classification['likely_type'] = self._determine_likely_type(classification)
        classification['confidence'] = self._calculate_confidence(classification)
        
        return classification
    
    def _determine_likely_type(self, c: Dict) -> str:
        """Enhanced type determination with multi-signal fusion."""
        
        # Priority 1: Strong negative signals
        if c['is_boilerplate'] or c['is_journal_header']:
            return 'boilerplate'
        
        if c['is_email'] or c['is_url']:
            return 'contact_info'
        
        # Priority 2: Author list detection (CRITICAL)
        if c['has_author_pattern'] and c['word_count'] < 100:
            return 'authors'
        
        # Priority 3: Semantic + validation
        if self.use_semantic and c['semantic_best_match'][1] > 0.4:
            sem_type, sem_score = c['semantic_best_match']
            
            # Title: strict validation
            if sem_type == 'title':
                # Reject if looks like authors
                if c['has_author_pattern'] or c['comma_count'] >= 3:
                    return 'authors'
                # Reject if has superscripts
                if c['has_superscript']:
                    return 'authors'
                # Accept if reasonable length and not institution
                if 5 <= c['word_count'] <= 60 and not c['is_institution']:
                    return 'title'
            
            # Authors
            elif sem_type == 'author':
                if c['has_names'] >= 1 or c['spacy_persons'] >= 1:
                    return 'authors'
            
            # Affiliation
            elif sem_type == 'affiliation':
                if c['is_institution'] or c['spacy_orgs'] >= 1:
                    return 'affiliation'
            
            # Abstract
            elif sem_type == 'abstract':
                if 50 <= c['word_count'] <= 600:
                    return 'abstract'
            
            # Keywords/Publication
            elif sem_type in ['keywords', 'publication']:
                return sem_type
        
        # Priority 4: SpaCy signals
        if self.use_spacy:
            if c['spacy_persons'] >= 2 and c['word_count'] < 80:
                return 'authors'
            if c['spacy_orgs'] >= 1 and c['is_institution']:
                return 'affiliation'
        
        # Priority 5: Heuristic fallbacks
        if c['is_institution'] and 5 <= c['word_count'] <= 60:
            return 'affiliation'
        elif c['is_publisher'] or c['is_doi']:
            return 'publication_info'
        elif c['has_names'] >= 2 and c['word_count'] < 60:
            return 'authors'
        elif 50 <= c['word_count'] <= 600:
            return 'content'
        elif c['word_count'] < 3:
            return 'noise'
        
        return 'unknown'
    


    def _calculate_confidence(self, c: Dict) -> float:
        """Compute confidence score using a weighted, normalized combination of signals."""
        
        # === 1️⃣ Base rule-based confidence ===
        base_conf = 0.5  # neutral default
        
        if c.get('is_boilerplate') or c.get('is_journal_header'):
            base_conf = 0.95
        elif c.get('is_email') or c.get('is_url'):
            base_conf = 0.9
        elif c.get('is_doi'):
            base_conf = 0.85
        elif c.get('has_author_pattern'):
            base_conf = 0.75
        
        # === 2️⃣ Semantic similarity confidence ===
        semantic_conf = 0.0
        if self.use_semantic and 'semantic_best_match' in c:
            sem_score = c['semantic_best_match'][1]
            # Smooth scaling between 0.5 and 1.0 for sem_score in [0.4, 1.0]
            semantic_conf = max(0.0, min(1.0, (sem_score - 0.4) / 0.6))
        
        # === 3️⃣ Named Entity Recognition (NER) confidence ===
        ner_conf = 0.0
        if self.use_spacy:
            # Weight the number of recognized entities
            ner_conf = (
                0.05 * min(c.get('spacy_persons', 0), 4) + 
                0.03 * min(c.get('spacy_orgs', 0), 3)
            )
            ner_conf = min(ner_conf, 0.85)
        
        # === 4️⃣ Combine the scores using learned or tunable weights ===
        weights = {
            'base': 0.5,
            'semantic': 0.3,
            'ner': 0.2
        }
        
        weighted_sum = (
            weights['base'] * base_conf +
            weights['semantic'] * semantic_conf +
            weights['ner'] * ner_conf
        )
        
        # === 5️⃣ Normalize with a soft sigmoid for smooth scaling ===
        confidence = 1 / (1 + math.exp(-4 * (weighted_sum - 0.5)))
        
        return round(confidence, 3)

    
    def preprocess_blocks(self, text_blocks: List[Dict]) -> List[Dict]:
        """Preprocess and classify all blocks."""
        enriched_blocks = []
        
        for block in text_blocks:
            if len(block['text'].split()) < 2:
                continue
            
            classification = self.classify_line(
                block['text'],
                block['text_clean'],
                block['position'],
                block['font_size'],
                block['avg_font_size']
            )
            
            enriched_block = {**block, **classification}
            enriched_blocks.append(enriched_block)
        
        return enriched_blocks
    
    def extract_title(self, blocks: List[Dict]) -> Optional[str]:
        """Extract title with multi-stage filtering."""
        candidates = []
        
        for idx, block in enumerate(blocks[:30]):
            if block['page'] > 1:
                break
            
            # Skip bad types
            if block.get('likely_type') in ['boilerplate', 'contact_info', 'noise', 'authors', 'affiliation']:
                continue
            
            # Title criteria
            if not (4 <= block['word_count'] <= 60):
                continue
            
            if block['position'] not in ['body', 'top']:
                continue
            
            if block['font_size'] < 10:
                continue
            
            # Calculate score
            score = block['font_size'] * 1.5
            
            # Boost for semantic match
            if self.use_semantic:
                title_score = block.get('semantic_scores', {}).get('title', 0)
                author_score = block.get('semantic_scores', {}).get('author', 0)
                
                if title_score > author_score + 0.05:
                    score += title_score * 40
                else:
                    score *= 0.5  # Penalize if author score is close
            
            # Penalties
            if block['has_author_pattern']:
                score *= 0.2
            if block['has_superscript']:
                score *= 0.25
            if block['comma_count'] >= 3:
                score *= 0.3
            if block['is_institution']:
                score *= 0.2
            if block['has_names'] > 4:
                score *= 0.3
            if block['is_boilerplate']:
                score *= 0.1
            
            # Boost for early appearance
            if idx < 5:
                score *= 1.3
            elif idx < 10:
                score *= 1.1
            
            candidates.append({
                'text': block['text_clean'],
                'score': score,
                'confidence': block.get('confidence', 0.5),
                'idx': idx,
                'debug_info': {
                    'font_size': block['font_size'],
                    'word_count': block['word_count'],
                    'has_author_pattern': block['has_author_pattern'],
                    'semantic_title': block.get('semantic_scores', {}).get('title', 0),
                }
            })
        
        if not candidates:
            return None
        
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        best = candidates[0]
        # More lenient threshold
        return best['text'] if best['score'] > 5 and best['confidence'] > 0.3 else None
    
    def extract_authors(self, blocks: List[Dict], title: Optional[str]) -> List[str]:
        """Extract authors with fallback strategies."""
        authors = []
        seen = set()
        
        # Strategy 1: Look after title
        title_found = False
        title_idx = -1
        
        if title:
            for idx, block in enumerate(blocks[:40]):
                if title[:25] in block['text_clean']:
                    title_found = True
                    title_idx = idx
                    break
        
        # Strategy 2: If no title, look in early blocks
        start_idx = title_idx + 1 if title_found else 0
        
        for block in blocks[start_idx:50]:
            if block['page'] > 1:
                break
            
            # Stop at abstract
            if re.search(r'\babstract\b', block['text'], re.I) and block['word_count'] > 30:
                break
            
            # Identify author blocks
            is_author_block = (
                block.get('likely_type') == 'authors' or
                (block['has_names'] >= 1 and block['word_count'] < 100 and not block['is_institution']) or
                block['has_author_pattern'] or
                block['spacy_persons'] >= 2
            )
            
            if is_author_block:
                # Use spaCy
                if self.use_spacy and 'spacy_entities' in block:
                    persons = block['spacy_entities'].get('persons', [])
                    for person in persons:
                        clean_name = self.clean_text(person)
                        if clean_name and 5 < len(clean_name) < 40 and clean_name not in seen:
                            # Validate name (must have at least 2 parts)
                            if len(clean_name.split()) >= 2:
                                authors.append(clean_name)
                                seen.add(clean_name)
                
                # Regex fallback
                if len(authors) < 3:
                    names = re.findall(self.patterns['name_pattern'], block['text_clean'])
                    for name in names:
                        if name not in seen and 5 < len(name) < 40:
                            if len(name.split()) >= 2:
                                authors.append(name)
                                seen.add(name)
        
        return authors[:15]
    
    def extract_affiliations(self, blocks: List[Dict]) -> List[str]:
        """Extract affiliations."""
        affiliations = []
        seen = set()
        
        for block in blocks[:60]:
            if block['page'] > 1:
                break
            
            if re.search(r'\babstract\b', block['text'], re.I) and block['word_count'] > 30:
                break
            
            if block.get('likely_type') == 'affiliation' or (
                block['is_institution'] and 
                5 <= block['word_count'] <= 70
            ):
                # Use spaCy orgs
                if self.use_spacy and 'spacy_entities' in block:
                    orgs = block['spacy_entities'].get('organizations', [])
                    for org in orgs:
                        clean_org = self.clean_text(org)
                        if clean_org not in seen and len(clean_org) > 8:
                            affiliations.append(clean_org)
                            seen.add(clean_org)
                
                # Full text
                clean_text = self.clean_text(block['text'])
                if clean_text not in seen and 10 < len(clean_text) < 300:
                    affiliations.append(clean_text)
                    seen.add(clean_text)
        
        return affiliations[:12]
    
    def extract_abstract(self, blocks: List[Dict], full_text: str) -> Optional[str]:
        """Extract abstract with multiple strategies."""
        
        # Strategy 1: Semantic detection
        if self.use_semantic:
            for block in blocks[:80]:
                if block['page'] > 2:
                    break
                
                if (block.get('likely_type') == 'abstract' or 
                    (50 <= block['word_count'] <= 600 and 
                     block.get('semantic_scores', {}).get('abstract', 0) > 0.42)):
                    
                    return block['text_clean']
        
        # Strategy 2: Regex with flexible patterns
        patterns = [
            r'(?i)abstract\s*[:\-]?\s*(.*?)(?=\n\s*(?:keywords?|introduction|1\.|i\.|background|methods|\n\s*\n[A-Z]))',
            r'(?i)abstract\s*[:\-]?\s*(.*?)(?=\n\s*\n\s*[A-Z])',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, full_text, re.S)
            if match:
                abstract = match.group(1).strip()
                abstract = self.clean_text(abstract)
                abstract = re.sub(r'\s+', ' ', abstract)
                word_count = len(abstract.split())
                
                if 40 <= word_count <= 1000:
                    return abstract
        
        return None
    
    def extract_keywords(self, blocks: List[Dict], full_text: str) -> List[str]:
        """Extract keywords."""
        
        # Semantic approach
        if self.use_semantic:
            for block in blocks[:80]:
                if block['page'] > 1:
                    break
                
                if (block.get('semantic_scores', {}).get('keywords', 0) > 0.48 and
                    3 <= block['word_count'] <= 80):
                    text = re.sub(r'(?i)^keywords?\s*:?\s*', '', block['text'])
                    keywords = re.split(r'[;,•\n]', text)
                    keywords = [self.clean_text(k) for k in keywords if k.strip()]
                    
                    if len(keywords) >= 2:
                        return keywords[:15]
        
        # Regex approach
        patterns = [
            r'(?i)keywords?\s*[:\-]?\s*(.*?)(?:\n\s*\n|introduction|1\.|\n\s*[A-Z])',
            r'(?i)index terms\s*[:\-]?\s*(.*?)(?:\n\s*\n|introduction)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, full_text, re.S)
            if match:
                kw_text = match.group(1).strip()
                keywords = re.split(r'[;,•\n]', kw_text)
                keywords = [self.clean_text(k) for k in keywords if k.strip()]
                keywords = [k for k in keywords if 2 <= len(k.split()) <= 10]
                
                if keywords:
                    return keywords[:15]
        
        return []
    
    def extract_year(self, full_text: str, blocks: List[Dict]) -> Optional[str]:
        """Extract publication year."""
        
        # Check headers/footers
        for block in blocks[:20] + blocks[-15:]:
            if block['position'] in ['header', 'footer', 'top', 'bottom']:
                years = re.findall(self.patterns['year'], block['text'])
                if years:
                    years = [int(y) for y in years if 1970 <= int(y) <= 2030]
                    if years:
                        return str(max(years))
        
        # SpaCy dates
        if self.use_spacy:
            entities = self.extract_entities_with_spacy(full_text[:4000])
            for date in entities.get('dates', []):
                years = re.findall(self.patterns['year'], date)
                if years:
                    years = [int(y) for y in years if 1970 <= int(y) <= 2030]
                    if years:
                        return str(max(years))
        
        # Fallback: first 2000 chars
        years = re.findall(self.patterns['year'], full_text[:2000])
        if years:
            years = [int(y) for y in years if 1970 <= int(y) <= 2030]
            if years:
                return str(max(years))
        
        return None
    
    def extract_publication_info(self, full_text: str, blocks: List[Dict]) -> Optional[str]:
        """Extract venue/publisher."""
        
        # Semantic approach
        if self.use_semantic:
            for block in blocks[:30]:
                if (block.get('semantic_scores', {}).get('publication', 0) > 0.5 or
                    block.get('is_publisher') or block.get('is_doi')):
                    
                    text_lower = block['text'].lower()
                    
                    # Check publishers
                    publishers = {
                        'ieee': 'IEEE Publication',
                        'springer': 'Springer',
                        'elsevier': 'Elsevier',
                        'acm': 'ACM Digital Library',
                        'arxiv': 'arXiv Preprint',
                        'nature': 'Nature Publishing',
                        'wiley': 'Wiley',
                        'pnas': 'PNAS',
                        'circulation': 'Circulation (AHA)',
                        'arthritis': 'Arthritis & Rheumatology',
                    }
                    
                    for key, value in publishers.items():
                        if key in text_lower:
                            return value
                    
                    # Check for DOI
                    doi_match = re.search(self.patterns['doi'], block['text'], re.I)
                    if doi_match:
                        return f"DOI: {doi_match.group(0)}"
        
        # Fallback: search header/footer
        header_footer = " ".join([b['text'] for b in blocks[:15] + blocks[-10:] 
                                   if b['position'] in ['header', 'footer', 'top', 'bottom']])
        text_to_search = (header_footer + " " + full_text[:3000]).lower()
        
        publishers = {
            'ieee': 'IEEE Publication',
            'springer': 'Springer',
            'elsevier': 'Elsevier',
            'acm': 'ACM Digital Library',
            'arxiv': 'arXiv Preprint',
            'nature': 'Nature Publishing',
            'wiley': 'Wiley',
            'pnas': 'PNAS',
            'circulation': 'Circulation (AHA)',
            'arthritis': 'Arthritis & Rheumatology',
            'journal of immunology': 'Journal of Immunology',
            'molecular and cellular': 'Molecular and Cellular Biochemistry',
        }
        
        for key, value in publishers.items():
            if key in text_to_search:
                return value
        
        # DOI fallback
        doi_match = re.search(self.patterns['doi'], text_to_search, re.I)
        if doi_match:
            return f"DOI: {doi_match.group(0)}"
        
        return None
    
    def extract_with_pymupdf(self, pdf_path: str) -> Dict:
        """Main extraction method with comprehensive error handling."""
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            return {
                "error": f"Failed to open PDF: {str(e)}",
                "extraction_method": "pymupdf-nlp-semantic-v4"
            }
        
        folder_name = os.path.basename(os.path.dirname(pdf_path))
        
        try:
            # Extract text
            full_text, text_blocks = self.extract_top_words(doc)
            
            if not text_blocks:
                doc.close()
                return {
                    "error": "No text blocks extracted",
                    "folder_context": folder_name,
                    "extraction_method": "pymupdf-nlp-semantic-v4"
                }
            
            # Preprocess and classify blocks
            enriched_blocks = self.preprocess_blocks(text_blocks)
            
            # Extract metadata
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
                "authors": authors if authors else [],
                "affiliations": affiliations if affiliations else [],
                "abstract": abstract,
                "keywords": keywords if keywords else [],
                "year": year,
                "venue": venue,
                "folder_context": folder_name,
                "extraction_method": "pymupdf-nlp-semantic-v4",
                "nlp_features_used": {
                    "spacy_ner": self.use_spacy,
                    "semantic_similarity": self.use_semantic
                },
                "extraction_quality": self._assess_quality(title, authors, abstract, year, venue)
            }
            
            return result
            
        except Exception as e:
            doc.close()
            return {
                "error": f"Extraction failed: {str(e)}",
                "folder_context": folder_name,
                "extraction_method": "pymupdf-nlp-semantic-v4"
            }
    
    def _assess_quality(self, title, authors, abstract, year, venue) -> str:
        """Assess extraction quality."""
        score = 0
        
        if title and len(title) > 10:
            score += 2
        if authors and len(authors) >= 1:
            score += 2
        if abstract and len(abstract) > 50:
            score += 2
        if year:
            score += 1
        if venue:
            score += 1
        
        if score >= 7:
            return "excellent"
        elif score >= 5:
            return "good"
        elif score >= 3:
            return "moderate"
        else:
            return "poor"
    
    def extract_pdfs_in_folder(self, folder_path: str) -> Dict:
        """Process all PDFs in a folder."""
        results = {}
        pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))

        if not pdf_files:
            print(f"No PDF files found in: {folder_path}")
            return {}

        print(f"Found {len(pdf_files)} PDFs in folder. Starting extraction...\n")

        for pdf_path in pdf_files:
            file_name = os.path.basename(pdf_path)
            print(f"\n{'='*60}")
            print(f"Processing: {file_name}")
            print(f"{'='*60}")

            try:
                metadata = self.extract_with_pymupdf(pdf_path)
                
                # Print extraction summary
                if "error" in metadata:
                    print(f"  Error: {metadata['error']}")
                else:
                    quality = metadata.get('extraction_quality', 'unknown')
                    print(f"    Quality: {quality.upper()}")
                    print(f"  Title: {'  ' if metadata.get('title') else '   '}")
                    print(f"  Authors: {len(metadata.get('authors', []))} found")
                    print(f"  Abstract: {'   ' if metadata.get('abstract') else '   '}")
                    print(f"  Year: {metadata.get('year', 'N/A')}")
                    print(f"  Venue: {metadata.get('venue', 'N/A')[:50]}")
                    
            except Exception as e:
                print(f"  Unexpected error: {e}")
                metadata = {"error": str(e)}

            results[file_name] = metadata

        print(f"\n{'='*60}")
        print("Folder extraction completed.")
        print(f"{'='*60}\n")
        
        # Summary statistics
        quality_counts = defaultdict(int)
        for data in results.values():
            if "error" not in data:
                quality = data.get('extraction_quality', 'unknown')
                quality_counts[quality] += 1
        
        print("\n Extraction Quality Summary:")
        for quality in ['excellent', 'good', 'moderate', 'poor', 'unknown']:
            count = quality_counts.get(quality, 0)
            if count > 0:
                print(f"  {quality.capitalize()}: {count}")
        
        return results


# Example usage
if __name__ == "__main__":
    import json
    
    # Initialize extractor with enhanced settings
    extractor = PDFMetadataExtractor(
        top_n_words=4000,  # Increased to capture more content
        use_semantic=True,
        use_spacy=True
    )
    
    # Process folder
    folder_path = "D:\\Gomathi_ai\\Dataset\\Dataset\\Amit Saxena"
    results = extractor.extract_pdfs_in_folder(folder_path)
    
    # Save results
    output_file = "extracted_metadata_v4.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n    Results saved to: {output_file}")
    
    # Generate detailed report
    print("\n" + "="*60)
    print("DETAILED EXTRACTION REPORT")
    print("="*60)
    
    for filename, data in results.items():
        if "error" in data:
            continue
        
        print(f"\n{filename}")
        print(f"  Quality: {data.get('extraction_quality', 'N/A')}")
        
        if data.get('title'):
            print(f"  Title: {data['title'][:80]}{'...' if len(data['title']) > 80 else ''}")
        else:
            print(f"  Title:   NOT FOUND")
        
        if data.get('authors'):
            print(f"  Authors: {', '.join(data['authors'][:3])}{'...' if len(data['authors']) > 3 else ''}")
        else:
            print(f"  Authors:   NOT FOUND")
        
        if data.get('abstract'):
            print(f"  Abstract: {data['abstract'][:100]}...")
        else:
            print(f"  Abstract:   NOT FOUND")
        
        print(f"  Year: {data.get('year', '  NOT FOUND')}")
        print(f"  Venue: {data.get('venue', '  NOT FOUND')}")
        
        if data.get('keywords'):
            print(f"  Keywords: {', '.join(data['keywords'][:5])}")
    
    print("\n" + "="*60)