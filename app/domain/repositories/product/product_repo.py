from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.product import Product, ProductWithCategory

class ProductRepository(ABC):
    @abstractmethod
    async def create(self, name: str, image_url: str, category_id: int) -> Product:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Product]:
        pass

    @abstractmethod
    async def get_all_with_categories(self) -> List[ProductWithCategory]:
        pass
    
    @abstractmethod
    async def get(self, product_id: int) -> Optional[Product]:
        pass 