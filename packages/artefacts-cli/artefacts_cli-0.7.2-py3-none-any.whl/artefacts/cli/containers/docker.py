from collections.abc import Generator
import json
import os
from pathlib import Path
import platform
from typing import Any, Tuple
from uuid import uuid4

from artefacts.cli.constants import DEFAULT_API_URL
from artefacts.cli.containers import CMgr
from artefacts.cli.utils import ensure_available

ensure_available("docker")

import docker  # noqa: E402
from docker import APIClient  # noqa: E402


class DockerManager(CMgr):
    def __init__(self):
        self.client = APIClient()

    def build(self, **kwargs) -> Tuple[str, Generator]:
        kwargs["tag"] = kwargs.pop("name")
        # Ensure `path` is a string, the Docker package does not support pathlib.
        kwargs["path"] = str(kwargs.pop("path"))
        # Remove intermediate containers
        kwargs["rm"] = True
        logs = []
        img_id = None
        for entry in self.client.build(**kwargs):
            line_data = [
                json.loads(v) for v in entry.decode("utf-8").split("\r\n") if len(v) > 0
            ]
            for data in line_data:
                if "stream" in data:
                    line = data["stream"].strip()
                    if not line.startswith("---") and len(line) > 0:
                        print(f"[{kwargs['tag'].split('/')[-1]}] {line}")
                        logs.append(line)
                elif "aux" in data and "ID" in data["aux"]:
                    img_id = data["aux"]["ID"]
        if img_id is None:
            img_id = self.client.inspect_image(kwargs["tag"])["Id"]
        return img_id, iter(logs)

    def check(
        self,
        image: str,
    ) -> bool:
        return len(self.client.images(name=image)) > 0

    def run(
        self,
        image: str,
        project: str,
        jobname: str = None,
        artefacts_dir: str = Path("~/.artefacts").expanduser(),
        api_url: str = DEFAULT_API_URL,
        api_key: str = None,
        with_gui: bool = False,
    ) -> Tuple[Any, Generator]:
        """
        Run an application as an Artefacts-enabled container in a Docker engine

        The arguments are considered straightforward, except the different
        priorities between `artefacts_dir` and `api_key`:
        * `api_key` has the highest priority. When specified, `artefacts_dir`
          is ignored. The container will rely on the key as an environment
          variable (ARTEFACTS_KEY).
        * Whenever `api_key` is not provided, the container gets `artefacts_dir`
          mounted as volume. The directory must contain a valid configuration
          with the project's key.
        """
        env = {
            "JOB_ID": str(uuid4()),
            "ARTEFACTS_JOB_NAME": jobname,
            "ARTEFACTS_API_URL": api_url,
        }

        env["ARTEFACTS_KEY"] = self._get_artefacts_api_key(project, artefacts_dir)
        if env["ARTEFACTS_KEY"] is None:
            return None, iter(
                [
                    f"Missing API key for the project. Does `{artefacts_dir}/config` exist and contain your key? Alternatively ARTEFACTS_KEY can be set with the key."
                ]
            )
        try:
            if platform.system() in ["Darwin", "Windows"]:
                # Assume we run in Docker Desktop
                env["DISPLAY"] = "host.docker.internal:0"
            else:
                env["DISPLAY"] = os.environ.get("DISPLAY", ":0")

            if not with_gui:
                env["QT_QPA_PLATFORM"] = "offscreen"

            container_conf = dict(
                image=image,
                environment=env,
                detach=False,
                host_config=self.client.create_host_config(
                    network_mode="host",
                ),
            )

            container = self.client.create_container(**container_conf)
            self.client.start(container=container.get("Id"))

            for entry in self.client.logs(container=container.get("Id"), stream=True):
                print(entry.decode("utf-8").strip())

            return container, iter([])
        except docker.errors.ImageNotFound:
            return None, iter(
                [f"Image {image} not found by Docker. Perhaps need to build first?"]
            )
        except Exception as e:
            return None, iter([f"Failed to run from {image}. All we know: {e}"])
