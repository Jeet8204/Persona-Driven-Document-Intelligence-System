Approach Explanation: Persona-Driven Document Intelligence
This document outlines the methodology and architectural choices made for the Persona-Driven Document Intelligence System. The primary goal is to extract relevant information from a collection of PDF documents and rank it based on a user-defined persona and job-to-be-done, all while adhering to strict operational constraints such as CPU-only execution, limited model size, and offline functionality. The design emphatically prioritizes robustness, accuracy, and efficiency across all stages of the pipeline.

1. Core Architecture
The system is engineered with a modular and decoupled architecture, ensuring maintainability, scalability, and clear separation of concerns. Each component plays a specific, well-defined role in the overall pipeline, contributing to the system's resilience and performance:

PDF Processing (app/processing/pdf_parser.py): This is the foundational layer, meticulously designed for transforming unstructured PDF data into semantically meaningful, structured text segments. It directly addresses the inherent challenges of PDF parsing, particularly the accurate extraction of headings and associated content.

Embedding (app/ranking/embedding.py): This module acts as the crucial bridge between human language and machine-understandable numerical representations. It is responsible for converting textual content into dense vector embeddings, enabling mathematical comparison for semantic similarity.

Ranking (app/ranking/engine.py): As the intelligence core, this component calculates semantic similarity scores and prioritizes document content based on the user's specific query (persona and job task). It incorporates advanced techniques like Maximal Marginal Relevance (MMR) for diverse results.

Input/Output Formatting (app/io/formatter.py): This module manages the presentation of the final, processed results in a user-friendly and machine-readable JSON format, ensuring consistency and ease of integration with other systems.

Configuration (app/config.py): A centralized hub for all system-wide parameters, thresholds, and file paths. This design choice significantly enhances robustness by allowing for easy tuning and adaptation to different document types or performance requirements without necessitating changes to the core logic.

2. Detailed Component Breakdown and Robustness
2.1. PDF Processing (app/processing/pdf_parser.py)
This module is arguably the most critical for the system's overall accuracy and robustness, as the quality of downstream ranking heavily depends on the precision of extracted content and the correct identification of headings. The approach prioritizes resilience against varying PDF structures and quality:

Text Extraction Foundation with Layout Awareness:

The module primarily utilizes PyMuPDF (fitz), a high-performance library known for its efficiency and, crucially, its ability to access detailed layout information. Unlike simpler text extractors, PyMuPDF allows inspecting individual text spans (text fragments), providing attributes like font_size, font name, bbox (bounding box coordinates), and flags (indicating properties like bold or italic). This granular access to visual properties is fundamental for robust and intelligent heading detection.

Code Insight: page.get_text("dict")["blocks"] is used to retrieve text organized into blocks, lines, and spans, preserving the layout structure essential for heuristic analysis.

OCR Fallback for Comprehensive Accessibility:

A crucial robustness feature is the integrated OCR (Optical Character Recognition) fallback. If PyMuPDF detects that a page has no selectable text layer (a common scenario for scanned documents or PDFs created from images), the system automatically renders that page as a high-resolution image (page.get_pixmap(dpi=OCR_RESOLUTION_DPI)). Pillow then processes this image, and pytesseract performs OCR to extract text. This ensures that content from visually-rich or legacy PDFs is not lost, even if it introduces some OCR-related noise. The OCR_RESOLUTION_DPI in app/config.py allows balancing OCR accuracy with processing speed.

Intelligent Sectioning Strategy (Robust Stateful Heuristic):

The current implementation uses a stateful heuristic approach as its primary method for identifying headings and segmenting content. This is particularly robust for PDFs without explicit internal outlines (bookmarks) or with inconsistent outline structures.

Heuristic-Based Heading Detection: This involves dynamically analyzing the visual properties of text spans on each page:

Font Analysis: Text spans are considered potential headings if their font_size is above a MIN_HEADING_FONT_SIZE threshold, they are marked as bold (checked via the is_heading helper function which inspects span["font"].lower() and span["flags"]), and their word_count is concise (<= HEADING_MAX_WORDS). These thresholds are configurable in app/config.py, allowing the system to adapt robustly to different document styles and conventions without code changes.

Stateful Content Segmentation: A key aspect of this heuristic is its intelligent content segmentation across pages. The extract_sections_from_file function maintains a current_section state. When a text block is identified as a new heading, it signals the logical end of the previous section's content and the beginning of a new one. All subsequent non-heading text blocks are then sequentially accumulated as the content (content_blocks) belonging to that specific heading. This dynamic process ensures that each extracted section's text field accurately corresponds only to the content directly under its section_title, preventing the inclusion of unrelated or noisy content, even if the section spans multiple pages.

Code Insight:

# In pdf_parser.py: extract_sections_from_file
current_section = None # State variable
for page_num, page in enumerate(doc):
    blocks = page.get_text("dict").get("blocks", [])
    blocks.sort(key=lambda b: b["bbox"][1]) # Process in reading order
    for b in blocks:
        if b['type'] == 0: # Text block
            # ... (text extraction from block)
            first_span = b["lines"][0]["spans"][0]
            if is_heading(first_span): # Check if it's a new heading
                if current_section: # If previous section exists, finalize it
                    # ... (join content_blocks, extract subsections, append to all_sections)
                # Start new section
                current_section = {
                    "filename": os.path.basename(pdf_path),
                    "page_number": page_num + 1,
                    "section_title": clean_text(first_span['text']),
                    "content_blocks": [], # Accumulator for content
                }
            elif current_section: # If not a heading, and we're in a section
                current_section["content_blocks"].append(block_text)
# ... (finalize last section)


This stateful logic allows the parser to build complete sections by accumulating text blocks that belong to the same logical section, even if they are separated by page breaks.

Subsection Granularity for Fine-Grained Analysis:

Within each identified section's main content, the text is further segmented into subsections (typically representing paragraphs). This is achieved by splitting the text on multiple newline characters (\n{2,}). A MIN_WORDS_FOR_SUBSECTION threshold (configurable in app/config.py) is applied to prevent very short, potentially noisy, or fragmented text snippets from being erroneously treated as meaningful subsections, thereby improving the quality of the smaller content chunks.

Comprehensive Text Cleaning (clean_text):

The clean_text utility is applied aggressively to all extracted text. It performs two critical cleaning operations:

Whitespace Normalization: re.sub(r'\s+', ' ', text).strip() replaces multiple whitespace characters with a single space and removes leading/trailing whitespace. This standardizes text formatting.

Control Character Removal: Crucially, it filters out a broad range of non-printable ASCII control characters ([\x00-\x08\x0b\x0c\x0e-\x1f\x7f]). These hidden characters often appear in PDF extractions and can corrupt embeddings, interfere with text display, or cause parsing errors in downstream components. Their removal significantly enhances data quality and overall system robustness.

2.2. Embedding (app/ranking/embedding.py)
This module forms the backbone of the system's semantic understanding, transforming human language into a mathematically comparable format.

Sentence Transformer for High-Quality Semantic Representation: The system leverages the sentence-transformers library, a powerful and widely-used tool for generating high-quality text embeddings. These models are pre-trained on vast amounts of text data to understand intricate semantic relationships, effectively mapping sentences and paragraphs into a dense vector space where texts with similar meanings are positioned numerically closer together.

Efficient Lazy Model Loading: The EmbeddingModel class is designed for efficiency. It implements lazy loading, meaning the SentenceTransformer model (specified by SENTENCE_TRANSFORMER_MODEL_PATH in app/config.py) is loaded into memory only when its get_embeddings method is called for the first time. This optimizes startup time and resource usage if embeddings are not immediately required.

Code Insight:

