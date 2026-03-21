from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.channel_post import ChannelPost  # noqa: E402,F401
from app.models.tracked_channel import TrackedChannel  # noqa: E402,F401
