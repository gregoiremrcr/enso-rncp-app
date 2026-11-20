from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import FRONTEND_ORIGIN
from app.errors import unexpected_error
from app.routers.routes import router

app = FastAPI(
    title="ENSO Monitor API",
    description="Série historique RONI de la NOAA CPC. RONI et ONI sont des indices distincts. Cette API ne fournit aucune prévision.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware, allow_origins=[FRONTEND_ORIGIN], allow_methods=["GET"], allow_headers=["*"]
)
app.include_router(router, prefix="/api/v1")


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
    messages = {
        400: "bad_request",
        404: "not_found",
        422: "validation_error",
        503: "service_unavailable",
    }
    message = exc.detail if isinstance(exc.detail, str) else "Requête invalide."
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {"code": messages.get(exc.status_code, "http_error"), "message": message}
        },
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Les paramètres de la requête sont invalides.",
            }
        },
    )


app.add_exception_handler(Exception, unexpected_error)
