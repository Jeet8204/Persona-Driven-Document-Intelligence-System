# import datetime

# def format_output(documents_metadata, persona_role, job_task, processing_time, ranked_sections, ranked_subsections):
#     """Formats the final results into the required JSON structure."""
    
#     # Filter out the similarity score for the final JSON
#     final_sections = [
#         {k: v for k, v in sec.items() if k != 'similarity'}
#         for sec in ranked_sections
#     ]
#     final_subsections = [
#         {k: v for k, v in sub.items() if k != 'similarity'}
#         for sub in ranked_subsections
#     ]

#     output_data = {
#         "metadata": {
#             "input_documents": [doc['filename'] for doc in documents_metadata],
#             "persona": persona_role,
#             "job_to_be_done": job_task,
#             "processing_timestamp": datetime.datetime.now().isoformat(),
#             "processing_time_seconds": round(processing_time, 2)
#         },
#         "extracted_sections": final_sections,
#         "subsection_analysis": final_subsections
#     }
#     return output_data



import datetime

def format_output(documents_metadata, persona_role, job_task, processing_time, ranked_sections, ranked_subsections):
    """
    Formats the final results into the required JSON structure, limited to the top 5
    most relevant sections and subsections.
    """
    
    # --- NEW: Take only the top 5 from the pre-ranked lists ---
    top_5_sections = ranked_sections[:5]
    top_5_subsections = ranked_subsections[:5]

    # Filter out internal scores before creating the final output
    final_sections = [
        {k: v for k, v in sec.items() if k not in ['similarity', 'score']}
        for sec in top_5_sections # CHANGED: Iterate over the sliced list
    ]
    final_subsections = [
        {k: v for k, v in sub.items() if k not in ['similarity', 'score']}
        for sub in top_5_subsections # CHANGED: Iterate over the sliced list
    ]

    output_data = {
        "metadata": {
            "input_documents": [doc['filename'] for doc in documents_metadata],
            "persona": persona_role,
            "job_to_be_done": job_task,
            "processing_timestamp": datetime.datetime.now().isoformat(),
            "processing_time_seconds": round(processing_time, 2)
        },
        "extracted_sections": final_sections,
        "subsection_analysis": final_subsections
    }
    return output_data