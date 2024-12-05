from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.api.routes import store_brands, store_locations, auth

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Cijene.me API",
        version="1.0.0",
        description="Vidjecemo sto odje da stavimo brat moiiii !!",
        routes=app.routes,
    )
    
    # Add JWT bearer security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT Bearer token"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(store_brands.router)
app.include_router(store_locations.router)
app.include_router(auth.router)