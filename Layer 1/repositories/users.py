# Created by Andrew Thibodeau
# File *users.py* stores functions that are used to interact with the
# users table in the Synaptic database. Possible interactions include
# create_user(), get_user_by_id(), get_user_by_username(), get_user_by_email(), delete_user()


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import DateTime, select
from models.user import User
from datetime import datetime
from typing import Optional

async def create_user(db: AsyncSession,
                                email : str,
                                username: str,
                                current_active_knowledge_graph_id : str,
                                ) -> User:
    
    now = datetime.datetime.now()

    new_user = User(
        email = email,
        username = username,
        current_active_knowledge_graph_id = current_active_knowledge_graph_id,
        created_at = now,
        updated_at = now)
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def get_user_by_id(db: AsyncSession,
                         user_id: int
                         ) -> Optional[User]:
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    return result.scalar_one_or_none
    
async def get_user_by_username(db: AsyncSession,
                               username: str
                               ) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.username == username)
    )

    return result.scalar_one_or_none

async def get_user_by_email(db: AsyncSession,
                            email: str) -> Optional[User]:
    
    result = await db.execute(
        select(User).where(User.email == email)
    )

    return result.scalar_one_or_none

async def username_exists(db: AsyncSession,
                          username:str
                          ) -> Optional[User]:
    
    user = await get_user_by_username(db, username)

    return user is not None

async def email_exists(db: AsyncSession,
                   email: str
                   ) -> Optional[User]:
    user = await get_user_by_email(db, email)

    return user is not None

async def update_current_active_knowledge_graph_id(db: AsyncSession,
                                                   user_id: int,
                                                   knowledge_graph_id: Optional[str]
                                                   ) -> Optional[User]:
    user = await get_user_by_id(db, user_id)

    if user is None:
        return None
    
    user.current_active_knowledge_graph_id = knowledge_graph_id
    user.updated_at = datetime.datetime.now

    await db.commit()
    await db.refresh(user)

    return user

async def delete_user(db: AsyncSession,
                      user_id: int
                      ) -> bool:
    
    user = await get_user_by_id(db, user_id)

    if user is None:
        return False
    
    await db.delete(user)
    await db.commit()

    return True