from fastapi import HTTPException

class DatabaseError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=500,
            content={
                "error": "Database error",
                "message": detail
            }
        ) 