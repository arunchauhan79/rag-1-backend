from fastapi import HTTPException, status

class AppBaseException(HTTPException):
    def __init__(self, status_code: int, error_code: str, detail: str):
        self.error_code = error_code
        super().__init__(status_code=status_code, detail=detail)


class UserAlreadyExistsException(AppBaseException):
    def __init__(self, detail="User already exists"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, error_code="USER_ALREADY_EXISTS", detail=detail)

class BadRequestException(AppBaseException):
    def __init__(self, detail="Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, error_code="BAD_REQUEST", detail=detail)

class UnauthorizedException(AppBaseException):
    def __init__(self, detail="Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, error_code="UNAUTHORIZED", detail=detail)

class ForbiddenException(AppBaseException):
    def __init__(self, detail="Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, error_code="FORBIDDEN", detail=detail)

class NotFoundException(AppBaseException):
    def __init__(self, detail="Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, error_code="NOT_FOUND", detail=detail)

class MethodNotAllowedException(AppBaseException):
    def __init__(self, detail="Method not allowed"):
        super().__init__(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, error_code="METHOD_NOT_ALLOWED", detail=detail)

class ConflictException(AppBaseException):
    def __init__(self, detail="Conflict occurred"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, error_code="CONFLICT", detail=detail)

class UnprocessableEntityException(AppBaseException):
    def __init__(self, detail="Unprocessable entity"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, error_code="UNPROCESSABLE_ENTITY", detail=detail)




class DatabaseConnectionException(AppBaseException):
    def __init__(self, detail="Failed to connect to the database"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_code="DATABASE_CONNECTION_FAILED", detail=detail)

class DatabaseTimeoutException(AppBaseException):
    def __init__(self, detail="Database operation timed out"):
        super().__init__(status_code=status.HTTP_504_GATEWAY_TIMEOUT, error_code="DATABASE_TIMEOUT", detail=detail)

class DatabaseQueryException(AppBaseException):
    def __init__(self, detail="Database query failed"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_code="DATABASE_QUERY_FAILED", detail=detail)

class DataIntegrityException(AppBaseException):
    def __init__(self, detail="Data integrity violation"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, error_code="DATA_INTEGRITY_ERROR", detail=detail)