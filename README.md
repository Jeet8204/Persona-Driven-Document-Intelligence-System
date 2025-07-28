---

# 📚 Persona-Driven Document Intelligence System 🎯

This project implements a sophisticated system designed to extract relevant information from a collection of PDF documents and intelligently rank it based on a user-defined persona and job-to-be-done. It leverages advanced natural language processing techniques, including semantic similarity and Maximal Marginal Marginal Relevance (MMR), to provide a focused, diverse, and highly intelligent summary of the most pertinent document content. The system is engineered to operate efficiently under strict constraints, including CPU-only execution, limited model size, and offline functionality.

---

## 📑 Table of Contents

- [🚀 Features](#🚀-features)
- [📁 File Structure](#📁-file-structure)
- [⚙ Setup](#⚙-setup)
  - [📝 Prerequisites](#📝-prerequisites)
  - [🔧 Installation](#🔧-installation)
  - [📥 Downloading the Embedding Model](#📥-downloading-the-embedding-model)
  - [🐳 Docker Usage](#🐳-docker-usage)
- [🛠 Usage](#🛠-usage)
  - [📂 Input JSON Structure](#📂-input-json-structure)
  - [🔢 Command-Line Arguments](#🔢-command-line-arguments)
  - [💡 Example Usage](#💡-example-usage)
- [🛡 Troubleshooting & Tips](#🛡-troubleshooting--tips)
- [🏗 How It Works (Architecture Overview)](#🏗-how-it-works-architecture-overview)
- [⚠ Important Notes](#⚠-important-notes)
- [👥 Authors](#👥-authors)

---

## 🚀 Features

- *🔍 Robust PDF Content Extraction*: Stateful parsing with PyMuPDF and OCR fallback for scanned documents.
- *🗂 Intelligent Heading & Sectioning*: Heuristic detection of headings and dynamic section assembly.
- *🧹 Comprehensive Text Cleaning*: Whitespace normalization and control-character removal.
- *🧠 Semantic Embedding*: High-quality, normalized embeddings via Sentence Transformers.
- *👤 Persona-Driven Ranking*: Semantic relevance to persona-and-task query.
- *🌐 Diversity-Aware Ranking (MMR)*: Balances relevance and novelty to avoid redundancy.
- *💡 **Multilingual Heading Detection** (English, Hindi, French)*
- *🏆 Fixed Top 5 Results*: Presents the top 5 most relevant and diverse text segments.
- *📊 Structured JSON Output*: Clean, consumable JSON without internal metadata.
- *💻 CPU-Optimized & Offline Capable*: Designed for offline execution after one-time setup.

---

## 📁 File Structure

To clearly visualize the project's file organization on GitHub:

```

persona\_document\_intel/                      \# 🚀 Root project directory
├── app/                                     \# Core application modules
│   ├── config.py                            \# ⚙ Configuration settings and constants
│   ├── io/                                  \# Input/Output formatting
│   │   └── formatter.py                     \# 📄 JSON output schema implementation
│   ├── processing/                          \# PDF parsing and cleaning logic
│   │   └── pdf\_parser.py                    \# 📄 Stateful heading detection & OCR fallback
│   └── ranking/                             \# Embedding and ranking engine
│       ├── embedding.py                     \# 📄 Sentence Transformer integration
│       └── engine.py                        \# 📄 MMR-based ranking implementation
├── data/                                    \# Input/output storage for runs
│   ├── input/                               \# 📂 PDF files and config JSONs for processing
│   └── output/                              \# 📂 Generated analysis JSON outputs
├── models/                                  \# 📦 Downloaded Sentence Transformer models
├── scripts/                                 \# Utility scripts
│   └── download\_models.py                   \# 📄 Model download helper
├── tests/                                   \# 🧪 Unit test suite
│   └── test\_ranking.py                      \# 📄 Ranking engine tests
├── venv/                                    \# 🐍 Python virtual environment (local setup)
├── Dockerfile                               \# 🐳 Container configuration for reproducible execution
├── requirements.txt                         \# 📜 Python dependencies list
└── run.py                                   \# 🚀 Command-Line Interface (CLI) entry point

````

---

## ⚙ Setup

### 📝 Prerequisites

-   **Python 3.8+** (recommended to use a virtual environment)
-   **pip** (Python package installer)
-   **Tesseract OCR Engine**:
    -   **Windows**: Install via [Chocolatey](https://chocolatey.org):
        ```powershell
        # Open PowerShell as Administrator
        choco install tesseract-ocr -y
        ```
    -   **macOS**:
        ```bash
        brew install tesseract
        ```
    -   **Ubuntu/Debian**:
        ```bash
        sudo apt-get install tesseract-ocr
        ```

### 🔧 Installation

1.  **Clone the repository**:
    ```bash
    git clone <repo_url> # Replace with your actual repository URL
    cd <repo_name>       # Change to your project directory
    ```

2.  **Create & activate virtual environment**:
    * **macOS/Linux (bash/zsh)**:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    * **Windows PowerShell**:
        ```powershell
        python -m venv venv
        .\venv\Scripts\Activate.ps1
        ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### 📥 Downloading the Embedding Model

The system uses pre-trained Sentence Transformer models. These need to be downloaded once.

```bash
python scripts/download_models.py
````

This script will download the required embedding model (e.g., `sentence-transformers/all-MiniLM-L6-v2`) into the `models/` directory.

### 🐳 Docker Usage

Docker provides a consistent and offline environment for running the system.

1.  **Build Image**:

    ```bash
    docker build -t persona-doc-intel .
    ```

2.  **Run Container**:
    The system uses volume mounts to access your input PDFs and save output JSONs.

      * **Linux/macOS**:

        ```bash
        docker run --rm \
          -v "$(pwd)/data/input:/app/data/input" \
          -v "$(pwd)/data/output:/app/data/output" \
          persona-doc-intel \
          --input_json data/input/input_config.json \
          --output_file data/output/analysis_output.json
        ```

      * **Windows PowerShell**:

        ```powershell
        docker run --rm `
          -v "${PWD}\data\input:/app/data/input" `
          -v "${PWD}\data\output:/app/data/output" `
          persona-doc-intel `
          --input_json data/input/input_config.json `
          --output_file data/data/output/analysis_output.json
        ```

-----

## 🛠 Usage

### 📂 Input JSON Structure

The `input.json` file (or whatever you name your input configuration) must be placed in `data/input/`. It defines the persona, task, and documents to analyze.

```json
{
  "challenge_info": { "challenge_id": "challenge1b" },
  "persona": { "role": "Your Persona Role (e.g., Software Engineer)" },
  "job_to_be_done": { "task": "Your task description (e.g., find information about microservices architecture)" },
  "documents": [
    { "filename": "document1.pdf" },
    { "filename": "document2.pdf" },
    { "filename": "document_N.pdf" }
  ]
}
```

### 🔢 Command-Line Arguments

  - `--input_json` (required): Path to the input JSON configuration file (relative to `/app`).
  - `--output_file` (optional): Path to the output JSON file (default: `data/output/<challenge_id>_output.json`).

### 💡 Example Usage

```bash
python run.py \
  --input_json data/input/input_config.json \
  --output_file data/output/my_analysis.json
```

-----

## 🛡 Troubleshooting & Tips

  - *Missing Text Extraction*: If results are empty for some PDFs, verify PyMuPDF compatibility; use OCR fallback by setting OCR\_RESOLUTION\_DPI in app/config.py.
  - *Slow Embedding*: Opt for a smaller model (e.g., paraphrase-MiniLM-L3-v2) via scripts/download\_models.py.
  - *High Memory Usage*: Adjust CANDIDATE\_POOL\_SIZE and BATCH\_SIZE in app/config.py.
  - *Docker Permission Issues*: On Linux, run docker run with `--user $(id -u):$(id -id -g)`.
  - *Offline Operation*: Remember to download the embedding model via `scripts/download_models.py` *before* running Docker with `--network none`.

-----

## 🏗 How It Works (Architecture Overview)

Refer to `approach_explanation.md` for a detailed component breakdown: PDF parsing, text cleaning, semantic embedding, persona-driven ranking (using MMR), and JSON formatting. The system is designed to be fully modular and CPU-optimized.

-----

## ⚠ Important Notes

  - **📦 Model Size**: The embedding model should be kept under 1GB for optimal offline compatibility within Docker constraints.
  - **🔄 Error Handling**: The system incorporates graceful fallbacks to ensure stable execution on edge cases.
  - **⚙ Customization**: Key thresholds and paths are designed to be configurable (e.g., in `app/config.py`).

-----

## 👥 Authors

  * Jeet Mukherjee
  * Shaunak Samanta
  * Aritra Sinha

**Acknowledgement**

  * Adobe Hackathon 2025 – Challenge inspiration
  * HuggingFace `sentence-transformers` for semantic similarity

-----
