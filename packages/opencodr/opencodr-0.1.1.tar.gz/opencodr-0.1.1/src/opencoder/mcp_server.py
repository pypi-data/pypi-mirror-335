import logging
import os
import subprocess
from pathlib import Path
from typing import List, Optional

from mcp.server.fastmcp import FastMCP

debug_env = os.getenv("DEBUG", "0")

if debug_env == "0":
    logging.getLogger("mcp.server.lowlevel.server").disabled = True
else:
    logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.DEBUG)

OC_PATH = os.environ.get("OC_PATH", str(Path.cwd())).split(":")
ALLOWED_GIT_CMDS = {"status", "log", "branch", "commit", "diff", "pull", "rev-parse"}


def validate_path(path: str) -> str:
    """Ensure the requested path is within allowed directories."""
    abs_path = os.path.abspath(path)
    if not any(abs_path.startswith(os.path.abspath(d)) for d in OC_PATH):
        raise ValueError("Access to this path is not allowed.")
    return abs_path


mcp = FastMCP("FileEditor")


@mcp.tool()
async def read_file(path: str) -> str:
    """Read a file and return its content with line numbers"""
    try:
        validated_path = validate_path(path)
        result = subprocess.run(
            ["cat", "-n", validated_path], capture_output=True, text=True
        )
        if result.returncode != 0:
            return f"Error:\n{result.stderr}"
        return result.stdout
    except Exception as e:
        return f"Error:\n{str(e)}"


@mcp.tool()
async def edit_file(
    path: str, start_line: int, new_text: str, end_line: Optional[int] = None
) -> str:
    """Edit a file using 'ed', given a start and end line."""
    try:
        validated_path = validate_path(path)

        if end_line is None:
            end_line = start_line

        commands = [
            f"{start_line},{end_line}d",  # Delete lines in the range [start_line, end_line]
            f"{start_line}i",  # Insert new text starting at start_line
            new_text,  # Insert the new text
            ".",  # End of input to 'ed'
            "w",  # Write changes to file
            "q",  # Quit the editor
        ]

        result = subprocess.run(
            ["ed", validated_path],
            input="\n".join(commands),
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return f"Error: {result.stderr}"

        return await read_file(path=validated_path)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def git(command: str, args: Optional[List[str]] = None) -> str:
    """Execute a whitelisted git command using subprocess."""
    try:
        if command.startswith("git "):
            command = command[4:]

        if command not in ALLOWED_GIT_CMDS:
            return f"Error: Command '{command}' is not whitelisted."

        git_command = ["git", command]
        if args:
            git_command.extend(args)

        result = subprocess.run(
            git_command,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return f"Error: {result.stderr}"

        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    mcp.run()


if __name__ == "__main__":
    main()
