# backend/app.py
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
# Ensure all necessary utils are imported
from utils.file_handler import save_file, allowed_file, UPLOAD_FOLDER
from utils.text_extractor import extract_text
from utils.analyzer import analyze_resume

app = Flask(__name__)
# Apply CORS to all routes, including the new /reanalyze
CORS(app)

# Keep track of analyzed data (in memory for simplicity, use DB for production)
# Stores data based on the unique_filename (fileId) generated during upload
analysis_results = {}

@app.route('/upload', methods=['POST'])
def upload_and_analyze():
    # --- Input Validation ---
    if 'resumeFile' not in request.files:
        return jsonify({"error": "No resume file part"}), 400
    if 'jobDescriptionText' not in request.form:
        return jsonify({"error": "No job description text part"}), 400

    file = request.files['resumeFile']
    job_desc_text = request.form.get('jobDescriptionText', '').strip()

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Please use PDF or DOCX."}), 400
    if not job_desc_text:
        return jsonify({"error": "Job description text cannot be empty."}), 400

    # --- File Handling ---
    filepath, unique_filename = save_file(file)
    if not filepath:
        # Log error server-side maybe
        return jsonify({"error": "Failed to save uploaded file."}), 500

    # --- Text Extraction ---
    try:
        resume_text = extract_text(filepath)
        if resume_text is None:
            # If extraction returns None explicitly (e.g., unsupported format internally)
            raise ValueError("Text extraction returned None.")
    except Exception as e:
        print(f"Error during text extraction for {filepath}: {e}")
        # Clean up the uploaded file if extraction fails
        try:
            os.remove(filepath)
        except OSError as remove_error:
            print(f"Error deleting failed file {filepath}: {remove_error}")
        return jsonify({"error": f"Could not extract text from resume: {e}"}), 500

    # --- Analysis ---
    try:
        # Assume analyze_resume handles potential errors internally or raises them
        rating, suggestions = analyze_resume(resume_text, job_desc_text)
    except Exception as e:
        print(f"Error during analysis for {unique_filename}: {e}")
        # Optionally keep file for debugging or remove
        return jsonify({"error": f"Failed to analyze resume content: {e}"}), 500


    # --- Store Results ---
    # Storing results associated with the unique filename (acting as an ID)
    # Useful for potential future features or downloading the *original* file.
    analysis_results[unique_filename] = {
        "rating": rating,
        "suggestions": suggestions,
        "resume_text": resume_text,  # Store the full extracted text
        "job_desc_text": job_desc_text, # Store job description used for this analysis
        "original_filename": file.filename,
        "filepath": filepath # Store path primarily for the download function
    }

    # --- Response ---
    # Send the full text back to the frontend for the editor.
    # Note: Frontend (App.js) should use the key "resumeText".
    return jsonify({
        "message": "Analysis complete!",
        "fileId": unique_filename, # Important for linking download to original file
        "rating": rating,
        "suggestions": suggestions,
        "resumeText": resume_text,  # <-- Sends FULL resume text
        "jobDescriptionText": job_desc_text # Send JD text back for consistency if needed
    }), 200


# --- NEW Endpoint for Re-analyzing Edited Text ---
@app.route('/reanalyze', methods=['POST'])
def reanalyze_edited_resume():
    # --- Input Validation ---
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    edited_resume_text = data.get('resumeText', '').strip()
    job_desc_text = data.get('jobDescriptionText', '').strip() # Get original JD text

    if not edited_resume_text:
        return jsonify({"error": "Edited resume text cannot be empty."}), 400
    if not job_desc_text:
         # This shouldn't happen if frontend sends it, but good to check
        return jsonify({"error": "Job description text cannot be empty."}), 400

    # --- Analysis ---
    try:
        # Re-run the same analysis function with the new text
        rating, suggestions = analyze_resume(edited_resume_text, job_desc_text)
    except Exception as e:
        print(f"Error during re-analysis: {e}")
        # Provide a generic error message to the user
        return jsonify({"error": f"Failed to re-analyze resume content: {e}"}), 500

    # --- Response ---
    # Return only the updated rating and suggestions
    return jsonify({
        "rating": rating,
        "suggestions": suggestions
    }), 200


# --- Download Endpoint (No changes needed) ---
# This downloads the ORIGINAL file associated with the fileId
@app.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    result = analysis_results.get(file_id) # Look up stored data by fileId

    # Check if fileId is known and has necessary data
    if not result:
         return jsonify({"error": "Analysis session not found or expired."}), 404 # More accurate error

    # Check rating after confirming result exists
    current_rating = result.get('rating') # Use .get for safety
    if current_rating is None or current_rating < 75:
        error_msg = f"Rating ({current_rating if current_rating is not None else 'N/A'}) is below 75% required for download."
        return jsonify({"error": error_msg}), 403 # Forbidden might be more appropriate than 404

    filepath = result.get('filepath')
    original_filename = result.get('original_filename', 'resume_download') # Safer default

    if not filepath or not os.path.exists(filepath):
        print(f"Error: Original file path {filepath} for ID {file_id} not found on server.")
        # Don't expose server path to user
        return jsonify({"error": "File download failed: Original resource not found on server."}), 404

    try:
        # Use safe directory and filename handling
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        return send_from_directory(directory=directory, path=filename, as_attachment=True, download_name=original_filename)
    except Exception as e:
        print(f"Error sending file {filepath} for ID {file_id}: {e}")
        return jsonify({"error": f"Could not send file due to server error."}), 500

# --- Main Execution ---
if __name__ == '__main__':
    # Consider environment variables for host, port, debug
    # Example: host = os.environ.get('FLASK_HOST', '127.0.0.1')
    # Example: port = int(os.environ.get('FLASK_PORT', 5000))
    # Example: debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(debug=True) # Keep debug=True for development ONLY