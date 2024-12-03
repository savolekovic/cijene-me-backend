from typing import List, Optional
from uuid import UUID
from app.domain.models import StoreBrand
from app.domain.repositories import StoreBrandRepository

class StoreBrandUseCases:
    def __init__(self, store_brand_repository: StoreBrandRepository):
        self.repository = store_brand_repository

    async def create_store_brand(self, name: str) -> StoreBrand:
        store_brand = StoreBrand(name=name)
        return await self.repository.create(store_brand)
    
    async def get_store_brand(self, store_brand_id: UUID) -> Optional[StoreBrand]:
        return await self.repository.get_by_id(store_brand_id)
    
    async def get_all_store_brands(self) -> List[StoreBrand]:
        return await self.repository.get_all()
    
    async def update_store_brand(self, store_brand_id: UUID, name: str) -> Optional[StoreBrand]:
        store_brand = StoreBrand(id=store_brand_id, name=name)
        return await self.repository.update(store_brand_id, store_brand)
    
    async def delete_store_brand(self, store_brand_id: UUID) -> bool:
        return await self.repository.delete(store_brand_id) 