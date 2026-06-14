from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional
from models.document import Document

async def create_document(db: AsyncSession,
                    user_id : str,
                    knowledge_graph_id : str,
                    title : str,
                    original_filename : str, 
                    content_type : str, 
                    file_size_bytes : int,
                    sha256_hash : str,
                    source_type : str,
                    authority_level : int,
                    s3_key : str,
                    status : str,
                    ):
    
    now = datetime.datetime.now()

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
                    created_at = now,
                    updated_at = now)
    
    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)
    return new_document

async def get_documents(db: AsyncSession):
    result = await db.execute(select(Document))
    return result.scalars().all()


async def find_duplicate_document(db: AsyncSession,
                                  sha256_hash: str) -> Document:
    result = await db.execute(
        select(Document).where(Document.sha256_hash == sha256_hash)
    )
    return result.scalar_one_or_none

async def get_document_by_id(db: AsyncSession,
                             doc_id: str) -> Optional[Document]:
    result = await db.execute(
        select(Document).where(Document.id == doc_id)
    )
    return result.scalar_one_or_none

async def update_document_status(db: AsyncSession,
                                 doc_id : str,
                                 status: str) -> bool:
    
    doc = get_document_by_id(db, doc_id)

    if doc is None:
        return False
    
    doc.status = status
    doc.updated_at = datetime.datetime.now()

    await db.commit()
    await db.refresh(doc)

    return True