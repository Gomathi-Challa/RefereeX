# # # # # import xml.etree.ElementTree as ET
# # # # # from grobid_client.grobid_client import GrobidClient
# # # # # import os
# # # # # import json

# # # # # def parse_grobid_xml(xml_string: str) -> dict:
# # # # #     """
# # # # #     Parses the TEI XML output from GROBID's 'processHeaderDocument'
# # # # #     and extracts key metadata fields.
# # # # #     """
    
# # # # #     # Define the XML namespace (GROBID uses TEI)
# # # # #     ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

# # # # #     try:
# # # # #         root = ET.fromstring(xml_string)
# # # # #     except ET.ParseError as e:
# # # # #         print(f"Error parsing XML: {e}")
# # # # #         return {"error": "Failed to parse XML response."}

# # # # #     metadata = {
# # # # #         "title": None,
# # # # #         "authors": [],
# # # # #         "abstract": None,
# # # # #         "keywords": [],
# # # # #         "publication_date": None
# # # # #     }

# # # # #     # --- Title ---
# # # # #     # Find the title statement
# # # # #     title_stmt = root.find('.//tei:titleStmt', ns)
# # # # #     if title_stmt is not None:
# # # # #         # Find the main title
# # # # #         title_elem = title_stmt.find('tei:title', ns)
# # # # #         if title_elem is not None:
# # # # #             metadata['title'] = "".join(title_elem.itertext()).strip()

# # # # #     # --- Authors & Affiliations ---
# # # # #     author_elements = root.findall('.//tei:teiHeader//tei:author', ns)
# # # # #     for author_elem in author_elements:
# # # # #         author = {}
        
# # # # #         # Get full name
# # # # #         pers_name = author_elem.find('tei:persName', ns)
# # # # #         if pers_name is not None:
# # # # #             first = pers_name.find('tei:forename[@type="first"]', ns)
# # # # #             middle = pers_name.findall('tei:forename[@type="middle"]', ns)
# # # # #             last = pers_name.find('tei:surname', ns)
            
# # # # #             full_name_parts = []
# # # # #             if first is not None and first.text:
# # # # #                 full_name_parts.append(first.text)
# # # # #             for m in middle:
# # # # #                 if m is not None and m.text:
# # # # #                     full_name_parts.append(m.text)
# # # # #             if last is not None and last.text:
# # # # #                 full_name_parts.append(last.text)
            
# # # # #             author['full_name'] = " ".join(full_name_parts)
            
# # # # #             # Get email
# # # # #             email = author_elem.find('tei:email', ns)
# # # # #             if email is not None and email.text:
# # # # #                 author['email'] = email.text
        
# # # # #         # Get affiliation
# # # # #         affiliation = author_elem.find('tei:affiliation/tei:orgName', ns)
# # # # #         if affiliation is not None:
# # # # #             author['affiliation'] = "".join(affiliation.itertext()).strip()

# # # # #         if author:
# # # # #             metadata['authors'].append(author)

# # # # #     # --- Abstract ---
# # # # #     abstract_elem = root.find('.//tei:profileDesc/tei:abstract', ns)
# # # # #     if abstract_elem is not None:
# # # # #         # Join all text blocks within the abstract
# # # # #         metadata['abstract'] = " ".join(
# # # # #             p.text.strip() for p in abstract_elem.findall('tei:p', ns) if p.text
# # # # #         )

# # # # #     # --- Keywords ---
# # # # #     keywords_elem = root.find('.//tei:profileDesc/tei:textClass/tei:keywords', ns)
# # # # #     if keywords_elem is not None:
# # # # #         metadata['keywords'] = [
# # # # #             term.text.strip() for term in keywords_elem.findall('tei:term', ns) if term.text
# # # # #         ]
        
# # # # #     # --- Publication Date ---
# # # # #     date_elem = root.find('.//tei:publicationStmt/tei:date', ns)
# # # # #     if date_elem is not None and date_elem.get('when'):
# # # # #         metadata['publication_date'] = date_elem.get('when')

# # # # #     return metadata


# # # # # # --- Main execution ---
# # # # # if __name__ == "__main__":
    
# # # # #     # 1. Initialize the client
# # # # #     # This assumes your GROBID server is at http://localhost:8070
# # # # #     client = GrobidClient(
# # # # #         grobid_server="http://localhost:8070",
# # # # #         batch_size=1000,
# # # # #         coordinates=["p", "byline"],  # Request coordinates for paragraphs and bylines
# # # # #         check_server=True  # Ping server on startup
# # # # #     )

# # # # #     # Define the path to your PDF
# # # # #     pdf_file_path = "D:\\Gomathi_ai\\Dataset\\Dataset\\Amit Saxena\\A Review of Clustering Techniques.pdf"
    
# # # # #     # 2. Process the PDF
# # # # #     # 'process_header_pdf' is optimized for *just* the header (title, author, abstract)
# # # # #     # 'process_fulltext_pdf' does the whole document (slower, more data)
# # # # #     print(f"Processing {pdf_file_path}...")
    
# # # # #     try:
# # # # #         # This sends the PDF and gets back the raw TEI XML as a string
# # # # #         result_xml = client.process_pdf(
# # # # #             "processHeaderDocument",       # service name
# # # # #             pdf_file_path,                 # path to your PDF
# # # # #             generateIDs=True,              # assign unique IDs in TEI
# # # # #             consolidate_header=True,       # clean header metadata
# # # # #             consolidate_citations=False,   # skip citation cleanup
# # # # #             include_raw_citations=False,   # exclude raw citations
# # # # #             include_raw_affiliations=True, # include affiliations
# # # # #             tei_coordinates=["p", "byline"], # request paragraph/byline coordinates
# # # # #             segment_sentences=False        # no sentence segmentation
# # # # #         )


# # # # #         result_path = client.process_pdf(
# # # # #             "processHeaderDocument",
# # # # #             pdf_file_path,
# # # # #             generateIDs=True,
# # # # #             consolidate_header=True,
# # # # #             consolidate_citations=False,
# # # # #             include_raw_citations=False,
# # # # #             include_raw_affiliations=True,
# # # # #             tei_coordinates=["p", "byline"],
# # # # #             segment_sentences=False
# # # # #         )

# # # # #         # Handle tuple return
# # # # #         if isinstance(result_path, tuple):
# # # # #             result_path = result_path[0]

# # # # #         # Some versions just return the path, so read that file
# # # # #         if os.path.isfile(result_path):
# # # # #             print(f"Reading TEI XML from {result_path}")
# # # # #             with open(result_path, "r", encoding="utf-8") as f:
# # # # #                 result_xml = f.read()
# # # # #         else:
# # # # #             print("Expected TEI file not found or invalid result path:")
# # # # #             print(result_path)
# # # # #             result_xml = ""

# # # # #         # Now parse it
# # # # #         if result_xml.strip().startswith("<"):
# # # # #             extracted_data = parse_grobid_xml(result_xml)
# # # # #             print("\n--- Extracted Metadata ---")
# # # # #             print(json.dumps(extracted_data, indent=2))
# # # # #         else:
# # # # #             print("GROBID did not return valid XML. Here's what came back:")
# # # # #             print(result_xml[:300])



# # # # #     except Exception as e:
# # # # #         print(f"\nAn error occurred while processing {pdf_file_path}")
# # # # #         print(e)

# # # # import requests

# # # # pdf_path = "D:/Gomathi_ai/Dataset/Dataset/Amit Saxena/A Review of Clustering Techniques.pdf"
# # # # url = "http://localhost:8070/api/processHeaderDocument"

# # # # with open(pdf_path, "rb") as f:
# # # #     files = {"input": f}
# # # #     response = requests.post(url, files=files)

# # # # if response.status_code == 200:
# # # #     tei_xml = response.text
# # # #     print("Received TEI XML:\n", tei_xml)  # preview
# # # # else:
# # # #     print("Error:", response.status_code, response.text)

# # # # import requests
# # # # import sys
# # # # import xml.etree.ElementTree as ET
# # # # import json
# # # # sys.stdout.reconfigure(encoding='utf-8')

# # # # pdf_path = r"D:\Gomathi_ai\Dataset\Dataset\Amit Saxena\A Review of Clustering Techniques.pdf"
# # # # url = "http://localhost:8070/api/processFulltextDocument"

# # # # with open(pdf_path, "rb") as f:
# # # #     files = {"input": f}
# # # #     params = {"consolidateHeader": 1, "generateIDs": 1}
# # # #     response = requests.post(url, files=files, params=params)

# # # # if response.status_code == 200:
# # # #     tei_xml = response.text
# # # #     print(" GROBID returned TEI XML successfully.")

# # # #     # print(tei_xml[:].encode("utf-8", errors="replace").decode("utf-8"))
# # # #   # Preview first 1000 chars
# # # # else:
# # # #     print(" Error:", response.status_code)
# # # #     print(response.text)



# # # # def parse_tei(tei_xml: str):
# # # #     ns = {"tei": "http://www.tei-c.org/ns/1.0"}  # TEI namespace
# # # #     root = ET.fromstring(tei_xml)

# # # #     data = {}

# # # #     # 1. File description / Metadata
# # # #     fileDesc = root.find("tei:teiHeader/tei:fileDesc", ns)
# # # #     if fileDesc is not None:
# # # #         # Title
# # # #         title_elem = fileDesc.find("tei:titleStmt/tei:title", ns)
# # # #         data["title"] = title_elem.text if title_elem is not None else None

# # # #         # Funder
# # # #         funder_elem = fileDesc.findall("tei:titleStmt/tei:funder/tei:orgName", ns)
# # # #         data["funders"] = [f.text for f in funder_elem] if funder_elem else []

# # # #         # Publication info
# # # #         pubStmt = fileDesc.find("tei:publicationStmt", ns)
# # # #         if pubStmt is not None:
# # # #             publisher = pubStmt.find("tei:publisher", ns)
# # # #             date = pubStmt.find("tei:date", ns)
# # # #             data["publisher"] = publisher.text if publisher is not None else None
# # # #             data["pub_date"] = date.text if date is not None else None

# # # #         # Authors
# # # #         authors = []
# # # #         biblStructs = fileDesc.findall("tei:sourceDesc/tei:biblStruct", ns)
# # # #         for bibl in biblStructs:
# # # #             analytic = bibl.find("tei:analytic", ns)
# # # #             if analytic is not None:
# # # #                 for author in analytic.findall("tei:author", ns):
# # # #                     persName = author.find("tei:persName", ns)
# # # #                     if persName is not None:
# # # #                         forename = persName.find("tei:forename", ns)
# # # #                         surname = persName.find("tei:surname", ns)
# # # #                         full_name = " ".join(filter(None, [forename.text if forename is not None else None,
# # # #                                                           surname.text if surname is not None else None]))
# # # #                         # Affiliation
# # # #                         affiliation = author.find("tei:affiliation/tei:orgName", ns)
# # # #                         aff_text = affiliation.text if affiliation is not None else None
# # # #                         authors.append({"name": full_name, "affiliation": aff_text})
# # # #         data["authors"] = authors

# # # #         # Document identifiers
# # # #         idnos = fileDesc.findall(".//tei:idno", ns)
# # # #         data["identifiers"] = {idn.attrib.get("type"): idn.text for idn in idnos if idn.text}

