from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

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

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

