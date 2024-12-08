from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from typing import List, Optional
from app.domain.models.product.category import Category
from app.domain.repositories.product.category_repo import CategoryRepository
from app.infrastructure.database.models.product import CategoryModel

class PostgresCategoryRepository(CategoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str) -> Category:
        db_category = CategoryModel(name=name)
        self.session.add(db_category)
        await self.session.commit()
        await self.session.refresh(db_category)

        return Category(
            id=db_category.id,
            name=db_category.name,
            created_at=db_category.created_at
        )

    async def get_all(self) -> List[Category]:
        query = select(CategoryModel).order_by(asc(CategoryModel.name))
        result = await self.session.execute(query)
        db_categories = result.scalars().all()
        
        return [
            Category(
                id=db_category.id,
                name=db_category.name,
                created_at=db_category.created_at
            )
            for db_category in db_categories
        ]

    async def get(self, category_id: int) -> Optional[Category]:
        query = select(CategoryModel).where(CategoryModel.id == category_id)
        result = await self.session.execute(query)
        db_category = result.scalar_one_or_none()
        
        if db_category:
            return Category(
                id=db_category.id,
                name=db_category.name,
                created_at=db_category.created_at
            )
        return None 