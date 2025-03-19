import uuid

from sqlalchemy import Column, JSON
from sqlmodel import Field
from sqlalchemy.orm import registry

from ..general.models import BaseModel, ClientBaseModel


mapper_registry = registry()

class Integration(ClientBaseModel, table=True):
    name: str = Field(index=True)
    icon: str = Field(index=True)
    type: str = Field(index=True)
    tag: str = Field(index=True, nullable=True)
    enabled: bool = Field(default=True, nullable=True)
    description: str = Field(index=True, nullable=True)
    code_reference: str = Field(index=True)
    setup_config: dict = Field(sa_column=Column(JSON))


class Link(BaseModel, table=True):
    auth_config: dict = Field(sa_column=Column(JSON))
    integration_id: uuid.UUID = Field(foreign_key="integration.id")
