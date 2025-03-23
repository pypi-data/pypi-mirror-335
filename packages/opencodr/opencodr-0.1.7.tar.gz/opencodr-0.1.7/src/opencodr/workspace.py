import shutil
import subprocess
from importlib.resources import files
from pathlib import Path

import typer

from opencodr.app_meta import app_name

DOCKER_TMPL = """
FROM {app_name}/base

WORKDIR /workspace

COPY .git /workspace/.git
COPY .opencodr /workspace/.opencodr

RUN git worktree add readonly
RUN git worktree add dev
RUN git worktree add fuzz
CMD ["/bin/bash"]
"""


class Workspace:
    app: typer.Typer

    def __init__(self):
        self.app = typer.Typer()
        self.app.command(
            name="create", help="Creates a docker image to sandbox the agent"
        )(self.create_workspace)
        self.app.command(name="start", help="Shortcut to start the container")(
            self.start_workspace
        )
        self.app.command(name="stop", help="Shortcut to stop the container")(
            self.stop_workspace
        )

    def _check_docker_exists(self):
        if not shutil.which("docker"):
            raise typer.BadParameter("Docker is not installed or not in PATH.")

    def _check_docker_image_exists(self, image_name: str):
        result = subprocess.run(
            ["docker", "images", "-q", image_name], capture_output=True, text=True
        )

        return result.stdout.strip() != ""

    def _build_docker_image(self, dockerfile_path: Path, image_name: str):
        dockerfile_dir = dockerfile_path.parent

        subprocess.run(
            ["docker", "build", "-t", image_name, "-f", str(dockerfile_path.name), "."],
            cwd=dockerfile_dir,
            check=True,
        )

    def create_base_image(self):
        self._check_docker_exists()

        base_dockerfile_path = files(app_name).joinpath("assets", "dockerfile.base")

        if not base_dockerfile_path.exists():
            raise FileNotFoundError(
                f"Base Dockerfile not found at {base_dockerfile_path}"
            )

        self._build_docker_image(base_dockerfile_path, f"{app_name}/base")

    def create_workspace(self):
        self._check_docker_exists()

        if not self._check_docker_image_exists(f"{app_name}/base"):
            self.create_base_image()

        wks_dir = Path.cwd()
        dockerfile_path = wks_dir / f"Dockerfile.{app_name}"

        if dockerfile_path.exists():
            typer.echo(f"Dockerfile.{app_name} already exists in the project root.\n")
        else:
            dockerfile_content = DOCKER_TMPL.format(app_name=app_name)
            dockerfile_path.write_text(dockerfile_content)

    def start_workspace(self):
        self._check_docker_exists()
        wks_dir = Path.cwd()
        wks_name = wks_dir.name
        dockerfile_path = wks_dir / f"Dockerfile.{app_name}"

        if not dockerfile_path.exists():
            raise FileNotFoundError(f"Dockerfile not found at {dockerfile_path}\n")

        image_name = f"{app_name}/{wks_name}"

        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
        )
        existing_containers = result.stdout.splitlines()

        if wks_name in existing_containers:
            running_result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
            )
            running_containers = running_result.stdout.splitlines()

            if wks_name in running_containers:
                typer.echo(f"Workspace '{wks_name}' is already running.\n")
            else:
                subprocess.run(["docker", "start", "-ai", wks_name], check=True)
            return

        if not self._check_docker_image_exists(f"{app_name}/base"):
            self.create_base_image()

        self._build_docker_image(dockerfile_path, image_name)

        subprocess.run(
            [
                "docker",
                "run",
                "--name",
                wks_name,
                "-it",
                image_name,
            ],
            check=True,
        )

    def stop_workspace(self):
        self._check_docker_exists()

        wks_name = Path.cwd().name

        subprocess.run(["docker", "stop", wks_name], check=True)

        typer.echo(f"Workspace '{wks_name}' stopped\n")
