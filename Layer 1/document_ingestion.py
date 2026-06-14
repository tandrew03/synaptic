from typing import Annotated
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
from PIL import Image
import io
from typing import Optional
import hashlib
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import os
from sqlalchemy.future import select
from sqlalchemy import DateTime
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

# map document type to authority level
TYPE_LEVEL = {
    "user_note": 0,
    "supplemental_reading": 1,
    "lecture": 2,
    "textbook": 3,
    "exam": 4
}

# DB URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL",
                "postgresql+asyncpg://synaptic_user:synaptic_password@localhost:5432/synaptic"
          )


# async engine
engine = create_async_engine(
    DATABASE_URL, 
    echo = True, 
    future=True
)

# create async session
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



# model for documents
class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    knowledge_graph_id = Column(String)
    title = Column(String)
    original_filename = Column(String)
    content_type = Column(String)
    file_size_bytes = Column(Integer)
    sha256_hash = Column(String)
    source_type = Column(String)
    authority_level = Column(Integer)
    s3_key = Column(String)
    status = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)



async def create_document(db: AsyncSession,
                    user_id = str,
                    knowledge_graph_id = str,
                    title = str,
                    original_filename = str, 
                    content_type = str, 
                    file_size_bytes = int,
                    sha256_hash = str,
                    source_type = str,
                    authority_level = int,
                    s3_key = str,
                    status = str,
                    created_at = DateTime,
                    updated_at = DateTime):
    
    new_document = Document(
                    user_id = user_id,
                    knowledge_graph_id = knowledge_graph_id,
                    title = title,
                    original_filename = original_filename,
                    content_type = content_type,
                    file_size_bytes = file_size_bytes,
                    sha256_hash = sha256_hash,
                    source_type = source_type,
                    authority_level = authority_level,
                    s3_key = s3_key,
                    status = status,
                    created_at = created_at,
                    updated_at = updated_at)
    
    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)
    return new_document


async def get_documents(db: AsyncSession):
    result = await db.execute(select(Document))
    return result.scalars().all()




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
6. Compute SHA-256 Hash

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

2. Check PostgreSQL for duplicate file entry (deduplication)
3. Create DB row with status
4. upload to s3
5. update DB row with s3 key and status
6. Queue Celery via Redis
7. return 202
8. Eventually return document_is, status, filename, content_type, sha256 hash, duplicate bool
"""

# MAKE KNOWLEDGE GRAPH ID OPTIONAL, USE DATABASE INTERATION TO DET
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile, 
                            knowledge_graph_id: Annotated[str, Form(...)],
                            source_type: Annotated[str, Form(...)],
                            title: Optional[str] = Form(None),
                            db: AsyncSession = Depends(get_db)):
    
    if not knowledge_graph_id:
        raise HTTPException(status_code=400, detail='Knowledge Graph ID doesnt exist')
    if source_type not in TYPE_LEVEL:
        raise HTTPException(status_code=400, detail='Unsupported file source type.')
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail='Unsupported file type')
    
    try:
        # change to read files in chunks rather than all at once
        # this is better for memory management
        contents = await file.read()
        authority_level = TYPE_LEVEL[source_type]
        sha256_hash = hashlib.sha256(contents).hexdigest()
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

    return JSONResponse(content = {"filename": file.filename, "knowledge_graph_id": knowledge_graph_id, "source_type" : source_type, "auth_level": authority_level, "sha256_hash": sha256_hash, "status": "Valid file"})

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )
