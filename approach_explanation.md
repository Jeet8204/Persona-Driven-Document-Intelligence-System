# Approach Explanation: Persona-Driven Document Intelligence

This document outlines the **architecture**, **design principles**, and **methodological choices** made for the Persona-Driven Document Intelligence System. The primary goal is to extract relevant information from a collection of PDF documents and intelligently rank it based on a **user-defined persona** and **job-to-be-done**, all while adhering to strict operational constraints:

-   **CPU-only execution**
-   **Model size ≤ 1GB**
-   **Offline (no internet access during inference)**

---

## 📐 Core Architecture

The system is designed with a **modular, decoupled architecture** to ensure:

-   Maintainability
-   Scalability
-   Clear separation of concerns
-   Resilience and performance

### Module Overview

| Module            | Path                                   | Responsibility                                                                 |
| :---------------- | :------------------------------------- | :----------------------------------------------------------------------------- |
| **PDF Parsing** | `app/processing/pdf_parser.py`         | Converts raw PDF content into structured, semantically meaningful segments.    |
| **Embedding** | `app/ranking/embedding.py`             | Translates text into dense vector representations for semantic similarity.     |
| **Ranking Engine**| `app/ranking/engine.py`                | Prioritizes relevant sections using semantic similarity and MMR.                 |
| **Formatter** | `app/io/formatter.py`                  | Outputs structured JSON results for easy consumption.                            |
| **Configuration** | `app/config.py`                        | Centralized parameter store for thresholds, paths, and model settings.         |

---

## 🧩 Detailed Component Breakdown

### 1. PDF Processing (`app/processing/pdf_parser.py`)

This is the **foundation** of the pipeline. Its goal is to robustly parse PDFs regardless of their structure or visual layout.

#### Features

-   **Text Extraction via PyMuPDF (`fitz`)**
    -   Layout-aware text span inspection
    -   Uses: `page.get_text("dict")["blocks"]`
    -   Extracts: `font_size`, `bbox`, `font`, and `flags` (e.g., bold/italic)

-   **OCR Fallback**
    -   For scanned/image-based PDFs with no selectable text
    -   Renders pages as images: `page.get_pixmap(dpi=OCR_RESOLUTION_DPI)`
    -   OCR via `pytesseract`, image processed by `Pillow`
    -   Configurable DPI: `OCR_RESOLUTION_DPI` in `config.py`

-   **Heuristic Heading Detection**
    -   Heading detection logic:
        -   Large font size: `> MIN_HEADING_FONT_SIZE`
        -   Bold fonts
        -   Short phrase (`<= HEADING_MAX_WORDS`)
    -   Stateless utility: `is_heading(span)`

-   **Stateful Section Accumulation**

    ```python
    current_section = None
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict").get("blocks", [])
        blocks.sort(key=lambda b: b["bbox"][1]) # Process in reading order
        for b in blocks:
            if b['type'] == 0:  # Text block
                # Heading detection (simplified conceptual code)
                if is_heading(first_span): # Assume first_span is derived from the block
                    if current_section:
                        # finalize previous section (join content_blocks, extract subsections, append to all_sections)
                        pass 
                    # start new section
                    current_section = {
                        "filename": os.path.basename(pdf_path),
                        "page_number": page_num + 1,
                        "section_title": clean_text(first_span['text']), # clean_text utility applied
                        "content_blocks": [], # Accumulator for content
                    }
                elif current_section: # If not a heading, and we're in a section
                    # Assuming block_text is extracted from b
                    current_section["content_blocks"].append(block_text) 
    # ... (finalize last section after loop)
    ```

### 2. Embedding (`app/ranking/embedding.py`)

Handles semantic transformation of text using `sentence-transformers`.

* **Features**
    * **Lazy Model Loading:** Model loaded only on first use.
        ```python
        if self.model is None:
            self._load_model() # Private method to handle the actual loading
        ```
    * **Vector Normalization:** Uses `normalize_embeddings=True` for cosine similarity via `np.dot()`.
        ```python
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True # THIS IS KEY for efficient cosine similarity
        )
        ```
    * **Compact Model Recommendation:** Use small, performant models like:
        -   `all-MiniLM-L6-v2`
        -   `paraphrase-MiniLM-L3-v2`

### 3. Ranking (`app/ranking/engine.py`)

Ranks document content using semantic similarity and Maximal Marginal Relevance (MMR).

* **Features**
    * **Query Construction:** Combines `persona_role` + `job_task` into one coherent query string.
    * **Section Scoring:**
        ```python
        section['score'] = (
            title_sims[i] * title_weight +
            content_sims[i] * content_weight
        )
        ```
    * **MMR Algorithm:** Balances relevance & diversity.
        * **Formula:**
            ```python
            mmr_score = lambda_val * relevance - (1 - lambda_val) * max_sim
            ```
    * **Stores Embeddings for Reuse:**
        ```python
        section['embedding'] = content_embeddings[i]
        sub['embedding'] = subsection_embeddings[i]
        ```

### 4. Output Formatter (`app/io/formatter.py`)

Responsible for structuring the output.

* **Features**
    * **JSON Output Schema:** Includes metadata, persona & job, processing time, and ranked sections/subsections.
    * **Cleans Internal Keys:**
        ```python
        final_sections = [
            {k: v for k, v in sec.items() if k not in ['similarity', 'score', 'embedding']}
            for sec in ranked_sections[:5] # Example: filtering top 5 and internal keys
        ]
        ```

### 5. Configuration (`app/config.py`)

Centralizes parameters and thresholds.

* **Highlights**
    * `MIN_HEADING_FONT_SIZE`
    * `HEADING_MAX_WORDS`
    * `OCR_RESOLUTION_DPI`
    * `SENTENCE_TRANSFORMER_MODEL_PATH`
    * `CANDIDATE_POOL_SIZE`, `lambda_val` for MMR

---

## ⚙️ Operational Constraints

| Constraint             | Implementation                                                                                                                              |
| :--------------------- | :------------------------------------------------------------------------------------------------------------------------------------------ |
| **CPU-Only Execution** | `Sentence-transformers` used in CPU mode; all processing pipeline optimized for CPU.                                                         |
| **Model Size ≤ 1GB** | Use MiniLM-based models (e.g., `all-MiniLM-L6-v2`) chosen via `scripts/download_models.py` to fit within the size limit.                      |
| **Offline Execution** | All processing done locally post-download. `scripts/download_models.py` fetches models before offline execution. No internet access during inference. |

---

## 🧱 Robustness & Error Handling

* **OCR fallback** for non-extractable PDFs.
* **Text cleaning** to remove hidden control characters.
* **Graceful fallbacks** for:
    * Empty documents
    * Missing files
    * Model initialization errors
* `try-except` blocks around I/O and model loading.

---

## ✅ Summary

The system is:
* **Robust** against PDF variations
* **Accurate** in content extraction and ranking
* **Efficient** for low-resource environments
