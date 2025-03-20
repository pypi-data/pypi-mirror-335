"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from typing import Optional
from fastapi import HTTPException, status


class BadRequestException(HTTPException):
    """Exception for bad requests"""

    def __init__(self, message: Optional[str] = None):
        super(BadRequestException, self).__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


class UnauthorizedException(HTTPException):
    """Exception for unauthorized requests"""

    def __init__(self, message: Optional[str] = None):
        super(UnauthorizedException, self).__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )


class UnsupportedMediaTypeException(HTTPException):
    """Exception for unsupported media types"""

    def __init__(self, message: Optional[str] = None):
        super(UnsupportedMediaTypeException, self).__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=message
        )


class ForbiddenException(HTTPException):
    """Exception for forbidden requests"""

    def __init__(self, message: Optional[str] = None):
        super(ForbiddenException, self).__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )


class NotFoundException(HTTPException):
    """Exception for not found resources"""

    def __init__(self, message: Optional[str] = None):
        super(NotFoundException, self).__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message
        )


class ConflictException(HTTPException):
    """Exception for conflicts"""

    def __init__(self, message: Optional[str] = None):
        super(ConflictException, self).__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=message
        )


class UnprocessableEntityException(HTTPException):
    """Exception for unprocessable entity errors"""

    def __init__(self, message: Optional[str] = None):
        super(UnprocessableEntityException, self).__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message
        )


class InternalServerException(HTTPException):
    """Exception for internal server errors"""

    def __init__(self, message: Optional[str] = None):
        super(InternalServerException, self).__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
