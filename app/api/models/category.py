from pydantic import BaseModel

class CategoryRequest(BaseModel):
    name: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Voće i Povrće"
            }
        } 
        