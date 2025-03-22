from typing import Generic, Literal, Optional, Protocol, TypeVar, Union
from exponent.core.types.command_data import CommandDataType
from pydantic import BaseModel, Field, JsonValue, ValidationInfo, field_validator


DEFAULT_CODE_BLOCK_TIMEOUT = 30

FileWriteStrategyName = Literal[
    "FULL_FILE_REWRITE", "UDIFF", "SEARCH_REPLACE", "NATURAL_EDIT"
]
WRITE_STRATEGY_NATURAL_EDIT: Literal["NATURAL_EDIT"] = "NATURAL_EDIT"
WRITE_STRATEGY_FULL_FILE_REWRITE: Literal["FULL_FILE_REWRITE"] = "FULL_FILE_REWRITE"
WRITE_STRATEGY_UDIFF: Literal["UDIFF"] = "UDIFF"
WRITE_STRATEGY_SEARCH_REPLACE: Literal["SEARCH_REPLACE"] = "SEARCH_REPLACE"


class ExponentEvent(BaseModel):
    chat_uuid: str
    event_uuid: str
    parent_uuid: Optional[str]
    turn_uuid: str

    metadata: dict[str, JsonValue] = Field(default_factory=dict)


class CodeBlockEvent(ExponentEvent):
    language: str
    content: str
    timeout: int = DEFAULT_CODE_BLOCK_TIMEOUT
    require_confirmation: bool = False


class EditContent(BaseModel):
    content: str
    original_file: Optional[str] = None


class NaturalEditContent(BaseModel):
    natural_edit: str
    intermediate_edit: Optional[str]
    original_file: Optional[str]
    new_file: Optional[str]
    error_content: Optional[str]

    @property
    def is_resolved(self) -> bool:
        return self.new_file is not None or self.error_content is not None

    @property
    def is_noop(self) -> bool:
        return bool(
            self.new_file is not None
            and self.original_file is not None
            and self.new_file == self.original_file
        )


class FileWriteEvent(ExponentEvent):
    file_path: str
    language: str
    write_strategy: FileWriteStrategyName
    write_content: Union[NaturalEditContent, EditContent]
    content: str
    error_content: Optional[str]
    require_confirmation: bool = False

    @field_validator("write_content")
    def validate_write_content_type(
        cls, v: Union[NaturalEditContent, EditContent], info: ValidationInfo
    ) -> Union[NaturalEditContent, EditContent]:
        write_strategy = info.data.get("write_strategy")
        if write_strategy == WRITE_STRATEGY_NATURAL_EDIT:
            if not isinstance(v, NaturalEditContent):
                raise ValueError(
                    "When write_strategy is NATURAL_EDIT, write_content must be NaturalEditContent"
                )
        else:
            if not isinstance(v, EditContent):
                raise ValueError(
                    "For non-NATURAL_EDIT strategies, write_content must be EditContent"
                )
        return v


T = TypeVar("T", bound=CommandDataType)


class HoldsCommandData(Protocol, Generic[T]):
    data: T


class CommandEvent(ExponentEvent):
    data: CommandDataType = Field(..., discriminator="type")
    require_confirmation: bool = False


LocalEventType = Union[FileWriteEvent, CodeBlockEvent, CommandEvent]
