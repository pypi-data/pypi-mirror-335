import asyncio
import shutil
from importlib.metadata import version

import click
import requests
import urllib3
from pendulum import from_format

from orbis.api import houston
from orbis.config import (
    SOFTWARE_QUERIES_FILE_PATH,
    parse_yaml,
    validate_input_args,
)
from orbis.data.models import ReportMetadata
from orbis.report.generator import generate_report
from orbis.utils.fileio import compress_output_files, create_output_folder, perform_cleanup
from orbis.utils.logger import get_logger, update_early_logger_level

# Suppress InsecureRequestWarning when SSL verification is disabled
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def display_input_arguments(start_date, end_date, organization_id, clusters=None, workspaces=None):
    """Display input arguments."""
    click.echo(f"Input Arguments:\nStart Date: {start_date}\nEnd Date: {end_date}\nOrganization ID: {organization_id}")
    if clusters:
        click.echo(f"Clusters: {clusters}")
    if workspaces:
        click.echo(f"Workspaces: {workspaces}")


def get_version():
    """Get orbis version."""
    try:
        return version("astronomer-orbis")
    except Exception:
        return "unknown"


@click.group(help="Orbis CLI for generating deployment compute reports.", context_settings={"max_content_width": shutil.get_terminal_size().columns - 10})
@click.version_option(version=get_version(), prog_name="orbis")
@click.pass_context
def cli(ctx):
    ctx.max_content_width = 200
    if ctx.invoked_subcommand is None:
        click.echo("Orbis CLI")
        click.echo("\nAvailable commands:")
        click.echo("  compute-astro     Generate deployment compute reports for Astro")
        click.echo("  compute-software  Generate deployment compute reports for Astronomer Software")
        ctx.exit(0)


@cli.command(name="version")
def version_cmd():
    """Show orbis version."""
    click.echo(f"orbis, version {get_version()}")


@cli.command(name="compute-software")
@click.option("-s", "--start_date", required=True, help="Start Date. Format: YYYY-MM-DD")
@click.option("-e", "--end_date", required=True, help="End Date. Format: YYYY-MM-DD")
@click.option("-o", "--organization_id", required=True, help="Organization ID")
@click.option("-v", "--verbose", count=True, help="Increase verbosity (use -v, -vv, or -vvv for more detailed logging)")
@click.option("-w", "--workspaces", default="", help="Comma-separated list of workspace IDs")
@click.option("-r", "--resume", is_flag=True, help="Resume from previous run")
@click.option("-z", "--compress", is_flag=True, help="Create compressed output of HTML, CSV, and JSON files")
@click.option("-p", "--persist", is_flag=True, help="Persist temporary generated images/files in the output folder")
@click.option("-u", "--url", default="", help="Pre-signed URL (in quotes) to upload report")
@click.option("--verify-ssl", default=True, type=bool, help="Disable SSL verification for requests")
@click.pass_context
def compute_software(ctx, start_date, end_date, organization_id, verbose, workspaces, resume, compress, persist, url, clusters=False, verify_ssl=True):
    """Generate deployment compute reports for Astronomer Software."""
    generate_report_common(ctx, start_date, end_date, organization_id, verbose, clusters, workspaces, resume, compress, persist, url, verify_ssl=verify_ssl)


def generate_report_common(ctx, start_date, end_date, organization_id, verbose, clusters, workspaces, resume, compress, persist, url, verify_ssl=True):
    if not all([start_date, end_date, organization_id]):
        click.echo("Error: start_date, end_date, and organization_id are required.")
        ctx.exit(1)

    # Update early logger level based on verbosity
    update_early_logger_level(verbose)

    start_date = from_format(start_date, "YYYY-MM-DD")
    end_date = from_format(end_date, "YYYY-MM-DD")

    workspaces = [workspace for workspace in workspaces.strip().split(",") if workspace]
    display_input_arguments(start_date, end_date, organization_id, workspaces=workspaces)

    click.echo("Validating input arguments...")
    validate_input_args(organization_id, start_date, end_date)
    click.clear()

    generate_software_report(start_date, end_date, organization_id, verbose, workspaces, resume, compress, persist, url, verify_ssl=verify_ssl)


