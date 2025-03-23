import unittest
from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import MagicMock, patch

import typer

from opencodr.app_meta import app_name
from opencodr.workspace import Workspace


class TestWorkspace(unittest.TestCase):
    def setUp(self):
        self.workspace = Workspace()
        self.test_image_name = "opencodr/test"
        self.test_dockerfile_path = Path("/test/Dockerfile.opencodr")

    @patch("shutil.which")
    def test_check_docker_exists_success(self, mock_which):
        mock_which.return_value = "/usr/bin/docker"

        try:
            self.workspace._check_docker_exists()
        except Exception as e:
            self.fail(f"_check_docker_exists raised {e} unexpectedly")

    @patch("shutil.which")
    def test_check_docker_exists_failure(self, mock_which):
        mock_which.return_value = None

        with self.assertRaises(typer.BadParameter) as context:
            self.workspace._check_docker_exists()

        self.assertEqual(
            str(context.exception), "Docker is not installed or not in PATH."
        )

    @patch("subprocess.run")
    def test_check_docker_image_exists_true(self, mock_run):
        process_mock = MagicMock()
        process_mock.stdout = "image_id_123"
        mock_run.return_value = process_mock

        result = self.workspace._check_docker_image_exists(self.test_image_name)

        mock_run.assert_called_once_with(
            ["docker", "images", "-q", self.test_image_name],
            capture_output=True,
            text=True,
        )

        self.assertTrue(result)

    @patch("subprocess.run")
    def test_check_docker_image_exists_false(self, mock_run):
        process_mock = MagicMock()
        process_mock.stdout = ""
        mock_run.return_value = process_mock

        result = self.workspace._check_docker_image_exists(self.test_image_name)

        mock_run.assert_called_once_with(
            ["docker", "images", "-q", self.test_image_name],
            capture_output=True,
            text=True,
        )

        self.assertFalse(result)

    @patch("subprocess.run")
    def test_build_docker_image_success(self, mock_run):
        self.workspace._build_docker_image(
            self.test_dockerfile_path, self.test_image_name
        )
        mock_run.assert_called_once_with(
            [
                "docker",
                "build",
                "-t",
                self.test_image_name,
                "-f",
                self.test_dockerfile_path.name,
                ".",
            ],
            cwd=self.test_dockerfile_path.parent,
            check=True,
        )

    @patch("subprocess.run")
    def test_build_docker_image_failure(self, mock_run):
        mock_run.side_effect = CalledProcessError(1, "docker build")

        with self.assertRaises(CalledProcessError):
            self.workspace._build_docker_image(
                self.test_dockerfile_path, self.test_image_name
            )

    @patch.object(Workspace, "create_base_image")
    @patch.object(Workspace, "_check_docker_image_exists")
    @patch.object(Workspace, "_check_docker_exists")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.write_text")
    def test_create_workspace_new_dockerfile(
        self,
        mock_write_text,
        mock_exists,
        mock_check_docker_exists,
        mock_check_docker_image_exists,
        mock_create_base_image,
    ):
        mock_exists.return_value = False
        mock_check_docker_image_exists.return_value = False

        self.workspace.create_workspace()

        mock_check_docker_exists.assert_called_once()
        mock_check_docker_image_exists.assert_called_once_with(f"{app_name}/base")
        mock_create_base_image.assert_called_once()
        mock_write_text.assert_called_once()

    @patch.object(Workspace, "create_base_image")
    @patch.object(Workspace, "_check_docker_image_exists")
    @patch.object(Workspace, "_check_docker_exists")
    @patch("pathlib.Path.exists")
    @patch("typer.echo")
    def test_create_workspace_existing_dockerfile(
        self,
        mock_echo,
        mock_exists,
        mock_check_docker_exists,
        mock_check_docker_image_exists,
        mock_create_base_image,
    ):
        mock_exists.return_value = True
        mock_check_docker_image_exists.return_value = True

        self.workspace.create_workspace()

        mock_check_docker_exists.assert_called_once()
        mock_check_docker_image_exists.assert_called_once_with(f"{app_name}/base")
        mock_create_base_image.assert_not_called()
        mock_echo.assert_called_once_with(
            f"Dockerfile.{app_name} already exists in the project root.\n"
        )

    @patch("shutil.which")
    def test_docker_not_installed(self, mock_which):
        mock_which.return_value = False

        with self.assertRaises(typer.BadParameter):
            self.workspace.start_workspace()

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.cwd")
    def test_dockerfile_not_found(
        self,
        mock_cwd,
        mock_path_exists,
    ):
        mock_cwd.return_value = Path("/test")
        mock_path_exists.return_value = False

        with self.assertRaises(FileNotFoundError):
            self.workspace.start_workspace()

    @patch("pathlib.Path.exists")
    @patch("subprocess.run")
    @patch.object(Workspace, "create_base_image")
    @patch("pathlib.Path.cwd")
    def test_base_image_missing(
        self,
        mock_cwd,
        mock_create_base_image,
        mock_subprocess,
        mock_path_exists,
    ):
        mock_cwd.return_value = Path("/test")
        mock_path_exists.return_value = True
        mock_subprocess.side_effect = [
            MagicMock(stdout=""),
            MagicMock(stdout=""),
            MagicMock(),
            MagicMock(),
        ]

        self.workspace.start_workspace()
        mock_create_base_image.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("subprocess.run")
    @patch("pathlib.Path.cwd")
    @patch.object(Workspace, "_build_docker_image")
    def test_container_already_running(
        self,
        mock_build_image,
        mock_cwd,
        mock_subprocess,
        mock_path_exists,
    ):
        mock_build_image.return_value = True
        mock_cwd.return_value = Path("/test")
        mock_path_exists.return_value = True
        mock_subprocess.side_effect = [
            MagicMock(stdout=self.test_image_name),
            MagicMock(stdout=self.test_image_name),
            MagicMock(),
        ]

        self.workspace.start_workspace()

        mock_subprocess.assert_any_call(
            ["docker", "ps", "-a", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
        )
        assert not any(
            call[0] == ["docker", "start", "-ai", self.test_image_name]
            for call in mock_subprocess.mock_calls
        ), "docker start was called with the wrong arguments"

    @patch("pathlib.Path.exists")
    @patch("subprocess.run")
    @patch("pathlib.Path.cwd")
    def test_container_exists_but_not_running(
        self,
        mock_cwd,
        mock_subprocess,
        mock_path_exists,
    ):
        mock_cwd.return_value = Path("/test")
        mock_path_exists.return_value = True
        mock_subprocess.side_effect = [
            MagicMock(stdout="test"),
            MagicMock(stdout=""),
            MagicMock(),
        ]

        self.workspace.start_workspace()

        mock_subprocess.assert_any_call(["docker", "start", "-ai", "test"], check=True)

    @patch("pathlib.Path.exists")
    @patch("subprocess.run")
    @patch.object(Workspace, "_check_docker_exists")
    @patch.object(Workspace, "_check_docker_image_exists", return_value=True)
    @patch.object(Workspace, "_build_docker_image")
    @patch("pathlib.Path.cwd")
    def test_start_workspace_creates_new_container(
        self,
        mock_cwd,
        mock_build_image,
        mock_check_image,
        mock_check_docker,
        mock_subprocess,
        mock_path_exists,
    ):
        mock_path_exists.return_value = True
        mock_cwd.return_value = Path("/test")
        mock_subprocess.side_effect = [
            MagicMock(stdout=""),
            MagicMock(stdout=""),
        ]

        self.workspace.start_workspace()

        mock_check_docker.assert_called_once()
        mock_check_image.assert_called_once_with("opencodr/base")
        mock_build_image.assert_called_once_with(
            self.test_dockerfile_path, self.test_image_name
        )
        mock_subprocess.assert_any_call(
            ["docker", "run", "--name", "test", "-it", self.test_image_name], check=True
        )

    @patch("pathlib.Path.cwd")
    @patch("subprocess.run")
    @patch.object(Workspace, "_check_docker_exists")
    @patch("typer.echo")
    def test_stop_workspace(
        self,
        mock_typer_echo,
        mock_check_docker_exists,
        mock_subprocess,
        mock_cwd,
    ):
        mock_cwd.return_value = Path("/test")
        mock_check_docker_exists.return_value = True
        mock_subprocess.return_value = MagicMock(stdout="")
        self.workspace.stop_workspace()

        mock_check_docker_exists.assert_called_once()

        mock_subprocess.assert_called_once_with(["docker", "stop", "test"], check=True)

        mock_typer_echo.assert_called_once_with("Workspace 'test' stopped\n")


if __name__ == "__main__":
    unittest.main()
