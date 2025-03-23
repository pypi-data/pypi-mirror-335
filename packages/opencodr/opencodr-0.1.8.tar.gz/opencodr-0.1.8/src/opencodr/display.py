import asyncio
import re
import subprocess
import sys
import tempfile
from typing import Any, Coroutine, Dict, List, Optional, Tuple

from litellm import Message, Usage
from openai.types.chat import ChatCompletionToolMessageParam
from rich.console import Group
from rich.live import Live
from rich.markdown import Markdown
from rich.padding import Padding
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text
from rich.tree import Tree

from opencodr.console import console
from opencodr.types import ToolCallError

rewind_cmd_rgx = r"^(e-|\-)(\d+)$"


def edit_msg(text):
    with tempfile.NamedTemporaryFile(suffix=".tmp", mode="w+", delete=False) as tmpfile:
        tmpfile_path = tmpfile.name
        tmpfile.write(text)

    subprocess.run(["vim", tmpfile_path])

    with open(tmpfile_path, "r") as f:
        content = f.read()

    return content


def multiline_prompt(end_marker: str = "EOF") -> str:
    lines = []

    while True:
        line = input("  > ")
        if re.match(rewind_cmd_rgx, line.strip()):
            return line.strip()
        if line.strip().lower() == end_marker.lower():
            sys.stdout.write("\033[A\033[K")
            break
        lines.append(line)

    return "\n".join(lines)


def truncate_lines(output: str, max_lines=25) -> str:
    lines = output.splitlines()
    if len(lines) > max_lines:
        truncated_output = (
            "\n".join(lines[:max_lines]) + f"\n\n+{len(lines) - max_lines} more lines"
        )
        return truncated_output
    return output


role_styles = {
    "system": "bold reverse green",
    "user": "bold reverse blue",
    "assistant": "bold reverse magenta",
    "tool": "bold reverse bright_black",
}


def rich_message(role: str, content: str, usage: Optional[Usage] = None):
    return Group(
        Text(
            f"{role}:",
            style=f"{role_styles[role]}",
        ),
        Padding(
            Markdown(content),
            (
                0,
                0,
                0,
                2,
            ),
        ),
    )


async def rich_tool_tree_live(
    tool_calls: Dict[
        Tuple[str, str], Coroutine[Any, Any, ChatCompletionToolMessageParam]
    ],
) -> List[Message]:
    tool_tree = Tree(":pick: tools")
    tool_nodes = {}
    messages: List[Message] = []

    with Live(Group(Padding(tool_tree, (0, 0, 0, 2))), refresh_per_second=4) as live:
        for (tool_name, tool_call_id), _ in tool_calls.items():
            node = tool_tree.add(
                Spinner(name="point", text=f"[yellow]{tool_name}[/yellow]")
            )
            tool_nodes[(tool_name, tool_call_id)] = node

        async def process_tool_call(tool_name, tool_call_id, exec_task):
            node = tool_nodes[(tool_name, tool_call_id)]
            try:
                result = await exec_task
                node.label = f":green_circle: [green]{tool_name}[/green]"
                node.add(Panel(Markdown(truncate_lines(result["content"]))))
                messages.append(Message(**result))
            except ToolCallError as e:
                node.label = f":red_circle: [red]{tool_name}[/red]"
                node.add(Panel(Markdown(truncate_lines(e.tool_message["content"]))))
                messages.append(Message(**e.tool_message))
            live.update(tool_tree)

        await asyncio.gather(
            *(
                process_tool_call(tool_name, tool_call_id, exec_task)
                for (tool_name, tool_call_id), exec_task in tool_calls.items()
            )
        )

    return messages


def rich_tool_tree(tool_completions: List[Tuple[str | None, str]]):
    tool_tree = Tree(":pick: tools")
    for tool_name, tool_output in tool_completions:
        node = tool_tree.add(f":white_circle: [green]{tool_name}[/green]")
        if tool_output:
            node.add(Panel(truncate_lines(tool_output)))
    return Group(Padding(tool_tree, (0, 0, 0, 2)))


def display_history(messages: List[Message]):
    for i, message in enumerate(messages):
        if hasattr(message, "tool_call_id"):
            continue
        if message.tool_calls:
            tool_output = []

            for tool_call in message.tool_calls:
                output = ""
                for subsequent_message in messages[i + 1 :]:
                    if (
                        getattr(subsequent_message, "tool_call_id", None)
                        == tool_call.id
                    ):
                        if subsequent_message.content:
                            output = subsequent_message.content
                        break
                tool_output.append((tool_call.function.name, output))

            if message.content:
                console.print(rich_message(role=message.role, content=message.content))
            console.print(rich_tool_tree(tool_output))
        if message.tool_calls is None:
            console.print(
                rich_message(
                    role=message.role,
                    content=message.content if message.content else "",
                )
            )
