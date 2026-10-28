from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


def request_id(request: Request) -> str:
    value = getattr(request.state, "request_id", None)
    if value is None:
        value = str(uuid4())
        request.state.request_id = value
    return value


def error_response(request: Request, status_code: int, code: str, message: str, source_version: str, warnings: list[str]) -> JSONResponse:
    request_identifier = request_id(request)
    payload = {
        "meta": {
            "source_version": source_version,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "data_status": "no_aplica",
            "warnings": warnings,
        },
        "error": {
            "code": code,
            "message": message,
            "request_id": request_identifier,
        },
    }
    return JSONResponse(status_code=status_code, content=payload, headers={"X-Request-ID": request_identifier})
