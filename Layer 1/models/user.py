# File creates a model for what a User should look like in the Users table

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy import DateTime
from db.base import Base

# model class for users
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    username = Column(String)
    hashed_password = Column(String)
    current_active_knowledge_graph_id = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
