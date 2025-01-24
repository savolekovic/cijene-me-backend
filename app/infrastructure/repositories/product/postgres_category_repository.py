from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import DatabaseError
from app.domain.repositories.product.category_repo import CategoryRepository
from app.domain.models.product.category import Category
from app.infrastructure.database.models.product import CategoryModel, ProductModel
from typing import List, Optional
from app.infrastructure.logging.logger import get_logger
from app.api.responses.category import CategoryResponse, PaginatedCategoryResponse, SimpleCategoryResponse

logger = get_logger(__name__)

class PostgresCategoryRepository(CategoryRepository):
    def __init__(self, session: AsyncSession = None):
        pass

    async def create(self, name: str, db: AsyncSession) -> Category:
        try:
            category_db = CategoryModel(name=name)
            db.add(category_db)
            await db.flush()
            await db.commit()
            return Category(
                id=category_db.id,
                name=category_db.name,
                created_at=category_db.created_at
            )
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            await db.rollback()
            raise DatabaseError(f"Failed to create category: {str(e)}")

    async def get_all(self, db: AsyncSession, page: int = 1, per_page: int = 10, search: str = None) -> PaginatedCategoryResponse:
        try:
            # Base query for data
            query = select(CategoryModel)
            
            # Base query for count
            count_query = select(CategoryModel)
            
            # Add search filter if search query is provided
            if search:
                search_pattern = f"%{search}%"
                search_filter = CategoryModel.name.ilike(search_pattern)
                query = query.where(search_filter)
                count_query = count_query.where(search_filter)
            
            # Get total count
            count_result = await db.execute(select(func.count()).select_from(count_query.subquery()))
            total_count = count_result.scalar()
            
            # Add ordering and pagination to the main query
            query = query.order_by(CategoryModel.name)
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)
            
            # Get paginated data
            result = await db.execute(query)
            categories = result.scalars().all()
            
            # Convert to response model
            category_list = [
                CategoryResponse(
                    id=category.id,
                    name=category.name,
                    created_at=category.created_at
                )
                for category in categories
            ]
            
            return PaginatedCategoryResponse(
                total_count=total_count,
                data=category_list
            )
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            raise DatabaseError(f"Failed to get categories: {str(e)}")

    async def get(self, category_id: int, db: AsyncSession) -> Optional[Category]:
        try:
            result = await db.execute(
                select(CategoryModel).where(CategoryModel.id == category_id)
            )
            category = result.scalar_one_or_none()
            if category:
                return Category(
                    id=category.id,
                    name=category.name,
                    created_at=category.created_at
                )
            return None
        except Exception as e:
            logger.error(f"Error getting category {category_id}: {str(e)}")
            raise DatabaseError(f"Failed to get category: {str(e)}")

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
                return Category(
                    id=category_db.id,
                    name=category_db.name,
                    created_at=category_db.created_at
                )
            return None
        except Exception as e:
            logger.error(f"Error updating category: {str(e)}")
            await db.rollback()
            raise DatabaseError(f"Failed to update category: {str(e)}")

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

    async def get_by_name(self, name: str, db: AsyncSession) -> Optional[Category]:
        try:
            result = await db.execute(
                select(CategoryModel).where(CategoryModel.name.ilike(name))
            )
            category = result.scalar_one_or_none()
            if category:
                return Category(
                    id=category.id,
                    name=category.name,
                    created_at=category.created_at
                )
            return None
        except Exception as e:
            logger.error(f"Error getting category by name: {str(e)}")
            raise DatabaseError(f"Failed to get category by name: {str(e)}")

    async def get_products_in_category(self, category_id: int, db: AsyncSession) -> List[ProductModel]:
        try:
            result = await db.execute(
                select(ProductModel).where(ProductModel.category_id == category_id)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting products in category {category_id}: {str(e)}")
            raise DatabaseError(f"Failed to get products in category: {str(e)}")

    async def get_all_simple(self, db: AsyncSession, search: str = None) -> List[SimpleCategoryResponse]:
        try:
            # Base query
            query = select(CategoryModel)
            
            # Add search filter if search query is provided
            if search:
                search_pattern = f"%{search}%"
                query = query.where(CategoryModel.name.ilike(search_pattern))
            
            # Add ordering
            query = query.order_by(CategoryModel.name)
            
            # Get data
            result = await db.execute(query)
            categories = result.scalars().all()
            
            # Convert to response model
            return [
                SimpleCategoryResponse(
                    id=category.id,
                    name=category.name
                )
                for category in categories
            ]
        except Exception as e:
            logger.error(f"Error getting simplified categories list: {str(e)}")
            raise DatabaseError(f"Failed to get simplified categories list: {str(e)}")