# # # #     # 2. Profile: Keywords, Abstract
# # # #     profile = root.find("tei:teiHeader/tei:profileDesc", ns)
# # # #     if profile is not None:
# # # #         # Keywords
# # # #         keywords = profile.findall("tei:textClass/tei:keywords/tei:term", ns)
# # # #         data["keywords"] = [k.text for k in keywords if k.text]

# # # #         # Abstract
# # # #         abstract = profile.find("tei:abstract", ns)
# # # #         if abstract is not None:
# # # #             paras = abstract.findall("tei:p", ns)
# # # #             data["abstract"] = " ".join([p.text for p in paras if p.text])

# # # #     # 3. Body headings (section titles)
# # # #     body = root.find("tei:text/tei:body", ns)
# # # #     headings = []
# # # #     if body is not None:
# # # #         for head in body.findall(".//tei:head", ns):
# # # #             if head.text:
# # # #                 headings.append(head.text)
# # # #     data["headings"] = headings

# # # #     # 4. References / Back matter
# # # #     back = root.find("tei:text/tei:back", ns)
# # # #     references = []
# # # #     if back is not None:
# # # #         for bibl in back.findall(".//tei:biblStruct", ns):
# # # #             analytic = bibl.find("tei:analytic", ns)
# # # #             if analytic is not None:
# # # #                 ref_auth = analytic.find("tei:author/tei:persName/tei:surname", ns)
# # # #                 ref_title = analytic.find("tei:title", ns)
# # # #                 references.append({
# # # #                     "author": ref_auth.text if ref_auth is not None else None,
# # # #                     "title": ref_title.text if ref_title is not None else None
# # # #                 })
# # # #     data["references"] = references

# # # #     return data

# # # # # Example usage
# # # # parsed_json = parse_tei(tei_xml)
# # # # print(json.dumps(parsed_json, indent=2, ensure_ascii=False))

# # # import requests
# # # import sys
# # # import xml.etree.ElementTree as ET
# # # import json
# # # import re

# # # sys.stdout.reconfigure(encoding='utf-8')

# # # pdf_path = r"D:\Gomathi_ai\Dataset\Dataset\Amit Saxena\A Review of Clustering Techniques.pdf"
# # # url = "http://localhost:8070/api/processFulltextDocument"

# # # # Request GROBID fulltext (you already had this)
# # # with open(pdf_path, "rb") as f:
# # #     files = {"input": f}
# # #     params = {"consolidateHeader": 1, "generateIDs": 1}
# # #     response = requests.post(url, files=files, params=params)

# # # if response.status_code != 200:
# # #     print("Error:", response.status_code)
# # #     print(response.text)
# # #     raise SystemExit(1)

# # # tei_xml = response.text
# # # print("GROBID returned TEI XML successfully.")

# # # # -----------------------
# # # # Parsing helpers
# # # # -----------------------
# # # def get_text(elem):
# # #     """Safely return element text trimmed, or None."""
# # #     if elem is None:
# # #         return None
# # #     txt = elem.text
# # #     return txt.strip() if txt and txt.strip() else None

# # # def join_person_name(pers_elem, ns):
# # #     """Return formatted name from persName element (forename(s) + surname)."""
# # #     if pers_elem is None:
# # #         return None
# # #     names = []
# # #     # include all forename nodes (first/middle) in order
# # #     forename_nodes = pers_elem.findall("tei:forename", ns)
# # #     for f in forename_nodes:
# # #         if f.text and f.text.strip():
# # #             names.append(f.text.strip())
# # #     surname = pers_elem.find("tei:surname", ns)
# # #     if surname is not None and surname.text and surname.text.strip():
# # #         names.append(surname.text.strip())
# # #     return " ".join(names) if names else None

# # # def extract_affiliation_text(aff_elem, ns):
# # #     if aff_elem is None:
# # #         return None
# # #     parts = []
# # #     for org in aff_elem.findall(".//tei:orgName", ns):
# # #         if org.text and org.text.strip():
# # #             parts.append(org.text.strip())
# # #     # address parts
# # #     for addr in aff_elem.findall(".//tei:addrLine", ns):
# # #         if addr.text and addr.text.strip():
# # #             parts.append(addr.text.strip())
# # #     settlement = aff_elem.find(".//tei:settlement", ns)
# # #     if settlement is not None and settlement.text and settlement.text.strip():
# # #         parts.append(settlement.text.strip())
# # #     country = aff_elem.find(".//tei:country", ns)
# # #     if country is not None and country.text and country.text.strip():
# # #         parts.append(country.text.strip())
# # #     return ", ".join(parts) if parts else None

# # # # -----------------------
# # # # Main parser
# # # # -----------------------
# # # def parse_tei_and_filter(tei_xml: str, ref_keywords=None, top_n=5):
# # #     if ref_keywords is None:
# # #         ref_keywords = ["clustering", "density", "grid", "subspace", "dbscan", "clique", "partition", "model-based"]
# # #     # lowercase keywords for matching
# # #     ref_keywords = [k.lower() for k in ref_keywords]

# # #     ns = {"tei": "http://www.tei-c.org/ns/1.0"}
# # #     root = ET.fromstring(tei_xml)

# # #     out = {}

# # #     # 1. fileDesc metadata
# # #     fileDesc = root.find("tei:teiHeader/tei:fileDesc", ns)
# # #     if fileDesc is not None:
# # #         title_elem = fileDesc.find("tei:titleStmt/tei:title", ns)
# # #         out["title"] = get_text(title_elem)

# # #         funders = [get_text(x) for x in fileDesc.findall("tei:titleStmt/tei:funder/tei:orgName", ns)]
# # #         out["funders"] = [f for f in funders if f]

# # #         pubStmt = fileDesc.find("tei:publicationStmt", ns)
# # #         out["publisher"] = get_text(pubStmt.find("tei:publisher", ns)) if pubStmt is not None else None
# # #         date_elem = fileDesc.find("tei:publicationStmt/tei:date", ns)
# # #         out["pub_date"] = date_elem.attrib.get("when") if date_elem is not None and date_elem.attrib.get("when") else get_text(date_elem)

# # #         # authors (from biblStruct -> analytic)
# # #         authors_list = []
# # #         for bibl in fileDesc.findall("tei:sourceDesc/tei:biblStruct", ns):
# # #             analytic = bibl.find("tei:analytic", ns)
# # #             if analytic is None:
# # #                 continue
# # #             for author in analytic.findall("tei:author", ns):
# # #                 pers = author.find("tei:persName", ns)
# # #                 name = join_person_name(pers, ns)
# # #                 # affiliation for this author (first orgName)
# # #                 aff_elem = author.find("tei:affiliation", ns)
# # #                 aff_text = extract_affiliation_text(aff_elem, ns)
# # #                 authors_list.append({"name": name, "affiliation": aff_text})
# # #         out["authors"] = authors_list

# # #         # identifiers
# # #         idnos = {}
# # #         for idn in fileDesc.findall(".//tei:idno", ns):
# # #             typ = idn.attrib.get("type")
# # #             if typ and idn.text and idn.text.strip():
# # #                 idnos[typ] = idn.text.strip()
# # #         out["identifiers"] = idnos

# # #     # 2. profileDesc -> keywords + abstract (use recursive lookup for <p>)
# # #     profile = root.find("tei:teiHeader/tei:profileDesc", ns)
# # #     out["keywords"] = []
# # #     out["abstract"] = None
# # #     if profile is not None:
# # #         # keywords
# # #         kterms = profile.findall(".//tei:textClass/tei:keywords/tei:term", ns)
# # #         out["keywords"] = [k.text.strip() for k in kterms if k.text and k.text.strip()]

# # #         # abstract: find any <p> inside abstract recursively
# # #         abstract_root = profile.find("tei:abstract", ns)
# # #         if abstract_root is not None:
# # #             paras = abstract_root.findall(".//tei:p", ns)
# # #             if paras:
# # #                 texts = []
# # #                 for p in paras:
# # #                     # ET .text sometimes None when deeper tags inside; collect .itertext()
# # #                     txt = "".join(p.itertext()).strip()
# # #                     if txt:
# # #                         texts.append(txt)
# # #                 out["abstract"] = " ".join(texts) if texts else None
# # #             else:
# # #                 # fallback: any text directly under abstract
# # #                 txt = "".join(abstract_root.itertext()).strip()
# # #                 out["abstract"] = txt if txt else None

# # #     # 3. headings: collect <head> texts; filter trivial numeric-only or tiny ones, de-duplicate preserving order
# # #     body = root.find("tei:text/tei:body", ns)
# # #     headings = []
# # #     seen = set()
# # #     if body is not None:
# # #         for head in body.findall(".//tei:head", ns):
# # #             htxt = head.text.strip() if head.text and head.text.strip() else None
# # #             if not htxt:
# # #                 # check inner text via itertext
# # #                 htxt = "".join(head.itertext()).strip()
# # #             if not htxt:
# # #                 continue
# # #             # skip if purely numeric like "2." or "3"
# # #             if re.match(r'^\s*\d+\.?\s*$', htxt):
# # #                 continue
# # #             # skip extremely short garbage (one char or coordinates)
# # #             if len(htxt) <= 1:
# # #                 continue
# # #             if htxt not in seen:
# # #                 headings.append(htxt)
# # #                 seen.add(htxt)
# # #     out["headings"] = headings

# # #     # 4. references in back/listBibl: build rich objects and filter
# # #     back = root.find("tei:text/tei:back", ns)
# # #     refs = []
# # #     if back is None:
# # #         # sometimes references are directly under teiHeader/back or teiHeader/tei:back - try generic search
# # #         back = root.find(".//tei:back", ns)

# # #     if back is not None:
# # #         for bibl in back.findall(".//tei:listBibl/tei:biblStruct", ns) + back.findall(".//tei:biblStruct", ns):
# # #             ref = {"title": None, "authors": [], "publisher": None, "journal": None, "year": None, "pages": None, "type": None, "raw_text": None}
# # #             # analytic title & authors
# # #             analytic = bibl.find("tei:analytic", ns)
# # #             if analytic is not None:
# # #                 title_a = analytic.find("tei:title", ns)
# # #                 if title_a is not None and title_a.text and title_a.text.strip():
# # #                     ref["title"] = title_a.text.strip()
# # #                 # authors list
# # #                 for author in analytic.findall("tei:author", ns):
# # #                     pers = author.find("tei:persName", ns)
# # #                     name = join_person_name(pers, ns)
# # #                     if name:
# # #                         ref["authors"].append(name)

# # #             # monogr (journal/book) info
# # #             monogr = bibl.find("tei:monogr", ns)
# # #             if monogr is not None:
# # #                 mon_title = monogr.find("tei:title", ns)
# # #                 if mon_title is not None and mon_title.text and mon_title.text.strip():
# # #                     # treat as journal or book title depending on context
# # #                     ref["journal"] = mon_title.text.strip()
# # #                     if ref["title"] is None:
# # #                         # sometimes monogr/title is the main title (books)
# # #                         ref["title"] = mon_title.text.strip()
# # #                 # imprint info
# # #                 imprint = monogr.find("tei:imprint", ns)
# # #                 if imprint is not None:
# # #                     pub = imprint.find("tei:publisher", ns)
# # #                     if pub is not None and pub.text and pub.text.strip():
# # #                         ref["publisher"] = pub.text.strip()
# # #                     # date
# # #                     date = imprint.find("tei:date", ns)
# # #                     if date is not None:
# # #                         # prefer @when
# # #                         year = date.attrib.get("when") or get_text(date)
# # #                         if year:
# # #                             # extract year only if full date
# # #                             m = re.match(r'^(\d{4})', year)
# # #                             ref["year"] = m.group(1) if m else year
# # #                     # pages or biblScope
# # #                     bscopes = imprint.findall("tei:biblScope", ns)
# # #                     if bscopes:
# # #                         # try to get page range
# # #                         pages = []
# # #                         for bs in bscopes:
# # #                             if bs.attrib.get("unit") == "page":
# # #                                 frm = bs.attrib.get("from")
# # #                                 to = bs.attrib.get("to")
# # #                                 if frm or to:
# # #                                     pages.append(f"{frm or ''}-{to or ''}")
# # #                         if pages:
# # #                             ref["pages"] = ";".join(pages)

