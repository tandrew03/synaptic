# File defines functions that allow for interaction with the documents table in the Synaptic database

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional
from models.document import Document


"""
Function is used to create a document instance

Inputs:
    db:                 async db session
    user_id:            UUID defined in Synaptic backend -> no user input
    knowledge_graph_id: current working knowledge graph
    title:              name of the document
    original filename:  for parsing purposes (OCR, text extract, etc)
    content_type:       application/pdf, image/png, etc
    file_size_bytes:    file size 
    sha256_hash:        used for deduplication check
    source_type:        what the source is (user note, textbook, lecture note, etc)
    authority_level:    directly used from source_type mapping
    s3_key:             AWS s3 bucket key
    status:             error check/ success confirmation var

Return:
    New Document

"""
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
    
    now = datetime.now()

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


"""
Function is used to return documents
"""
async def get_documents(db: AsyncSession):
    result = await db.execute(select(Document))
    return result.scalars().all()



"""
Function is used to see if document already exists the in the databse for the select user

Takes the sha256 document hash as an input, queries the database to find a document where the documents
hash is the query hash. If it exsists return the document. 
"""
async def find_duplicate_document(db: AsyncSession,
                                  sha256_hash: str) -> Document:
    result = await db.execute(
        select(Document).where(Document.sha256_hash == sha256_hash)
    )
    return result.scalar_one_or_none()


"""
Function is used to obtain a document for a specified user via the document ID
"""
async def get_document_by_id(db: AsyncSession,
                             doc_id: str) -> Optional[Document]:
    result = await db.execute(
        select(Document).where(Document.id == doc_id)
    )
    return result.scalar_one_or_none()

async def update_document_status(db: AsyncSession,
                                 doc_id : str,
                                 status: str) -> bool:
    
    doc = await get_document_by_id(db, doc_id)

    if doc is None:
        return False
    
    doc.status = status
    doc.updated_at = datetime.now()

    await db.commit()
    await db.refresh(doc)

    return True