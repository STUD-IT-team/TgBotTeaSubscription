from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict

class Transaction_Table(BaseModel):
    MAX_ADDRESS_LENGTH: ClassVar[int] = 50
    MAX_NAME_LENGTH: ClassVar[int] = 100
    MAX_RATE: ClassVar[int] = 5

    id: int
    user_id: int
    number: str
    admin_id: int
    date_of_approve: datetime


    model_config = ConfigDict(populate_by_name=True)