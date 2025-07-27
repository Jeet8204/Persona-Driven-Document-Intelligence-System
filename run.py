

import argparse
import os
import json
import time

from app.processing.pdf_parser import extract_all_documents
from app.ranking.engine import RankingEngine
from app.io.formatter import format_output
from app.config import SENTENCE_TRANSFORMER_MODEL_PATH

def main():
    # --- CHANGED: Argument parsing now takes a single JSON input file ---
    parser = argparse.ArgumentParser(description="Persona-Driven Document Intelligence System")
    parser.add_argument("--input_json", required=True, help="Path to the input JSON file.")
    parser.add_argument("--output_file", default=None, help="Path to the output JSON file. A default name will be generated if not provided.")
    args = parser.parse_args()

    # 1. Read and parse the input JSON
    print(f"📄 Loading input from {args.input_json}...")
    with open(args.input_json, 'r', encoding='utf-8') as f:
        input_data = json.load(f)

    # Extracting details from the JSON structure
    persona_role = input_data['persona']['role']
    job_task = input_data['job_to_be_done']['task']
    documents_metadata = input_data['documents']

    # Construct full paths for the PDF documents (assumes they are in the same directory as the JSON)
    input_dir = os.path.dirname(args.input_json)
    pdf_paths = [os.path.join(input_dir, doc['filename']) for doc in documents_metadata]

    # Determine the output file path, generating a default if not provided
    output_file = args.output_file
    if not output_file:
        challenge_id = input_data.get('challenge_info', {}).get('challenge_id', 'default')
        output_filename = f"{challenge_id}_output.json"
        output_file = f"./data/output/{output_filename}"

    start_time = time.time()

    # 2. Initialize the Ranking Engine
    print("🚀 Initializing Ranking Engine...")
    try:
        ranking_engine = RankingEngine(model_path=SENTENCE_TRANSFORMER_MODEL_PATH)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run 'python scripts/download_models.py' to download the required model files.")
        return

    # 3. Extract content from the specified list of documents
    # NOTE: This requires a change in `pdf_parser.py` to accept a list of file paths.
    print(f"📄 Extracting content from {len(pdf_paths)} PDF(s)...")
    extracted_data = extract_all_documents(pdf_paths)
    if not extracted_data:
        print("No content could be extracted from the documents. Exiting.")
        return

    # 4. Perform the ranking
    print("🧠 Ranking sections and subsections...")
    query = f"{persona_role}. {job_task}"
    ranked_sections, ranked_subsections = ranking_engine.rank(query, extracted_data)

    # 5. Format and save the output
    print("💾 Formatting and saving output...")
    processing_time = time.time() - start_time
    final_output = format_output(
        documents_metadata, persona_role, job_task,
        processing_time, ranked_sections, ranked_subsections
    )

    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)

    print(f"\n✅ Success! Processing complete.")
    print(f"   Output written to: {output_file}")
    print(f"   Total processing time: {processing_time:.2f} seconds")


if __name__ == "__main__":
    main()