from datetime import datetime, timezone

from pydantic import BaseModel


class BaseResponse(BaseModel):
    timestamp: datetime = datetime.now(timezone.utc)
    status: str = "200"
