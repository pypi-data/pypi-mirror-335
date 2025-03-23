import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict


class OpenCoderConfig(BaseModel):
    OC_MAX_TOKENS: Optional[int] = None
    OC_MAX_DEPTH: Optional[int] = None
    OC_BASE_URL: Optional[str] = None
    OC_MODEL: str

    model_config = ConfigDict(extra="allow")

    @classmethod
    def load_from_rc(cls, file_path: Path):
        conf = dotenv_values(file_path)

        command = f"bash -c 'source {file_path} && env'"
        result = subprocess.run(
            command, shell=True, executable="/bin/bash", text=True, capture_output=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to source {file_path}: {result.stderr}")

        env_vars = {}
        for line in result.stdout.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                if key in conf:
                    env_vars[key] = value
                if not os.environ.get(key) and key in conf:
                    os.environ[key] = value

        return cls.model_validate(env_vars)


class MCPServerConfig(BaseModel):
    command: str
    args: List[str]
    env: Optional[Dict[str, Any]] = None


class MCPServersConfig(BaseModel):
    @classmethod
    def load_from_json(cls, file_path: Path) -> Dict[str, MCPServerConfig]:
        if not file_path.exists():
            raw_data = {}

        else:
            with open(file_path, "r") as f:
                raw_data = json.load(f)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        mcp_server_path = os.path.join(current_dir, "mcp_server.py")
        raw_data["shell"] = {
            "command": "python",
            "args": [mcp_server_path],
        }

        return {key: MCPServerConfig(**value) for key, value in raw_data.items()}
