from typing import Dict, List, Optional
from uuid import UUID
from app.domain.models import StoreBrand
from app.domain.repositories import StoreBrandRepository

class InMemoryStoreBrandRepository(StoreBrandRepository):
    def __init__(self):
        self.store_brands: Dict[UUID, StoreBrand] = {}

    async def create(self, store_brand: StoreBrand) -> StoreBrand:
        self.store_brands[store_brand.id] = store_brand
        return store_brand

    async def get_by_id(self, store_brand_id: UUID) -> Optional[StoreBrand]:
        return self.store_brands.get(store_brand_id)

    async def get_all(self) -> List[StoreBrand]:
        return list(self.store_brands.values())

    async def update(self, store_brand_id: UUID, store_brand: StoreBrand) -> Optional[StoreBrand]:
        if store_brand_id in self.store_brands:
            self.store_brands[store_brand_id] = store_brand
            return store_brand
        return None

    async def delete(self, store_brand_id: UUID) -> bool:
        if store_brand_id in self.store_brands:
            del self.store_brands[store_brand_id]
            return True
        return False 