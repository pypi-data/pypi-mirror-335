import uuid
from typing import Optional

from sqlalchemy import DateTime, func
from sqlmodel import SQLModel, Field
import datetime


class BaseModel(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_on: datetime = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
        nullable=False,
    )
    modified_on: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"onupdate": func.now(), "server_default": func.now()},
    )


class ClientBaseModel(BaseModel):
    company: uuid.UUID = Field(index=True)
