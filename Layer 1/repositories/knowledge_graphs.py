from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import DateTime, select
from models.knowledge_graph import Knowledge_graph
from typing import Optional


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
    
#get_graph_by_id()
async def get_graph_by_id(db: AsyncSession,
                          knowledge_graph_id: str) -> Optional[Knowledge_graph]:
    result = await db.execute(
        select(Knowledge_graph).where(Knowledge_graph.id == knowledge_graph_id)
    )

    return result.scalar_one_or_none


#get_graphs_for_user()
#verify_graph_belongs_to_user()
#update_knowledge_graph()
#delete_knowledge_graph()
#count_graphs_for_user()