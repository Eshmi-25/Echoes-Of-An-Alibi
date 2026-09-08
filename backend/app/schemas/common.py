from datetime import datetime

from pydantic import BaseModel


class TimestampedModel(BaseModel):
    created_at: datetime
    updated_at: datetime
