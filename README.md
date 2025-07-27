
  # Persona-Driven Document Intelligence System 🎯

This project implements a sophisticated system designed to extract relevant information from a collection of PDF documents and intelligently rank it based on a user-defined persona and job-to-be-done. It leverages advanced natural language processing techniques, including semantic similarity and Maximal Marginal Relevance (MMR), to provide a focused, diverse, and highly intelligent summary of the most pertinent document content. The system is engineered to operate efficiently under strict constraints, including CPU-only execution, limited model size, and offline functionality.

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

---

## 🚀 Features

- *🔍 Robust PDF Content Extraction*: Stateful parsing with PyMuPDF and OCR fallback for scanned documents.
- *🗂 Intelligent Heading & Sectioning*: Heuristic detection of headings and dynamic section assembly.
- *🧹 Comprehensive Text Cleaning*: Whitespace normalization and control-character removal.
- *🧠 Semantic Embedding*: High-quality, normalized embeddings via Sentence Transformers.
- *👤 Persona-Driven Ranking*: Semantic relevance to persona-and-task query.
- *🌐 Diversity-Aware Ranking (MMR)*: Balances relevance and novelty to avoid redundancy.
- *🏆 Fixed Top 5 Results*: Presents the top 5 most relevant and diverse text segments.
- *📊 Structured JSON Output*: Clean, consumable JSON without internal metadata.
- *💻 CPU-Optimized & Offline Capable*: Designed for offline execution after one-time setup.

---
```
## 📁 File Structure

text
📁 persona_document_intel/                   # 🚀 Root project directory
├── 🔧 app/                                  # Core application modules
│   ├── ⚙ config.py                         # Configuration settings and constants
│   ├── 📂 io/                               # Input/Output formatting
│   │   └── 📄 formatter.py                  #   JSON output schema implementation
│   ├── 📂 processing/                       # PDF parsing and cleaning logic
│   │   └── 📄 pdf_parser.py                 #   Stateful heading detection & OCR fallback
│   └── 📂 ranking/                          # Embedding and ranking engine
│       ├── 📄 embedding.py                  #   Sentence Transformer integration
│       └── 📄 engine.py                     #   MMR-based ranking implementation
├── 🗄 data/                                 # Input/output storage
│   ├── 📂 input/                            #   PDF files and config JSONs
│   └── 📂 output/                           #   Generated analysis JSON
├── 📦 models/                               # Downloaded transformer models
├── 🛠 scripts/                              # Utility scripts
│   └── 📄 download_models.py                #   Model download helper
├── 🧪 tests/                                # Unit test suite
│   └── 📄 test_ranking.py                   #   Ranking engine tests
├── 🐍 venv/                                 # Python virtual environment
├── 🐳 Dockerfile                            # Container configuration
├── 📜 requirements.txt                      # Python dependencies
└── 🚀 run.py                                # CLI entry point


---
```
## ⚙ Setup

### 📝 Prerequisites

- *🐍 Python 3.8+*
- *📦 pip*
- *🔡 Tesseract OCR Engine*:
  - *Windows*: Install via [Chocolatey](https://chocolatey.org):
    powershell
    choco install tesseract -y
    
  - *macOS*: brew install tesseract
  - *Ubuntu/Debian*: sudo apt-get install tesseract-ocr

### 🔧 Installation

1. *Clone the repository*:
    ```
   bash
   git clone <repo_url>
   cd <repo_name>
    ```
   
2. *Create & activate virtual environment*:
   ```
   - *macOS/Linux (bash/zsh)*:
     bash
     python3 -m venv venv
     source venv/bin/activate
   ```

   ```
   - *Windows PowerShell*:
     powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1

   ```
     

3. *Install dependencies*:

   bash
   pip install -r requirements.txt
   

### 📥 Downloading the Embedding Model
```
bash
python scripts/download_models.py
```


### 🐳 Docker Usage
```

- *Build Image*:
  bash
docker build -t persona-doc-intel .
```
  
- *Run Container*:
  
  - *Linux/macOS*:
    bash
```
docker run --rm \
  -v "$(pwd)/data/input:/app/data/input" \
  -v "$(pwd)/data/output:/app/data/output" \
  persona-doc-intel \
  --input_json data/input/input_config.json \
  --output_file data/output/analysis_output.json
```
  - *Windows PowerShell*:
    powershell

```
docker run --rm `
  -v "${PWD}\data\input:/app/data/input" `
  -v "${PWD}\data\output:/app/data/output" `
  persona-doc-intel `
  --input_json data/input/input_config.json `
  --output_file data/output/analysis_output.json
```
    

---

## 🛠 Usage

### 📂 Input JSON Structure

json
{
  "challenge_info": { "challenge_id": "challenge1b" },
  "persona": { "role": "Your Persona Role" },
  "job_to_be_done": { "task": "Your task description" },
  "documents": [
    { "filename": "doc1.pdf" },
    { "filename": "doc2.pdf" }
  ]
}


### 🔢 Command-Line Arguments

- --input_json (required): Path to input JSON.
- --output_file (optional): Output JSON path (default: data/output/<challenge_id>_output.json).

### 💡 Example Usage

bash
python run.py \
  --input_json data/input/input_config.json \
  --output_file data/output/my_analysis.json


---

## 🛡 Troubleshooting & Tips

- *Missing Text Extraction*: Verify PyMuPDF compatibility; use OCR fallback by setting OCR_RESOLUTION_DPI in app/config.py.
- *Slow Embedding*: Opt for a smaller model (e.g., paraphrase-MiniLM-L3-v2) via scripts/download_models.py.
- *High Memory Usage*: Adjust CANDIDATE_POOL_SIZE and BATCH_SIZE in app/config.py.
- *Docker Permission Issues*: On Linux, run docker run with --user $(id -u):$(id -g).

---

## 🏗 How It Works (Architecture Overview)

Refer to approach_explanation.md for component breakdown: PDF parsing, embedding, ranking (MMR), and JSON formatting. The system is fully modular and CPU-optimized.

---

## ⚠ Important Notes

- *📦 Model Size*: Keep under 1GB for offline compatibility.
- *🔄 Error Handling*: Graceful fallbacks ensure stable execution on edge cases.
- *⚙ Customization*: All thresholds and paths are configurable in app/config.py.
