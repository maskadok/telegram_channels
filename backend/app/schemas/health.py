from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    environment: str
    database: str
    tracked_channels: int
    stored_posts: int
    scheduler_running: bool
