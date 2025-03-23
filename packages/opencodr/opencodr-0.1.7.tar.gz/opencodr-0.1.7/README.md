<div align="center"  id="readme-top">
  <a>
    <img src="https://raw.githubusercontent.com/notpolomarco/opencodr/main/images/logo.svg" alt="Logo" width="120" height="80">
  </a>
  <p align="center">
    Open source coding agent in your terminal
    <br />
    &middot;
    <a href="https://github.com/notpolomarco/opencodr/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/notpolomarco/opencodr/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#initialization">Initialization</a></li>
        <li><a href="#configuration">Configuration</a></li>
      </ul>
    </li>
    <li>
    <a href="#usage">Usage</a>
    <ul>
        <li><a href="#generate">Generate</a></li>
        <li><a href="#workspace">Workspace</a></li>
      </ul>
    </li>
    <li><a href="#contributing">Contributing</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

<p align="">
<img src="https://github.com/notpolomarco/opencodr/raw/main/images/mascot.jpeg" alt="Product Name Screen Shot" width="250" height="250">
</p>

<div align="">

`opencodr` is a simple recursive function combined with the [Function Calling API](https://docs.litellm.ai/docs/completion/function_call) + [Model Context Protocol](https://modelcontextprotocol.io/introduction) to create agentic behavior.

- ❌ No Auth Screens
- ❌ No Provider Lock-in

API Key(s) + A Terminal Is All You Need™️

</div>

## Built With

[![LiteLLM](https://img.shields.io/badge/%F0%9F%9A%85_litellm-lightblue?style=for-the-badge&link=https%3A%2F%2Fdocs.litellm.ai%2F)](https://docs.litellm.ai/)

[![Pydantic v2](https://img.shields.io/endpoint?style=for-the-badge&url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)

[![Typer][typer-logo]](https://typer.tiangolo.com/)

[![Rich][rich-logo]](https://rich.readthedocs.io/en/stable/introduction.html)

[![Docker](https://img.shields.io/badge/Docker-blue?logo=docker&logoColor=fff&style=for-the-badge)](https://docs.docker.com/)

<!-- GETTING STARTED -->

## Getting Started

### Prerequisites

- [Python>=3.13](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/get-started/) (Optional but _highly_ recommended)

### Installation

```
> MacBookPro:example user$ pip install opencodr
```

```
> MacBookPro:example user$ opencodr init opencodr --help

✋ opencodr project not initialized. Run `opencodr init`
```

### Initialization

Run the following command from the **root** of your project:

```
> MacBookPro:example user$ opencodr init

📄 .rc file generated at /workspace/example/.opencodr/.rc
✔️ .opencodr added to .gitignore
```

```
> MacBookPro:example user$ opencodr --help

 Usage: opencodr [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the     │
│                               current shell.                 │
│ --show-completion             Show completion for the        │
│                               current shell, to copy it or   │
│                               customize the installation.    │
│ --help                        Show this message and exit.    │
╰──────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────╮
│ gen                                                          │
│ workspace                                                    │
╰──────────────────────────────────────────────────────────────╯
```

### Configuration

`/workspace/example/.opencodr/.rc`

```bash
# List of allowed directories, Separated with colons (:) e.g "/path/to/a/dir:/path/to/b/dir"
export OC_PATH="$(pwd)"

# <provider>/<model_name>
export OC_MODEL="openrouter/openai/gpt-4o"

# export OC_BASE_URL=""
# export OC_MAX_TOKENS=""
# export OC_MAX_DEPTH=""

# Provider API Keys
export OPENROUTER_API_KEY=""
# export OPENAI_API_KEY=""
# export ANTHROPIC_API_KEY=""
```

> **_NOTE:_** See [https://docs.litellm.ai/docs/providers](https://docs.litellm.ai/docs/providers) for the list of supported models

`/workspace/example/.opencodr/mcp.json` _(Optional)_

```json
{
  "sqlite": {
    "command": "uvx",
    "args": ["mcp-server-sqlite", "--db-path", "./test.db"]
  },
  "puppeteer": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
  }
}
```

Prompt Overrides _(Optional)_

`/workspace/example/.opencodr/SYSTEM.txt`

`/workspace/example/.opencodr/REPROMPT.txt`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

### generate

```
> MacBookPro:example user$ opencodr gen --help

 Usage: opencodr gen [OPTIONS]

╭─ Options ────────────────────────────────────────────────────╮
│ --f           TEXT  Load prompt from file [default: None]    │
│ --help              Show this message and exit.              │
╰──────────────────────────────────────────────────────────────╯
```

### workspace

> **_NOTE:_** Requires Docker

```
> MacBookPro:example user$ opencodr workspace --help

 Usage: opencodr workspace [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                  │
╰──────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────╮
│ create   Creates a docker image to sandbox the agent         │
│ start    Shortcut to start the container                     │
│ stop     Shortcut to stop the container                      │
╰──────────────────────────────────────────────────────────────╯
```

# Contributing

### Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### Repo Setup

```bash
git clone https://github.com/notpolomarco/opencodr.git
cd opencodr
```

### Create Virtual Environment

```bash
uv venv
source .venv/bin/activate
```

### Install

```bash
uv pip install -e ".[dev]"
pre-commit install
pre-commit install --hook-type pre-push
```

> _*NOTE*_: to test any new features in workspace mode, build the base image from `/opencodr/dockerfile.dev`
```bash
uv build
docker build -t opencodr/base -f dockerfile.dev .
```


[rich-logo]: https://img.shields.io/badge/rich-white?style=for-the-badge
[typer-logo]: https://img.shields.io/badge/typer-black?style=for-the-badge&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8%2BCjxzdmcKICAgaWQ9InN2ZzgiCiAgIHZlcnNpb249IjEuMSIKICAgdmlld0JveD0iMCAwIDE1OC43NSAxMTAuNTA5MzIiCiAgIGhlaWdodD0iMTEwLjUwOTMybW0iCiAgIHdpZHRoPSIxNTguNzVtbSIKICAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogICB4bWxuczpzdmc9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogICB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiCiAgIHhtbG5zOmNjPSJodHRwOi8vY3JlYXRpdmVjb21tb25zLm9yZy9ucyMiCiAgIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyI%2BCiAgPGRlZnMKICAgICBpZD0iZGVmczIiIC8%2BCiAgPG1ldGFkYXRhCiAgICAgaWQ9Im1ldGFkYXRhNSI%2BCiAgICA8cmRmOlJERj4KICAgICAgPGNjOldvcmsKICAgICAgICAgcmRmOmFib3V0PSIiPgogICAgICAgIDxkYzpmb3JtYXQ%2BaW1hZ2Uvc3ZnK3htbDwvZGM6Zm9ybWF0PgogICAgICAgIDxkYzp0eXBlCiAgICAgICAgICAgcmRmOnJlc291cmNlPSJodHRwOi8vcHVybC5vcmcvZGMvZGNtaXR5cGUvU3RpbGxJbWFnZSIgLz4KICAgICAgPC9jYzpXb3JrPgogICAgPC9yZGY6UkRGPgogIDwvbWV0YWRhdGE%2BCiAgPHJlY3QKICAgICB5PSItNjAuNDk0ODgxIgogICAgIHg9Ii01Ny4yNDkzNCIKICAgICBoZWlnaHQ9IjIzNy4yOTk3MSIKICAgICB3aWR0aD0iNTkxLjE2ODk1IgogICAgIGlkPSJyZWN0ODI0IgogICAgIHN0eWxlPSJvcGFjaXR5OjAuOTg7ZmlsbDpub25lO2ZpbGwtb3BhY2l0eToxO3N0cm9rZS13aWR0aDowLjQyOTY1NCIgLz4KICA8ZwogICAgIGlkPSJnODE4IgogICAgIHRyYW5zZm9ybT0idHJhbnNsYXRlKC02Mi41OTM3NjQsLTYwLjQ5NDg4MSkiPgogICAgPGcKICAgICAgIGlkPSJnMTgiCiAgICAgICB0cmFuc2Zvcm09Im1hdHJpeCgwLjk1MDEyNzY3LDAsMCwwLjk1MDEyNzY3LDYuNzk3MzUxOCwzLjAxNzAyMDgpIj4KICAgICAgPHJlY3QKICAgICAgICAgc3R5bGU9ImZpbGw6I2ZmZmZmZjtmaWxsLW9wYWNpdHk6MTtzdHJva2U6bm9uZTtzdHJva2Utd2lkdGg6MS4xODM5OSIKICAgICAgICAgaWQ9InJlY3QxNyIKICAgICAgICAgd2lkdGg9IjE2Ny4wODI4MSIKICAgICAgICAgaGVpZ2h0PSIxMTYuMzA5OTciCiAgICAgICAgIHg9IjU4LjcyNTE3NCIKICAgICAgICAgeT0iNjAuNDk0ODgxIgogICAgICAgICByeT0iMTIuMDAwNDQ3IiAvPgogICAgICA8cmVjdAogICAgICAgICBzdHlsZT0iZmlsbDojMDAwMDAwO2ZpbGwtb3BhY2l0eToxO3N0cm9rZTpub25lO3N0cm9rZS13aWR0aDoxLjA0OTI5IgogICAgICAgICBpZD0icmVjdDE3LTMiCiAgICAgICAgIHdpZHRoPSIxNTEuNTExODkiCiAgICAgICAgIGhlaWdodD0iMTAwLjczOTE0IgogICAgICAgICB4PSI2Ni41MTA2MzUiCiAgICAgICAgIHk9IjY4LjI4MDI4MSIKICAgICAgICAgcnk9IjEwLjM5MzkwNSIgLz4KICAgICAgPHBhdGgKICAgICAgICAgc3R5bGU9ImZvbnQtd2VpZ2h0OmJvbGQ7Zm9udC1zaXplOjE2LjkzMzNweDtmb250LWZhbWlseTonVWJ1bnR1IE1vbm8nOy1pbmtzY2FwZS1mb250LXNwZWNpZmljYXRpb246J1VidW50dSBNb25vIEJvbGQnO2ZpbGw6I2ZmZmZmZjtzdHJva2Utd2lkdGg6MS4zMTE0MiIKICAgICAgICAgZD0ibSAxMjQuNTIwMTksMTA0LjA5Njc5IHYgNC4wNTc0MSBhIDMuMTc1LDMuMTc1IDEzNSAwIDEgLTMuMTc1LDMuMTc1IGwgLTcuMzMwNzEsMCBhIDMuMTc1LDMuMTc1IDEzNSAwIDAgLTMuMTc1LDMuMTc1IGwgMCwyMS43MDk4OSBhIDMuMTc1LDMuMTc1IDEzNSAwIDEgLTMuMTc1LDMuMTc1IGggLTQuMDU3NDEgYSAzLjE3NSwzLjE3NSA0NSAwIDEgLTMuMTc1LC0zLjE3NSBsIDAsLTIxLjcwOTg5IGEgMy4xNzUsMy4xNzUgNDUgMCAwIC0zLjE3NSwtMy4xNzUgaCAtNy4zMzA3MTcgYSAzLjE3NSwzLjE3NSA0NSAwIDEgLTMuMTc1LC0zLjE3NSB2IC00LjA1NzQxIGEgMy4xNzUsMy4xNzUgMTM1IDAgMSAzLjE3NSwtMy4xNzUgaCAzMS40MTg4MzcgYSAzLjE3NSwzLjE3NSA0NSAwIDEgMy4xNzUsMy4xNzUgeiIKICAgICAgICAgaWQ9InRleHQxLTktMC00LTktMi05LTgtMy04LTEtNy02IgogICAgICAgICBhcmlhLWxhYmVsPSJUIgogICAgICAgICB0cmFuc2Zvcm09Im1hdHJpeCgxLjQ5NjEzMzksMCwwLDEuNDk2MTMzOSw3LjU1OTY5NDMsLTYxLjExODY2NikiIC8%2BCiAgICAgIDxwYXRoCiAgICAgICAgIHN0eWxlPSJjb2xvcjojMDAwMDAwOy1pbmtzY2FwZS1mb250LXNwZWNpZmljYXRpb246J1VidW50dSBNb25vIEJvbGQnO2ZpbGw6I2ZmZmZmZjstaW5rc2NhcGUtc3Ryb2tlOm5vbmUiCiAgICAgICAgIGQ9Im0gLTMwMy4wMjU0Nyw5MzcuMDk3OTcgMTQuMDcyNDIsMjEuNDgzNzQgYSA1LjI0NzI4MzIsNS4yNDcyODMyIDkwLjAxODg5IDAgMSAtMC4wMDIsNS43NTMzIGwgLTE0LjA3MjUyLDIxLjQ1MzAyIGEgMS44NTczMDc1LDEuODU3MzA3NSA2MS42MzE4MjQgMCAwIDEuNTUyOTksMi44NzYwMyBsIDkuOTMxMzgsMCBhIDYuMzA1NzM4NSw2LjMwNTczODUgMTUxLjM4ODkxIDAgMCA1LjMwMTcxLC0yLjg5MTkyIGwgMTMuNzkzMzIsLTIxLjQyMTI0IGEgNS4zNDUyODQ1LDUuMzQ1Mjg0NSA5MC4wMTczNTggMCAwIDAuMDAyLC01Ljc4NDk3IGwgLTEzLjc5NDg2LC0yMS40NTIxOCBhIDYuMzAxMTk2Nyw2LjMwMTE5NjcgMjguNjI4NDQ1IDAgMCAtNS4yOTk5NiwtMi44OTMwNSBsIC05LjkyOTQ0LDAgYSAxLjg1ODc3MjQsMS44NTg3NzI0IDExOC4zODcwNyAwIDAgLTEuNTU0ODksMi44NzcyNyB6IgogICAgICAgICBpZD0icGF0aDQtMDgtMS02IgogICAgICAgICB0cmFuc2Zvcm09InRyYW5zbGF0ZSgzOTIuMzA4MTksLTg0Mi43OTI2KSIgLz4KICAgIDwvZz4KICA8L2c%2BCjwvc3ZnPgo%3D
