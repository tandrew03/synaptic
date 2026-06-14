from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy import DateTime
from db.base import Base

# model for knowledge graphs
class Knowledge_graph(Base):
    __tablename__ = 'knowledge_graphs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    description = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
