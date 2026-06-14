from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import DateTime
from models.knowledge_graph import Knowledge_graph

async def create_knowledge_graph(db: AsyncSession,
                                user_id : str,
                                description: str, 
                                created_at : DateTime,
                                updated_at: DateTime):
    
    new_knowledge_graph = Knowledge_graph(
        user_id = user_id,
        description = description,
        created_at = created_at,
        updated_at = updated_at)
    
    db.add(new_knowledge_graph)
    await db.commit()
    await db.refresh(new_knowledge_graph)
    return new_knowledge_graph
    