# # #             # if there is an idno (doi, etc.)
# # #             for idn in bibl.findall(".//tei:idno", ns):
# # #                 typ = idn.attrib.get("type")
# # #                 if typ and idn.text:
# # #                     ref.setdefault("identifiers", {})[typ] = idn.text.strip()

# # #             # raw_text: create a concatenated string for keyword matching
# # #             raw_parts = []
# # #             if ref["title"]:
# # #                 raw_parts.append(ref["title"])
# # #             if ref["journal"]:
# # #                 raw_parts.append(ref["journal"])
# # #             if ref["publisher"]:
# # #                 raw_parts.append(ref["publisher"])
# # #             if ref["authors"]:
# # #                 raw_parts.append(" ".join(ref["authors"]))
# # #             raw_text = " ".join(raw_parts).lower()
# # #             ref["raw_text"] = raw_text

# # #             refs.append(ref)

# # #     # Filter references by keywords (case-insensitive), preserve doc order
# # #     matched = []
# # #     for r in refs:
# # #         if any(k in (r["raw_text"] or "") for k in ref_keywords):
# # #             matched.append(r)
# # #     # If not enough matched, fallback to top refs in original order
# # #     if len(matched) < top_n:
# # #         # add missing ones from refs in order (skip duplicates)
# # #         for r in refs:
# # #             if r in matched:
# # #                 continue
# # #             matched.append(r)
# # #             if len(matched) >= top_n:
# # #                 break
# # #     # limit to top_n
# # #     out["top_references"] = matched[:top_n]

# # #     return out

# # # # -----------------------
# # # # Run parser, print JSON
# # # # -----------------------
# # # parsed = parse_tei_and_filter(tei_xml, top_n=5)
# # # print(json.dumps(parsed, indent=2, ensure_ascii=False))

# # # grobid_metadata.py
# # import os
# # import requests
# # import sys
# # import xml.etree.ElementTree as ET
# # import json
# # import re

# # sys.stdout.reconfigure(encoding='utf-8')


# # class GrobidExtractor:
# #     def __init__(self, grobid_url="http://localhost:8070/api/processFulltextDocument"):
# #         self.grobid_url = grobid_url

# #     # ------------- Helper functions -------------
# #     def get_text(self, elem):
# #         if elem is None:
# #             return None
# #         txt = elem.text
# #         return txt.strip() if txt and txt.strip() else None

# #     def join_person_name(self, pers_elem, ns):
# #         if pers_elem is None:
# #             return None
# #         names = []
# #         for f in pers_elem.findall("tei:forename", ns):
# #             if f.text and f.text.strip():
# #                 names.append(f.text.strip())
# #         surname = pers_elem.find("tei:surname", ns)
# #         if surname is not None and surname.text and surname.text.strip():
# #             names.append(surname.text.strip())
# #         return " ".join(names) if names else None

# #     def extract_affiliation_text(self, aff_elem, ns):
# #         if aff_elem is None:
# #             return None
# #         parts = []
# #         for org in aff_elem.findall(".//tei:orgName", ns):
# #             if org.text and org.text.strip():
# #                 parts.append(org.text.strip())
# #         for addr in aff_elem.findall(".//tei:addrLine", ns):
# #             if addr.text and addr.text.strip():
# #                 parts.append(addr.text.strip())
# #         settlement = aff_elem.find(".//tei:settlement", ns)
# #         if settlement is not None and settlement.text and settlement.text.strip():
# #             parts.append(settlement.text.strip())
# #         country = aff_elem.find(".//tei:country", ns)
# #         if country is not None and country.text and country.text.strip():
# #             parts.append(country.text.strip())
# #         return ", ".join(parts) if parts else None

# #     # ------------- Core parser -------------
# #     def parse_tei_and_filter(self, tei_xml: str, ref_keywords=None, top_n=5):
# #         if ref_keywords is None:
# #             ref_keywords = ["clustering", "density", "grid", "subspace", "dbscan", "clique", "partition", "model-based"]
# #         ref_keywords = [k.lower() for k in ref_keywords]

# #         ns = {"tei": "http://www.tei-c.org/ns/1.0"}
# #         root = ET.fromstring(tei_xml)
# #         out = {}

# #         # ---- Metadata ----
# #         fileDesc = root.find("tei:teiHeader/tei:fileDesc", ns)
# #         if fileDesc is not None:
# #             title_elem = fileDesc.find("tei:titleStmt/tei:title", ns)
# #             out["title"] = self.get_text(title_elem)
# #             out["funders"] = [self.get_text(x) for x in fileDesc.findall("tei:titleStmt/tei:funder/tei:orgName", ns) if self.get_text(x)]
# #             pubStmt = fileDesc.find("tei:publicationStmt", ns)
# #             out["publisher"] = self.get_text(pubStmt.find("tei:publisher", ns)) if pubStmt is not None else None
# #             date_elem = fileDesc.find("tei:publicationStmt/tei:date", ns)
# #             out["pub_date"] = date_elem.attrib.get("when") if date_elem is not None and date_elem.attrib.get("when") else self.get_text(date_elem)

# #             authors_list = []
# #             for bibl in fileDesc.findall("tei:sourceDesc/tei:biblStruct", ns):
# #                 analytic = bibl.find("tei:analytic", ns)
# #                 if analytic is None:
# #                     continue
# #                 for author in analytic.findall("tei:author", ns):
# #                     pers = author.find("tei:persName", ns)
# #                     name = self.join_person_name(pers, ns)
# #                     aff_elem = author.find("tei:affiliation", ns)
# #                     aff_text = self.extract_affiliation_text(aff_elem, ns)
# #                     authors_list.append({"name": name, "affiliation": aff_text})
# #             out["authors"] = authors_list

# #             idnos = {}
# #             for idn in fileDesc.findall(".//tei:idno", ns):
# #                 typ = idn.attrib.get("type")
# #                 if typ and idn.text and idn.text.strip():
# #                     idnos[typ] = idn.text.strip()
# #             out["identifiers"] = idnos

# #         # ---- Profile: keywords & abstract ----
# #         profile = root.find("tei:teiHeader/tei:profileDesc", ns)
# #         out["keywords"] = []
# #         out["abstract"] = None
# #         if profile is not None:
# #             kterms = profile.findall(".//tei:textClass/tei:keywords/tei:term", ns)
# #             out["keywords"] = [k.text.strip() for k in kterms if k.text and k.text.strip()]
# #             abstract_root = profile.find("tei:abstract", ns)
# #             if abstract_root is not None:
# #                 paras = abstract_root.findall(".//tei:p", ns)
# #                 texts = ["".join(p.itertext()).strip() for p in paras if "".join(p.itertext()).strip()]
# #                 out["abstract"] = " ".join(texts) if texts else "".join(abstract_root.itertext()).strip()

# #         # ---- Headings ----
# #         body = root.find("tei:text/tei:body", ns)
# #         headings = []
# #         seen = set()
# #         if body is not None:
# #             for head in body.findall(".//tei:head", ns):
# #                 htxt = "".join(head.itertext()).strip()
# #                 if not htxt or re.match(r'^\s*\d+\.?\s*$', htxt) or len(htxt) <= 1:
# #                     continue
# #                 if htxt not in seen:
# #                     headings.append(htxt)
# #                     seen.add(htxt)
# #         out["headings"] = headings

# #         # ---- References ----
# #         back = root.find("tei:text/tei:back", ns)
# #         refs = []
# #         if back is None:
# #             back = root.find(".//tei:back", ns)
# #         if back is not None:
# #             for bibl in back.findall(".//tei:biblStruct", ns):
# #                 ref = {"title": None, "authors": [], "publisher": None, "journal": None, "year": None, "pages": None, "type": None, "raw_text": None}
# #                 analytic = bibl.find("tei:analytic", ns)
# #                 if analytic is not None:
# #                     title_a = analytic.find("tei:title", ns)
# #                     if title_a is not None and title_a.text and title_a.text.strip():
# #                         ref["title"] = title_a.text.strip()
# #                     for author in analytic.findall("tei:author", ns):
# #                         pers = author.find("tei:persName", ns)
# #                         name = self.join_person_name(pers, ns)
# #                         if name:
# #                             ref["authors"].append(name)
# #                 monogr = bibl.find("tei:monogr", ns)
# #                 if monogr is not None:
# #                     mon_title = monogr.find("tei:title", ns)
# #                     if mon_title is not None and mon_title.text and mon_title.text.strip():
# #                         ref["journal"] = mon_title.text.strip()
# #                         if ref["title"] is None:
# #                             ref["title"] = mon_title.text.strip()
# #                     imprint = monogr.find("tei:imprint", ns)
# #                     if imprint is not None:
# #                         pub = imprint.find("tei:publisher", ns)
# #                         if pub is not None and pub.text and pub.text.strip():
# #                             ref["publisher"] = pub.text.strip()
# #                         date = imprint.find("tei:date", ns)
# #                         if date is not None:
# #                             year = date.attrib.get("when") or self.get_text(date)
# #                             if year:
# #                                 m = re.match(r'^(\d{4})', year)
# #                                 ref["year"] = m.group(1) if m else year
# #                 raw_parts = [x for x in [ref["title"], ref["journal"], ref["publisher"], " ".join(ref["authors"])] if x]
# #                 ref["raw_text"] = " ".join(raw_parts).lower()
# #                 refs.append(ref)

# #         matched = [r for r in refs if any(k in (r["raw_text"] or "") for k in ref_keywords)]
# #         if len(matched) < top_n:
# #             for r in refs:
# #                 if r not in matched:
# #                     matched.append(r)
# #                     if len(matched) >= top_n:
# #                         break
# #         out["top_references"] = matched[:top_n]

# #         return out

# #     # ------------- Single PDF Extraction -------------
# #     def extract_pdf(self, pdf_path):
# #         with open(pdf_path, "rb") as f:
# #             files = {"input": f}
# #             params = {"consolidateHeader": 1, "generateIDs": 1}
# #             response = requests.post(self.grobid_url, files=files, params=params)
# #         if response.status_code != 200:
# #             print(f"     Error processing {pdf_path}: {response.status_code}")
# #             return None
# #         return self.parse_tei_and_filter(response.text)

# #     # ------------- Folder Extraction -------------
# #     def extract_pdfs_in_folder(self, folder_path):
# #         results = {}
# #         for file in os.listdir(folder_path):
# #             if file.lower().endswith(".pdf"):
# #                 full_path = os.path.join(folder_path, file)
# #                 print(f"Processing: {file}")
# #                 parsed = self.extract_pdf(full_path)
# #                 if parsed:
# #                     results[file] = parsed
# #         return results
    
