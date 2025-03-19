import uuid
from typing import Optional

from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class BaseModel(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs = {"onupdate": lambda: datetime.now(timezone.utc)}
    )


class OrganizationBaseModel(BaseModel):
    organization: uuid.UUID = Field(index=True)
