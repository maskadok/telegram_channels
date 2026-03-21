from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_sync_service
from app.schemas.sync import SyncRequest, SyncResponse
from app.services.telegram_client import TelegramAuthError
from app.services.telegram_sync import SyncInProgressError, TelegramSyncService

router = APIRouter()


@router.post("/sync", response_model=SyncResponse)
async def sync_channels(
    payload: SyncRequest | None = None,
    sync_service: TelegramSyncService = Depends(get_sync_service),
) -> SyncResponse:
    try:
        summary = await sync_service.sync_channels(
            channel_usernames=payload.channel_usernames if payload else None,
            limit=payload.limit if payload else None,
        )
    except SyncInProgressError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except TelegramAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return SyncResponse.from_summary(summary)
