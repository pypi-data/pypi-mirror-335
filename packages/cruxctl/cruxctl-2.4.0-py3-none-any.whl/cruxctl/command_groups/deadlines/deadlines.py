import yaml
import logging
import warnings
from pathlib import Path

import typer
from rich.console import Console
from typing_extensions import Annotated

from cruxctl.command_groups.deadlines import deadlines_snooze
from cruxctl.command_groups.deadlines.dataset_deadline_client import (
    DatasetDeadlineClient,
    DeadlineRecommendationClient,
)
from cruxctl.command_groups.profile.profile import get_current_profile
from cruxctl.common.models.data_format import DataFormat
from cruxctl.command_groups.deadlines.deadline_validations import (
    csv_file_validation,
)

from cruxctl.common.typer_constants import PROFILE_OPTION, LISTING_LIMIT_OPTION
from cruxctl.common.utils.api_utils import set_api_token
from crux_odin.dict_utils import yaml_file_to_dict
from crux_odin.types.deadlines import (
    DeadlineMinute,
    DeadlineHour,
    DeadlineDayOfMonth,
    DeadlineMonth,
    DeadlineDayOfWeek,
    DeadlineYear,
    FileFrequency,
    Timezone,
)
from cruxctl.common.utils.schedule_utils import (
    OperationMode,
    process_recommended_deadline,
    normalize_frequencies,
    partition_cron,
    delete_existing_deadline_prompt,
    create_custom_deadline,
    apply_recommended_deadline_prompt,
)

app = typer.Typer()
app.registered_commands += deadlines_snooze.app.registered_commands

console = Console()

warnings.filterwarnings("ignore")


@app.command("get-all")
def get_all(
    limit: Annotated[int, LISTING_LIMIT_OPTION] = 100,
    output_format: Annotated[
        DataFormat,
        typer.Option(
            "--output-format",
            "-o",
            case_sensitive=False,
            help="The output display format",
        ),
    ] = DataFormat.table,
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Lists all delivery deadline entries
    """
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)

    console.print(
        DatasetDeadlineClient().get_all_deadlines(
            profile=profile, token=token, limit=limit, output_format=output_format
        )
    )


@app.command()
def get(
    dataset_id: Annotated[str, typer.Argument(help="Dataset ID to get for")],
    output_format: Annotated[
        DataFormat,
        typer.Option(
            "--output-format",
            "-o",
            case_sensitive=False,
            help="The output display format",
        ),
    ] = DataFormat.table,
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Gets the delivery deadline entries matching the dataset ID
    """
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)

    console.print(
        DatasetDeadlineClient().get_all_deadlines(
            profile=profile,
            token=token,
            output_format=output_format,
            dataset_id=dataset_id,
        )
    )