# # if __name__ == "__main__":
    
# #     extractor = GrobidExtractor()
# #     folder = r"D:\Gomathi_ai\Dataset\Dataset\Amit Saxena"
# #     result2 = extractor.extract_pdfs_in_folder(folder)


# #     # Save JSON output
# #     with open("amit_saxena_results_grobid.json", "w", encoding="utf-8") as f:
# #         json.dump(result2, f, indent=2, ensure_ascii=False)
# #     print(" Extraction complete. Results saved to amit_saxena_results.json")


# ### THE ABOVE CODE WORKS FINE. NOW THE UNIFIED PIPELINE CODE IS BELOW ###
# # import os
# # import json
# # import redis
# # import requests
# # import xml.etree.ElementTree as ET
# # import re
# # from typing import Dict, List, Optional
# # from collections import defaultdict

# # # Import the processing functions from other modules
# # from ner_metadata import NerExtractor
# # from keywords_metadata import UnifiedKeywordExtractor
# # from topic_metadata import extract_topics


# # class UnifiedPipeline:
# #     """
# #     End-to-end pipeline that:
# #     1. Extracts metadata using GROBID (stores in JSON)
# #     2. Collects raw text for NER, keywords, and topics (stores in Redis)
# #     3. Processes all PDFs per author/folder together
# #     4. Saves results in organized JSON and Redis cache
# #     """
    
# #     def __init__(
# #         self,
# #         grobid_url="http://localhost:8070/api/processFulltextDocument",
# #         redis_host='localhost',
# #         redis_port=6379,
# #         redis_db=0
# #     ):
# #         self.grobid_url = grobid_url
        
# #         # Initialize Redis connection
# #         try:
# #             self.redis_client = redis.Redis(
# #                 host=redis_host,
# #                 port=redis_port,
# #                 db=redis_db,
# #                 decode_responses=True
# #             )
# #             self.redis_client.ping()
# #             print("     Redis connection established")
# #         except Exception as e:
# #             print(f"   Redis connection failed: {e}. Running without cache.")
# #             self.redis_client = None
        
# #         # Initialize extractors
# #         self.ner_extractor = NerExtractor
# #         self.keyword_extractor = UnifiedKeywordExtractor(log_file="keyword_extraction.log")
        
# #         # Load NER model once
# #         self.ner_extractor.load_ner_model()
    
# #     # ==================== GROBID HELPER METHODS ====================
    
# #     def get_text(self, elem):
# #         if elem is None:
# #             return None
# #         txt = elem.text
# #         return txt.strip() if txt and txt.strip() else None

# #     def join_person_name(self, pers_elem, ns):
# #         if pers_elem is None:
# #             return None
# #         names = []
# #         for f in pers_elem.findall("tei:forename", ns):
# #             if f.text and f.text.strip():
# #                 names.append(f.text.strip())
# #         surname = pers_elem.find("tei:surname", ns)
# #         if surname is not None and surname.text and surname.text.strip():
# #             names.append(surname.text.strip())
# #         return " ".join(names) if names else None

# #     def extract_affiliation_text(self, aff_elem, ns):
# #         if aff_elem is None:
# #             return None
# #         parts = []
# #         for org in aff_elem.findall(".//tei:orgName", ns):
# #             if org.text and org.text.strip():
# #                 parts.append(org.text.strip())
# #         for addr in aff_elem.findall(".//tei:addrLine", ns):
# #             if addr.text and addr.text.strip():
# #                 parts.append(addr.text.strip())
# #         settlement = aff_elem.find(".//tei:settlement", ns)
# #         if settlement is not None and settlement.text and settlement.text.strip():
# #             parts.append(settlement.text.strip())
# #         country = aff_elem.find(".//tei:country", ns)
# #         if country is not None and country.text and country.text.strip():
# #             parts.append(country.text.strip())
# #         return ", ".join(parts) if parts else None

# #     # ==================== TEXT EXTRACTION FROM TEI ====================
    
# #     def extract_raw_text_from_tei(self, tei_xml: str) -> Dict[str, str]:
# #         """
# #         Extract different types of text from TEI XML for various processing needs:
# #         - raw_text: For NER (preserves case, entities)
# #         - abstract_text: For keyword extraction (focused content)
# #         - body_text: For topic modeling (full document content)
# #         """
# #         ns = {"tei": "http://www.tei-c.org/ns/1.0"}
# #         root = ET.fromstring(tei_xml)
        
# #         text_data = {
# #             "raw_text": "",
# #             "abstract_text": "",
# #             "body_text": ""
# #         }
        
# #         # Extract abstract (preserves original case for NER)
# #         profile = root.find("tei:teiHeader/tei:profileDesc", ns)
# #         if profile is not None:
# #             abstract_root = profile.find("tei:abstract", ns)
# #             if abstract_root is not None:
# #                 paras = abstract_root.findall(".//tei:p", ns)
# #                 texts = ["".join(p.itertext()).strip() for p in paras if "".join(p.itertext()).strip()]
# #                 text_data["abstract_text"] = " ".join(texts) if texts else "".join(abstract_root.itertext()).strip()
        
# #         # Extract body text (preserves original case)
# #         body = root.find("tei:text/tei:body", ns)
# #         if body is not None:
# #             # Get all paragraphs and divs
# #             all_text_elements = []
# #             for elem in body.iter():
# #                 if elem.tag.endswith('p') or elem.tag.endswith('head'):
# #                     text = "".join(elem.itertext()).strip()
# #                     if text and len(text) > 10:  # Skip very short fragments
# #                         all_text_elements.append(text)
            
# #             text_data["body_text"] = " ".join(all_text_elements)
        
# #         # Combine for full raw text (for NER - needs case preserved)
# #         text_data["raw_text"] = f"{text_data['abstract_text']} {text_data['body_text']}".strip()
        
# #         return text_data

# #     # ==================== GROBID PARSING ====================
    
# #     def parse_tei_metadata(self, tei_xml: str, ref_keywords=None, top_n=5):
# #         """Parse TEI XML for metadata only (original GROBID functionality)"""
# #         if ref_keywords is None:
# #             ref_keywords = ["clustering", "density", "grid", "subspace", "dbscan", 
# #                           "clique", "partition", "model-based"]
# #         ref_keywords = [k.lower() for k in ref_keywords]

# #         ns = {"tei": "http://www.tei-c.org/ns/1.0"}
# #         root = ET.fromstring(tei_xml)
# #         out = {}

# #         # ---- Metadata ----
# #         fileDesc = root.find("tei:teiHeader/tei:fileDesc", ns)
# #         if fileDesc is not None:
# #             title_elem = fileDesc.find("tei:titleStmt/tei:title", ns)
# #             out["title"] = self.get_text(title_elem)
# #             out["funders"] = [self.get_text(x) for x in fileDesc.findall("tei:titleStmt/tei:funder/tei:orgName", ns) if self.get_text(x)]
# #             pubStmt = fileDesc.find("tei:publicationStmt", ns)
# #             out["publisher"] = self.get_text(pubStmt.find("tei:publisher", ns)) if pubStmt is not None else None
# #             date_elem = fileDesc.find("tei:publicationStmt/tei:date", ns)
# #             out["pub_date"] = date_elem.attrib.get("when") if date_elem is not None and date_elem.attrib.get("when") else self.get_text(date_elem)

# #             authors_list = []
# #             for bibl in fileDesc.findall("tei:sourceDesc/tei:biblStruct", ns):
# #                 analytic = bibl.find("tei:analytic", ns)
# #                 if analytic is None:
# #                     continue
# #                 for author in analytic.findall("tei:author", ns):
# #                     pers = author.find("tei:persName", ns)
# #                     name = self.join_person_name(pers, ns)
# #                     aff_elem = author.find("tei:affiliation", ns)
# #                     aff_text = self.extract_affiliation_text(aff_elem, ns)
# #                     authors_list.append({"name": name, "affiliation": aff_text})
# #             out["authors"] = authors_list

# #             idnos = {}
# #             for idn in fileDesc.findall(".//tei:idno", ns):
# #                 typ = idn.attrib.get("type")
# #                 if typ and idn.text and idn.text.strip():
# #                     idnos[typ] = idn.text.strip()
# #             out["identifiers"] = idnos

# #         # ---- Profile: keywords & abstract ----
# #         profile = root.find("tei:teiHeader/tei:profileDesc", ns)
# #         out["keywords"] = []
# #         out["abstract"] = None
# #         if profile is not None:
# #             kterms = profile.findall(".//tei:textClass/tei:keywords/tei:term", ns)
# #             out["keywords"] = [k.text.strip() for k in kterms if k.text and k.text.strip()]
# #             abstract_root = profile.find("tei:abstract", ns)
# #             if abstract_root is not None:
# #                 paras = abstract_root.findall(".//tei:p", ns)
# #                 texts = ["".join(p.itertext()).strip() for p in paras if "".join(p.itertext()).strip()]
# #                 out["abstract"] = " ".join(texts) if texts else "".join(abstract_root.itertext()).strip()

# #         # ---- Headings ----
# #         body = root.find("tei:text/tei:body", ns)
# #         headings = []
# #         seen = set()
# #         if body is not None:
# #             for head in body.findall(".//tei:head", ns):
# #                 htxt = "".join(head.itertext()).strip()
# #                 if not htxt or re.match(r'^\s*\d+\.?\s*$', htxt) or len(htxt) <= 1:
# #                     continue
# #                 if htxt not in seen:
# #                     headings.append(htxt)
# #                     seen.add(htxt)
# #         out["headings"] = headings

# #         # ---- References ----
# #         back = root.find("tei:text/tei:back", ns)
# #         refs = []
# #         if back is None:
# #             back = root.find(".//tei:back", ns)
# #         if back is not None:
# #             for bibl in back.findall(".//tei:biblStruct", ns):
# #                 ref = {"title": None, "authors": [], "publisher": None, "journal": None, 
# #                       "year": None, "pages": None, "type": None, "raw_text": None}
# #                 analytic = bibl.find("tei:analytic", ns)
# #                 if analytic is not None:
# #                     title_a = analytic.find("tei:title", ns)
# #                     if title_a is not None and title_a.text and title_a.text.strip():
# #                         ref["title"] = title_a.text.strip()
# #                     for author in analytic.findall("tei:author", ns):
# #                         pers = author.find("tei:persName", ns)
# #                         name = self.join_person_name(pers, ns)
# #                         if name:
# #                             ref["authors"].append(name)
# #                 monogr = bibl.find("tei:monogr", ns)
# #                 if monogr is not None:
# #                     mon_title = monogr.find("tei:title", ns)
# #                     if mon_title is not None and mon_title.text and mon_title.text.strip():
# #                         ref["journal"] = mon_title.text.strip()
# #                         if ref["title"] is None:
# #                             ref["title"] = mon_title.text.strip()
# #                     imprint = monogr.find("tei:imprint", ns)
# #                     if imprint is not None:
# #                         pub = imprint.find("tei:publisher", ns)
# #                         if pub is not None and pub.text and pub.text.strip():
# #                             ref["publisher"] = pub.text.strip()
# #                         date = imprint.find("tei:date", ns)
# #                         if date is not None:
# #                             year = date.attrib.get("when") or self.get_text(date)
# #                             if year:
# #                                 m = re.match(r'^(\d{4})', year)
# #                                 ref["year"] = m.group(1) if m else year
# #                 raw_parts = [x for x in [ref["title"], ref["journal"], ref["publisher"], " ".join(ref["authors"])] if x]
# #                 ref["raw_text"] = " ".join(raw_parts).lower()
# #                 refs.append(ref)

