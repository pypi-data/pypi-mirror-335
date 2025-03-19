import configparser
import getpass
import json
import os
import platform
import random
import subprocess
import tarfile
import tempfile
import time
from urllib.parse import urlparse
import webbrowser

import yaml
import click
import requests
from pathlib import Path
from gitignore_parser import parse_gitignore

from artefacts.cli import init_job, generate_scenarios, AuthenticationError, __version__
from artefacts.cli import app_containers as containers
from artefacts.cli.constants import DEPRECATED_FRAMEWORKS, SUPPORTED_FRAMEWORKS
from artefacts.cli.utils import add_output_from_default, config_validation, read_config

HOME = os.path.expanduser("~")
CONFIG_DIR = f"{HOME}/.artefacts"
CONFIG_PATH = f"{CONFIG_DIR}/config"


def get_git_revision_hash() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .decode("ascii")
            .strip()
        )
    except subprocess.CalledProcessError:
        return ""


def get_git_revision_branch() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            .decode("ascii")
            .strip()
        )
    except subprocess.CalledProcessError:
        return ""


def get_conf_from_file():
    config = configparser.ConfigParser()
    if not os.path.isfile(CONFIG_PATH):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        config["DEFAULT"] = {}
        with open(CONFIG_PATH, "w") as f:
            config.write(f)
    config.read(CONFIG_PATH)
    return config


def get_artefacts_api_url(project_profile):
    return os.environ.get(
        "ARTEFACTS_API_URL",
        project_profile.get(
            "ApiUrl",
            "https://app.artefacts.com/api",
        ),
    )


class APIConf:
    def __init__(self, project_name: str, job_name: str = None) -> None:
        config = get_conf_from_file()
        if project_name in config:
            profile = config[project_name]
        else:
            profile = {}
        self.api_url = get_artefacts_api_url(profile)
        self.api_key = os.environ.get("ARTEFACTS_KEY", profile.get("ApiKey", None))
        if self.api_key is None:
            batch_id = os.environ.get("AWS_BATCH_JOB_ID", None)
            job_id = os.environ.get("ARTEFACTS_JOB_ID", None)
            if batch_id is None or job_id is None:
                raise click.ClickException(
                    f"No API KEY set. Please run 'artefacts config add {project_name}'"
                )
            auth_type = "Internal"
            # Batch id for array jobs contains array index
            batch_id = batch_id.split(":")[0]
            self.headers = {"Authorization": f"{auth_type} {job_id}:{batch_id}"}
        else:
            auth_type = "ApiKey"
            self.headers = {"Authorization": f"{auth_type} {self.api_key}"}
        self.headers["User-Agent"] = (
            f"ArtefactsClient/{__version__} ({platform.platform()}/{platform.python_version()})"
        )
        if job_name:
            click.echo(f"[{job_name}] Connecting to {self.api_url} using {auth_type}")
        else:
            click.echo(f"Connecting to {self.api_url} using {auth_type}")


def validate_artefacts_config(config_file: str) -> dict:
    pass


@click.group()
def config():
    return


@config.command()
def path():
    """
    Get the configuration file path
    """
    click.echo(CONFIG_PATH)


def add_key_to_conf(project_name, api_key):
    config = get_conf_from_file()
    config[project_name] = {"ApiKey": api_key}
    with open(CONFIG_PATH, "w") as f:
        config.write(f)


@config.command()
@click.argument("project_name")
def add(project_name):
    """
    Set configuration for PROJECT_NAME
    """
    config = get_conf_from_file()
    if project_name in config:
        profile = config[project_name]
    else:
        profile = {}
    api_url = get_artefacts_api_url(profile)
    dashboard_url = api_url.split("/api")[0]
    settings_page_url = f"{dashboard_url}/{project_name}/settings"
    # Check if running on WSL
    if "WSLENV" in os.environ:
        os.system(f'cmd.exe /C start "" {settings_page_url} 2>/dev/null')
    else:
        webbrowser.open(settings_page_url)
    click.echo(f"Opening the project settings page: {settings_page_url}")
    api_key = click.prompt(
        f"Please enter your API KEY for {project_name}", type=str, hide_input=True
    )
    add_key_to_conf(project_name, api_key)
    click.echo(f"API KEY saved for {project_name}")
    if click.confirm(
        "Would you like to download the generated artefacts.yaml file? This will overwrite any existing config file in the current directory."
    ):
        api_conf = APIConf(project_name)
        config_file_name = "artefacts.yaml"
        config_file_url = f"{api_url}/{project_name}/{config_file_name}"
        r = requests.get(config_file_url, headers=api_conf.headers)
        with open(config_file_name, "wb") as f:
            f.write(r.content)
    return


