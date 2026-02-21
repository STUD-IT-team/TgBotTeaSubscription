from __future__ import annotations


from pydantic import BaseModel
from pydantic import ConfigDict

class User_Table(BaseModel):
    id: int
    tg_id: int
    last_notification_date: str
    model_config = ConfigDict(populate_by_name=True)