# #         matched = [r for r in refs if any(k in (r["raw_text"] or "") for k in ref_keywords)]
# #         if len(matched) < top_n:
# #             for r in refs:
# #                 if r not in matched:
# #                     matched.append(r)
# #                     if len(matched) >= top_n:
# #                         break
# #         out["top_references"] = matched[:top_n]

# #         return out

# #     # ==================== REDIS CACHE OPERATIONS ====================
    
# #     def cache_author_text(self, author_name: str, pdf_name: str, text_data: Dict[str, str]):
# #         """Store extracted text in Redis cache organized by author"""
# #         if not self.redis_client:
# #             return
        
# #         try:
# #             # Store in Redis with hierarchical keys: author:pdf:text_type
# #             for text_type, text_content in text_data.items():
# #                 key = f"text:{author_name}:{pdf_name}:{text_type}"
# #                 self.redis_client.set(key, text_content)
# #                 # Set expiration to 24 hours
# #                 self.redis_client.expire(key, 86400)
# #         except Exception as e:
# #             print(f"Failed to cache text for {pdf_name}: {e}")
    
# #     def get_author_combined_text(self, author_name: str) -> Dict[str, str]:
# #         """Retrieve and combine all texts for an author from Redis"""
# #         if not self.redis_client:
# #             return {"raw_text": "", "abstract_text": "", "body_text": ""}
        
# #         try:
# #             # Get all keys for this author
# #             pattern = f"text:{author_name}:*"
# #             keys = self.redis_client.keys(pattern)
            
# #             combined = defaultdict(list)
            
# #             for key in keys:
# #                 # Parse key to get text type
# #                 parts = key.split(":")
# #                 if len(parts) >= 4:
# #                     text_type = parts[3]
# #                     text_content = self.redis_client.get(key)
# #                     if text_content:
# #                         combined[text_type].append(text_content)
            
# #             # Combine all texts of each type
# #             return {
# #                 text_type: " ".join(texts)
# #                 for text_type, texts in combined.items()
# #             }
# #         except Exception as e:
# #             print(f"Failed to retrieve cached text for {author_name}: {e}")
# #             return {"raw_text": "", "abstract_text": "", "body_text": ""}
    
# #     def cache_results(self, author_name: str, result_type: str, data: Dict):
# #         """Cache processing results (NER, keywords, topics) in Redis"""
# #         if not self.redis_client:
# #             return
        
# #         try:
# #             key = f"results:{author_name}:{result_type}"
# #             self.redis_client.set(key, json.dumps(data, ensure_ascii=False))
# #             self.redis_client.expire(key, 86400)
# #         except Exception as e:
# #             print(f"Failed to cache {result_type} results for {author_name}: {e}")
    
# #     # ==================== MAIN PROCESSING PIPELINE ====================
    
# #     def process_single_pdf(self, pdf_path: str, author_name: str, pdf_name: str) -> Optional[Dict]:
# #         """Process a single PDF through GROBID and extract text for caching"""
# #         print(f"  Processing: {pdf_name}")
        
# #         try:
# #             # Call GROBID API
# #             with open(pdf_path, "rb") as f:
# #                 files = {"input": f}
# #                 params = {"consolidateHeader": 1, "generateIDs": 1}
# #                 response = requests.post(self.grobid_url, files=files, params=params)
            
# #             if response.status_code != 200:
# #                 print(f"     GROBID error for {pdf_name}: {response.status_code}")
# #                 return None
            
# #             tei_xml = response.text
            
# #             # Parse metadata (for GROBID JSON)
# #             metadata = self.parse_tei_metadata(tei_xml)
            
# #             # Extract raw text (for NER, keywords, topics)
# #             text_data = self.extract_raw_text_from_tei(tei_xml)
            
# #             # Cache the extracted text
# #             self.cache_author_text(author_name, pdf_name, text_data)
            
# #             return metadata
            
# #         except Exception as e:
# #             print(f"     Error processing {pdf_name}: {e}")
# #             return None
    
# #     def process_author_folder(self, author_folder_path: str, author_name: str) -> Dict:
# #         """Process all PDFs for a single author"""
# #         print(f"\n{'='*60}")
# #         print(f"Processing author: {author_name}")
# #         print(f"{'='*60}")
        
# #         grobid_results = {}
        
# #         # Step 1: Process all PDFs and cache text
# #         pdf_files = [f for f in os.listdir(author_folder_path) if f.lower().endswith(".pdf")]
        
# #         for pdf_file in pdf_files:
# #             pdf_path = os.path.join(author_folder_path, pdf_file)
# #             metadata = self.process_single_pdf(pdf_path, author_name, pdf_file)
# #             if metadata:
# #                 grobid_results[pdf_file] = metadata
        
# #         print(f"\n     Processed {len(grobid_results)} PDFs")
        
# #         # Step 2: Retrieve combined text from cache
# #         print(f"  Retrieving cached text for analysis...")
# #         combined_text = self.get_author_combined_text(author_name)
        
# #         # Step 3: Run NER on combined raw text (preserves entities)
# #         print(f"  Running NER extraction...")
# #         ner_results = {}
# #         if combined_text["raw_text"]:
# #             ner_results = self.ner_extractor.extract_ner_metadata(
# #                 combined_text["raw_text"],
# #                 log_errors=False
# #             )
# #             self.cache_results(author_name, "ner", ner_results)
        
# #         # Step 4: Run keyword extraction on abstract + body
# #         print(f"  Running keyword extraction...")
# #         keyword_results = {}
# #         keyword_text = f"{combined_text['abstract_text']} {combined_text['body_text']}".strip()
# #         if keyword_text:
# #             keyword_results = self.keyword_extractor.extract_text_keywords(
# #                 keyword_text,
# #                 top_n=20
# #             )
# #             self.cache_results(author_name, "keywords", keyword_results)
        
# #         # Step 5: Run topic modeling on body text
# #         print(f"  Running topic extraction...")
# #         topic_results = {}
# #         if combined_text["body_text"]:
# #             topic_results = extract_topics(
# #                 combined_text["body_text"],
# #                 n_topics=10,
# #                 n_words=10
# #             )
# #             self.cache_results(author_name, "topics", topic_results)
        
# #         print(f"     Analysis complete for {author_name}")
        
# #         return {
# #             "grobid_metadata": grobid_results,
# #             "ner_results": ner_results,
# #             "keyword_results": keyword_results,
# #             "topic_results": topic_results
# #         }
    
# #     def process_dataset(self, base_folder: str, output_dir: str = "output"):
# #         """
# #         Process entire dataset folder structure.
# #         Each subfolder = one author.
# #         """
# #         os.makedirs(output_dir, exist_ok=True)
        
# #         # Get all author folders
# #         author_folders = [
# #             f for f in os.listdir(base_folder)
# #             if os.path.isdir(os.path.join(base_folder, f))
# #         ]
        
# #         print(f"\n{'='*60}")
# #         print(f"Starting pipeline for {len(author_folders)} authors")
# #         print(f"{'='*60}")
        
# #         for author_name in author_folders:
# #             author_path = os.path.join(base_folder, author_name)
            
# #             # Process this author
# #             results = self.process_author_folder(author_path, author_name)
            
# #             # Save GROBID metadata JSON (original format)
# #             grobid_output_file = os.path.join(
# #                 output_dir,
# #                 f"{author_name}_grobid_metadata.json"
# #             )
# #             with open(grobid_output_file, "w", encoding="utf-8") as f:
# #                 json.dump(
# #                     results["grobid_metadata"],
# #                     f,
# #                     indent=2,
# #                     ensure_ascii=False
# #                 )
            
# #             # Save analysis results JSON (NER + Keywords + Topics)
# #             analysis_output_file = os.path.join(
# #                 output_dir,
# #                 f"{author_name}_analysis.json"
# #             )
# #             with open(analysis_output_file, "w", encoding="utf-8") as f:
# #                 json.dump(
# #                     {
# #                         "ner": results["ner_results"],
# #                         "keywords": results["keyword_results"],
# #                         "topics": results["topic_results"]
# #                     },
# #                     f,
# #                     indent=2,
# #                     ensure_ascii=False
# #                 )
            
# #             print(f"     Saved results to {output_dir}/")
        
# #         print(f"\n{'='*60}")
# #         print(f"Pipeline complete! Results saved to {output_dir}/")
# #         print(f"{'='*60}\n")


# # # ==================== MAIN EXECUTION ====================

# # if __name__ == "__main__":
# #     # Initialize pipeline
# #     pipeline = UnifiedPipeline(
# #         grobid_url="http://localhost:8070/api/processFulltextDocument",
# #         redis_host='localhost',
# #         redis_port=6379,
# #         redis_db=0
# #     )
    
# #     # Process dataset
# #     dataset_folder = r"D:\Gomathi_ai\Dataset\Dataset"
# #     pipeline.process_dataset(dataset_folder, output_dir="output")

# import os
# import json
# import redis
# import requests
# import xml.etree.ElementTree as ET
# import re
# from typing import Dict, List, Optional, Tuple
# from collections import defaultdict
# import traceback

# # Import the processing functions from other modules
# from ner_metadata import NerExtractor
# from keywords_metadata import UnifiedKeywordExtractor
# from topic_metadata import extract_topics


# class UnifiedPipeline:
#     """
#     End-to-end pipeline that:
#     1. Extracts metadata using GROBID (stores in JSON)
#     2. Collects raw text for NER, keywords, and topics (stores in Redis)
#     3. Processes all PDFs per author/folder together
#     4. Saves results in organized JSON and Redis cache
#     """
    
#     def __init__(
#         self,
#         grobid_url="http://localhost:8070/api/processFulltextDocument",
#         redis_host='localhost',
#         redis_port=6379,
#         redis_db=0
#     ):
#         self.grobid_url = grobid_url
        
#         # Initialize Redis connection
#         try:
#             self.redis_client = redis.Redis(
#                 host=redis_host,
#                 port=redis_port,
#                 db=redis_db,
#                 decode_responses=True
#             )
#             self.redis_client.ping()
#             print("     Redis connection established")
#         except Exception as e:
#             print(f"   Redis connection failed: {e}. Running without cache.")
#             self.redis_client = None
        
#         # Initialize extractors
#         self.ner_extractor = NerExtractor
#         self.keyword_extractor = UnifiedKeywordExtractor(log_file="keyword_extraction.log")
        
#         # Load NER model once
#         try:
#             self.ner_extractor.load_ner_model()
#             print("     NER model loaded successfully")
#         except Exception as e:
#             print(f"   NER model loading failed: {e}")
    
#     # ==================== GROBID HELPER METHODS ====================
    
#     def get_text(self, elem):
#         if elem is None:
#             return None
#         txt = elem.text
#         return txt.strip() if txt and txt.strip() else None

#     def join_person_name(self, pers_elem, ns):
#         if pers_elem is None:
#             return None
#         names = []
#         for f in pers_elem.findall("tei:forename", ns):
#             if f.text and f.text.strip():
#                 names.append(f.text.strip())
#         surname = pers_elem.find("tei:surname", ns)
#         if surname is not None and surname.text and surname.text.strip():
#             names.append(surname.text.strip())
#         return " ".join(names) if names else None

