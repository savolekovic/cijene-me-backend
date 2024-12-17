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

class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        self.error = "Validation error"
        self.status_code = 400
        super().__init__(self.message)

class AuthenticationError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) 

class ConflictError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=409,
            detail=detail
        ) 