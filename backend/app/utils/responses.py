from typing import Any, Optional
from fastapi.responses import JSONResponse
from fastapi import status


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK,
    meta: Optional[dict] = None
) -> JSONResponse:
    """Standard success response envelope."""
    content = {
        "success": True,
        "message": message,
        "data": data
    }
    if meta:
        content["meta"] = meta

    return JSONResponse(status_code=status_code, content=content)


def error_response(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    error_code: str = "ERROR",
    details: Any = None
) -> JSONResponse:
    """Standard error response envelope."""
    content = {
        "success": False,
        "message": message,
        "error_code": error_code,
    }
    if details:
        content["details"] = details

    return JSONResponse(status_code=status_code, content=content)


def paginated_response(
    items: list,
    total: int,
    page: int,
    limit: int,
    message: str = "Data retrieved successfully"
) -> JSONResponse:
    """Standard paginated response envelope."""
    total_pages = (total + limit - 1) // limit

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": message,
            "data": items,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        }
    )