# In embedding.py: EmbeddingModel.get_embeddings
if self.model is None:
    self._load_model() # Private method to handle the actual loading
# ... (rest of get_embeddings logic)


This pattern ensures the model is loaded only once and only when truly needed.

Vector Generation with Crucial Normalization: The get_embeddings method efficiently converts input texts (which include the combined persona-job query, extracted section titles, and subsection content) into numerical numpy array embeddings. A critical optimization here is the use of normalize_embeddings=True during the encoding process.

Code Insight:

# In embedding.py: EmbeddingModel.get_embeddings
embeddings = self.model.encode(
    texts,
    convert_to_numpy=True,
    show_progress_bar=False,
    normalize_embeddings=True # THIS IS KEY
)


By normalizing embeddings to unit vectors (length 1), the dot product between two such vectors becomes mathematically equivalent to their cosine similarity. This allows the RankingEngine to use np.dot() (which is generally faster) instead of sklearn.metrics.pairwise.cosine_similarity for calculating similarities, leading to performance gains during ranking.

2.3. Ranking (app/ranking/engine.py)
This is where the "intelligence" of the system manifests, prioritizing content based on its relevance to the user's specific needs, with a focus on both relevance and diversity.

Unified Query Representation for Focused Relevance: The persona_role and job_task (e.g., "PhD Researcher. Prepare a literature review...") are intelligently concatenated into a single, coherent query string. This unified query is then embedded, ensuring that the ranking process considers both aspects simultaneously and provides a highly focused relevance score.

Comprehensive Content Vectorization: All extracted section_title and subsection['text'] fields from the PDF documents are independently converted into embeddings. This creates a rich set of vectors that numerically represent every meaningful chunk of content within the document collection.

Weighted Initial Scoring for Sections: For sections, an initial relevance score (section['score']) is calculated using a weighted sum of the cosine similarity of the query to the section's title and its full text content.

Code Insight:

# In engine.py: rank method, for sections
title_weight, content_weight = 0.6, 0.4 # Configurable weights
# ... (calculate title_sims and content_sims)
section['score'] = (title_sims[i] * title_weight) + (content_sims[i] * content_weight)


This allows the system to prioritize matches found in the more concise section_title (which often summarizes the content) over broader matches found only in the longer text content, leading to more accurate initial rankings.

Maximal Marginal Relevance (MMR) for Diversity: This is a critical enhancement designed to overcome the limitation of pure relevance ranking, which often returns redundant information.

Purpose: MMR re-ranks results to ensure that selected documents are not only highly relevant to the query but also diverse from each other. This prevents the output from being dominated by highly similar sections that might cover the exact same point, ensuring a broader and more informative summary.

How it Works (_apply_mmr method):

It first selects the document with the highest initial relevance score to the query.

Then, in an iterative process, it selects the next document that maximizes a combination of its relevance to the query and its dissimilarity to all already-selected documents.

The lambda_val parameter (defaulting to 0.7) controls this trade-off: a higher lambda_val prioritizes relevance, while a lower one prioritizes diversity.

Code Insight:

# In engine.py: _apply_mmr method
relevance = relevance_scores[idx] # Relevance to query
max_sim = np.max(cosine_similarity(doc_embeddings[idx].reshape(1, -1), selected_embeddings)) # Redundancy to selected
mmr_score = lambda_val * relevance - (1 - lambda_val) * max_sim # MMR formula


The rank method now takes a larger CANDIDATE_POOL_SIZE (e.g., 25) from the initial ranking and passes this pool to _apply_mmr, which then selects the final top_k (fixed at 5) diverse results.

Storing Embeddings for MMR:

section['embedding'] = content_embeddings[i] and sub['embedding'] = subsection_embeddings[i] are added.

Purpose: The MMR algorithm needs direct access to the embeddings of the documents to calculate their similarity to each other. Storing them directly in the document dictionaries avoids redundant re-calculation.

