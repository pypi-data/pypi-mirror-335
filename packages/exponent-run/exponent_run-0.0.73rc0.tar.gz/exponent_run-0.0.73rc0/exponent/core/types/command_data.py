from enum import Enum
from typing import Any, ClassVar, Literal, Optional, Union

from pydantic import BaseModel


class CommandType(str, Enum):
    THINKING = "thinking"
    FILE_READ = "file_read"
    SUMMARIZE = "summarize"
    STEP_OUTPUT = "step_output"
    PROTOTYPE = "prototype"
    DB_QUERY = "db_query"
    DB_GET_TABLE_NAMES = "db_get_table_names"
    DB_GET_TABLE_SCHEMA = "db_get_table_schema"


class CommandData(BaseModel):
    executable: ClassVar[bool]


class FileReadCommandData(CommandData):
    executable: ClassVar[bool] = True
    type: Literal[CommandType.FILE_READ] = CommandType.FILE_READ

    file_path: str
    language: str


class ThinkingCommandData(CommandData):
    executable: ClassVar[bool] = False
    type: Literal[CommandType.THINKING] = CommandType.THINKING

    content: str
    signature: Optional[str] = None


class PrototypeCommandData(CommandData):
    executable: ClassVar[bool] = True
    type: Literal[CommandType.PROTOTYPE] = CommandType.PROTOTYPE

    command_name: str
    # Structured data extracted from LLM output
    content_json: dict[str, Any]
    # Raw text extracted from LLM output
    content_raw: str
    # Rendered LLM output for frontend display
    content_rendered: str

    llm_command_name_override: Optional[str] = None

    @property
    def llm_command_name(self) -> str:
        return self.llm_command_name_override or self.command_name


# deprecated, use StepOutputCommandData instead
class SummarizeCommandData(CommandData):
    executable: ClassVar[bool] = True
    type: Literal[CommandType.SUMMARIZE] = CommandType.SUMMARIZE

    summary: str


class StepOutputCommandData(CommandData):
    executable: ClassVar[bool] = True
    type: Literal[CommandType.STEP_OUTPUT] = CommandType.STEP_OUTPUT

    step_output_raw: str


class DBQueryCommandData(CommandData):
    executable: ClassVar[bool] = True
    type: Literal[CommandType.DB_QUERY] = CommandType.DB_QUERY

    query: str


class DBGetTableNamesCommandData(CommandData):
    executable: ClassVar[bool] = True
    type: Literal[CommandType.DB_GET_TABLE_NAMES] = CommandType.DB_GET_TABLE_NAMES


class DBGetTableSchemaCommandData(CommandData):
    executable: ClassVar[bool] = True
    type: Literal[CommandType.DB_GET_TABLE_SCHEMA] = CommandType.DB_GET_TABLE_SCHEMA

    table_name: str


CommandDataType = Union[
    FileReadCommandData,
    ThinkingCommandData,
    PrototypeCommandData,
    SummarizeCommandData,  # deprecated
    DBQueryCommandData,
    DBGetTableNamesCommandData,
    DBGetTableSchemaCommandData,
    StepOutputCommandData,
]