#     def extract_affiliation_text(self, aff_elem, ns):
#         if aff_elem is None:
#             return None
#         parts = []
#         for org in aff_elem.findall(".//tei:orgName", ns):
#             if org.text and org.text.strip():
#                 parts.append(org.text.strip())
#         for addr in aff_elem.findall(".//tei:addrLine", ns):
#             if addr.text and addr.text.strip():
#                 parts.append(addr.text.strip())
#         settlement = aff_elem.find(".//tei:settlement", ns)
#         if settlement is not None and settlement.text and settlement.text.strip():
#             parts.append(settlement.text.strip())
#         country = aff_elem.find(".//tei:country", ns)
#         if country is not None and country.text and country.text.strip():
#             parts.append(country.text.strip())
#         return ", ".join(parts) if parts else None

#     # ==================== TEXT EXTRACTION FROM TEI ====================
    
#     def extract_raw_text_from_tei(self, tei_xml: str) -> Dict[str, str]:
#         """
#         Extract different types of text from TEI XML for various processing needs
#         """
#         ns = {"tei": "http://www.tei-c.org/ns/1.0"}
#         root = ET.fromstring(tei_xml)
        
#         text_data = {
#             "raw_text": "",
#             "abstract_text": "",
#             "body_text": ""
#         }
        
#         # Extract abstract
#         profile = root.find("tei:teiHeader/tei:profileDesc", ns)
#         if profile is not None:
#             abstract_root = profile.find("tei:abstract", ns)
#             if abstract_root is not None:
#                 paras = abstract_root.findall(".//tei:p", ns)
#                 texts = ["".join(p.itertext()).strip() for p in paras if "".join(p.itertext()).strip()]
#                 text_data["abstract_text"] = " ".join(texts) if texts else "".join(abstract_root.itertext()).strip()
        
#         # Extract body text
#         body = root.find("tei:text/tei:body", ns)
#         if body is not None:
#             all_text_elements = []
#             for elem in body.iter():
#                 if elem.tag.endswith('p') or elem.tag.endswith('head'):
#                     text = "".join(elem.itertext()).strip()
#                     if text and len(text) > 10:
#                         all_text_elements.append(text)
            
#             text_data["body_text"] = " ".join(all_text_elements)
        
#         # Combine for full raw text
#         text_data["raw_text"] = f"{text_data['abstract_text']} {text_data['body_text']}".strip()
        
#         return text_data

#     # ==================== GROBID PARSING ====================
    
#     def parse_tei_metadata(self, tei_xml: str, ref_keywords=None, top_n=5):
#         """Parse TEI XML for metadata only"""
#         if ref_keywords is None:
#             ref_keywords = ["clustering", "density", "grid", "subspace", "dbscan", 
#                           "clique", "partition", "model-based"]
#         ref_keywords = [k.lower() for k in ref_keywords]

#         ns = {"tei": "http://www.tei-c.org/ns/1.0"}
#         root = ET.fromstring(tei_xml)
#         out = {}

#         # Metadata
#         fileDesc = root.find("tei:teiHeader/tei:fileDesc", ns)
#         if fileDesc is not None:
#             title_elem = fileDesc.find("tei:titleStmt/tei:title", ns)
#             out["title"] = self.get_text(title_elem)
#             out["funders"] = [self.get_text(x) for x in fileDesc.findall("tei:titleStmt/tei:funder/tei:orgName", ns) if self.get_text(x)]
#             pubStmt = fileDesc.find("tei:publicationStmt", ns)
#             out["publisher"] = self.get_text(pubStmt.find("tei:publisher", ns)) if pubStmt is not None else None
#             date_elem = fileDesc.find("tei:publicationStmt/tei:date", ns)
#             out["pub_date"] = date_elem.attrib.get("when") if date_elem is not None and date_elem.attrib.get("when") else self.get_text(date_elem)

#             authors_list = []
#             for bibl in fileDesc.findall("tei:sourceDesc/tei:biblStruct", ns):
#                 analytic = bibl.find("tei:analytic", ns)
#                 if analytic is None:
#                     continue
#                 for author in analytic.findall("tei:author", ns):
#                     pers = author.find("tei:persName", ns)
#                     name = self.join_person_name(pers, ns)
#                     aff_elem = author.find("tei:affiliation", ns)
#                     aff_text = self.extract_affiliation_text(aff_elem, ns)
#                     authors_list.append({"name": name, "affiliation": aff_text})
#             out["authors"] = authors_list

#             idnos = {}
#             for idn in fileDesc.findall(".//tei:idno", ns):
#                 typ = idn.attrib.get("type")
#                 if typ and idn.text and idn.text.strip():
#                     idnos[typ] = idn.text.strip()
#             out["identifiers"] = idnos

#         # Profile: keywords & abstract
#         profile = root.find("tei:teiHeader/tei:profileDesc", ns)
#         out["keywords"] = []
#         out["abstract"] = None
#         if profile is not None:
#             kterms = profile.findall(".//tei:textClass/tei:keywords/tei:term", ns)
#             out["keywords"] = [k.text.strip() for k in kterms if k.text and k.text.strip()]
#             abstract_root = profile.find("tei:abstract", ns)
#             if abstract_root is not None:
#                 paras = abstract_root.findall(".//tei:p", ns)
#                 texts = ["".join(p.itertext()).strip() for p in paras if "".join(p.itertext()).strip()]
#                 out["abstract"] = " ".join(texts) if texts else "".join(abstract_root.itertext()).strip()

#         # Headings
#         body = root.find("tei:text/tei:body", ns)
#         headings = []
#         seen = set()
#         if body is not None:
#             for head in body.findall(".//tei:head", ns):
#                 htxt = "".join(head.itertext()).strip()
#                 if not htxt or re.match(r'^\s*\d+\.?\s*$', htxt) or len(htxt) <= 1:
#                     continue
#                 if htxt not in seen:
#                     headings.append(htxt)
#                     seen.add(htxt)
#         out["headings"] = headings

#         # References
#         back = root.find("tei:text/tei:back", ns)
#         refs = []
#         if back is None:
#             back = root.find(".//tei:back", ns)
#         if back is not None:
#             for bibl in back.findall(".//tei:biblStruct", ns):
#                 ref = {"title": None, "authors": [], "publisher": None, "journal": None, 
#                       "year": None, "pages": None, "type": None, "raw_text": None}
#                 analytic = bibl.find("tei:analytic", ns)
#                 if analytic is not None:
#                     title_a = analytic.find("tei:title", ns)
#                     if title_a is not None and title_a.text and title_a.text.strip():
#                         ref["title"] = title_a.text.strip()
#                     for author in analytic.findall("tei:author", ns):
#                         pers = author.find("tei:persName", ns)
#                         name = self.join_person_name(pers, ns)
#                         if name:
#                             ref["authors"].append(name)
#                 monogr = bibl.find("tei:monogr", ns)
#                 if monogr is not None:
#                     mon_title = monogr.find("tei:title", ns)
#                     if mon_title is not None and mon_title.text and mon_title.text.strip():
#                         ref["journal"] = mon_title.text.strip()
#                         if ref["title"] is None:
#                             ref["title"] = mon_title.text.strip()
#                     imprint = monogr.find("tei:imprint", ns)
#                     if imprint is not None:
#                         pub = imprint.find("tei:publisher", ns)
#                         if pub is not None and pub.text and pub.text.strip():
#                             ref["publisher"] = pub.text.strip()
#                         date = imprint.find("tei:date", ns)
#                         if date is not None:
#                             year = date.attrib.get("when") or self.get_text(date)
#                             if year:
#                                 m = re.match(r'^(\d{4})', year)
#                                 ref["year"] = m.group(1) if m else year
#                 raw_parts = [x for x in [ref["title"], ref["journal"], ref["publisher"], " ".join(ref["authors"])] if x]
#                 ref["raw_text"] = " ".join(raw_parts).lower()
#                 refs.append(ref)

#         matched = [r for r in refs if any(k in (r["raw_text"] or "") for k in ref_keywords)]
#         if len(matched) < top_n:
#             for r in refs:
#                 if r not in matched:
#                     matched.append(r)
#                     if len(matched) >= top_n:
#                         break
#         out["top_references"] = matched[:top_n]

#         return out

#     # ==================== REDIS CACHE OPERATIONS ====================
    
#     def cache_author_text(self, author_name: str, pdf_name: str, text_data: Dict[str, str]):
#         """Store extracted text in Redis cache organized by author"""
#         if not self.redis_client:
#             return
        
#         try:
#             for text_type, text_content in text_data.items():
#                 key = f"text:{author_name}:{pdf_name}:{text_type}"
#                 self.redis_client.set(key, text_content)
#                 self.redis_client.expire(key, 86400)
#         except Exception as e:
#             print(f"Failed to cache text for {pdf_name}: {e}")
    
#     def get_author_combined_text(self, author_name: str) -> Dict[str, str]:
#         """Retrieve and combine all texts for an author from Redis"""
#         if not self.redis_client:
#             return {"raw_text": "", "abstract_text": "", "body_text": ""}
        
#         try:
#             pattern = f"text:{author_name}:*"
#             keys = self.redis_client.keys(pattern)
            
#             combined = defaultdict(list)
            
#             for key in keys:
#                 parts = key.split(":")
#                 if len(parts) >= 4:
#                     text_type = parts[3]
#                     text_content = self.redis_client.get(key)
#                     if text_content:
#                         combined[text_type].append(text_content)
            
#             return {
#                 text_type: " ".join(texts)
#                 for text_type, texts in combined.items()
#             }
#         except Exception as e:
#             print(f"Failed to retrieve cached text for {author_name}: {e}")
#             return {"raw_text": "", "abstract_text": "", "body_text": ""}
    
#     def cache_results(self, author_name: str, result_type: str, data: Dict):
#         """Cache processing results in Redis"""
#         if not self.redis_client:
#             return
        
#         try:
#             key = f"results:{author_name}:{result_type}"
#             self.redis_client.set(key, json.dumps(data, ensure_ascii=False))
#             self.redis_client.expire(key, 86400)
#         except Exception as e:
#             print(f"Failed to cache {result_type} results for {author_name}: {e}")
    
#     # ==================== MAIN PROCESSING PIPELINE ====================
    
#     def process_single_pdf(self, pdf_path: str, author_name: str, pdf_name: str) -> Optional[Dict]:
#         """Process a single PDF through GROBID and extract text for caching"""
#         print(f"  Processing: {pdf_name}")
        
#         try:
#             with open(pdf_path, "rb") as f:
#                 files = {"input": f}
#                 params = {"consolidateHeader": 1, "generateIDs": 1}
#                 response = requests.post(self.grobid_url, files=files, params=params, timeout=60)
            
#             if response.status_code != 200:
#                 print(f"     GROBID error for {pdf_name}: {response.status_code}")
#                 return None
            
#             tei_xml = response.text
            
#             metadata = self.parse_tei_metadata(tei_xml)
#             text_data = self.extract_raw_text_from_tei(tei_xml)
#             self.cache_author_text(author_name, pdf_name, text_data)
            
#             return metadata
            
#         except Exception as e:
#             print(f"     Error processing {pdf_name}: {e}")
#             return None
    