@app.command()
def insert(
    file_path: Annotated[
        Path, typer.Option("--file", "-f", help="Path to the ODIN dataset spec")
    ],
    deadline_minute: Annotated[
        DeadlineMinute,
        typer.Option(
            "--deadline-minute",
            "-min",
            help="Minute of the delivery deadline. Allowed values: 0-59.",
        ),
    ] = None,
    deadline_hour: Annotated[
        DeadlineHour,
        typer.Option(
            "--deadline-hour",
            "-hr",
            help=(
                "Hour of the delivery deadline. Allowed values: 0-23. "
                "Leave * if expected every hour."
            ),
        ),
    ] = None,
    deadline_day_of_month: Annotated[
        DeadlineDayOfMonth,
        typer.Option(
            "--deadline-day-of-the-month",
            "-dom",
            help=(
                "Day of the month delivery deadline. Allowed values: 1-31. "
                "Leave * if expected every day."
            ),
        ),
    ] = None,
    deadline_month: Annotated[
        DeadlineMonth,
        typer.Option(
            "--deadline-month",
            "-m",
            help=(
                "Month of the delivery deadline. Allowed values: 1-12."
                " Leave * if expected every month."
            ),
        ),
    ] = None,
    deadline_day_of_week: Annotated[
        DeadlineDayOfWeek,
        typer.Option(
            "--deadline-day-of-week",
            "-dow",
            help=(
                "Day of the week delivery deadline. Allowed values: 0-6."
                " Leave * if expected every day."
            ),
        ),
    ] = None,
    deadline_year: Annotated[
        DeadlineYear,
        typer.Option(
            "--deadline-year",
            "-y",
            help=(
                "Selected year. Will most likely be * as"
                " deliveries are expected every year."
            ),
        ),
    ] = None,
    file_frequency: Annotated[
        FileFrequency,
        typer.Option(
            "--file-frequency",
            "-freq",
            help="Frequency of the file. Example values: daily, weekly, monthly, yearly",
        ),
    ] = None,
    timezone: Annotated[
        Timezone,
        typer.Option(
            "--timezone",
            "-tz",
            help="Timezone for the deadline",
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            is_flag=True,
            help=(
                "Force apply the custom deadline even if it conflicts "
                "with existing ones, and will bypass the additional "
                "recommendation sequence. Note that a custom deadline "
                "must be provided for this option to be applicable."
            ),
        ),
    ] = False,
    mode: Annotated[
        OperationMode,
        typer.Option(
            "--mode",
            help=(
                "Mode to apply the custom deadline when '--force' is used. "
                "'replace' to replace existing deadlines or 'append' to add "
                "to existing deadlines. This is only applicable if '--force' "
                "is also applied."
            ),
            case_sensitive=False,
        ),
    ] = "append",
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Inserts a single delivery deadline
    """
    custom_deadline = None
    recommended_deadline = None
    existing_deadlines = []
    recommended_deadlines = []
    if not profile:
        profile = get_current_profile()

    custom_deadline_parameters = {
        "deadline_minute": deadline_minute,
        "deadline_hour": deadline_hour,
        "deadline_day_of_month": deadline_day_of_month,
        "deadline_month": deadline_month,
        "deadline_day_of_week": deadline_day_of_week,
        "deadline_year": deadline_year,
        "file_frequency": file_frequency,
        "timezone": timezone,
    }
    if all(param is not None for param in custom_deadline_parameters.values()):
        custom_deadline = create_custom_deadline(**custom_deadline_parameters)
    elif any(param is not None for param in custom_deadline_parameters.values()):
        missing_params = [
            param
            for param, value in custom_deadline_parameters.items()
            if value is None
        ]
        if missing_params:
            raise ValueError(
                f"Missing deadline parameters: {', '.join(missing_params)}"
            )

    # Suppress logging
    logging.getLogger().setLevel(logging.ERROR)
    workflow = yaml_file_to_dict(str(file_path))
    if "availability_deadlines" in workflow:
        existing_deadlines = [
            create_custom_deadline(**deadline)
            for deadline in workflow["availability_deadlines"]
        ]
    else:
        workflow["availability_deadlines"] = existing_deadlines

    if force:
        if not custom_deadline:
            console.print(
                "Warning: --force option is set but no custom deadline is provided; "
                "the --force flag will not be applied.",
                style="yellow",
            )
        else:
            if mode == "append":
                workflow["availability_deadlines"].append(custom_deadline)
            elif mode == "replace":
                workflow["availability_deadlines"] = [custom_deadline]
    else:
        token = set_api_token(console, profile)
        deadline_client = DeadlineRecommendationClient()
        recommended_deadline = deadline_client.get_recommended_deadline(
            profile=profile,
            token=token,
            dataset_id=workflow["metadata"]["dataset_id"],
        )
        if recommended_deadline:
            file_frequency = normalize_frequencies(
                recommended_deadline.get("cadence_processing_end")
            )
            timezone = recommended_deadline.get("user_timezone")
            recommended_deadline = process_recommended_deadline(recommended_deadline)
            recommended_deadline_partitions = partition_cron(recommended_deadline)
            for recommended_deadline in recommended_deadline_partitions:
                recommended_deadline_parts = recommended_deadline.split(" ")
                recommended_deadline = create_custom_deadline(
                    deadline_minute=recommended_deadline_parts[0],
                    deadline_hour=recommended_deadline_parts[1],
                    deadline_day_of_month=recommended_deadline_parts[2],
                    deadline_month=recommended_deadline_parts[3],
                    deadline_day_of_week=recommended_deadline_parts[4],
                    deadline_year=recommended_deadline_parts[5],
                    file_frequency=file_frequency,
                    timezone=timezone,
                )
                recommended_deadlines.append(recommended_deadline)
        existing_deadlines.sort()
        recommended_deadlines.sort()

        def handle_deadlines(existing, recommended, custom_params):
            if existing:
                if delete_existing_deadline_prompt(console, existing_deadlines):
                    workflow["availability_deadlines"] = []
            if recommended:
                if apply_recommended_deadline_prompt(console, recommended_deadlines):
                    workflow["availability_deadlines"].extend(recommended_deadlines)
                    return
            console.print("Please enter the details for the new deadline:")
            custom_deadline = create_custom_deadline(**custom_params)
            workflow["availability_deadlines"].append(custom_deadline)

        handle_deadlines(
            existing_deadlines, recommended_deadlines, custom_deadline_parameters
        )
    workflow["availability_deadlines"] = [
        deadline if isinstance(deadline, dict) else deadline.__dict__
        for deadline in workflow["availability_deadlines"]
    ]
    with open(file_path, "w") as file:
        yaml.dump(workflow, file, sort_keys=False)
    console.print("[green]Deadline configuration updated successfully.[/green]")
    logging.getLogger().setLevel(logging.INFO)


@app.command("import")
def bulk_import(
    ctx: typer.Context,
    file_path: Annotated[
        Path,
        typer.Argument(
            help="""
    Path to CSV file to import.\n
    The CSV must have a header with the following columns:\n
    dataset_id, deadline_minute, deadline_hour, deadline_day_of_month,
    deadline_month, deadline_day_of_week, deadline_year, timezone.\n
    [bold yellow]WARNING[/bold yellow]: No validation is performed on the CSV file.
    It is assumed that the content is valid and entries are deduplicated.
    """
        ),
    ],
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Imports a CSV file with the delivery deadline entries.
    """
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)

    csv_file_validation(ctx, profile, file_path, token=token)

    DatasetDeadlineClient().bulk_insert_deadlines(
        profile, file_path=str(file_path), token=token
    )
    console.print("[green]Import completed successfully[/green]")


