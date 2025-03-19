import os
import sys
from importlib import resources
from typing import Any

import yaml
from dotenv import find_dotenv, load_dotenv
from pendulum.datetime import DateTime

from orbis.utils.logger import get_early_logger

load_dotenv(find_dotenv(), override=True)

SOFTWARE_QUERIES_FILE_PATH = str(resources.files("orbis.config").joinpath("prometheus_queries.yaml"))
HOUSTON_QUERIES_FILE_PATH = str(resources.files("orbis.config").joinpath("houston_queries.yaml"))
CSV_TEMPLATE_PATH = str(resources.files("orbis.config").joinpath("csv_template.csv"))
ASTRO_SOFTWARE_API_TOKEN = os.environ.get("ASTRO_SOFTWARE_API_TOKEN")
KE_QUERIES = "ke"
CELERY_QUERIES = "celery"
SCHEDULER_QUERIES = "scheduler"
COLORS = ["lightgreen", "yellow", "red", "blue", "orange", "purple", "pink", "brown", "cyan", "magenta"]
DECIMAL_PRECISION = 2

logger = get_early_logger()


def validate_input_args(organization_id: str, start_date: DateTime, end_date: DateTime) -> None:
    """Validate input arguments."""
    if not organization_id:
        logger.error("Organization ID is required")
        sys.exit(2)
    if start_date > end_date:
        logger.error("Start Date cannot be greater than End Date")
        sys.exit(2)


def parse_yaml(file_name: str) -> Any:
    """Parse YAML file."""
    with open(file_name, encoding="utf-8") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error("Error while parsing YAML file: %s", exc)
            sys.exit(2)