def generate_software_report(start_date, end_date, organization_id, verbose, workspaces, resume, compress, persist, url, verify_ssl=True):
    organization_domain = organization_id
    display_input_arguments(start_date, end_date, organization_domain, workspaces=workspaces)
    try:
        organization_domain, namespaces, executor_types = houston.get_organization_metadata(base_domain=organization_domain, workspaces=workspaces, verify_ssl=verify_ssl)
    except Exception as e:
        click.echo(e)
        click.echo("Error occurred while fetching organization metadata. Please verify Token and Organization ID.")
        return

    if not namespaces:
        click.echo("No deployments found for the given organization. Please verify Organization ID and Workspace IDs.")
        return

    click.echo(f"Output folder: {organization_domain}")
    output_folder = create_output_folder(organization_domain)

    logger = get_logger("root", f"{output_folder}/{organization_domain}.log", verbose)
    logger.info("Generating report for Organization Domain: %s", organization_domain)
    logger.info("Start Date: %s", start_date)
    logger.info("End Date: %s", end_date)
    logger.info("Workspaces: %s", workspaces)

    click.echo(f"Generating report for {len(namespaces)} deployments under Organization Domain: {organization_domain}")

    generate_report_with_progress(organization_domain, start_date, end_date, namespaces, executor_types, resume, compress, persist, url, verify_ssl=verify_ssl)


def generate_report_with_progress(organization_name, start_date, end_date, namespaces, executor_types, resume, compress, persist, url, verify_ssl=True):
    total_steps = calculate_total_steps(namespaces, executor_types)
    with click.progressbar(length=total_steps, label="Processing") as bar:

        def update_progress():
            bar.update(1)

        metadata = ReportMetadata(organization_name=organization_name, start_date=start_date, end_date=end_date, namespaces=namespaces)

        asyncio.run(generate_report(metadata, executor_types, progress_callback=update_progress, is_resume=resume, verify_ssl=verify_ssl))

    click.clear()
    display_input_arguments(start_date, end_date, organization_name)
    click.echo(f"Generating report for {len(namespaces)} deployments under Organization: {organization_name}")
    bar.update(total_steps)
    click.echo("\nReport generated successfully. Find report under the output folder.")

    if compress or url:
        compressed_zip_file = compress_output_files(organization_name)
        click.echo("Report compressed successfully.")
        if url:
            click.echo("Uploading report...")
            payload = {"package": ("orbis_reports.zip", open(compressed_zip_file, "rb"), "application/zip")}
            requests.put(url=url, files=payload, timeout=300)
            click.echo("Report uploaded successfully.")

    if not persist:
        perform_cleanup(create_output_folder(organization_name), namespaces)


def calculate_total_steps(namespaces, executor_types):
    total_steps = 0

    # Parse the YAML queries file
    queries_file_path = SOFTWARE_QUERIES_FILE_PATH
    parsed_yaml_queries = parse_yaml(file_name=queries_file_path)

    # Count scheduler metrics (common for all)
    scheduler_metrics = len(parsed_yaml_queries.get("scheduler", {}))

    # Count non-reporting metrics
    non_reporting_metrics = sum(1 for key in ["total_task_success", "total_task_failure"] if key in parsed_yaml_queries)

    # Count executor-specific metrics
    ke_metrics = len(parsed_yaml_queries.get("ke", {}))
    celery_metrics = len(parsed_yaml_queries.get("celery", {}))

    for namespace in namespaces:
        executor = executor_types[namespace].executor
        if executor.lower() == "kubernetes":
            # Add KE metrics and scheduler metrics
            total_steps += ke_metrics + scheduler_metrics + non_reporting_metrics
        elif executor.lower() == "celery":
            # Add Celery metrics and scheduler metrics
            total_steps += celery_metrics + scheduler_metrics + non_reporting_metrics

    return total_steps


if __name__ == "__main__":
    cli()
