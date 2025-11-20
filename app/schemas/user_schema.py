from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    surname: str
    second_name: str
    invocation: str
    rank_id: Optional[UUID]
    post_id: Optional[UUID]
