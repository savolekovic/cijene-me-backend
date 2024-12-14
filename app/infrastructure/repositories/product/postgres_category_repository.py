from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.repositories.product.category_repo import CategoryRepository
from app.domain.models.product.category import Category
from app.infrastructure.database.models.product import CategoryModel
from typing import List, Optional
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)

class PostgresCategoryRepository(CategoryRepository):
    def __init__(self, session: AsyncSession = None):
        pass

    async def create(self, name: str, db: AsyncSession) -> Category:
        category_db = CategoryModel(name=name)
        db.add(category_db)
        await db.flush()
        await db.commit()
        return Category.model_validate(category_db)

    async def get_all(self, db: AsyncSession) -> List[Category]:
        result = await db.execute(select(CategoryModel))
        categories = result.scalars().all()
        return [Category.model_validate(category) for category in categories]

    async def get(self, category_id: int, db: AsyncSession) -> Optional[Category]:
        result = await db.execute(
            select(CategoryModel).where(CategoryModel.id == category_id)
        )
        category = result.scalar_one_or_none()
        return Category.model_validate(category) if category else None

    async def update(self, category_id: int, category: Category, db: AsyncSession) -> Optional[Category]:
        try:
            result = await db.execute(
                select(CategoryModel).where(CategoryModel.id == category_id)
            )
            category_db = result.scalar_one_or_none()
            if category_db:
                category_db.name = category.name
                await db.flush()
                await db.commit()
                return Category.model_validate(category_db)
            logger.warning(f"Category not found for update: {category_id}")
            return None
        except Exception as e:
            logger.error(f"Error updating category {category_id}: {str(e)}")
            await db.rollback()
            raise

    async def delete(self, category_id: int, db: AsyncSession) -> bool:
        result = await db.execute(
            select(CategoryModel).where(CategoryModel.id == category_id)
        )
        category = result.scalar_one_or_none()
        if category:
            await db.delete(category)
            await db.flush()
            await db.commit()
            return True
        return False