from fastapi import APIRouter

from .predict import router as predict_router
from .logs import router as logs_router

router = APIRouter()
router.include_router(predict_router)
router.include_router(logs_router)