#     def process_author_folder(self, author_folder_path: str, author_name: str) -> Dict:
#         """Process all PDFs for a single author with error handling"""
#         print(f"\n{'='*60}")
#         print(f"Processing author: {author_name}")
#         print(f"{'='*60}")
        
#         grobid_results = {}
        
#         # Step 1: Process all PDFs and cache text
#         pdf_files = [f for f in os.listdir(author_folder_path) if f.lower().endswith(".pdf")]
        
#         for pdf_file in pdf_files:
#             pdf_path = os.path.join(author_folder_path, pdf_file)
#             metadata = self.process_single_pdf(pdf_path, author_name, pdf_file)
#             if metadata:
#                 grobid_results[pdf_file] = metadata
        
#         print(f"\n     Processed {len(grobid_results)} PDFs")
        
#         # Step 2: Retrieve combined text from cache
#         print(f"  Retrieving cached text for analysis...")
#         combined_text = self.get_author_combined_text(author_name)
        
#         # Step 3: Run NER with error handling
#         print(f"  Running NER extraction...")
#         ner_results = {}
#         if combined_text["raw_text"]:
#             try:
#                 ner_results = self.ner_extractor.extract_ner_metadata(
#                     combined_text["raw_text"],
#                     log_errors=False
#                 )
#                 self.cache_results(author_name, "ner", ner_results)
#                 print(f"     NER extraction successful")
#             except Exception as e:
#                 print(f"     NER extraction failed: {e}")
#                 ner_results = {}
        
#         # Step 4: Run keyword extraction with error handling
#         print(f"  Running keyword extraction...")
#         keyword_results = {}
#         keyword_text = f"{combined_text['abstract_text']} {combined_text['body_text']}".strip()
#         if keyword_text:
#             try:
#                 keyword_results = self.keyword_extractor.extract_text_keywords(
#                     keyword_text,
#                     top_n=20
#                 )
#                 self.cache_results(author_name, "keywords", keyword_results)
#                 print(f"     Keyword extraction successful")
#             except Exception as e:
#                 print(f"     Keyword extraction failed: {e}")
#                 keyword_results = {}
        
#         # Step 5: Run topic modeling with error handling
#         print(f"  Running topic extraction...")
#         topic_results = {}
#         if combined_text["body_text"]:
#             try:
#                 topic_results = extract_topics(
#                     combined_text["body_text"],
#                     n_topics=10,
#                     n_words=10
#                 )
#                 self.cache_results(author_name, "topics", topic_results)
#                 print(f"     Topic extraction successful")
#             except Exception as e:
#                 print(f"     Topic extraction failed: {e}")
#                 topic_results = {}
        
#         print(f"     Analysis complete for {author_name}")
        
#         return {
#             "grobid_metadata": grobid_results,
#             "ner_results": ner_results,
#             "keyword_results": keyword_results,
#             "topic_results": topic_results
#         }
    
#     def process_dataset(self, base_folder: str, output_dir: str = "output"):
#         """Process entire dataset folder structure"""
#         os.makedirs(output_dir, exist_ok=True)
        
#         author_folders = [
#             f for f in os.listdir(base_folder)
#             if os.path.isdir(os.path.join(base_folder, f))
#         ]
        
#         print(f"\n{'='*60}")
#         print(f"Starting pipeline for {len(author_folders)} authors")
#         print(f"{'='*60}")
        
#         for idx, author_name in enumerate(author_folders, 1):
#             print(f"\nProgress: {idx}/{len(author_folders)}")
#             author_path = os.path.join(base_folder, author_name)
            
#             try:
#                 results = self.process_author_folder(author_path, author_name)
                
#                 # Save GROBID metadata JSON
#                 grobid_output_file = os.path.join(
#                     output_dir,
#                     f"{author_name}_grobid_metadata.json"
#                 )
#                 with open(grobid_output_file, "w", encoding="utf-8") as f:
#                     json.dump(
#                         results["grobid_metadata"],
#                         f,
#                         indent=2,
#                         ensure_ascii=False
#                     )
                
#                 # Save analysis results JSON
#                 analysis_output_file = os.path.join(
#                     output_dir,
#                     f"{author_name}_analysis.json"
#                 )
#                 with open(analysis_output_file, "w", encoding="utf-8") as f:
#                     json.dump(
#                         {
#                             "ner": results["ner_results"],
#                             "keywords": results["keyword_results"],
#                             "topics": results["topic_results"]
#                         },
#                         f,
#                         indent=2,
#                         ensure_ascii=False
#                     )
                
#                 print(f"     Saved results to {output_dir}/")
#             except Exception as e:
#                 print(f"     Failed to process {author_name}: {e}")
#                 traceback.print_exc()
#                 continue
        
#         print(f"\n{'='*60}")
#         print(f"Pipeline complete! Results saved to {output_dir}/")
#         print(f"{'='*60}\n")


# def main():
#     """Main execution function"""
#     pipeline = UnifiedPipeline(
#         grobid_url="http://localhost:8070/api/processFulltextDocument",
#         redis_host='localhost',
#         redis_port=6379,
#         redis_db=0
#     )
    
#     dataset_folder = r"D:\\Gomathi_ai\\Dataset\\Dataset"
#     pipeline.process_dataset(dataset_folder, output_dir="output")


# if __name__ == "__main__":
#     main()

import os
import json
import redis
import requests
import xml.etree.ElementTree as ET
import re
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import traceback

# Import the processing functions from other modules
from ner_metadata import NerExtractor
from keywords_metadata import UnifiedKeywordExtractor
from topic_metadata import extract_topics


