# File creates a model for what a Document in the Documents table should look like

from sqlalchemy import Column, Integer, String
from sqlalchemy import DateTime
from db.base import Base

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