@config.command()
@click.argument("project_name")
def delete(project_name):
    """
    Delete configuration for PROJECT_NAME
    """
    config = get_conf_from_file()
    config.remove_section(project_name)
    with open(CONFIG_PATH, "w") as f:
        config.write(f)
    click.echo(f"{project_name} config removed")


@click.command()
@click.argument("project_name")
def hello(project_name):
    """Show message to confirm credentials allow access to PROJECT_NAME"""
    api_conf = APIConf(project_name)
    response = requests.get(
        f"{api_conf.api_url}/{project_name}/info",
        headers=api_conf.headers,
    )
    if response.status_code == 200:
        result = response.json()
        click.echo(
            "Hello " + click.style(f"{result['name']}@{result['framework']}", fg="blue")
        )
    else:
        result = response.json()
        raise click.ClickException(f"Error getting project info: {result['message']}")


@click.command()
@click.option(
    "--config",
    callback=config_validation,
    default="artefacts.yaml",
    help="Artefacts config file.",
)
@click.option(
    "--dryrun",
    is_flag=True,
    default=False,
    help="Dryrun: no tracking or test execution",
)
@click.option(
    "--nosim",
    is_flag=True,
    default=False,
    help="nosim: no simulator resource provided by Artefacts",
)
@click.option(
    "--noupload",
    is_flag=True,
    default=False,
    help="noupload: rosbags are not uploaded to cloud",
)
@click.option(
    "--noisolation",
    is_flag=True,
    default=False,
    help="noisolation: for debugging, break the 'middleware network' isolation between the test suite and the host (in ROS1: --reuse-master flag / in ROS2: --disable-isolation flag)",
)
@click.option(
    "--description",
    default=None,
    help="Optional description for this run",
)
@click.option(
    "--skip-validation",
    is_flag=True,
    default=False,
    is_eager=True,  # Necessary for callbacks to see it.
    help="Skip configuration validation, so that unsupported settings can be tried out, e.g. non-ROS settings or simulators like SAPIEN.",
)
@click.option(
    "--in-container",
    is_flag=True,
    default=False,
    help='[Experimental] Run the job inside a package container. The container image is build if it does not exist yet, with default name as "artefacts" (please use --with-image to override the image name). This option overrides (for now) --dryrun, --nosim, --noisolation and --description.',
)
@click.option(
    "--with-image",
    default=None,
    help="[Deprecated and unused from 0.8.0; Image names are now internally managed] Run the job using the image name passed here. Only used when running with --in-container set.",
)
@click.option(
    "--no-rebuild",
    is_flag=True,
    default=False,
    help="[Experimental] Override the default behaviour to always rebuild the container image (as we assume incremental testing).",
)
@click.option(
    "--with-gui",
    is_flag=True,
    default=False,
    help="Show any GUI if any is created by the test runs. By default, UI elements are run but hidden---only test logs are returned. Please note GUI often assume X11 (e.g. ROS), typically with Qt, so this may not work without a appropriate environment.",
)
@click.argument("jobname")
@click.pass_context
def run(
    ctx: click.Context,
    config,
    jobname,
    dryrun,
    nosim,
    noupload,
    noisolation,
    description="",
    skip_validation=False,
    in_container: bool = False,
    with_image: str = "artefacts",
    no_rebuild: bool = False,
    with_gui: bool = False,
):
    """
    Run JOBNAME locally

    * Directly in the shell by default.
    * Inside a packaged container when using the --in-container option.
    """
    warpconfig = read_config(config)
    project_id = warpconfig["project"]

    if in_container:
        click.echo("#" * 80)
        click.echo(f"# Job {jobname}".ljust(79, " ") + "#")
        click.echo("#" * 80)
        click.echo(f"[{jobname}] Checking container image")
        if not no_rebuild:
            ctx.invoke(
                containers.build,
                root=".",
            )
            click.echo(f"[{jobname}] Container image ready")
        click.echo(f"[{jobname}] Run in container")
        return ctx.invoke(
            containers.run,
            jobname=jobname,
            config=config,
            with_gui=with_gui,
        )

    api_conf = APIConf(project_id, jobname)
    click.echo(f"[{jobname}] Starting tests")
    if jobname not in warpconfig["jobs"]:
        click.secho(f"[{jobname}] Error: Job name not defined", err=True, bold=True)
        raise click.Abort()
    jobconf = warpconfig["jobs"][jobname]
    job_type = jobconf.get("type", "test")
    if job_type not in ["test"]:
        click.echo(f"[{jobname}] Job type not supported: {job_type}")
        return

    framework = jobconf["runtime"].get("framework", None)

    # migrate deprecated framework names
    if framework in DEPRECATED_FRAMEWORKS.keys():
        migrated_framework = DEPRECATED_FRAMEWORKS[framework]
        click.echo(
            f"[{jobname}] The selected framework '{framework}' is deprecated. Using '{migrated_framework}' instead."
        )
        framework = migrated_framework

    if framework not in SUPPORTED_FRAMEWORKS:
        click.echo(
            f"[{jobname}] WARNING: framework: '{framework}' is not officially supported. Attempting run."
        )

    batch_index = os.environ.get("AWS_BATCH_JOB_ARRAY_INDEX", None)
    if batch_index is not None:
        batch_index = int(batch_index)
        click.echo(f"[{jobname}] AWS BATCH ARRAY DETECTED, batch_index={batch_index}")
    scenarios, first = generate_scenarios(jobconf, batch_index)
    context = None
    execution_context = getpass.getuser() + "@" + platform.node()
    context = {
        "ref": get_git_revision_branch() + "~" + execution_context,
        "commit": get_git_revision_hash()[:8] + "~",
    }
    context["description"] = description
    try:
        warpjob = init_job(
            project_id,
            api_conf,
            jobname,
            jobconf,
            dryrun,
            nosim,
            noupload,
            noisolation,
            context,
            first,
        )
    except AuthenticationError:
        click.secho(
            f"[{jobname}] Unable to authenticate (Stage: Job initialisation), please check your project name and API key",
            err=True,
            bold=True,
        )
        raise click.Abort()

    job_success = True
    for scenario_n, scenario in enumerate(scenarios):
        click.echo(
            f"[{jobname}] Starting scenario {scenario_n + 1}/{len(scenarios)}: {scenario['name']}"
        )
        try:
            run = warpjob.new_run(scenario)
        except AuthenticationError:
            click.secho(
                f"[{jobname}] Unable to authenticate (Stage: Job run), please check your project name and API key",
                err=True,
                bold=True,
            )
            raise click.Abort()
        if framework is not None and framework.startswith("ros2:"):
            from artefacts.cli.ros2 import run_ros2_tests
            from artefacts.cli.utils_ros import get_TestSuite_error_result

            if "ros_testfile" not in run.params:
                click.secho(
                    f"[{jobname}] Test launch file not specified for ros2 project",
                    err=True,
                    bold=True,
                )
                result = get_TestSuite_error_result(
                    scenario["name"],
                    "launch_test file not specified error",
                    f"Please specify a `ros_testfile` in the artefacts.yaml scenario configuration.",
                )
                run.log_tests_results([result], False)
                run.stop()
            if dryrun:
                click.echo(f"[{jobname}] Performing dry run")
                results, success = {}, True
            else:
                try:
                    results, success = run_ros2_tests(run)
                except Exception as e:
                    warpjob.stop()
                    warpjob.log_tests_result(False)
                    click.secho(e, bold=True, err=True)
                    click.secho(
                        f"[{jobname}] artefacts failed to execute the tests",
                        err=True,
                        bold=True,
                    )
                    raise click.Abort()
            if success is None:
                run.stop()
                warpjob.stop()
                warpjob.log_tests_result(job_success)
                click.secho(
                    f"[{jobname}] Not able to execute tests. Make sure that ROS2 is sourced and that your launch file syntax is correct.",
                    err=True,
                    bold=True,
                )
                raise click.Abort()
            if not success:
                job_success = False
        elif framework is not None and framework.startswith("ros1:"):
            from artefacts.cli.ros1 import run_ros1_tests

            if "ros_testfile" not in run.params:
                click.secho(
                    f"[{jobname}] Test launch file not specified for ros1 project",
                    err=True,
                    bold=True,
                )
                raise click.Abort()
            if dryrun:
                click.echo(f"[{jobname}] Performing dry run")
                results, success = {}, True
            else:
                results, success = run_ros1_tests(run)
            if not success:
                job_success = False
        else:
            from artefacts.cli.other import run_other_tests

            if "run" not in run.params:
                click.secho(
                    f"[{jobname}] run command not specified for scenario",
                    err=True,
                    bold=True,
                )
                raise click.Abort()
            if dryrun:
                click.echo(f"[{jobname}] Performing dry run")
                results, success = {}, True
            else:
                results, success = run_other_tests(run)
            if not success:
                job_success = False
            if type(run.params.get("metrics", [])) is str:
                run.log_metrics()

        # Add for upload any default output generated by the run
        add_output_from_default(run)

        run.stop()
    warpjob.log_tests_result(job_success)
    click.echo(f"[{jobname}] Done")
    time.sleep(random.random() * 1)

    warpjob.stop()


