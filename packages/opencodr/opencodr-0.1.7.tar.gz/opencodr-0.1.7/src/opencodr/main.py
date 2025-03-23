import os
import sys
from pathlib import Path

import debugpy  # type: ignore
import typer

from opencodr.agent import Agent
from opencodr.app_meta import app_name, get_opencoder_dir
from opencodr.config import MCPServersConfig, OpenCoderConfig
from opencodr.mcp_client import Server
from opencodr.workspace import Workspace

if os.getenv("DEBUG") == "1":
    print("Waiting for debugger attach")
    debugpy.wait_for_client()

app = typer.Typer()

CONF_TMPL = """# List of allowed directories, Separated with colons (:) e.g "/path/to/a/dir:/path/to/b/dir"
export OC_PATH="$(pwd)"

# <provider>/<model_name>
export OC_MODEL=""

# export OC_BASE_URL=""
# export OC_MAX_TOKENS=""
# export OC_MAX_DEPTH=""

# Provider API Keys
export OPENROUTER_API_KEY=""
# export OPENAI_API_KEY=""
# export ANTHROPIC_API_KEY=""
"""


def init():
    project_dir = Path(os.getcwd()) / f".{app_name}"
    project_dir.mkdir(parents=True, exist_ok=True)

    env_file_path = project_dir / ".rc"

    if not env_file_path.exists():
        env_content = CONF_TMPL

        with open(env_file_path, "w") as env_file:
            env_file.write(env_content)

        typer.echo(f"📄 .rc file generated at {env_file_path}")
    else:
        typer.echo(f"📄 .rc file already exists at {env_file_path}")

    cwd = os.getcwd()
    gitignore_path = os.path.join(cwd, ".gitignore")

    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r+") as gitignore_file:
            gitignore_content = gitignore_file.read()

            if f".{app_name}" not in gitignore_content:
                gitignore_file.write(f"\n.{app_name}\n")
                typer.echo(f"✔️ .{app_name} added to .gitignore")
    else:
        typer.echo(
            f"⚠️ No .gitignore file found in the current directory. Remember to add .{app_name} to .gitignore manually."
        )


def main():
    project_dir = get_opencoder_dir()

    if project_dir is None and (len(sys.argv) < 2 or sys.argv[1] != "init"):
        return typer.echo("✋ opencodr project not initialized. Run `opencodr init`")

    if project_dir is None and (len(sys.argv) == 2 and sys.argv[1] == "init"):
        return init()

    opencoder_config_file_path = project_dir / ".rc"

    mcp_servers_config_file = project_dir / "mcp.json"
    mcp_server_configs = MCPServersConfig.load_from_json(mcp_servers_config_file)
    mcp_servers = [
        Server(name, srv_config) for name, srv_config in mcp_server_configs.items()
    ]

    conf = OpenCoderConfig.load_from_rc(opencoder_config_file_path)

    agent = Agent(conf, mcp_servers=mcp_servers)
    app.add_typer(agent.app, name=None)

    if os.getenv("WORKSPACE") != "1":
        wks = Workspace()
        app.add_typer(wks.app, name="workspace")

    app()
