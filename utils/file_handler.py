import os
import uuid
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Ensure the uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    try:
        os.makedirs(UPLOAD_FOLDER)
    except Exception as e:
        raise Exception(f"Error creating upload folder: {e}")

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    """Save the uploaded file to the server."""
    if file and allowed_file(file.filename):
        try:
            # Generate a unique filename
            unique_filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)

            # Save the file to the server
            file.save(filepath)

            return filepath, unique_filename
        except Exception as e:
            raise Exception(f"Error saving file: {e}")
    else:
        raise ValueError("Invalid file type. Only PDF and DOCX are allowed.")