2.4. Input/Output Formatting (app/io/formatter.py)
This module ensures the final results are presented clearly, consistently, and in a machine-readable format.

Standardized JSON Output Schema: The format_output function structures all relevant data—including document metadata, the defined persona and job task, total processing time, and the meticulously ranked sections and subsections—into a well-defined JSON schema. This standardized format is both human-readable and easily parsable by other applications.

Fixed Top 5 Output & Cleanliness: It explicitly ensures that only the top 5 ranked sections and subsections (as determined by engine.py's MMR output) are included in the final JSON. Crucially, it also filters out internal scoring keys like similarity, score, and embedding from the final JSON, presenting a clean output schema as required by the challenge.

Code Insight:

# In formatter.py: format_output
top_5_sections = ranked_sections[:5] # Final truncation
final_sections = [
    {k: v for k, v in sec.items() if k not in ['similarity', 'score', 'embedding']}
    for sec in top_5_sections # Filter internal keys
]


This ensures the output is concise and adheres to the specified format.

2.5. Configuration (app/config.py)
This file centralizes all configurable parameters for the application.

Purpose: It acts as a single source of truth for all system-wide parameters, including model paths, PDF parsing thresholds (MIN_HEADING_FONT_SIZE, HEADING_MAX_WORDS, MIN_WORDS_FOR_SUBSECTION, OCR_RESOLUTION_DPI), and default persona/job task values.

Robustness: This centralization makes the system highly adaptable. Users can tune parsing behavior or switch models without modifying core logic, facilitating easier experimentation and deployment across different document types. Detailed comments for each parameter enhance clarity.

3. Adherence to Operational Constraints
The system's design explicitly considers and adheres to the specified operational constraints, making it suitable for environments with limited resources or specific deployment requirements:

CPU-Only Execution: The entire processing pipeline, encompassing PDF parsing, OCR, embedding generation, and ranking, is meticulously optimized for CPU execution. While the sentence-transformers library is capable of leveraging GPU acceleration, it also provides highly efficient CPU implementations for many of its models, ensuring full compatibility with this constraint.

Model Size 
le 1GB: The selection of the Sentence Transformer model is a critical aspect of adhering to this constraint. The scripts/download_models.py utility allows for specifying the model to be downloaded. It is imperative to choose a pre-trained model (e.g., all-MiniLM-L6-v2, paraphrase-MiniLM-L3-v2) that fits within the 1GB disk size limit after download. These smaller, yet powerful, models are specifically designed to offer a robust balance of semantic performance and compact size for constrained environments.

No Internet Access during Execution: A fundamental requirement for many hackathon or secure environments is offline functionality. Once the Sentence Transformer model is downloaded (which is a one-time setup step performed via scripts/download_models.py), the entire document intelligence system operates completely offline. All necessary dependencies are local, and no external API calls or network requests are made during the core document processing and ranking phases, fully fulfilling this critical requirement.

4. Error Handling and Robustness Measures
Beyond the specific robustness features within each component, the system incorporates general error handling practices to ensure stability and provide informative feedback:

Comprehensive File Handling: try-except blocks are strategically implemented around critical file operations (e.g., fitz.open(pdf_path) for opening PDFs) and model loading (EmbeddingModel.load_model()). This allows the system to gracefully handle potential issues such as FileNotFoundError, corrupted PDF files, or problems during model initialization, providing informative error messages to the user rather than crashing.

Graceful Empty Input Handling: The RankingEngine.rank method explicitly includes checks for empty extracted_data. If no content can be extracted from the input PDFs, the method gracefully returns empty lists for ranked sections and subsections, preventing runtime errors and ensuring predictable behavior.

Proactive Text Preprocessing: The clean_text function and careful handling of empty strings (if not text: continue) throughout the PDF parsing process are crucial. This proactive preprocessing prevents malformed or empty text snippets from being passed to the embedding model or ranking engine, which could otherwise lead to errors or inaccurate results.