@app.command("export")
def bulk_export(
    file_path: Annotated[
        Path, typer.Argument(help="Path to CSV file to write data in locally")
    ],
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Exports a CSV file with all the delivery deadlines to the provided local path
    """
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)

    DatasetDeadlineClient().export_to_local_file(
        profile, file_path=str(file_path), token=token
    )
    console.print("[green]Export completed successfully[/green]")


@app.command()
def delete(
    id: Annotated[str, typer.Argument(help="ID to match for deletion")],
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Deletes the delivery deadline entries with the given ID
    """
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)

    DatasetDeadlineClient().delete_deadline_by_id(profile, token, id)
    console.print(f"[green]Deleted entry with ID: {id}[/green]")


@app.command("dataset-delete")
def dataset_delete(
    dataset_id: Annotated[str, typer.Argument(help="dataset_id to match for deletion")],
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Deletes the delivery deadline entries with the given dataset_id
    """
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)

    deadlines_by_dataset_id = DatasetDeadlineClient().get_all_deadlines(
        profile, token, dataset_id=dataset_id, output_format=DataFormat.json, limit=-1
    )

    console.print(deadlines_by_dataset_id)

    is_delete = typer.confirm(
        "Above are the entries matching with dataset_id, do you want to delete them?",
        default=False,
    )
    if is_delete:
        for deadline in deadlines_by_dataset_id:
            DatasetDeadlineClient().delete_deadline_by_id(
                profile, token, deadline["id"]
            )
        console.print(f"[green]Deleted entries with dataset ID: {dataset_id}[/green]")
    else:
        console.print("[red]No entries were deleted[/red]")


@app.command("bulk-delete")
def bulk_delete(
    file_path: Annotated[
        Path, typer.Argument(help="Path to CSV file to write data in locally")
    ],
    profile: Annotated[str, PROFILE_OPTION] = None,
):
    """
    Delete all deadlines from a CSV file. The deadlines are to be defined by the
     ID of the deadline record (which is a UUID), NOT the dataset's ID. The CSV
     file should have a single "id" column with the header included.
    """
    if not profile:
        profile = get_current_profile()
    token = set_api_token(console, profile)

    DatasetDeadlineClient().delete_deadlines_from_csv(
        profile, file_path=str(file_path), token=token
    )
    console.print("[green]Deadlines deleted successfully[/green]")
