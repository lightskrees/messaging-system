import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator, model_validator

from message.schemas import MessageResponse

# from pydantic_core.core_schema import ValidationInfo


class ConversationResponse(BaseModel):
    id: uuid.UUID
    conversation_name: Optional[str]
    is_group: bool
    created_at: datetime
    last_activity: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True

    # ToDo: still figuring out how to dynamically change conversation names according the authenticated user...

    # @model_validator(mode="after")
    # @classmethod
    # def validate_conversation_name(cls, model: "ConversationResponse", info: ValidationInfo):
    #     if model.is_group and not model.conversation_name:
    #         raise ValueError("group name is required.")
    #
    #     if not model.is_group:
    #         pass