class UnifiedPipeline:
    """
    End-to-end pipeline that:
    1. Extracts metadata using GROBID (stores in JSON)
    2. Collects raw text for NER, keywords, and topics (stores in Redis)
    3. Processes all PDFs per author/folder together
    4. Saves results in organized JSON and Redis cache
    """
    
    def __init__(
        self,
        grobid_url="http://localhost:8070/api/processFulltextDocument",
        redis_host='localhost',
        redis_port=6379,
        redis_db=0
    ):
        self.grobid_url = grobid_url
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True
            )
            self.redis_client.ping()
            print("     Redis connection established")
        except Exception as e:
            print(f"    Redis connection failed: {e}. Running without cache.")
            self.redis_client = None
        
        # Initialize extractors
        self.ner_extractor = NerExtractor
        self.keyword_extractor = UnifiedKeywordExtractor(log_file="keyword_extraction.log")
        
        # Load NER model once
        try:
            self.ner_extractor.load_ner_model()
            print("     NER model loaded successfully")
        except Exception as e:
            print(f"    NER model loading failed: {e}")
    
    # ==================== GROBID HELPER METHODS ====================
    
    def get_text(self, elem):
        if elem is None:
            return None
        txt = elem.text
        return txt.strip() if txt and txt.strip() else None

    def join_person_name(self, pers_elem, ns):
        if pers_elem is None:
            return None
        names = []
        for f in pers_elem.findall("tei:forename", ns):
            if f.text and f.text.strip():
                names.append(f.text.strip())
        surname = pers_elem.find("tei:surname", ns)
        if surname is not None and surname.text and surname.text.strip():
            names.append(surname.text.strip())
        return " ".join(names) if names else None

    def extract_affiliation_text(self, aff_elem, ns):
        if aff_elem is None:
            return None
        parts = []
        for org in aff_elem.findall(".//tei:orgName", ns):
            if org.text and org.text.strip():
                parts.append(org.text.strip())
        for addr in aff_elem.findall(".//tei:addrLine", ns):
            if addr.text and addr.text.strip():
                parts.append(addr.text.strip())
        settlement = aff_elem.find(".//tei:settlement", ns)
        if settlement is not None and settlement.text and settlement.text.strip():
            parts.append(settlement.text.strip())
        country = aff_elem.find(".//tei:country", ns)
        if country is not None and country.text and country.text.strip():
            parts.append(country.text.strip())
        return ", ".join(parts) if parts else None

    # ==================== TEXT EXTRACTION FROM TEI ====================
    
    def extract_raw_text_from_tei(self, tei_xml: str) -> Dict[str, str]:
        """
        Extract different types of text from TEI XML for various processing needs
        """
        ns = {"tei": "http://www.tei-c.org/ns/1.0"}
        root = ET.fromstring(tei_xml)
        
        text_data = {
            "raw_text": "",
            "abstract_text": "",
            "body_text": ""
        }
        
        # Extract abstract
        profile = root.find("tei:teiHeader/tei:profileDesc", ns)
        if profile is not None:
            abstract_root = profile.find("tei:abstract", ns)
            if abstract_root is not None:
                paras = abstract_root.findall(".//tei:p", ns)
                texts = ["".join(p.itertext()).strip() for p in paras if "".join(p.itertext()).strip()]
                text_data["abstract_text"] = " ".join(texts) if texts else "".join(abstract_root.itertext()).strip()
        
        # Extract body text
        body = root.find("tei:text/tei:body", ns)
        if body is not None:
            all_text_elements = []
            for elem in body.iter():
                if elem.tag.endswith('p') or elem.tag.endswith('head'):
                    text = "".join(elem.itertext()).strip()
                    if text and len(text) > 10:
                        all_text_elements.append(text)
            
            text_data["body_text"] = " ".join(all_text_elements)
        
        # Combine for full raw text
        text_data["raw_text"] = f"{text_data['abstract_text']} {text_data['body_text']}".strip()
        
        return text_data

    # ==================== GROBID PARSING ====================
    
    def parse_tei_metadata(self, tei_xml: str, ref_keywords=None, top_n=5):
        """Parse TEI XML for metadata only"""
        if ref_keywords is None:
            ref_keywords = ["clustering", "density", "grid", "subspace", "dbscan", 
                          "clique", "partition", "model-based"]
        ref_keywords = [k.lower() for k in ref_keywords]

        ns = {"tei": "http://www.tei-c.org/ns/1.0"}
        root = ET.fromstring(tei_xml)
        out = {}

        # Metadata
        fileDesc = root.find("tei:teiHeader/tei:fileDesc", ns)
        if fileDesc is not None:
            title_elem = fileDesc.find("tei:titleStmt/tei:title", ns)
            out["title"] = self.get_text(title_elem)
            out["funders"] = [self.get_text(x) for x in fileDesc.findall("tei:titleStmt/tei:funder/tei:orgName", ns) if self.get_text(x)]
            pubStmt = fileDesc.find("tei:publicationStmt", ns)
            out["publisher"] = self.get_text(pubStmt.find("tei:publisher", ns)) if pubStmt is not None else None
            date_elem = fileDesc.find("tei:publicationStmt/tei:date", ns)
            out["pub_date"] = date_elem.attrib.get("when") if date_elem is not None and date_elem.attrib.get("when") else self.get_text(date_elem)

            authors_list = []
            for bibl in fileDesc.findall("tei:sourceDesc/tei:biblStruct", ns):
                analytic = bibl.find("tei:analytic", ns)
                if analytic is None:
                    continue
                for author in analytic.findall("tei:author", ns):
                    pers = author.find("tei:persName", ns)
                    name = self.join_person_name(pers, ns)
                    aff_elem = author.find("tei:affiliation", ns)
                    aff_text = self.extract_affiliation_text(aff_elem, ns)
                    authors_list.append({"name": name, "affiliation": aff_text})
            out["authors"] = authors_list

            idnos = {}
            for idn in fileDesc.findall(".//tei:idno", ns):
                typ = idn.attrib.get("type")
                if typ and idn.text and idn.text.strip():
                    idnos[typ] = idn.text.strip()
            out["identifiers"] = idnos

        # Profile: keywords & abstract
        profile = root.find("tei:teiHeader/tei:profileDesc", ns)
        out["keywords"] = []
        out["abstract"] = None
        if profile is not None:
            kterms = profile.findall(".//tei:textClass/tei:keywords/tei:term", ns)
            out["keywords"] = [k.text.strip() for k in kterms if k.text and k.text.strip()]
            abstract_root = profile.find("tei:abstract", ns)
            if abstract_root is not None:
                paras = abstract_root.findall(".//tei:p", ns)
                texts = ["".join(p.itertext()).strip() for p in paras if "".join(p.itertext()).strip()]
                out["abstract"] = " ".join(texts) if texts else "".join(abstract_root.itertext()).strip()

        # Headings
        body = root.find("tei:text/tei:body", ns)
        headings = []
        seen = set()
        if body is not None:
            for head in body.findall(".//tei:head", ns):
                htxt = "".join(head.itertext()).strip()
                if not htxt or re.match(r'^\s*\d+\.?\s*$', htxt) or len(htxt) <= 1:
                    continue
                if htxt not in seen:
                    headings.append(htxt)
                    seen.add(htxt)
        out["headings"] = headings

        # References
        back = root.find("tei:text/tei:back", ns)
        refs = []
        if back is None:
            back = root.find(".//tei:back", ns)
        if back is not None:
            for bibl in back.findall(".//tei:biblStruct", ns):
                ref = {"title": None, "authors": [], "publisher": None, "journal": None, 
                      "year": None, "pages": None, "type": None, "raw_text": None}
                analytic = bibl.find("tei:analytic", ns)
                if analytic is not None:
                    title_a = analytic.find("tei:title", ns)
                    if title_a is not None and title_a.text and title_a.text.strip():
                        ref["title"] = title_a.text.strip()
                    for author in analytic.findall("tei:author", ns):
                        pers = author.find("tei:persName", ns)
                        name = self.join_person_name(pers, ns)
                        if name:
                            ref["authors"].append(name)
                monogr = bibl.find("tei:monogr", ns)
                if monogr is not None:
                    mon_title = monogr.find("tei:title", ns)
                    if mon_title is not None and mon_title.text and mon_title.text.strip():
                        ref["journal"] = mon_title.text.strip()
                        if ref["title"] is None:
                            ref["title"] = mon_title.text.strip()
                    imprint = monogr.find("tei:imprint", ns)
                    if imprint is not None:
                        pub = imprint.find("tei:publisher", ns)
                        if pub is not None and pub.text and pub.text.strip():
                            ref["publisher"] = pub.text.strip()
                        date = imprint.find("tei:date", ns)
                        if date is not None:
                            year = date.attrib.get("when") or self.get_text(date)
                            if year:
                                m = re.match(r'^(\d{4})', year)
                                ref["year"] = m.group(1) if m else year
                raw_parts = [x for x in [ref["title"], ref["journal"], ref["publisher"], " ".join(ref["authors"])] if x]
                ref["raw_text"] = " ".join(raw_parts).lower()
                refs.append(ref)

        matched = [r for r in refs if any(k in (r["raw_text"] or "") for k in ref_keywords)]
        if len(matched) < top_n:
            for r in refs:
                if r not in matched:
                    matched.append(r)
                    if len(matched) >= top_n:
                        break
        out["top_references"] = matched[:top_n]

        return out

    # ==================== REDIS CACHE OPERATIONS ====================
    
    def cache_author_text(self, author_name: str, pdf_name: str, text_data: Dict[str, str]):
        """Store extracted text in Redis cache organized by author"""
        if not self.redis_client:
            return
        
        try:
            for text_type, text_content in text_data.items():
                key = f"text:{author_name}:{pdf_name}:{text_type}"
                self.redis_client.set(key, text_content)
                self.redis_client.expire(key, 86400)
        except Exception as e:
            print(f"Failed to cache text for {pdf_name}: {e}")
    
    def get_author_combined_text(self, author_name: str) -> Dict[str, str]:
        """Retrieve and combine all texts for an author from Redis"""
        if not self.redis_client:
            return {"raw_text": "", "abstract_text": "", "body_text": ""}
        
        try:
            pattern = f"text:{author_name}:*"
            keys = self.redis_client.keys(pattern)
            
            combined = defaultdict(list)
            
            for key in keys:
                parts = key.split(":")
                if len(parts) >= 4:
                    text_type = parts[3]
                    text_content = self.redis_client.get(key)
                    if text_content:
                        combined[text_type].append(text_content)
            
            return {
                text_type: " ".join(texts)
                for text_type, texts in combined.items()
            }
        except Exception as e:
            print(f"Failed to retrieve cached text for {author_name}: {e}")
            return {"raw_text": "", "abstract_text": "", "body_text": ""}
    
    def cache_results(self, author_name: str, result_type: str, data: Dict):
        """Cache processing results in Redis"""
        if not self.redis_client:
            return
        
        try:
            key = f"results:{author_name}:{result_type}"
            self.redis_client.set(key, json.dumps(data, ensure_ascii=False))
            self.redis_client.expire(key, 86400)
        except Exception as e:
            print(f"Failed to cache {result_type} results for {author_name}: {e}")
    
    # ==================== MAIN PROCESSING PIPELINE ====================
    
    def process_single_pdf(self, pdf_path: str, author_name: str, pdf_name: str) -> Optional[Dict]:
        """Process a single PDF through GROBID and extract text for caching"""
        print(f"  Processing: {pdf_name}")
        
        try:
            with open(pdf_path, "rb") as f:
                files = {"input": f}
                params = {"consolidateHeader": 1, "generateIDs": 1}
                response = requests.post(self.grobid_url, files=files, params=params, timeout=60)
            
            if response.status_code != 200:
                print(f"       GROBID error for {pdf_name}: {response.status_code}")
                return None
            
            tei_xml = response.text
            
            metadata = self.parse_tei_metadata(tei_xml)
            text_data = self.extract_raw_text_from_tei(tei_xml)
            self.cache_author_text(author_name, pdf_name, text_data)
            
            return metadata
            
        except Exception as e:
            print(f"       Error processing {pdf_name}: {e}")
            return None
    
    def process_dataset(
        self,
        base_folder: str,
        output_dir: str = "output",
        run_ner: bool = True,
        run_keywords: bool = True,
        run_topics: bool = True
    ):
        """Process entire dataset folder structure"""
        os.makedirs(output_dir, exist_ok=True)
        author_folders = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]

        print(f"\n{'='*60}")
        print(f"Starting pipeline for {len(author_folders)} authors")
        print(f"{'='*60}")

        for idx, author_name in enumerate(author_folders, 1):
            print(f"\nProgress: {idx}/{len(author_folders)}")
            author_path = os.path.join(base_folder, author_name)

            try:
                results = self.process_author_folder(
                    author_path,
                    author_name,
                    run_ner=run_ner,
                    run_keywords=run_keywords,
                    run_topics=run_topics
                )

                grobid_output_file = os.path.join(output_dir, f"{author_name}_grobid_metadata.json")
                with open(grobid_output_file, "w", encoding="utf-8") as f:
                    json.dump(results["grobid_metadata"], f, indent=2, ensure_ascii=False)

                analysis_output_file = os.path.join(output_dir, f"{author_name}_analysis.json")
                with open(analysis_output_file, "w", encoding="utf-8") as f:
                    json.dump({
                        "ner": results["ner_results"],
                        "keywords": results["keyword_results"],
                        "topics": results["topic_results"]
                    }, f, indent=2, ensure_ascii=False)

                print(f"   Saved results to {output_dir}/")
            except Exception as e:
                print(f"   Failed to process {author_name}: {e}")
                traceback.print_exc()
                continue

        print(f"\n{'='*60}")
        print(f"Pipeline complete! Results saved to {output_dir}/")
        print(f"{'='*60}\n")

    
    def process_author_folder(
        self,
        author_folder_path: str,
        author_name: str,
        run_ner: bool = True,
        run_keywords: bool = True,
        run_topics: bool = True
    ) -> Dict:
        """Process all PDFs for a single author with optional feature toggles"""
        print(f"\n{'='*60}")
        print(f"Processing author: {author_name}")
        print(f"{'='*60}")

        grobid_results = {}

        # Step 1: Process all PDFs
        pdf_files = [f for f in os.listdir(author_folder_path) if f.lower().endswith(".pdf")]

        for pdf_file in pdf_files:
            pdf_path = os.path.join(author_folder_path, pdf_file)
            metadata = self.process_single_pdf(pdf_path, author_name, pdf_file)
            if metadata:
                grobid_results[pdf_file] = metadata

        print(f"\n       Processed {len(grobid_results)} PDFs")

        # Step 2: Retrieve cached text
        print(f"  Retrieving cached text for analysis...")
        combined_text = self.get_author_combined_text(author_name)

        # Step 3: Run NER (if enabled)
        ner_results = {}
        if run_ner:
            print(f"  Running NER extraction...")
            if combined_text.get("raw_text"):
                try:
                    ner_results = self.ner_extractor.extract_ner_metadata(
                        combined_text["raw_text"],
                        log_errors=False
                    )
                    self.cache_results(author_name, "ner", ner_results)
                    print(f"       NER extraction successful")
                except Exception as e:
                    print(f"      NER extraction failed: {e}")
        else:
            print("  Skipping NER extraction (disabled)")

        # Step 4: Run keyword extraction (if enabled)
        keyword_results = {}
        if run_keywords:
            print(f"  Running keyword extraction...")
            keyword_text = f"{combined_text.get('abstract_text', '')} {combined_text.get('body_text', '')}".strip()
            if keyword_text:
                try:
                    keyword_results = self.keyword_extractor.extract_text_keywords(keyword_text, top_n=20)
                    self.cache_results(author_name, "keywords", keyword_results)
                    print(f"       Keyword extraction successful")
                except Exception as e:
                    print(f"      Keyword extraction failed: {e}")
        else:
            print("  Skipping keyword extraction (disabled)")

        # Step 5: Run topic modeling (if enabled)
        topic_results = {}
        if run_topics:
            print(f"  Running topic extraction...")
            if combined_text.get("body_text"):
                try:
                    topic_results = extract_topics(
                        combined_text["body_text"],
                        n_topics=10,
                        n_words=10
                    )
                    self.cache_results(author_name, "topics", topic_results)
                    print(f"       Topic extraction successful")
                except Exception as e:
                    print(f"      Topic extraction failed: {e}")
        else:
            print("  Skipping topic extraction (disabled)")

        print(f"       Analysis complete for {author_name}")

        return {
            "grobid_metadata": grobid_results,
            "ner_results": ner_results,
            "keyword_results": keyword_results,
            "topic_results": topic_results
        }



def main():
    pipeline = UnifiedPipeline(
        grobid_url="http://localhost:8070/api/processFulltextDocument",
        redis_host='localhost',
        redis_port=6379,
        redis_db=0
    )

    dataset_folder = r"D:\Gomathi_ai\Dataset\Dataset"
    pipeline.process_dataset(
        dataset_folder,
        output_dir="output",
        run_ner=False,         # skip NER
        run_keywords=False,    # skip keywords
        run_topics=False       # skip topics
    )



if __name__ == "__main__":
    main()