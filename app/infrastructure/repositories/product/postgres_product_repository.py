from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from typing import List, Optional
from app.domain.models.product.product import Product, ProductWithCategory
from app.domain.repositories.product.product_repo import ProductRepository
from app.infrastructure.database.models.product import ProductModel, CategoryModel

class PostgresProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_with_categories(self) -> List[ProductWithCategory]:
        query = select(ProductModel, CategoryModel.name.label('category_name'))\
            .join(CategoryModel)\
            .order_by(asc(ProductModel.name))
        
        result = await self.session.execute(query)
        products_with_categories = result.all()
        
        return [
            ProductWithCategory(
                id=product.id,
                name=product.name,
                image_url=product.image_url,
                category_id=product.category_id,
                category_name=category_name,
                created_at=product.created_at
            )
            for product, category_name in products_with_categories
        ] 