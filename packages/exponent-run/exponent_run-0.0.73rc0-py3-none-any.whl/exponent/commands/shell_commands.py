import asyncio
import difflib
import sys
import time
from collections.abc import Callable, Coroutine, Iterable
from concurrent.futures import Future
from typing import Any, Literal, Optional, Union
from datetime import datetime
import questionary
from .utils import (
    ask_for_quit_confirmation,
    get_short_git_commit_hash,
    launch_exponent_browser,
)
import click
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import FormattedText, HTML
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.syntax import Syntax

from exponent.commands.common import (
    check_inside_git_repo,
    check_running_from_home_directory,
    check_ssl,
    create_chat,
    inside_ssh_session,
    redirect_to_login,
    start_client,
)
from exponent.commands.settings import use_settings
from exponent.commands.types import (
    StrategyChoice,
    StrategyOption,
    exponent_cli_group,
)
from exponent.commands.utils import (
    ConnectionTracker,
    Spinner,
    ThinkingSpinner,
    start_background_event_loop,
)
from exponent.core.config import Environment, Settings, is_editable_install
from exponent.core.graphql.client import GraphQLClient
from exponent.core.graphql.mutations import HALT_CHAT_STREAM_MUTATION
from exponent.core.graphql.queries import EVENTS_FOR_CHAT_QUERY
from exponent.core.graphql.subscriptions import CHAT_EVENTS_SUBSCRIPTION
from exponent.core.remote_execution.exceptions import ExponentError, RateLimitError
from exponent.core.types.generated.strategy_info import (
    ENABLED_STRATEGY_INFO_LIST,
)

# enum of color themes
COLOR_THEMES = Literal["default", "white_on_green", "white_on_red", "white_on_blue"]

SLASH_COMMANDS = {
    "/help": "Show available commands",
    "/autorun": "Toggle autorun mode",
    "/web": "Move chat to a web browser",
    "/cmd": "Execute a terminal command directly and give the result as context",
    "/thinking": "Toggle thinking mode to show/hide AI's thinking process",
}


@exponent_cli_group()
def shell_cli() -> None:
    pass


if is_editable_install():
    model = "CLAUDE_3_7_SONNET"
else:
    model = "CLAUDE_3_POINT_5_SONNET"


@shell_cli.command()
@click.option(
    "--model",
    help="LLM model",
    required=True,
    default=model,
)
@click.option(
    "--strategy",
    prompt=True,
    prompt_required=False,
    type=StrategyChoice(ENABLED_STRATEGY_INFO_LIST),
    cls=StrategyOption,
    default="NATURAL_EDIT",
)
@click.option(
    "--autorun",
    is_flag=True,
    help="Enable autorun mode",
)
@click.option(
    "--depth",
    type=click.IntRange(1, 30, clamp=True),
    help="Depth limit of the chat if autorun mode is enabled",
    default=5,
)
@click.option(
    "--thinking",
    is_flag=True,
    help="Enable thinking mode to show AI's thinking process",
)
@click.option(
    "--chat-id",
    help="ID of an existing chat session to reconnect",
    required=False,
)
@click.option(
    "--prompt",
    help="Initial prompt",
)
@click.option(
    "--headless",
    is_flag=True,
    help="Run single prompt in headless mode",
)
@use_settings
def shell(
    settings: Settings,
    model: str,
    strategy: str,
    chat_id: Optional[str] = None,
    autorun: bool = False,
    depth: int = 0,
    thinking: bool = False,
    prompt: Optional[str] = None,
    headless: bool = False,
) -> None:
    """Start an Exponent session in your current shell."""

    if not headless and not sys.stdin.isatty():
        print("Terminal not available, running in headless mode")
        headless = True

    if headless and not prompt:
        print("Error: --prompt option is required with headless mode")
        sys.exit(1)

    if not settings.api_key:
        redirect_to_login(settings)
        return

    is_running_from_home_directory = check_running_from_home_directory(
        # We don't require a confirmation for exponent shell because it's more likely
        # there's a legitimate reason for running Exponent from home directory when using shell
        require_confirmation=False
    )

    if not is_running_from_home_directory:  # Prevent double warnings from being shown
        check_inside_git_repo(settings)

    check_ssl()

    api_key = settings.api_key
    base_api_url = settings.base_api_url
    base_ws_url = settings.base_ws_url
    gql_client = GraphQLClient(api_key, base_api_url, base_ws_url)
    loop = start_background_event_loop()
    parent_event_uuid: Optional[str] = None
    checkpoints: list[dict[str, Any]] = []

    if chat_id is None:
        chat_uuid = asyncio.run_coroutine_threadsafe(
            create_chat(api_key, base_api_url, base_ws_url), loop
        ).result()
    else:
        chat_uuid = chat_id

        events = asyncio.run_coroutine_threadsafe(
            _get_events_for_chat(gql_client, chat_uuid), loop
        ).result()
        parent_event_uuid = _get_parent_event_uuid(events)
        checkpoints = _get_checkpoints(events)

    if chat_uuid is None:
        sys.exit(1)

    connection_tracker = ConnectionTracker()

    # If Claude 3.7 is selected, use the new XML strategy
    if (
        is_editable_install()
        and strategy == "NATURAL_EDIT"
        and "CLAUDE_3_7_SONNET" in model
    ):
        strategy = "NATURAL_EDIT_CLAUDE_3_7_XML"
        print("> Using Claude 3.7 XML NATURAL_EDIT strategy\n")

    client_coro = start_client(
        api_key,
        base_api_url,
        base_ws_url,
        chat_uuid,
        connection_tracker=connection_tracker,
    )

    if headless:
        assert prompt is not None

        chat = Chat(
            chat_uuid,
            parent_event_uuid,
            settings.base_url,
            gql_client,
            model,
            strategy,
            autorun,
            depth,
            StaticView(),
            checkpoints=checkpoints,
            thinking=thinking,
        )

        client_task = loop.create_task(client_coro)
        turn_task = loop.create_task(chat.send_prompt(prompt))

        asyncio.run_coroutine_threadsafe(
            asyncio.wait({client_task, turn_task}, return_when=asyncio.FIRST_COMPLETED),
            loop,
        ).result()
    else:
        chat = Chat(
            chat_uuid,
            parent_event_uuid,
            settings.base_url,
            gql_client,
            model,
            strategy,
            autorun,
            depth,
            LiveView(),
            checkpoints=checkpoints,
            thinking=thinking,
        )

        client_fut = asyncio.run_coroutine_threadsafe(client_coro, loop)
        input_handler = InputHandler()
        shell = Shell(
            prompt, loop, input_handler, chat, connection_tracker, settings.environment
        )
        shell.run()
        client_fut.cancel()

    print("Jump back into this chat by running:")
    print(f"  exponent shell --chat-id {chat_uuid}")
    print()
    print("Or continue in a web browser at:")
    print(f"  {chat.url()}")
    print()
    print("Bye!")


async def _get_events_for_chat(
    gql_client: GraphQLClient, chat_uuid: str
) -> list[dict[str, Any]]:
    result = await gql_client.execute(EVENTS_FOR_CHAT_QUERY, {"chatUuid": chat_uuid})
    return result.get("eventsForChat", {}).get("events", [])  # type: ignore


def _get_parent_event_uuid(events: list[dict[str, Any]]) -> Optional[str]:
    if len(events) > 0:
        uuid = events[-1]["eventUuid"]
        assert isinstance(uuid, str)

        return uuid

    return None


def _get_checkpoints(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        event for event in events if event.get("__typename") == "CheckpointCreatedEvent"
    ]


