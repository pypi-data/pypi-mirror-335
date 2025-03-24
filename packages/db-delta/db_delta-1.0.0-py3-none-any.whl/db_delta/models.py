import json
from enum import Enum
from typing import Dict, Any, List, Literal

from pydantic import BaseModel, StringConstraints, Field, model_validator
from typing_extensions import Annotated


class PutItem(BaseModel):
    action: Literal["put_item"]
    key: Dict[str, str | int | float]
    item: Dict[str, Any]


class UpdateTypeEnum(str, Enum):
    ADDED = "added"
    UPDATED = "updated"
    REMOVED = "removed"


class FieldUpdate(BaseModel):
    field: Annotated[str, StringConstraints(min_length=1)]
    update_type: UpdateTypeEnum
    new_value: Annotated[Any | None, Field(default=None)]

    @model_validator(mode="after")
    def validate_model(self):

        match self.update_type:
            case UpdateTypeEnum.ADDED:
                if self.new_value is None:
                    raise Exception("Update type 'ADDED' requires 'new_value'.")  # noqa

            case UpdateTypeEnum.UPDATED:
                if self.new_value is None:
                    raise Exception(
                        "Update type 'UPDATED' requires 'new_value' and 'old_value'."  # noqa
                    )

        return self


class UpdatedItem(BaseModel):
    action: Literal["update_item"]
    key: Dict[str, str | int | float]
    updated_fields: List[FieldUpdate]


class DeletedItem(BaseModel):
    action: Literal["delete_item"]
    key: Dict[str, str | int | float]


class ChangeSet(BaseModel):
    changes: Annotated[
        List[PutItem | UpdatedItem | DeletedItem], Field(discriminator="action")
    ]

    @classmethod
    def from_json(cls, path: str):
        with open(path, "r") as f:
            changes = json.load(f)
        return cls(changes=changes)
