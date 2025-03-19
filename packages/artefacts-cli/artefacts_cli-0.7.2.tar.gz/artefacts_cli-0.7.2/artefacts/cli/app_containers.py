import os
from pathlib import Path

import click

from c2d.core import Converter

from artefacts.cli.constants import DEFAULT_API_URL
from artefacts.cli.utils import config_validation, read_config
from artefacts.cli.containers.utils import ContainerMgr


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def containers(ctx: click.Context, debug: bool):
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug


@containers.command()
@click.option(
    "--path",
    default=".",
    help="[Deprecated since 0.8.0; please see --root] Path to the root of the project.",
)
@click.option(
    "--root",
    default=".",
    help="Path to the root of the project.",
)
@click.option(
    "--dockerfile",
    default="Dockerfile",
    help="Path to a custom Dockerfile. Defaults to Dockerfile under `path` (see option of the same name).",
)
@click.option(
    "--name",
    required=False,
    help="[Deprecated since 0.8.0; not used and will disappear after 0.8.0] Name for the generated image",
)
@click.option(
    "--config",
    callback=config_validation,
    default="artefacts.yaml",
    help="Path to the Artefacts configuration file. It defaults to `./artefacts.yaml`",
)
@click.pass_context
def build(
    ctx: click.Context,
    path: str,
    root: str,
    dockerfile: str,
    name: str,
    config: str,
):
    try:
        artefacts_config = read_config(config)
    except FileNotFoundError:
        raise click.ClickException(
            f"Project config file not found: {config}. Please provide an Artefacts configuration file to proceed (running `artefacts init` allows to generate one)."
        )
    prefix = artefacts_config["project"].strip().lower()
    dockerfiles = []
    if os.path.exists(dockerfile):
        for job_name in artefacts_config["jobs"]:
            dockerfiles.append(
                dict(
                    path=root,
                    dockerfile=dockerfile,
                    name=f"{prefix}/{job_name.strip().lower()}",
                )
            )
    else:
        # The split on `prefix` is to ensure there is no slash (project names are org/project) confusing the path across supported OS.
        dest_root = (
            Path.home()
            / Path(".artefacts")
            / Path("projects")
            / Path(*(prefix.split("/")))
            / Path("containers")
        )
        if not dest_root.exists():
            click.echo(
                f"No {dockerfile} found here. Let's generate one per scenario based on artefacts.yaml. They will be available under the `{dest_root}` folder and used from there."
            )
        # No condition on generating the Dockerfiles as:
        #   - Fast
        #   - We consider entirely managed, so any manual change should be ignored.
        scenarios = Converter().process(config, as_text=False)
        for idx, df in enumerate(scenarios.values()):
            job_name = df.job_name.strip().lower()
            dest = dest_root / Path(job_name)
            dest.mkdir(parents=True, exist_ok=True)
            _dockerfile = os.path.join(dest, "Dockerfile")
            df.dump(_dockerfile)
            click.echo(f"[{job_name}] Using generated Dockerfile at: {_dockerfile}")
            dockerfiles.append(
                dict(
                    path=root,
                    dockerfile=_dockerfile,
                    name=f"{prefix}/{job_name}",
                )
            )
    handler = ContainerMgr()
    if len(dockerfiles) > 0:
        for specs in dockerfiles:
            # No condition on building the images, as relatively fast when already exists, and straightforward logic.
            image, _ = handler.build(**specs)
    else:
        click.echo("No Dockerfile, nothing to do.")


@containers.command()
@click.argument("name")
@click.pass_context
def check(ctx: click.Context, name: str):
    if name is None:
        name = "artefacts"
    handler = ContainerMgr()
    result = handler.check(name)
    if ctx.parent is None:
        # Print only if the command is called directly.
        print(f"Package {name} exists and ready to use.")
    return result


@containers.command()
@click.argument("jobname")
@click.option(
    "--config",
    callback=config_validation,
    default="artefacts.yaml",
    help="Path to the Artefacts configuration file. It defaults to `./artefacts.yaml`",
)
@click.option(
    "--with-gui",
    "with_gui",
    default=False,
    help="Show any GUI if any is created by the test runs. By default, UI elements are run but hidden---only test logs are returned. Please note GUI often assume an X11 environment, typically with Qt, so this may not work without a appropriate environment.",
)
@click.pass_context
def run(ctx: click.Context, jobname: str, config: str, with_gui: bool):
    try:
        artefacts_config = read_config(config)
    except FileNotFoundError:
        raise click.ClickException(f"Project config file not found: {config}")
    project = artefacts_config["project"]
    handler = ContainerMgr()
    params = dict(
        image=f"{project.strip().lower()}/{jobname}",
        project=project,
        jobname=jobname,
        with_gui=with_gui,
        # Hidden settings primarily useful to Artefacts developers
        api_url=os.environ.get("ARTEFACTS_API_URL", DEFAULT_API_URL),
        api_key=os.environ.get("ARTEFACTS_KEY", None),
    )
    container, logs = handler.run(**params)
    if container:
        print(f"Package run complete: Container Id for inspection: {container['Id']}")
    else:
        print("Package run failed:")
        for entry in logs:
            print("\t- " + entry)