@click.command()
@click.option(
    "--config",
    callback=config_validation,
    default="artefacts.yaml",
    help="Artefacts config file.",
)
@click.option(
    "--description",
    default=None,
    help="Optional description for this run",
)
@click.option(
    "--skip-validation",
    is_flag=True,
    default=False,
    is_eager=True,  # Necessary for callbacks to see it.
    help="Skip configuration validation, so that unsupported settings can be tried out, e.g. non-ROS settings or simulators like SAPIEN.",
)
@click.argument("jobname")
def run_remote(config, description, jobname, skip_validation=False):
    """
    Run JOBNAME in the cloud by packaging local sources.
    if a `.artefactsignore` file is present, it will be used to exclude files from the source package.

    This command requires to have a linked GitHub repository
    """
    try:
        warpconfig = read_config(config)
    except FileNotFoundError:
        raise click.ClickException(f"Project config file not found: {config}")
    project_id = warpconfig["project"]
    api_conf = APIConf(project_id)
    project_folder = os.path.dirname(os.path.abspath(config))
    dashboard_url = urlparse(api_conf.api_url)
    dashboard_url = f"{dashboard_url.scheme}://{dashboard_url.netloc}/{project_id}"

    try:
        warpconfig["jobs"][jobname]
    except KeyError:
        raise click.ClickException(
            f"Can't find a job named '{jobname}' in config '{config}'"
        )

    # Mutate job and then keep only the selected job in the config
    run_config = warpconfig.copy()
    job = warpconfig["jobs"][jobname]

    # Use the same logic as `run` for expanding scenarios based on array params
    job["scenarios"]["settings"], _ = generate_scenarios(job, None)

    # Ensure unique names
    for idx, scenario in enumerate(job["scenarios"]["settings"]):
        scenario["name"] = f"{scenario['name']}-{idx}"

    run_config["jobs"] = {jobname: job}
    if "on" in run_config:
        del run_config["on"]

    click.echo("Packaging source...")

    with tempfile.NamedTemporaryFile(
        prefix=project_id.split("/")[-1], suffix=".tgz", delete=True
    ) as temp_file:
        # get list of patterns to be ignored in .artefactsignore
        ignore_file = Path(project_folder) / Path(".artefactsignore")
        try:
            ignore_matches = parse_gitignore(ignore_file)
        except FileNotFoundError:
            ignore_matches = lambda x: False  # noqa: E731
        with tarfile.open(fileobj=temp_file, mode="w:gz") as tar_file:
            for root, dirs, files in os.walk(project_folder):
                for file in files:
                    absolute_path = os.path.join(root, file)
                    relative_path = os.path.relpath(absolute_path, project_folder)
                    # ignore .git folder
                    if relative_path.startswith(".git/"):
                        continue
                    # ignore paths in ignored_paths
                    if ignore_matches(absolute_path):
                        continue
                    # Prevent artefacts.yaml from being included twice
                    if os.path.basename(absolute_path) == "artefacts.yaml":
                        continue
                    tar_file.add(absolute_path, arcname=relative_path, recursive=False)
            # Write the modified config file to a temp file and add it
            with tempfile.NamedTemporaryFile("w") as tf:
                yaml.dump(run_config, tf)
                tar_file.add(tf.name, arcname="artefacts.yaml", recursive=False)

        temp_file.flush()
        temp_file.seek(0)

        # Request signed upload URLs
        upload_urls_response = requests.put(
            f"{api_conf.api_url}/{project_id}/upload_source",
            headers=api_conf.headers,
        )

        if not upload_urls_response.ok:
            try:
                result = upload_urls_response.json()
            except requests.exceptions.JSONDecodeError:
                raise click.ClickException(
                    f"Apologies, problem in interacting with the Artefacts backend: {upload_urls_response.status_code} {upload_urls_response.reason}. Response text: {upload_urls_response.text}."
                )

            if (
                upload_urls_response.status_code == 403
                and result["message"] == "Not allowed"
            ):
                raise click.ClickException(
                    f"Missing access! Please make sure your API key is added at {dashboard_url}/settings"
                )

            if upload_urls_response.status_code == 402:
                raise click.ClickException(
                    f"Billing issue, please go to {dashboard_url}/settings to correct: {result['error']}"
                )

            if "message" in result:
                raise click.ClickException(
                    f"Error getting project info: {result['message']}"
                )
            elif "error" in result:
                raise click.ClickException(
                    f"Error getting project info: {result['error']}"
                )
            else:
                raise click.ClickException(
                    f"Error getting project info: {upload_urls_response.status_code} {upload_urls_response.reason}. Response text: {upload_urls_response.text}."
                )

        upload_urls = upload_urls_response.json()["upload_urls"]
        url = ""
        # github specific logic should later be moved to the github action, and instead support additional options or env variables for configuration for payload
        if description is None:
            if "GITHUB_RUN_ID" in os.environ:
                description = os.environ.get("GITHUB_WORKFLOW")
                url = f"{os.environ.get('GITHUB_SERVER_URL')}/{os.environ.get('GITHUB_REPOSITORY')}/actions/runs/{os.environ.get('GITHUB_RUN_ID')}"
            else:
                description = "Testing local source"
        # Mock the necessary parts of the GitHub event
        execution_context = getpass.getuser() + "@" + platform.node()
        integration_payload = {
            "head_commit": {
                # shown on the dashboard in the job details
                "message": description,
                "url": url,
            },
            "repository": {
                # used by the container-builder for creating the ecr repo name
                "full_name": os.environ.get("GITHUB_REPOSITORY", project_id),
            },
            # special key to distinguish the valid GitHub payload from these fabricated ones
            "ref": os.environ.get(
                "GITHUB_REF", get_git_revision_branch() + "~" + execution_context
            ),
            "after": os.environ.get("GITHUB_SHA", get_git_revision_hash()[:8] + "~"),
        }

        uploads = [
            ("archive.tgz", temp_file),
            ("artefacts.yaml", ("artefacts.yaml", yaml.dump(run_config))),
            (
                "integration_payload.json",
                ("integration_payload.json", json.dumps(integration_payload)),
            ),
        ]
        # get size of the archive file
        archive_size = os.path.getsize(temp_file.name)

        with click.progressbar(
            uploads,
            label=f"Uploading {archive_size / 1024 / 1024:.2f} MB of source code",
            item_show_func=lambda x: x and x[0],
        ) as bar:
            for filename, file in bar:
                response = requests.post(
                    upload_urls[filename]["url"],
                    data=upload_urls[filename]["fields"],
                    files={"file": file},
                )
                if not response.ok:
                    raise click.ClickException(
                        f"Failed to upload {filename}: {response.text}"
                    )

        click.echo(
            f"Uploading complete! The new job will show up shortly at {dashboard_url}"
        )


@click.group()
@click.version_option(version=__version__)
def artefacts():
    """A command line tool to interface with ARTEFACTS"""
    compute_env = os.getenv("AWS_BATCH_CE_NAME", "")
    if compute_env != "":
        click.echo(f"running version {__version__}")
        if (
            "development" in compute_env
            and os.getenv("ARTEFACTS_API_URL", None) is None
        ):
            os.environ["ARTEFACTS_API_URL"] = "https://ui.artefacts.com/api"


artefacts.add_command(config)
artefacts.add_command(hello)
artefacts.add_command(run)
artefacts.add_command(run_remote)
artefacts.add_command(containers.containers)


if __name__ == "__main__":
    artefacts()
