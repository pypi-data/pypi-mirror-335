import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Coroutine, Dict, List, Optional, Tuple, cast

import typer
from litellm import (
    ChatCompletionMessageToolCall,
    CustomStreamWrapper,
    Message,
    ModelResponse,
    Usage,
    completion,
    stream_chunk_builder,
    supports_function_calling,
)
from mcp import Tool
from mcp.types import CreateMessageRequestParams, CreateMessageResult, TextContent
from openai.types.chat import ChatCompletionToolMessageParam, ChatCompletion
from rich.live import Live
from rich.padding import Padding
from rich.spinner import Spinner
from rich.text import Text
from typing_extensions import Annotated

from opencodr.app_meta import get_opencoder_dir
from opencodr.async_typer import AsyncTyper
from opencodr.config import OpenCoderConfig
from opencodr.console import console
from opencodr.display import (
    display_history,
    edit_msg,
    multiline_prompt,
    rich_message,
    rich_tool_tree_live,
    role_styles,
    rewind_cmd_rgx,
)
from opencodr.mcp_client import Server
from opencodr.types import ToolCallError


class Agent:
    app: AsyncTyper
    messages: List[Message]
    usage: List[Usage]
    conf: OpenCoderConfig
    curr_depth: int = 0
    curr_tokens: int = 0
    tools: List[Tuple[Tool, Server]]
    tool_input_schemas: List[Dict[str, Any]]
    mcp_servers: List[Server]
    allow_tool_use: bool

    SYSTEM_MESSAGE_TEMPLATE = """You are a senior software engineering assistant"""
    REPROMPT_MESSAGE_TEMPLATE = "decide what to do next."

    def __init__(
        self,
        conf: OpenCoderConfig,
        messages: Optional[List[Message]] = None,
        mcp_servers: List[Server] = [],
    ):
        if conf is None:
            raise ValueError("config required")

        self.usage = []
        self.tools = []
        self.tool_input_schemas = []

        self.mcp_servers = mcp_servers

        self.conf = conf

        self.allow_tool_use = supports_function_calling(model=self.conf.OC_MODEL)

        system_message = self.SYSTEM_MESSAGE_TEMPLATE

        opencoder_dir = get_opencoder_dir()

        if opencoder_dir:
            for filename in os.listdir(opencoder_dir):
                if filename.lower() == "system.txt":
                    system_path = os.path.join(opencoder_dir, filename)
                    with open(system_path, "r", encoding="utf-8") as file:
                        system_message = file.read().strip()
                    break
                if filename.lower() == "reprompt.txt":
                    reprompt_path = os.path.join(opencoder_dir, filename)
                    with open(reprompt_path, "r", encoding="utf-8") as file:
                        self.REPROMPT_MESSAGE_TEMPLATE = file.read().strip()
                    break

        if messages is None:
            self.messages = [Message(role="system", content=system_message)]  # type: ignore
        else:
            self.messages = messages

        self.app = AsyncTyper()
        self.app.command(name="gen")(self.generate_cmd)

    async def cleanup_servers(self) -> None:
        for server in self.mcp_servers:
            await server.cleanup()

    async def exec_tool_call(
        self,
        tool_call: ChatCompletionMessageToolCall,
        progress_cb=None,
    ) -> ChatCompletionToolMessageParam:
        time.sleep(1)
        try:
            parsed_arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            raise ToolCallError(
                ChatCompletionToolMessageParam(
                    role="tool", tool_call_id=tool_call.id, content=str(e)
                )
            )

        (tool, server) = next(
            ((t, s) for (t, s) in self.tools if t.name == tool_call.function.name),
            (None, None),
        )

        if not tool or not server:
            raise ToolCallError(
                ChatCompletionToolMessageParam(
                    role="tool", tool_call_id=tool_call.id, content="Tool not found."
                )
            )

        try:
            result = await server.execute_tool(tool.name, parsed_arguments)
            if result is None:
                raise ToolCallError(
                    ChatCompletionToolMessageParam(
                        role="tool",
                        tool_call_id=tool_call.id,
                        content="Result is None",
                    )
                )

            # if isinstance(result, dict) and "progress" in result:
            #     progress = result["progress"]
            #     total = result["total"]

            tool_completion = ChatCompletionToolMessageParam(
                role="tool",
                tool_call_id=tool_call.id,
                content=(
                    "\n".join(
                        [
                            c.text if isinstance(c, TextContent) else ""
                            for c in result.content
                        ]
                    )
                ),
            )

            if result.isError:
                raise ToolCallError(tool_completion)

            return tool_completion
        except Exception as e:
            raise ToolCallError(
                ChatCompletionToolMessageParam(
                    role="tool", tool_call_id=tool_call.id, content=str(e)
                )
            )

    async def generate(self, prompt: Optional[str] = None):
        if not self.check_circuit_breakers():
            return

        if prompt is None:
            prompt = await self.handle_user_input()
            if prompt is None:
                return

        self.messages.append(Message(role="user", content=prompt))  # type: ignore

        response = await self.handle_stream_completion()

        if (
            self.allow_tool_use
            and isinstance(response, ChatCompletion)
            and response.choices[0].message.tool_calls
        ):
            tool_call_messages = await self.process_tool_calls(response)

            if len(tool_call_messages) > 0:
                self.messages.extend(tool_call_messages)

            self.curr_depth += 1

            reprompt = self.REPROMPT_MESSAGE_TEMPLATE
            console.print(rich_message(role="user", content=reprompt))

            await self.generate(prompt=reprompt)
        else:
            return await self.generate(prompt=None)

    def check_circuit_breakers(self) -> bool:
        if (
            self.conf.OC_MAX_DEPTH is not None
            and self.curr_depth >= self.conf.OC_MAX_DEPTH
        ):
            console.print("⛔️ [red]MAX DEPTH REACHED[/red]")
            return False

        if (
            self.conf.OC_MAX_TOKENS is not None
            and self.curr_tokens >= self.conf.OC_MAX_TOKENS
        ):
            console.print("⛔️ [red]MAX TOKENS EXCEEDED[/red]")
            return False

        return True

    async def handle_user_input(self) -> Optional[str]:
        console.print(Text(text="user:", style=role_styles["user"]))
        prompt = multiline_prompt()

        if prompt and prompt.lower() == "quit":
            sys.stdout.write("\033[A\033[K")
            sys.stdout.write("\033[A\033[K")
            return None

        match = re.match(rewind_cmd_rgx, prompt)

        if match:
            prefix, offset = match.groups()
            if prefix == "e-":
                await self.handle_rewind(int(offset), edit=True)
            else:
                await self.handle_rewind(int(offset), edit=False)
            return None

        return prompt

    async def handle_rewind(self, offset: int, edit=False) -> None:
        console.clear()
        offset = min(offset, len(self.messages))
        messages_to_remove = self.messages[-offset:]
        tool_call_ids_to_remove = set()
        last_msg = self.messages[-offset]

        if edit and last_msg.tool_calls is None:
            updated_msg_content = None
            model_extra = last_msg.model_extra or {}
            # do not allow editing of tool call responses
            if model_extra.get("tool_call_id") is None:
                updated_msg_content = edit_msg(self.messages[-offset].content)
                self.messages[-offset].content = updated_msg_content

            if offset > 1:
                display_history(self.messages[: -(offset - 1)])
                self.messages = self.messages[:-offset]
            else:
                display_history(self.messages)
                if last_msg.role == "user":
                    self.messages = self.messages[:-offset]

            await self.generate(
                prompt=updated_msg_content if last_msg.role == "user" else None
            )
        else:
            for message in messages_to_remove:
                model_extra = message.model_extra or {}
                tool_call_id = model_extra.get("tool_call_id")
                if tool_call_id:
                    tool_call_ids_to_remove.add(tool_call_id)

            for message in reversed(self.messages[:-offset]):
                if message.tool_calls:
                    message.tool_calls = [
                        tool_call
                        for tool_call in message.tool_calls
                        if tool_call.id not in tool_call_ids_to_remove
                    ]
                    if not message.tool_calls:
                        offset += 1
                        break

            self.messages = self.messages[:-offset]
            display_history(self.messages)

            await self.generate(prompt=None)

    async def handle_stream_completion(self) -> ModelResponse:
        chunks = []
        msg = ""

        with Live(
            Padding(Spinner(name="point"), (0, 0, 0, 2)),
            refresh_per_second=4,
        ) as live:
            s_response: CustomStreamWrapper = completion(
                stream=True,
                model=self.conf.OC_MODEL,
                tools=(
                    [
                        {
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description,
                                "parameters": tool.inputSchema,
                            },
                        }
                        for (tool, _) in self.tools
                    ]
                    if self.allow_tool_use
                    else None
                ),
                tool_choice="auto" if self.allow_tool_use else None,
                messages=self.messages,
            )

            for chunk in s_response:
                # Proper null checking for delta.content
                content_delta = chunk.choices[0].delta.content or ""
                msg += content_delta
                live.update(rich_message(role="assistant", content=msg))
                chunks.append(chunk)

            live.stop()

        response = cast(
            ModelResponse, stream_chunk_builder(chunks, messages=self.messages)
        )

        if hasattr(response.choices[0], "message"):
            self.messages.append(response.choices[0].message)

        if hasattr(response, "usage"):
            self.usage.append(response.usage)
            self.curr_tokens += response.usage.total_tokens

        return response

    async def process_tool_calls(self, response: ModelResponse) -> List[Message]:
        if (
            not hasattr(response.choices[0], "message")
            or not response.choices[0].message.tool_calls
        ):
            return []

        message = response.choices[0].message
        tool_calls = message.tool_calls or []

        tool_call_tasks: Dict[
            Tuple[str, str], Coroutine[Any, Any, ChatCompletionToolMessageParam]
        ] = {}

        for tool_call in tool_calls:
            if tool_call.function and tool_call.function.name and tool_call.id:
                tool_call_tasks[(tool_call.function.name, tool_call.id)] = (
                    self.exec_tool_call(tool_call)
                )

        return await rich_tool_tree_live(tool_call_tasks)

    async def sampling_callback(
        self,
        create_msg_params: CreateMessageRequestParams,
    ) -> CreateMessageResult:
        messages = []
        for m in create_msg_params.messages:
            messages.append(Message(role="assistant", content=m.content))  # type: ignore

        if create_msg_params.systemPrompt:
            messages = [
                Message(role="system", content=create_msg_params.systemPrompt)  # type: ignore
            ] + messages

        response = completion(
            stream=False,
            model=self.conf.OC_MODEL,
            messages=messages,
        )

        return CreateMessageResult(
            role="assistant",
            content=TextContent(
                type="text",
                text=response.choices[0].message.content,
            ),
            model=self.conf.OC_MODEL,
            stopReason="endTurn",
        )

    async def generate_cmd(
        self,
        f: Annotated[
            Optional[str], typer.Option("--f", help="Load prompt from file")
        ] = None,
    ):
        prompt: Optional[str] = None
        if f:
            file_path = Path(f)
            if file_path.exists() and file_path.suffix in {".txt", ".md"}:
                prompt = file_path.read_text(encoding="utf-8").strip()
            else:
                console.print(
                    "👎 [red]Invalid file path or unsupported format. Please provide a valid path to a .txt or .md file.[/red]"
                )
                return

        try:
            for server in self.mcp_servers:
                await server.initialize(sampling_callback=self.sampling_callback)
                self.tools.extend(
                    [(tool, server) for tool in await server.list_tools()]
                )

            console.print(
                rich_message(role="system", content=self.SYSTEM_MESSAGE_TEMPLATE)
            )
            await self.generate(prompt=prompt)
        except Exception as e:
            console.print(f"🤯 [red]{type(e).__name__}[/red]\n{e}")
            await self.cleanup_servers()
        finally:
            await self.cleanup_servers()
