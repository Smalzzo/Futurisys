import logging, uuid
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: Exception):
    error_id = str(uuid.uuid4())
    logger.exception(" error %s on %s %s", error_id, request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "erreur serveur", "error_id": error_id},
    )