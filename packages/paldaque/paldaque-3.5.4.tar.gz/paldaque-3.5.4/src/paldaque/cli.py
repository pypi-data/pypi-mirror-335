import sys
from importlib.metadata import version

import click
import palaestrai.core.runtime_config
from click_aliases import ClickAliasedGroup
from palaestrai.core import RuntimeConfig
from tabulate import tabulate

from . import read_experiments
from . import read_experiment_runs
from . import read_experiment_run_instances
from . import read_experiment_run_phases
from . import read_muscle_actions


@click.group(invoke_without_command=True, cls=ClickAliasedGroup)
@click.option(
    "-c",
    "--config",
    type=click.Path(),
    help="Supply custom runtime configuration file. "
    "(Default search path: %s)"
    % (palaestrai.core.runtime_config._RuntimeConfig.CONFIG_FILE_PATHS),
)
@click.option(
    "--store-uri",
    "-s",
    "store_uri",
    help=(
        "Specify a custom store uri, default is None which means to use the "
        "value provided in your runtime configuration file."
    ),
)
@click.version_option(version("paldaque"))
def main(config=None, store_uri=None):
    if config:
        try:
            with open(config, "r") as fp:
                RuntimeConfig().reset()  # Make sure we start fresh!
                RuntimeConfig().load(fp)
        except OSError as e:
            click.echo(
                "ERROR: Could not load config from %s: %s." % (config, e),
                file=sys.stderr,
            )
            exit(1)
    else:
        try:
            RuntimeConfig().load()
        except FileNotFoundError as e:
            click.echo(
                "Please create a runtime config. %s.\n"
                "Will continue with built-in defaults." % e,
                file=sys.stderr,
            )
    if store_uri is not None:
        RuntimeConfig().load({"store_uri": store_uri})

    click.echo(f"Trying to read from database with URI {RuntimeConfig().store_uri}")


@main.command(aliases=["e"])
def experiment():
    results = read_experiments(as_dict=True)

    click.echo(tabulate(results, headers="keys", tablefmt="pipe"))


@main.command(aliases=["r"])
@click.option("--experiment-id", "-e", "experiment_id", type=int, default=0)
def experiment_run(experiment_id):
    results = read_experiment_runs(experiment_id, as_dict=True)

    click.echo(tabulate(results, headers="keys", tablefmt="pipe"))


@main.command(aliases=["i"])
@click.option("--experiment-id", "-e", "experiment_id", type=int, default=0)
@click.option("--experiment-run-id", "-r", "experiment_run_id", type=int, default=0)
def experiment_run_instance(experiment_id, experiment_run_id):
    results = read_experiment_run_instances(
        experiment_id, experiment_run_id, as_dict=True
    )
    click.echo(tabulate(results, headers="keys", tablefmt="pipe"))


@main.command(aliases=["p"])
@click.option("--experiment-id", "-e", "experiment_id", type=int, default=0)
@click.option("--experiment-run-id", "-r", "experiment_run_id", type=int, default=0)
@click.option(
    "--experiment-run-instance-id",
    "-i",
    "experiment_run_instance_id",
    type=int,
    default=0,
)
def experiment_run_phase(experiment_id, experiment_run_id, experiment_run_instance_id):
    results = read_experiment_run_phases(
        experiment_id,
        experiment_run_id,
        experiment_run_instance_id,
        as_dict=True,
    )
    click.echo(tabulate(results, headers="keys", tablefmt="pipe"))


@main.command(aliases=["ma"])
@click.option("--experiment-id", "-e", "experiment_id", type=int, default=0)
@click.option("--experiment-run-id", "-r", "experiment_run_id", type=int, default=0)
@click.option(
    "--experiment-run-instance-id",
    "-i",
    "experiment_run_instance_id",
    type=int,
    default=0,
)
@click.option(
    "--experiment-run-phase-id",
    "-p",
    "experiment_run_phase_id",
    type=int,
    default=0,
)
@click.option(
    "--csv",
    "-c",
    "to_csv",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        resolve_path=True,
    ),
)
@click.option("--full-console-output", "-f", "full_console_output", is_flag=True)
@click.option("--max-read", "-m", "max_read", type=int, default=0)
@click.option("--batch-size", "-b", "start_limit", type=int, default=0)
@click.option("--offset", "-o", "start_offset", type=int, default=0)
def muscle_action(
    experiment_id,
    experiment_run_id,
    experiment_run_instance_id,
    experiment_run_phase_id,
    to_csv=None,
    full_console_output=False,
    max_read=0,
    start_limit=0,
    start_offset=0,
):
    read_muscle_actions(
        experiment_id=experiment_id,
        experiment_run_id=experiment_run_id,
        experiment_run_instance_id=experiment_run_instance_id,
        experiment_run_phase_id=experiment_run_phase_id,
        to_csv=to_csv,
        full_console_output=full_console_output,
        max_read=max_read,
        start_limit=start_limit,
        start_offset=start_offset,
    )
