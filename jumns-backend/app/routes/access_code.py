"""Routes for /api/access-code — status and activation."""

from fastapi import APIRouter, Request

from app.db.repositories.access_codes import AccessCodesRepository
from app.models.requests import ActivateCodeRequest
from app.models.responses import AccessCodeStatusResponse, ErrorResponse

router = APIRouter(prefix="/access-code", tags=["access-code"])


@router.get("/status")
async def get_status(request: Request) -> AccessCodeStatusResponse:
    repo = AccessCodesRepository()
    activated = repo.get_activation_status(request.state.user_id)
    return AccessCodeStatusResponse(activated=activated)


@router.post("/activate")
async def activate_code(request: Request, body: ActivateCodeRequest):
    repo = AccessCodesRepository()
    success = repo.activate_code(request.state.user_id, body.code)
    if success:
        return AccessCodeStatusResponse(activated=True)
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid or already used access code"},
    )
