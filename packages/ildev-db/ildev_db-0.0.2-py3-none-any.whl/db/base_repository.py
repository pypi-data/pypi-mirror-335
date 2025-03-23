from typing import Type, TypeVar, Generic, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy import asc, desc
from db.base_model import Base
from db.exception import handle_db_exceptions

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    @handle_db_exceptions(allow_return=True, return_data=None)
    async def get_one(self, db: AsyncSession, **filters) -> Optional[ModelType]:
        """Fetch one record."""
        stmt = select(self.model)    
        if filters:
            stmt = stmt.filter_by(**filters)

        result = await db.execute(stmt)
        return result.scalars().first()

    @handle_db_exceptions(allow_return=True, return_data=[])
    async def get_all(
        self, db: AsyncSession, offset: int = 0, limit: Optional[int] = 100, order_by: Optional[str] = None, sort: str = "asc",  **filters
    ) -> List[ModelType]:
        """
        Fetch multiple records based on provided filters with pagination.

        Args:
            db (AsyncSession): The database session.
            offset (int): The starting index of records to fetch. Default is 0.
            limit (Optional[int]): The maximum number of records to fetch.
                                   If None, returns all records.
            **filters: Key-value pairs for filtering results.

        Returns:
            List[ModelType]: A list of matching records.
        """
        stmt = select(self.model)

        if filters:
            stmt = stmt.filter_by(**filters)

        if order_by:
            column = getattr(self.model, order_by, None)
            if column:
                stmt = stmt.order_by(asc(column) if sort.lower() == "asc" else desc(column))

        if limit is not None:
            stmt = stmt.offset(offset).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    @handle_db_exceptions()
    async def create(self, db: AsyncSession, obj_data: dict) -> ModelType:
        """Create a new record."""
        obj = self.model(**obj_data)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    @handle_db_exceptions()
    async def update(self, db: AsyncSession, id: int, obj_data: dict) -> ModelType:
        """Update a record."""
        obj = await self.get_one(db, id=id)
        if obj is None:
            error_text = f"{self.model.__name__} with ID {id} not found"
            raise NoResultFound(error_text)
        
        for key, value in obj_data.items():
            setattr(obj, key, value)
        await db.flush()
        await db.refresh(obj)
        return obj       

    @handle_db_exceptions()
    async def delete(self, db: AsyncSession, id: int) -> bool:
        """Delete a record."""
        obj = await self.get_one(db, id=id)
        if obj:            
            await db.delete(obj)
            await db.flush()
            return True

        return False