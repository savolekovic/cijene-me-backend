from fastapi import HTTPException

class DatabaseError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=f"Database error: {detail}")

class NotFoundError(HTTPException):
    def __init__(self, resource: str, resource_id: int):
        super().__init__(
            status_code=404, 
            detail=f"{resource} with id {resource_id} not found"
        )

class ValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=f"Validation error: {detail}")

class AuthenticationError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) 