def pause_spinner(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(self: "LiveView", *args: Any, **kwargs: Any) -> Any:
        self.spinner.hide()
        self.spinner = self.default_spinner
        result = func(self, *args, **kwargs)
        self.spinner.show()
        return result

    return wrapper


def stop_spinner(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(self: "LiveView", *args: Any, **kwargs: Any) -> Any:
        self.spinner.hide()
        self.spinner = self.default_spinner
        result = func(self, *args, **kwargs)
        return result

    return wrapper


class BaseView:
    def render_event_summary(self, kind: str, event: dict[str, Any]) -> None:  # noqa: PLR0912
        if kind == "FileWriteEvent":
            summary = "Writing file..."

        elif kind == "FileWriteResultEvent":
            summary = "File written"

        elif kind == "CodeBlockEvent":
            summary = "Executing code..."

        elif kind == "CodeExecutionEvent":
            summary = "Code executed"

        elif kind == "CommandEvent":
            if event["data"]["type"] == "FILE_READ":
                summary = f"Reading file {event['data']['filePath']}..."
            elif event["data"]["type"] == "FILE_OPEN":
                summary = f"Opening file {event['data']['filePath']}..."
            else:
                summary = "Executing command..."

        else:
            return

        seqs = [
            clear_line_seq(),
            self._render_block_footer(summary, status="running", nl=False),
        ]
        render(seqs)

    def _render_block_header(
        self, text: str, theme: COLOR_THEMES = "default"
    ) -> list[str]:
        return [
            block_header_bg_seq(theme),
            block_header_fg_seq(theme),
            "\r",  # Return to start of line
            erase_line_seq(),
            " " + text,  # Single space before text
            reset_attrs_seq(),
            "\n",
        ]

    def _render_block_padding(self) -> list[str]:
        return [
            block_body_bg_seq(),
            erase_line_seq(),
            reset_attrs_seq(),
            "\n",
        ]

    def _render_block_footer(
        self, text: str, status: Optional[str] = None, nl: bool = True
    ) -> list[str]:
        seqs: list[Any] = [
            block_header_bg_seq(),
            block_header_fg_seq(),
            erase_line_seq(),
            " ",
        ]

        if status == "completed":
            seqs.append(
                [
                    fg_color_seq(2),
                    bold_seq(),
                    "✓ ",
                    not_bold_seq(),
                    block_header_fg_seq(),
                ]
            )
        elif status == "rejected":
            seqs.append(
                [
                    fg_color_seq(1),
                    bold_seq(),
                    "𐄂 ",
                    not_bold_seq(),
                    block_header_fg_seq(),
                ]
            )
        elif status == "running":
            seqs.append(["⚙️ "])

        seqs.append([text, reset_attrs_seq()])

        if nl:
            seqs.append(["\n"])

        return seqs

    def _render_natural_edit_diff(self, write: dict[str, Any]) -> list[Any]:
        diff = generate_diff(write.get("originalFile") or "", write["newFile"]).strip()

        highlighted_diff = highlight_code(
            diff, "udiff", line_numbers=False, padding=(0, 2)
        )

        return [
            self._render_block_header("diff"),
            self._render_block_padding(),
            highlighted_diff,
            self._render_block_padding(),
        ]

    def _render_natural_edit_error(self, error: str) -> list[str]:
        return [
            fg_color_seq(1),
            f"\nError: {error.strip()}\n\n",
            reset_attrs_seq(),
        ]

    def _render_code_block_start(self, lang: str) -> list[Any]:
        return [
            self._render_block_header(lang),
            self._render_block_padding(),
        ]

    def _render_code_block_content(self, content: str, lang: str) -> str:
        return highlight_code(content.strip(), lang, line_numbers=False, padding=(0, 2))

    def _render_code_block_output(self, content: str) -> list[Any]:
        lines = pad_left(content, "  ").split("\n")
        output = [[block_body_bg_seq(), erase_line_seq(), line, "\n"] for line in lines]

        return [
            self._render_block_header("output"),
            self._render_block_padding(),
            output,
            self._render_block_padding(),
        ]

    def _render_file_write_block_start(self, path: str) -> list[Any]:
        return [
            self._render_block_header(f"Editing file {path}"),
            self._render_block_padding(),
        ]

    def _render_file_write_block_content(self, content: str, lang: str) -> str:
        return highlight_code(content.strip(), lang, line_numbers=False, padding=(0, 2))

    def _render_file_write_block_result(self, result: Optional[str]) -> list[Any]:
        result = result or "Edit applied"
        return [self._render_block_footer(f"{result}", status="completed")]

    def _render_command_block_start(self, type_: str) -> list[Any]:
        return [
            self._render_block_header(type_.lower()),
            self._render_block_padding(),
        ]

    def _render_command_block_content(self, data: dict[str, Any]) -> list[Any]:
        if data["type"] == "PROTOTYPE":
            content = data["contentRendered"]
        else:
            content = data["filePath"].strip()

        lines = pad_left(content, "  ").split("\n")
        return [[block_body_bg_seq(), erase_line_seq(), line, "\n"] for line in lines]

    def _render_command_block_output(
        self, content: str, type_: str, lang: str
    ) -> list[Any]:
        highlighted_result = highlight_code(
            content.strip(),
            lang,
            line_numbers=False,
            padding=(0, 2),
        )

        return [
            self._render_block_header("output"),
            self._render_block_padding(),
            highlighted_result,
            self._render_block_padding(),
            self._render_block_footer(
                f"{type_.lower()} command executed", status="completed"
            ),
        ]

    def _render_checkpoint_created_block_start(self) -> list[Any]:
        header_text = "".join(
            [
                bold_seq(),
                "✓ ",
                not_bold_seq(),
                "checkpoint created",
            ]
        )
        return [
            self._render_block_header(header_text, "white_on_green"),
            self._render_block_padding(),
        ]

    def _render_checkpoint_content(self, content: str) -> list[Any]:
        # lines = .split("\n")
        # return [[block_body_bg_seq(), erase_line_seq(), line, "\n"] for line in lines]\
        return [
            highlight_code(content.strip(), "text", line_numbers=False, padding=(0, 2)),
        ]

    def _render_checkpoint_created_block(self, event: dict[str, Any]) -> list[Any]:
        content = f"{get_short_git_commit_hash(event['commitHash'])}: {event['commitMessage']}"

        return [
            self._render_checkpoint_created_block_start(),
            self._render_checkpoint_content(content),
            self._render_block_padding(),
            "\n",
        ]

    def _render_checkpoint_rollback_block_start(self) -> list[Any]:
        header_text = "".join(
            [
                bold_seq(),
                "✓ ",
                not_bold_seq(),
                "checkpoint rollback",
            ]
        )
        return [
            self._render_block_header(header_text, "white_on_blue"),
            self._render_block_padding(),
        ]

    def _render_checkpoint_rollback_block(self, event: dict[str, Any]) -> list[Any]:
        pretty_date = datetime.fromisoformat(
            event["gitMetadata"]["commit_date"]
        ).strftime("%Y-%m-%d %H:%M:%S")
        content = (
            f"{get_short_git_commit_hash(event['commitHash'])}: {event['commitMessage']}\n"
            f"{event['gitMetadata']['author_name']} <{event['gitMetadata']['author_email']}> {pretty_date}"
        )

        return [
            self._render_checkpoint_rollback_block_start(),
            self._render_checkpoint_content(content),
            self._render_block_padding(),
            "\n",
        ]

    def _render_checkpoint_error_block_start(self) -> list[Any]:
        return [
            self._render_block_header(
                f"{bold_seq()}𐄂 {not_bold_seq()}checkpoint error", "white_on_red"
            ),
            self._render_block_padding(),
        ]

    def _render_checkpoint_error_block(self, event: dict[str, Any]) -> list[Any]:
        return [
            self._render_checkpoint_error_block_start(),
            self._render_checkpoint_content(event["message"]),
            self._render_block_padding(),
            "\n",
        ]

    def _render_step_block_start(self, title: str) -> list[Any]:
        return [
            self._render_block_header(f"Step: {title}"),
            self._render_block_padding(),
        ]

    def _render_step_block_content(self, content: str) -> list[str]:
        """Render step content with proper formatting and background color.
        Returns a list of formatted lines ready for rendering.
        """
        # First reset any previous formatting
        reset_seq = reset_attrs_seq()
        bg_seq = block_body_bg_seq()
        erase_line_seq_str = erase_line_seq()

        # Apply padding and wrap lines with proper escape sequences
        formatted_lines = []
        lines = content.strip().split("\n")

        for line in lines:
            # erase_line_seq fills the entire line with the background color
            # We need to return to start of line first with \r
            formatted_line = f"\r{bg_seq}{erase_line_seq_str}  {line}{reset_seq}\n"
            formatted_lines.append(formatted_line)

        return formatted_lines

    def _render_step_result_content(self, content: str) -> list[Any]:
        formatted_content = pad_left(content, "  ")
        return [
            self._render_block_header("Step result"),
            self._render_block_padding(),
            formatted_content,
            self._render_block_padding(),
        ]


class LiveView(BaseView):
    def __init__(self) -> None:
        self.buffer: Buffer = NullBuffer()
        self.command_data: Optional[dict[str, Any]] = None
        self.confirmation_required: bool = True
        self.default_spinner = Spinner("Exponent is working...")
        self.msg_gen_spinner = Spinner("Exponent is thinking real hard...")
        self.thinking_spinner = ThinkingSpinner()
        self.step_spinner = Spinner("Exponent is working on a step...")
        self.thinking_start_time: Optional[float] = None
        self.exec_spinner = Spinner(
            "Exponent is waiting for the code to finish running..."
        )
        self.diff_spinner = Spinner("Exponent is generating file diff...")
        self.spinner = self.default_spinner
        self.pending_event: Optional[dict[str, Any]] = None

    def render_event(self, kind: str, event: dict[str, Any]) -> None:  # noqa: PLR0912
        if kind == "MessageStart":
            self._handle_message_start_event(event)
        elif kind == "MessageChunkEvent":
            if event["role"] == "assistant":
                self._handle_message_chunk_event(event)
        elif kind == "MessageEvent":
            if event["role"] == "assistant":
                self._handle_message_event(event)
        elif (
            kind == "CommandChunkEvent"
            and event.get("data", {}).get("__typename") == "ThinkingCommandData"
        ):
            # Start the thinking animation and record start time
            if self.spinner != self.thinking_spinner:
                if self.spinner:
                    self.spinner.hide()
                self.spinner = self.thinking_spinner
                # Record the start time before showing spinner
                self.thinking_start_time = time.time()
                # Pass the start time to spinner
                self.thinking_spinner.start_time = self.thinking_start_time
                self.spinner.show()
        elif (
            kind == "CommandEvent"
            and event.get("data", {}).get("__typename") == "ThinkingCommandData"
        ):
            # Treat CommandEvent with ThinkingCommandData as ThinkingEvent
            self._handle_thinking_event(
                {
                    "eventUuid": event["eventUuid"],
                    "parentUuid": event.get("parentUuid"),
                    "turnUuid": event.get("turnUuid"),
                    "content": event["data"]["content"],
                }
            )
        elif kind == "StepChunkEvent":
            self._handle_step_chunk_event(event)
        elif kind == "StepEvent":
            self._handle_step_event(event)
        elif kind == "StepConfirmationEvent":
            self._handle_step_confirmation_event(event)
        elif kind == "StepExecutionStartEvent":
            self._handle_step_execution_start_event(event)
        elif kind == "StepExecutionResultEvent":
            self._handle_step_execution_result_event(event)
        elif kind == "FileWriteChunkEvent":
            self._handle_file_write_chunk_event(event)
        elif kind == "FileWriteEvent":
            self._handle_file_write_event(event)
        elif kind == "FileWriteConfirmationEvent":
            self._handle_file_write_confirmation_event(event)
        elif kind == "FileWriteStartEvent":
            self._handle_file_write_start_event(event)
        elif kind == "FileWriteResultEvent":
            self._handle_file_write_result_event(event)
        elif kind == "CodeBlockChunkEvent":
            self._handle_code_block_chunk_event(event)
        elif kind == "CodeBlockEvent":
            self._handle_code_block_event(event)
        elif kind == "CodeBlockConfirmationEvent":
            self._handle_code_block_confirmation_event(event)
        elif kind == "CodeExecutionStartEvent":
            self._handle_code_execution_start_event(event)
        elif kind == "CodeExecutionEvent":
            self._handle_code_execution_event(event)
        elif kind == "CommandChunkEvent":
            if event["data"]["type"] in ["FILE_READ", "FILE_OPEN", "PROTOTYPE"]:
                self._handle_command_chunk_event(event)
        elif kind == "CommandEvent":
            if event["data"]["type"] in ["FILE_READ", "FILE_OPEN", "PROTOTYPE"]:
                self._handle_command_event(event)
        elif kind == "CommandConfirmationEvent":
            self._handle_command_confirmation_event(event)
        elif kind == "CommandStartEvent":
            self._handle_command_start_event(event)
        elif kind == "CommandResultEvent":
            self._handle_command_result_event(event)
        elif kind == "Error":
            error_message = event["message"]
            raise ExponentError(error_message)
        elif kind == "RateLimitError":
            error_message = event["message"]
            raise RateLimitError(error_message)
        elif kind == "CheckpointCreatedEvent":
            self._handle_checkpoint_created_event(event)
        elif kind == "CheckpointRollbackEvent":
            self._handle_checkpoint_rollback_event(event)
        elif kind == "CheckpointError":
            self._handle_checkpoint_error_event(event)

    def start_turn(self) -> None:
        self.spinner.show()

    def end_turn(self) -> None:
        self.spinner.hide()

    @pause_spinner
    def _handle_message_start_event(self, event: dict[str, Any]) -> None:
        self.spinner = self.msg_gen_spinner

    @pause_spinner
    def _handle_thinking_start_event(self, event: dict[str, Any]) -> None:
        # Use ThinkingSpinner for a specialized thinking animation
        self.spinner = self.thinking_spinner
        self.spinner.show()
        # Record the start time
        self.thinking_start_time = time.time()

    @pause_spinner
    def _handle_thinking_event(self, event: dict[str, Any]) -> None:
        # This handles the thinking event completion
        if self.spinner == self.thinking_spinner:
            self.spinner.hide()
            self.spinner = self.default_spinner

        # Calculate thinking duration
        if self.thinking_start_time is not None:
            duration = time.time() - self.thinking_start_time
            # Format duration nicely
            if duration < 1:
                duration_str = f"{int(duration * 1000)}ms"
            elif duration < 60:
                # Round to nearest second to match spinner display
                duration_str = f"{int(duration)}s"
            else:
                mins = int(duration // 60)
                secs = int(duration % 60)
                duration_str = f"{mins}m {secs}s"

            # Improved message with more natural language and decorations
            # Use render() instead of print() to ensure proper terminal rendering
            render(
                [
                    f"\r\x1b[2m\x1b[38;5;249m◇ Exponent thought for {duration_str} ◇\x1b[0m\n\n"
                ]
            )

            # Reset the start time
            self.thinking_start_time = None

    @stop_spinner
    def _handle_message_chunk_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["eventUuid"]
        seqs = []

        if self.buffer.event_uuid != event_uuid:
            self.buffer = CharBuffer(event_uuid)

        assert isinstance(self.buffer, CharBuffer)

        seqs.append(self.buffer.render_new_chars(event["content"]))
        render(seqs)

    @pause_spinner
    def _handle_message_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["eventUuid"]
        seqs = []

        if self.buffer.event_uuid != event_uuid:
            self.buffer = CharBuffer(event_uuid)

        assert isinstance(self.buffer, CharBuffer)

        seqs.append(self.buffer.render_new_chars(event["content"]))
        seqs.append(["\n\n"])
        render(seqs)

    @stop_spinner
    def _handle_file_write_chunk_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["eventUuid"]
        seqs: list[Any] = []

        if self.buffer.event_uuid != event_uuid:
            self.buffer = LineBuffer(event_uuid)

            seqs.append(
                [
                    self._render_block_header(f"Editing file {event['filePath']}"),
                    self._render_block_padding(),
                ]
            )

        assert isinstance(self.buffer, LineBuffer)

        write = event["writeContent"]
        content = write.get("naturalEdit") or write.get("content") or event["content"]

        formatted_content = self._render_file_write_block_content(
            content, event["language"]
        )

        seqs.append(self.buffer.render_new_lines(formatted_content))

        if (
            "intermediateEdit" in write and write["intermediateEdit"] is not None
        ):  # natural edit
            # when intermediateEdit is present in writeContent dict
            # it indicates the server is generating original/new file pair
            seqs.append([self._render_block_padding(), "\n"])
            render(seqs)
            self.spinner = self.diff_spinner
            self.spinner.show()
        else:
            render(seqs)

    @pause_spinner
    def _handle_file_write_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["eventUuid"]
        seqs: list[Any] = []

        if self.buffer.event_uuid != event_uuid:
            self.buffer = LineBuffer(event_uuid)
            seqs.append(self._render_file_write_block_start(event["filePath"]))

        assert isinstance(self.buffer, LineBuffer)

        write = event["writeContent"]

        if "newFile" in write:  # natural edit
            seqs.append(
                [
                    "\r",
                    move_cursor_up_seq(2),
                    erase_display_seq(),
                ]
            )

        content = write.get("naturalEdit") or write.get("content") or event["content"]

        formatted_content = self._render_file_write_block_content(
            content, event["language"]
        )

        seqs.append(
            [
                self.buffer.render_new_lines(formatted_content),
                self._render_block_padding(),
            ]
        )

        error = write.get("errorContent")

        if error is None:
            if write.get("newFile") is not None:
                seqs.append(self._render_natural_edit_diff(write))

            if event["requireConfirmation"]:
                seqs.append(
                    [
                        self._render_block_footer(
                            "Confirm edit with <C+y>. Sending a new message will dismiss code changes."
                        ),
                        "\n",
                    ]
                )
        else:
            seqs.append(self._render_natural_edit_error(error))

        render(seqs)
        self.confirmation_required = event["requireConfirmation"]

    @pause_spinner
    def _handle_file_write_confirmation_event(self, event: dict[str, Any]) -> None:
        if self.buffer.event_uuid != event["fileWriteUuid"]:
            return

        seqs = []

        if event["accepted"]:
            seqs.append(
                [
                    move_cursor_up_seq(2),
                    self._render_block_footer("Applying edit...", status="running"),
                    "\n",
                ]
            )
        elif self.confirmation_required:
            # user entered new prompt, cursor moved down
            # therefore we need to move it up, redraw status, and move it
            # back where it was

            seqs.append(
                [
                    move_cursor_up_seq(4),
                    self._render_block_footer("Edit dismissed", status="rejected"),
                    "\n\n\n",
                ]
            )

        render(seqs)

    @pause_spinner
    def _handle_file_write_start_event(self, event: dict[str, Any]) -> None:
        return

    @pause_spinner
    def _handle_file_write_result_event(self, event: dict[str, Any]) -> None:
        if self.buffer.event_uuid != event["fileWriteUuid"]:
            return

        seqs: list[Any] = []

        if self.confirmation_required:
            seqs.append([move_cursor_up_seq(2)])

        seqs.append([self._render_file_write_block_result(event["content"]), "\n"])

        render(seqs)

    @stop_spinner
    def _handle_command_chunk_event(self, event: dict[str, Any]) -> None:
        # Ignore thinking chunks
        if event["data"]["type"] == "THINKING":
            return

        type_ = self._get_command_type(event["data"])

        event_uuid = event["eventUuid"]
        seqs = []

        if self.buffer.event_uuid != event_uuid:
            self.buffer = CommandBuffer(event_uuid)

            seqs.append(
                [
                    self._render_block_header(type_),
                    self._render_block_padding(),
                ]
            )

        assert isinstance(self.buffer, CommandBuffer)

        formatted_content = self._render_command_block_content(event["data"])
        seqs.append(self.buffer.render_new_lines(formatted_content))
        render(seqs)

    @pause_spinner
    def _handle_command_event(self, event: dict[str, Any]) -> None:
        type_ = self._get_command_type(event["data"])
        event_uuid = event["eventUuid"]
        seqs: list[Any] = []

        if self.buffer.event_uuid != event_uuid:
            self.buffer = CommandBuffer(event_uuid)
            seqs.append(self._render_command_block_start(type_))

        assert isinstance(self.buffer, CommandBuffer)

        formatted_content = self._render_command_block_content(event["data"])
        seqs.append(self.buffer.render_new_lines(formatted_content))
        seqs.append(self._render_block_padding())

        if event["requireConfirmation"]:
            seqs.append(
                [
                    self._render_block_footer(
                        f"Confirm {type_} command with <C+y>. "
                        "Sending a new message will cancel this command."
                    ),
                    "\n",
                ]
            )

        render(seqs)
        self.command_data = event["data"]
        self.confirmation_required = event["requireConfirmation"]

    @pause_spinner
    def _handle_command_confirmation_event(self, event: dict[str, Any]) -> None:
        if self.buffer.event_uuid != event["commandUuid"]:
            return

        seqs = []

        if event["accepted"]:
            seqs.append(
                [
                    move_cursor_up_seq(2),
                    self._render_block_footer("Executing command...", status="running"),
                    "\n",
                ]
            )
        else:
            # user entered new prompt, cursor moved down
            # therefore we need to move it up, redraw status, and move it
            # back where it was

            seqs.append(
                [
                    move_cursor_up_seq(4),
                    self._render_block_footer(
                        "Command did not execute", status="rejected"
                    ),
                    "\n\n\n",
                ]
            )

        render(seqs)

    def _handle_command_start_event(self, event: dict[str, Any]) -> None:
        return

    @pause_spinner
    def _handle_command_result_event(self, event: dict[str, Any]) -> None:
        if self.buffer.event_uuid != event["commandUuid"] or self.command_data is None:
            return

        seqs: list[Any] = []

        if self.confirmation_required:
            seqs.append([move_cursor_up_seq(2)])

        # For FILE_READ commands, only show that the command ran successfully, not the file contents
        if self.command_data["type"] == "FILE_READ":
            seqs.append(
                [
                    self._render_block_footer(
                        "File read successfully", status="completed"
                    ),
                    "\n",
                ]
            )
        else:
            seqs.append(
                [
                    self._render_command_block_output(
                        event["content"],
                        self._get_command_type(self.command_data),
                        self.command_data.get("language", "txt"),
                    ),
                    "\n",
                ]
            )

        render(seqs)
        self.command_data = None

    @stop_spinner
    def _handle_code_block_chunk_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["eventUuid"]
        seqs = []

        if self.buffer.event_uuid != event_uuid:
            self.buffer = LineBuffer(event_uuid)

            seqs.append(
                [
                    self._render_block_header(event["language"]),
                    self._render_block_padding(),
                ]
            )

        assert isinstance(self.buffer, LineBuffer)

        formatted_content = self._render_code_block_content(
            event["content"], event["language"]
        )

        seqs.append(self.buffer.render_new_lines(formatted_content))
        render(seqs)

    @pause_spinner
    def _handle_code_block_event(self, event: dict[str, Any]) -> None:
        event_uuid = event["eventUuid"]
        seqs: list[Any] = []

        if self.buffer.event_uuid != event_uuid:
            self.buffer = LineBuffer(event_uuid)
            seqs.append(self._render_code_block_start(event["language"]))

        assert isinstance(self.buffer, LineBuffer)

        formatted_content = self._render_code_block_content(
            event["content"], event["language"]
        )

        seqs.append(self.buffer.render_new_lines(formatted_content))
        seqs.append(self._render_block_padding())

        if event["requireConfirmation"]:
            seqs.append(
                [
                    self._render_block_footer(
                        "Run this code now with <C+y>. Sending a new message will cancel this request."
                    ),
                    "\n",
                ]
            )

        render(seqs)
        self.confirmation_required = event["requireConfirmation"]

    @pause_spinner
    def _handle_code_block_confirmation_event(self, event: dict[str, Any]) -> None:
        if self.buffer.event_uuid != event["codeBlockUuid"]:
            return

        seqs = []

        if event["accepted"]:
            seqs.append(
                [
                    move_cursor_up_seq(2),
                    self._render_block_footer("Running code...", status="running"),
                    "\n",
                ]
            )
        else:
            # user entered new prompt, cursor moved down
            # therefore we need to move it up, redraw status, and move it
            # back where it was

            seqs.append(
                [
                    move_cursor_up_seq(4),
                    self._render_block_footer(
                        "Code did not execute", status="rejected"
                    ),
                    "\n\n\n",
                ]
            )

        render(seqs)

    @pause_spinner
    def _handle_code_execution_start_event(self, event: dict[str, Any]) -> None:
        self.spinner = self.exec_spinner

    @pause_spinner
    def _handle_code_execution_event(self, event: dict[str, Any]) -> None:
        if self.buffer.event_uuid != event["codeBlockUuid"]:
            return

        seqs: list[Any] = []

        if self.confirmation_required:
            seqs.append([move_cursor_up_seq(2)])

        seqs.append([self._render_code_block_output(event["content"]), "\n"])

        render(seqs)

    def _get_command_type(self, data: dict[str, Any]) -> str:
        if data["type"] == "PROTOTYPE":
            return str(data["commandName"])
        elif data["type"] == "FILE_READ":
            return "Read File"
        elif data["type"] == "FILE_OPEN":
            return "Open File"
        else:
            return str(data["type"]).title().replace("_", " ")

    def _handle_checkpoint_created_event(self, event: dict[str, Any]) -> None:
        render(self._render_checkpoint_created_block(event))

    def _handle_checkpoint_rollback_event(self, event: dict[str, Any]) -> None:
        render(self._render_checkpoint_rollback_block(event))

    def _handle_checkpoint_error_event(self, event: dict[str, Any]) -> None:
        render(self._render_checkpoint_error_block(event))

    @pause_spinner
    def _handle_step_chunk_event(self, event: dict[str, Any]) -> None:
        """Handle streaming chunks for step events.

        Simply shows a spinner while streaming step chunks.
        We'll let the final StepEvent handle the full rendering.
        """
        # Just show a spinner for step chunks coming in
        # Don't render partial content to avoid duplication
        self.spinner = self.step_spinner
        self.spinner.show()

    @pause_spinner
    def _handle_step_event(self, event: dict[str, Any]) -> None:
        """Handle a step event by rendering it with proper ANSI formatting.

        This is modeled after the file_write_event handler for consistency.
        """
        event_uuid = event["eventUuid"]
        seqs = []

        self.buffer = LineBuffer(event_uuid)

        # Get title with fallback
        title = event.get("stepTitle") or "Step"
        seqs.append(self._render_block_header(f"Step: {title}"))
        seqs.append(self._render_block_padding())

        # Get content with fallbacks and format it
        content = (
            event.get("stepContent")
            or event.get("stepDescription", "")
            or event.get("description", "")
        )

        if content:
            # Format lines with proper background color
            lines = content.strip().split("\n")
            formatted_lines = []
            for line in lines:
                formatted_lines.append(
                    [
                        block_body_bg_seq(),
                        erase_line_seq(),
                        "  " + line,
                        reset_attrs_seq(),
                        "\n",
                    ]
                )
            seqs.extend(formatted_lines)

        seqs.append(self._render_block_padding())

        # Check if this step requires confirmation
        require_confirmation = event.get("requireConfirmation", False)
        if require_confirmation:
            seqs.append(
                [
                    *self._render_block_footer(
                        "Confirm step with <C+y>. Sending a new message will cancel this step."
                    ),
                    "\n",
                ]
            )

        # Render it all at once
        render(seqs)

        # Store confirmation state and step event for later
        self.confirmation_required = require_confirmation
        if require_confirmation:
            self.pending_event = event

    @pause_spinner
    def _handle_step_confirmation_event(self, event: dict[str, Any]) -> None:
        """Handle confirmation events for steps.

        Updates the UI to show that a step has been confirmed or rejected.
        """
        # Copy exactly the file_write_confirmation_event handler pattern
        # This pattern is known to work correctly
        if self.buffer.event_uuid != event["stepUuid"]:
            return

        seqs = []

        if event["accepted"]:
            seqs.append(
                [
                    move_cursor_up_seq(2),
                    self._render_block_footer("Executing step...", status="running"),
                    "\n",
                ]
            )
        else:
            # user entered new prompt, cursor moved down
            # therefore we need to move it up, redraw status, and move it
            # back where it was
            seqs.append(
                [
                    move_cursor_up_seq(4),
                    self._render_block_footer(
                        "Step did not execute", status="rejected"
                    ),
                    "\n\n\n",
                ]
            )

        render(seqs)

        # If the step was rejected, clear pending state
        if not event["accepted"]:
            self.pending_event = None
            self.confirmation_required = False

    @pause_spinner
    def _handle_step_execution_start_event(self, event: dict[str, Any]) -> None:
        """Handle the start of step execution.

        Sets the appropriate spinner and does basic validation.
        """
        try:
            # Log the event UUID for debugging
            step_uuid = event.get("stepUuid")

            # Only change spinner if we have a step UUID
            if step_uuid and self.buffer.event_uuid.startswith("step-"):
                self.spinner = self.step_spinner
                self.spinner.show()
        except Exception as e:
            # Log the error but don't crash the entire UI
            render(
                [f"\r\x1b[31mError handling step execution start: {str(e)}\x1b[0m\n"]
            )

    @pause_spinner
    def _handle_step_execution_result_event(self, event: dict[str, Any]) -> None:
        """Handle the result of a step execution.

        Shows the step output/result and marks the step as completed.
        This is modeled after the file_write_result_event handler.
        """
        # Display results regardless of UUID matching to ensure we always see them
        seqs = []

        # Check for result content with fallbacks
        result = event.get("stepOutputRaw") or event.get("stepSummary", "")
        if result:
            # Render a result block with proper formatting
            seqs.append(self._render_block_header("Step result"))
            seqs.append(self._render_block_padding())

            # Format lines with proper background color
            lines = result.strip().split("\n")
            formatted_lines = []
            for line in lines:
                formatted_lines.append(
                    [
                        block_body_bg_seq(),
                        erase_line_seq(),
                        "  " + line,
                        reset_attrs_seq(),
                        "\n",
                    ]
                )
            seqs.extend(formatted_lines)

            seqs.append(self._render_block_padding())

        # Add the completion footer
        seqs.append(self._render_block_footer("Step completed", status="completed"))
        seqs.append(["\n"])

        render(seqs)

        # Reset all state now that execution is complete
        self.pending_event = None
        self.confirmation_required = False
        self.spinner = self.default_spinner

    def handle_checkpoint_interrupt(self, event: dict[str, Any]) -> None:
        self.buffer = NullBuffer()
        render(["Now back to it:", "\n", "\n"])
        self.render_event(event["__typename"], event)

        # rendering the event toggles on the spinner
        self.end_turn()


class StaticView(BaseView):
    def __init__(self) -> None:
        self.command_data: Optional[dict[str, Any]] = None
        self.thinking_start_time: Optional[float] = None
        self.pending_event: Optional[dict[str, Any]] = None
        self.confirmation_required: bool = False

    def render_event(self, kind: str, event: dict[str, Any]) -> None:  # noqa: PLR0912
        if kind == "MessageEvent":
            if event["role"] == "assistant":
                print(event["content"].strip())
                print()

        elif (
            kind == "CommandChunkEvent"
            and event.get("data", {}).get("__typename") == "ThinkingCommandData"
        ):
            # Record start time for thinking
            self.thinking_start_time = time.time()

        elif (
            kind == "CommandEvent"
            and event.get("data", {}).get("__typename") == "ThinkingCommandData"
        ):
            # Calculate thinking duration
            if self.thinking_start_time is not None:
                duration = time.time() - self.thinking_start_time
                # Format duration nicely
                if duration < 1:
                    duration_str = f"{int(duration * 1000)}ms"
                elif duration < 60:
                    # Round to nearest second to match spinner display
                    duration_str = f"{int(duration)}s"
                else:
                    mins = int(duration // 60)
                    secs = int(duration % 60)
                    duration_str = f"{mins}m {secs}s"

                # Improved message with more natural language and decorations
                # Use render() instead of print() to ensure proper terminal rendering
                render(
                    [
                        f"\x1b[2m\x1b[38;5;249m◇ Exponent thought for {duration_str} ◇\x1b[0m\n\n"
                    ]
                )

                # Reset the start time
                self.thinking_start_time = None

        elif kind == "StepChunkEvent" or kind == "StepEvent":
            title = event.get("stepTitle") or "Step"
            content = (
                event.get("stepContent")
                or event.get("stepDescription", "")
                or event.get("description", "")
            )

            if content:
                # For StaticView, we use simpler formatting without ANSI sequences
                formatted_content = ""
                for line in content.strip().split("\n"):
                    formatted_content += f"  {line}\n"

                seqs = [
                    self._render_block_header(f"Step: {title}"),
                    self._render_block_padding(),
                    formatted_content,
                    self._render_block_padding(),
                ]

                # Store for confirmation if needed
                if kind == "StepEvent" and event.get("requireConfirmation", False):
                    self.pending_event = event
                    self.confirmation_required = True
                    seqs.append(
                        self._render_block_footer(
                            "Confirm step with <C+y>. Sending a new message will cancel this step."
                        )
                    )

                render(seqs)

        elif kind == "StepExecutionResultEvent":
            result = event.get("stepOutputRaw") or event.get("stepSummary", "")
            if result:
                # For StaticView, we use simpler formatting without ANSI sequences
                formatted_result = ""
                for line in result.strip().split("\n"):
                    formatted_result += f"  {line}\n"

                seqs = [
                    self._render_block_header("Step result"),
                    self._render_block_padding(),
                    formatted_result,
                    self._render_block_padding(),
                    self._render_block_footer("Step completed", status="completed"),
                    "\n",
                ]
                render(seqs)

                # Clear pending event and reset confirmation flag
                self.pending_event = None
                self.confirmation_required = False

        elif kind == "CommandEvent":
            if event.get("data", {}).get("__typename") == "ThinkingCommandData":
                # We already handled this case above
                pass
            elif event.get("data", {}).get("type") in ["FILE_READ", "FILE_OPEN"]:
                command_type = (
                    "Read File"
                    if event.get("data", {}).get("type") == "FILE_READ"
                    else "Open File"
                )

                seqs = [
                    self._render_command_block_start(command_type),
                    self._render_command_block_content(event["data"]),
                    self._render_block_padding(),
                ]

                render(seqs)
                self.command_data = event["data"]

        elif kind == "FileWriteEvent":
            write = event["writeContent"]

            content = (
                write.get("naturalEdit") or write.get("content") or event["content"]
            )

            seqs = [
                self._render_file_write_block_start(event["filePath"]),
                self._render_file_write_block_content(content, event["language"]),
                self._render_block_padding(),
            ]

            error = write.get("errorContent")

            if error is None:
                if write.get("newFile") is not None:
                    seqs.append(self._render_natural_edit_diff(write))
            else:
                seqs.append(self._render_natural_edit_error(error))

            render(seqs)

        elif kind == "FileWriteResultEvent":
            seqs = [self._render_file_write_block_result(event["content"]), "\n"]
            render(seqs)

        elif kind == "CodeBlockEvent":
            seqs = [
                self._render_code_block_start(event["language"]),
                self._render_code_block_content(event["content"], event["language"]),
                self._render_block_padding(),
            ]

            render(seqs)

        elif kind == "CodeExecutionEvent":
            render([self._render_code_block_output(event["content"]), "\n"])

        elif kind == "CommandEvent":
            if event["data"]["type"] not in ["FILE_READ", "FILE_OPEN"]:
                return

            command_type = (
                "Read File" if event["data"]["type"] == "FILE_READ" else "Open File"
            )

            seqs = [
                self._render_command_block_start(command_type),
                self._render_command_block_content(event["data"]),
                self._render_block_padding(),
            ]

            render(seqs)
            self.command_data = event["data"]

        elif kind == "CommandResultEvent":
            if self.command_data is not None:
                # For FILE_READ commands, only show that the command ran successfully
                if self.command_data["type"] == "FILE_READ":
                    seqs = [
                        self._render_block_footer(
                            "File read successfully", status="completed"
                        ),
                        "\n",
                    ]
                else:
                    command_type = (
                        "Read File"
                        if self.command_data["type"] == "FILE_READ"
                        else "Open File"
                    )
                    seqs = [
                        self._render_command_block_output(
                            event["content"],
                            command_type,
                            self.command_data["language"],
                        ),
                        "\n",
                    ]

                render(seqs)
                self.command_data = None

        elif kind == "Error":
            error_message = event["message"]
            print(f"Error: {error_message}")
            print()
        elif kind == "RateLimitError":
            error_message = event["message"]
            print(f"Error: {error_message}")
            print(
                "Visit https://www.exponent.run/settings to update your billing settings."
            )
            print()

        elif kind == "CheckpointError":
            print(f"Checkpoint error: {event['message']}")
            print()

        elif kind == "CheckpointCreatedEvent":
            render(self._render_checkpoint_created_block(event))

    def start_turn(self) -> None:
        pass

    def end_turn(self) -> None:
        pass

    def handle_checkpoint_interrupt(self, event: dict[str, Any]) -> None:
        pass


class Chat:
    def __init__(
        self,
        chat_uuid: str,
        parent_event_uuid: Optional[str],
        base_url: str,
        gql_client: GraphQLClient,
        model: str,
        strategy: str,
        autorun: bool,
        depth: int,
        view: Union[StaticView, LiveView],
        checkpoints: list[dict[str, Any]],
        thinking: bool = False,
    ) -> None:
        self.chat_uuid = chat_uuid
        self.base_url = base_url
        self.gql_client = gql_client
        self.model = model
        self.strategy = strategy
        self.autorun = autorun
        self.depth = depth
        self.thinking = thinking
        self.view = view
        self.pending_event = None
        self.parent_uuid: Optional[str] = parent_event_uuid
        self.block_row_offset = 0
        self.console = Console()
        self.checkpoints = checkpoints
        self.inside_step_execution = False

    async def send_prompt(self, prompt: str) -> None:
        self.view.start_turn()

        await self.process_chat_subscription(
            {"prompt": {"message": prompt, "attachments": []}}
        )

    async def send_confirmation(self) -> None:
        if not self.pending_event:
            return

        # Make a local copy of the pending event before potentially clearing it
        # during subscription processing
        pending_event = self.pending_event

        if pending_event["__typename"] == "CodeBlockEvent":
            await self.process_chat_subscription(
                {
                    "codeBlockConfirmation": {
                        "accepted": True,
                        "codeBlockUuid": pending_event["eventUuid"],
                    }
                }
            )
        elif pending_event["__typename"] == "FileWriteEvent":
            await self.process_chat_subscription(
                {
                    "fileWriteConfirmation": {
                        "accepted": True,
                        "fileWriteUuid": pending_event["eventUuid"],
                    }
                }
            )
        elif pending_event["__typename"] == "CommandEvent":
            await self.process_chat_subscription(
                {
                    "commandConfirmation": {
                        "accepted": True,
                        "commandUuid": pending_event["eventUuid"],
                    }
                }
            )
        elif pending_event["__typename"] == "StepEvent":
            # Include the required stop_after_execution field which defaults to False
            # This field is required by the GraphStepConfirmationResponse schema
            confirm_payload = {
                "stepConfirmation": {
                    "accepted": True,
                    "stepUuid": pending_event["eventUuid"],
                    "stopAfterExecution": False,
                }
            }

            # Process without any debugging output
            await self.process_chat_subscription(confirm_payload)

    async def send_direct_action(self, action_type: str, args: dict[str, Any]) -> None:
        self.view.start_turn()
        print()
        if action_type == "shell":
            await self.process_chat_subscription(
                {"directAction": {"shellDirectAction": args}}
            )
        elif action_type == "checkpoint":
            await self.process_chat_subscription(
                {"directAction": {"createCheckpointDirectAction": args}}
            )

            if self.pending_event:
                self.view.handle_checkpoint_interrupt(self.pending_event)
        elif action_type == "rollback":
            await self.process_chat_subscription(
                {"directAction": {"checkpointRollbackDirectAction": args}}
            )
        else:
            raise ValueError(f"Unsupported direct action type: {action_type}")

    def toggle_autorun(self) -> bool:
        self.autorun = not self.autorun
        return self.autorun

    def toggle_thinking(self) -> bool:
        self.thinking = not self.thinking
        return self.thinking

    async def halt_stream(self) -> None:
        await self.gql_client.execute(
            HALT_CHAT_STREAM_MUTATION, {"chatUuid": self.chat_uuid}, "HaltChatStream"
        )

    def url(self) -> str:
        return f"{self.base_url}/chats/{self.chat_uuid}"

    async def process_chat_subscription(self, extra_vars: dict[str, Any]) -> None:
        vars = {
            "chatUuid": self.chat_uuid,
            "parentUuid": self.parent_uuid,
            "model": self.model,
            "strategyNameOverride": self.strategy,
            "useToolsConfig": "read_write",
            "requireConfirmation": not self.autorun,
            "depthLimit": self.depth,
            "enableThinking": self.thinking,
        }

        vars.update(extra_vars)

        try:
            async for response in self.gql_client.subscribe(
                CHAT_EVENTS_SUBSCRIPTION, vars
            ):
                event = response["authenticatedChat"]
                kind = event["__typename"]

                if kind == "StepConfirmationEvent" and event["accepted"]:
                    self.inside_step_execution = True
                elif kind == "StepExecutionResultEvent":
                    self.inside_step_execution = False

                # Render the event
                if not self.inside_step_execution:
                    self.view.render_event(kind, event)
                else:
                    self.view.render_event_summary(kind, event)

                # Track parent UUID for future requests
                self.parent_uuid = event.get("eventUuid") or self.parent_uuid

                # Handle storing pending events that need confirmation
                if kind in [
                    "CodeBlockEvent",
                    "FileWriteEvent",
                    "CommandEvent",
                    "StepEvent",
                ] and event.get("requireConfirmation"):
                    self.pending_event = event
                # Store checkpoints
                elif kind == "CheckpointCreatedEvent":
                    self.checkpoints.append(event)
                else:
                    self.pending_event = None

        except Exception as e:
            # Log subscription processing errors only if needed
            render([f"\r\x1b[31mError: {str(e)}\x1b[0m\n"])
        finally:
            self.view.end_turn()


class InputHandler:
    def __init__(self) -> None:
        self.kb = KeyBindings()
        self.shortcut_pressed = None

        self.session: PromptSession[Any] = PromptSession(
            completer=SlashCommandCompleter(),
            complete_while_typing=False,
            key_bindings=self.kb,
        )

        self.style = Style.from_dict(
            {
                "bottom-toolbar": "noreverse",
            }
        )

        @self.kb.add("c-y")
        def _(event: Any) -> None:
            self.shortcut_pressed = "<c-y>"
            event.app.exit()

        @self.kb.add("c-d")
        def _(event: Any) -> None:
            self.shortcut_pressed = "<c-d>"
            event.app.exit()

        @self.kb.add("c-a")
        def _(event: Any) -> None:
            self.shortcut_pressed = "<c-a>"
            event.app.exit()

        @self.kb.add("c-t")
        def _(event: Any) -> None:
            self.shortcut_pressed = "<c-t>"
            event.app.exit()

    def prompt(self, autorun: bool, thinking: bool) -> str:
        toolbar = []

        if autorun:
            toolbar.append(("ansired", "➔ autorun: on"))
        else:
            toolbar.append(("#777777", "➔ autorun: off"))

        toolbar.append(("", " "))
        toolbar.append(("#777777", "(toggle with <c-a>)"))
        toolbar.append(("", "   "))

        if thinking:
            toolbar.append(("ansiblue", "⋯ thinking: on"))
        else:
            toolbar.append(("#777777", "⋯ thinking: off"))

        toolbar.append(("", " "))
        toolbar.append(("#777777", "(toggle with <c-t>)"))

        self.shortcut_pressed = None

        user_input = self.session.prompt(
            HTML("<b><ansigreen>></ansigreen></b> "),
            bottom_toolbar=FormattedText(toolbar),
            style=self.style,
        )

        if self.shortcut_pressed:
            return self.shortcut_pressed
        else:
            assert isinstance(user_input, str)
            return user_input


class Shell:
    def __init__(
        self,
        prompt: Optional[str],
        loop: asyncio.AbstractEventLoop,
        input_handler: InputHandler,
        chat: Chat,
        connection_tracker: ConnectionTracker,
        environment: Environment,
    ) -> None:
        self.prompt = prompt
        self.loop = loop
        self.input_handler = input_handler
        self.chat = chat
        self.environment = environment
        self.stream_fut: Optional[Future[Any]] = None
        self.connection_tracker = connection_tracker

    def run(self) -> None:
        self._print_welcome_message()
        self._send_initial_prompt()

        while True:
            try:
                self._wait_for_stream_completion()
                text = self.input_handler.prompt(self.chat.autorun, self.chat.thinking)

                if text.startswith("/"):
                    self._run_command(text[1:].strip())
                elif text == "<c-y>":
                    self._confirm_execution()
                elif text == "<c-a>":
                    self._run_command("autorun")
                elif text == "<c-t>":
                    self._run_command("thinking")
                elif text in {"q", "exit"}:
                    print()
                    break
                elif text == "<c-d>":
                    print()
                    do_quit = ask_for_quit_confirmation()
                    print()

                    if do_quit:
                        break
                elif text:
                    print()
                    self._send_prompt(text)

            except KeyboardInterrupt:
                if self._handle_keyboard_interrupt():
                    break

            except ExponentError as e:
                self._print_error_message(e)
                break
            except RateLimitError as e:
                self._print_rate_limit_error_message(e)
                break

    def _handle_keyboard_interrupt(self) -> bool:
        try:
            if self.stream_fut is not None:
                self._run_coroutine(self.chat.halt_stream()).result()
                return True
            return ask_for_quit_confirmation()
        except KeyboardInterrupt:
            return True

    def _ensure_connected(self) -> None:
        if not self.connection_tracker.is_connected():
            self._run_coroutine(self._wait_for_reconnection()).result()

    async def _wait_for_reconnection(self) -> None:
        render([clear_line_seq(), "Disconnected..."])
        await asyncio.sleep(1)
        spinner = Spinner("Reconnecting...")
        spinner.show()
        await self.connection_tracker.wait_for_reconnection()
        spinner.hide()
        render([fg_color_seq(2), bold_seq(), "✓ Reconnected"])
        await asyncio.sleep(1)
        render([clear_line_seq()])

    def _print_welcome_message(self) -> None:
        print("Welcome to ✨ \x1b[1;32mExponent \x1b[4:3mSHELL\x1b[0m ✨")
        print()
        print("Type 'q', 'exit' or press <C-c> to exit")
        print("Enter '/help' to see a list of available commands")
        print()

    def _print_error_message(self, e: ExponentError) -> None:
        print(f"\n\n\x1b[1;31m{e}\x1b[0m")
        print("\x1b[3;33m")
        print("Reach out to team@exponent.run if you need support.")
        print("\x1b[0m")

    def _print_rate_limit_error_message(self, e: RateLimitError) -> None:
        print(f"\n\n\x1b[1;31m{e}\x1b[0m")
        print("\x1b[3;33m")
        print(
            "Visit https://www.exponent.run/settings to update your billing settings."
        )
        print("\x1b[0m")

    def _show_help(self) -> None:
        print()

        for command, description in SLASH_COMMANDS.items():
            print(f"{command} - {description}")

        print()

    def _run_command(self, command: str) -> None:
        parts = command.split(maxsplit=1)
        cmd = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        if cmd == "cmd":
            self._execute_shell_command(args)
        elif cmd == "help":
            self._show_help()
        elif cmd == "autorun":
            self._toggle_autorun()
        elif cmd == "thinking":
            self._toggle_thinking()
        elif cmd == "web":
            self._switch_cli_chat_to_web()
        elif cmd == "c" or cmd == "checkpoint":
            self._create_checkpoint()
        elif cmd == "r" or cmd == "rollback":
            self._checkpoint_rollback(args)
        else:
            print(f"\nUnknown command: /{command}\n")

    def _execute_shell_command(self, shell_command: str) -> None:
        if not shell_command:
            click.echo("\nError: Command command is empty. Usage: /cmd <command>\n")
            return

        self._ensure_connected()
        self.stream_fut = self._run_coroutine(
            self.chat.send_direct_action("shell", {"command": shell_command})
        )

    def _create_checkpoint(self) -> None:
        self._ensure_connected()
        self.stream_fut = self._run_coroutine(
            self.chat.send_direct_action("checkpoint", {"commitMessage": None})
        )

    def _checkpoint_rollback(self, args: str) -> None:
        self._ensure_connected()
        print()

        if not self.chat.checkpoints:
            print("No checkpoints to rollback to. Use /checkpoint to create one.\n")
            return

        choices = [
            questionary.Choice(
                title=f"{get_short_git_commit_hash(checkpoint['commitHash'])}: {checkpoint['commitMessage']}",
                value=index,
            )
            for index, checkpoint in enumerate(self.chat.checkpoints)
        ]
        checkpoint_index = questionary.select(
            "Chose a checkpoint to rollback to:",
            choices=choices,
            qmark="",
        ).ask()

        if checkpoint_index is None:
            print()
            return

        self.chat.checkpoints = self.chat.checkpoints[: checkpoint_index + 1]
        checkpoint_uuid = self.chat.checkpoints[-1]["eventUuid"]

        self.chat.parent_uuid = checkpoint_uuid
        self.stream_fut = self._run_coroutine(
            self.chat.send_direct_action(
                "rollback", {"checkpointCreatedEventUuid": checkpoint_uuid}
            )
        )

    def _toggle_autorun(self) -> None:
        self.chat.toggle_autorun()

        render(
            [
                "\r",
                move_cursor_up_seq(1),
                clear_line_seq(),
            ]
        )

    def _toggle_thinking(self) -> None:
        self.chat.toggle_thinking()

        render(
            [
                "\r",
                move_cursor_up_seq(1),
                clear_line_seq(),
            ]
        )

    def _switch_cli_chat_to_web(self) -> None:
        url = self.chat.url()
        print(f"\nThis chat has been moved to {url}\n")

        if not inside_ssh_session():
            launch_exponent_browser(
                self.environment, self.chat.base_url, self.chat.chat_uuid
            )

        while True:
            input()

    def _confirm_execution(self) -> None:
        render(
            [
                "\r",
                move_cursor_up_seq(1),
                clear_line_seq(),
            ]
        )

        # Check if we have a pending event to confirm
        if not self.chat.pending_event:
            print("\n(No pending event to confirm)\n")
            return

        # Debug: Add a marker so we know confirmation was triggered
        print(f"\n(Confirming {self.chat.pending_event['__typename']})\n")

        self._ensure_connected()
        self.stream_fut = self._run_coroutine(self.chat.send_confirmation())

    def _send_initial_prompt(self) -> None:
        if self.prompt is not None:
            self._send_prompt(self.prompt)

    def _send_prompt(self, text: str) -> None:
        self._ensure_connected()
        self.stream_fut = self._run_coroutine(self.chat.send_prompt(text))

    def _wait_for_stream_completion(self) -> None:
        if self.stream_fut is not None:
            self.stream_fut.result()
            self.stream_fut = None

    def _run_coroutine(self, coro: Coroutine[Any, Any, Any]) -> Future[Any]:
        return asyncio.run_coroutine_threadsafe(coro, self.loop)


class SlashCommandCompleter(Completer):
    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        text = document.text
        if text.startswith("/"):
            for command in SLASH_COMMANDS:
                if command.startswith(text):
                    yield Completion(command, start_position=-len(text))


class Buffer:
    def __init__(self, event_uuid: str) -> None:
        self.event_uuid = event_uuid


class NullBuffer(Buffer):
    def __init__(self) -> None:
        super().__init__("")


class CharBuffer(Buffer):
    def __init__(self, event_uuid: str) -> None:
        super().__init__(event_uuid)
        self.content_len = 0

    def render_new_chars(self, message: str) -> list[Any]:
        message = message.strip()
        chunk = message[self.content_len :]
        self.content_len = len(message)

        return [chunk]


class LineBuffer(Buffer):
    def __init__(self, event_uuid: str) -> None:
        super().__init__(event_uuid)
        self.line_count = 0

    def render_new_lines(
        self,
        code: str,
    ) -> list[Any]:
        seqs: list[Any] = []
        lines = code.split("\n")
        lines = lines[0 : len(lines) - 1]
        new_line_count = len(lines)

        if self.line_count > 0:
            seqs.append([move_cursor_up_seq(1), "\r"])
            lines = lines[self.line_count - 1 :]

        lines = [line + "\n" for line in lines]
        seqs.append(lines)
        self.line_count = new_line_count

        return seqs


# TODO maybe unify with LineBuffer?
class CommandBuffer(Buffer):
    def __init__(self, event_uuid: str) -> None:
        super().__init__(event_uuid)
        self.line_count = 0

    def render_new_lines(self, paths: list[Any]) -> list[Any]:
        seqs: list[Any] = []
        new_line_count = len(paths)

        if self.line_count > 0:
            seqs.append([move_cursor_up_seq(1), "\r"])
            paths = paths[self.line_count - 1 :]

        seqs.append(paths)
        self.line_count = new_line_count

        return seqs


def highlight_code(
    code: str, lang: str, line_numbers: bool = True, padding: tuple[int, int] = (0, 0)
) -> str:
    syntax = Syntax(
        code,
        lang,
        theme="monokai",
        line_numbers=line_numbers,
        word_wrap=True,
        padding=padding,
    )

    console = Console()

    with console.capture() as capture:
        console.print(syntax)

    return capture.get()


def generate_diff(before_lines: str, after_lines: str) -> str:
    diff = difflib.unified_diff(
        before_lines.split("\n"),
        after_lines.split("\n"),
        fromfile="before",
        tofile="after",
        lineterm="",
    )

    return "\n".join(list(diff)[2:])


def pad_left(text: str, padding: str) -> str:
    return "\n".join([padding + line for line in text.strip().split("\n")])


def fg_color_seq(c: int) -> str:
    return f"\x1b[{30 + c}m"


def bold_seq() -> str:
    return "\x1b[1m"


def not_bold_seq() -> str:
    return "\x1b[22m"


def block_header_bg_seq(theme: COLOR_THEMES = "default") -> str:
    if theme == "white_on_green":
        return "\x1b[48;5;22m"
    elif theme == "white_on_red":
        return "\x1b[48;5;131m"
    elif theme == "white_on_blue":
        return "\x1b[48;5;21m"
    else:
        return "\x1b[48;2;29;30;24m"


def block_header_fg_seq(theme: COLOR_THEMES = "default") -> str:
    if theme in ["white_on_green", "white_on_red", "white_on_blue"]:
        return "\x1b[38;5;231m"
    else:
        return "\x1b[38;5;246m"


def block_body_bg_seq() -> str:
    return "\x1b[48;5;235m"


def erase_line_seq() -> str:
    return "\x1b[2K"


def erase_display_seq() -> str:
    return "\x1b[0J"


def reset_attrs_seq() -> str:
    return "\x1b[0m"


def clear_line_seq() -> str:
    return f"\r{reset_attrs_seq()}{erase_line_seq()}"


def move_cursor_up_seq(n: int) -> str:
    if n > 0:
        return f"\x1b[{n}A"
    else:
        return ""


def move_cursor_down_seq(n: int) -> str:
    if n > 0:
        return f"\x1b[{n}B"
    else:
        return ""


def render(seqs: Union[str, list[Any], None]) -> None:
    print(collect(seqs), end="")
    sys.stdout.flush()


def collect(seqs: Union[str, list[Any], None]) -> str:
    if seqs is None:
        return ""

    if isinstance(seqs, str):
        return seqs

    assert isinstance(seqs, list)

    text = ""

    for seq in seqs:
        text += collect(seq)

    return text
