import pytest
from db.base_database import BaseDatabase

DATABASE_URL = "sqlite+aiosqlite:///./test_database.db"

@pytest.mark.asyncio
async def test_db_connection():
    """Test database session creation."""
    db = BaseDatabase(DATABASE_URL)
    get_db = db.get_db_session()

    async for db in get_db():
        assert db is not None
