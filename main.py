from fastapi import FastAPI
from app.api.routes import store_brands

app = FastAPI()
app.include_router(store_brands.router)