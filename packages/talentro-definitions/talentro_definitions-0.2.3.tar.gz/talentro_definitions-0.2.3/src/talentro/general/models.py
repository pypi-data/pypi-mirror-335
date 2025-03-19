import uuid
from typing import Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import SQLModel, Field
import datetime


class BaseModel(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
    )
    updated_at: Optional[datetime.datetime] = Field(
        sa_column=Column(DateTime(), onupdate=func.now())
    )


class ClientBaseModel(BaseModel):
    company: uuid.UUID = Field(index=True)
