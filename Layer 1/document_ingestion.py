from typing import Annotated
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
from PIL import Image
import io

# setup fast api
app = FastAPI()

# indicate which file types Synaptic can ingest from user.
ALLOWED_FILE_TYPES = {"application/pdf", "image/jpeg", "image/png", "image/webp", "text/plain"}

# subset of allowed files types for easier accessing due to allowed
# file size being the same
IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]

# declare the maximum allowed size for each file type
MAXIMUM_SIZE = {
    "application/pdf": 250 * 1024 * 1024,
    "image/jpeg": 25 * 1024 * 1024,
    "image/png": 25 * 1024 * 1024,
    "image/webp": 25 * 1024 * 1024,
    "text/plain": 5 * 1024 * 1024
}



"""
-------------------------------------
Orchestrator function for Fast API
-------------------------------------

-------------------------------------
What it does:
-------------------------------------
1. Checks allowed content type
2. Checks file size
3. Attempts to validate PDFs
4. Attempts to validate images
5. Returns structures errors

-------------------------------------
What needs to change:
-------------------------------------
1. Split reading the file into chunks rather than all at once
2. Move file size validation to before reading file to contents
3. Size validation eventually needs to exist as frontend limit, FastAPI validation, 
reverse proxy limit, application server limit, s3 policy
4. Need to check decalred MIME type, file extension, file signature (magic bytes), opening and parsing. 
5. Decompression bomb warnings for images
6. text validation for plain text
7. Needs to include metadata(file, course, source, auth level, title, user auth)


-------------------------------------
What it needs to do
-------------------------------------
1. Compute DHA0-256 Hash
2. Check PostgreSQL for duplicate file entry (deduplication)
3. Create DB row with status
4. upload to s3
5. update DB row with s3 key and status
6. Queue Celery via Redis
7. return 202
8. Eventually return document_is, status, filename, content_type, sha256 hash, duplicate bool
"""
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail='Unsupported file type')
    
    try:
        # change to read files in chunks rather than all at once
        # this is better for memory management
        contents = await file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to read file contents.")
        
    if file.content_type == 'application/pdf' and len(contents) > MAXIMUM_SIZE["application/pdf"]:
        raise HTTPException(status_code=400, detail="File too large")
    elif file.content_type == 'text/plain' and len(contents) > MAXIMUM_SIZE["text/plain"]:
        raise HTTPException(status_code=400, detail="File too large")
    elif file.content_type in IMAGE_TYPES and len(contents) > MAXIMUM_SIZE["image/jpeg"]:
        raise HTTPException(status_code=400, detail="File too large")
    
    try:
        if file.content_type == 'application/pdf':
            PdfReader(io.BytesIO(contents))
        elif file.content_type in IMAGE_TYPES:
            Image.open(io.BytesIO(contents)).verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Uploaded file is corrupted or unreadable.")

    return JSONResponse(content = {"filename": file.filename, "status": "Valid file"})

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )
