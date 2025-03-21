from datetime import datetime
from typing import Any, Sequence
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr

from moxn.base_models.content import Author, MessageRole


class BaseHeaders(BaseModel):
    user_id: str
    org_id: str | None = None
    api_key: SecretStr

    def to_headers(self) -> dict[str, str]:
        return {
            "user_id": self.user_id,
            "org_id": self.org_id or "",
            "api_key": self.api_key.get_secret_value(),
        }


class _Message(BaseModel):
    id: UUID | None = None
    version_id: UUID | None = Field(None, alias="versionId")
    name: str
    description: str
    author: Author
    role: MessageRole
    blocks: dict[str, Any] = Field(default_factory=dict, repr=False)

    model_config = ConfigDict(populate_by_name=True)


class _Prompt(BaseModel):
    id: UUID
    version_id: UUID = Field(..., alias="versionId")
    user_id: UUID = Field(..., alias="userId")
    org_id: UUID | None = Field(None, alias="orgId")
    name: str
    description: str
    task_id: UUID = Field(..., alias="taskId")
    created_at: datetime = Field(..., alias="createdAt")
    messages: Sequence[_Message] = Field(default_factory=list)
    message_order: list[UUID] = Field(default_factory=list, alias="messageOrder")
    raw_input: BaseModel | None = Field(None, alias="rawInput")
    rendered_input: dict | None = Field(None, alias="renderedInput")

    model_config = ConfigDict(populate_by_name=True)


class _Task(BaseModel):
    id: UUID
    version_id: UUID = Field(..., alias="versionId")
    user_id: UUID = Field(..., alias="userId")
    org_id: UUID | None = Field(None, alias="orgId")
    name: str
    description: str
    created_at: datetime = Field(..., alias="createdAt")
    prompts: Sequence[_Prompt] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)
