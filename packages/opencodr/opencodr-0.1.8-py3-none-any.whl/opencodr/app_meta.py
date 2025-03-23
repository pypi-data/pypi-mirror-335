from pathlib import Path

app_name = "opencodr"


def get_opencoder_dir() -> Path | None:
    current_dir = Path.cwd()

    for parent in [current_dir, *current_dir.parents]:
        opencoder_dir = parent / f".{app_name}"
        if opencoder_dir.is_dir():
            return opencoder_dir

        if (parent / ".git").is_dir():
            break

    return None


if __name__ == "__main__":
    print(get_opencoder_dir())
