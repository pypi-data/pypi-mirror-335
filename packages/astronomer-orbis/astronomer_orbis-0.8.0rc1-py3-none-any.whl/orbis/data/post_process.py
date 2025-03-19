import csv
import glob
import json
import os
from typing import Any

from orbis.data.models import MetricCalculation, NamespaceReport, PodStats, WorkerQueueStats
from orbis.report.csv.pods import post_process_kpo_pod_stats
from orbis.report.csv.queues import process_worker_queues_stats as get_worker_rows


def read_json_file(json_path: str) -> dict[str, Any]:
    """Read and parse JSON file."""
    with open(json_path) as f:
        return json.load(f)


def read_csv_headers(csv_path: str) -> list[str]:
    """Read CSV headers to understand the structure."""
    with open(csv_path) as f:
        reader = csv.reader(f)
        return next(reader)


def parse_scheduler_au(scheduler_au: str) -> tuple[float, float]:
    """Parse scheduler AU value and return CPU (vCPU) and Memory (GiB).

    Args:
        scheduler_au: String value that can be either a number or a descriptive string

    Returns:
        tuple[float, float]: (CPU in vCPU, Memory in GiB)
    """
    try:
        # Case 1: Simple number (e.g., "10")
        au_value = float(scheduler_au)
        return (au_value * 0.1, au_value * 0.384)  # 1 AU = 0.1 vCPU, 0.384 GiB
    except ValueError:
        # Case 2: Descriptive string (e.g., "1 vCPU, 4 GiB")
        try:
            # Extract CPU value
            cpu_part = scheduler_au.split(",")[0].strip()
            cpu_value = float(cpu_part.split()[0])  # Extract number from "1 vCPU"

            # Extract Memory value and convert to MiB
            mem_part = scheduler_au.split(",")[1].strip()
            mem_value = float(mem_part.split()[0])  # Extract number from "4 GiB"
            mem_mib = mem_value

            return (cpu_value, mem_mib)
        except (ValueError, IndexError):
            # If parsing fails, return zeros
            return (0.0, 0.0)


# Load worker type mapping
WORKER_MAP = {}
with open("worker_map.json") as f:
    worker_map_data = json.load(f)
    # Flatten the mapping for easier lookup
    for provider, machines in worker_map_data.items():
        for machine, specs in machines.items():
            WORKER_MAP[machine] = specs


def find_closest_machine_type(target_cpu: float, target_memory: float) -> str:
    """Find the closest matching machine type based on CPU and memory requirements.

    Args:
        target_cpu: Target CPU cores
        target_memory: Target memory in GB

    Returns:
        str: Machine type name or empty string if no match found
    """
    if target_cpu <= 0 or target_memory <= 0:
        return ""

    # Calculate differences for each machine type
    differences = []
    for type_name, specs in WORKER_MAP.items():
        # Skip if machine type is too small
        if specs["cpu"] < target_cpu * 0.8 or specs["mem"] < target_memory * 0.8:
            continue

        # Calculate weighted difference (CPU is more important)
        cpu_diff = abs(specs["cpu"] - target_cpu)
        mem_diff = abs(specs["mem"] - target_memory)
        total_diff = (cpu_diff * 2) + mem_diff  # CPU has double weight

        differences.append((total_diff, type_name))

    # Sort by difference and return the closest match
    differences.sort()
    return differences[0][1] if differences else ""


def get_machine_specs(machine_type: str) -> tuple[float, float]:
    """Get CPU and memory specs for a machine type.

    Args:
        machine_type: Machine type string (e.g. 'm5.xlarge' or 'A5')

    Returns:
        tuple[float, float]: (CPU cores, Memory in GB)
    """
    if not machine_type or machine_type == "N/A" or machine_type == "default":
        return 0.0, 0.0

    specs = WORKER_MAP.get(machine_type, {})
    return float(specs.get("cpu", 0.0)), float(specs.get("mem", 0.0))


def parse_memory_value(mem_str: str) -> float:
    """Parse memory value from string with units.
    Converts GiB to GB (1 GiB = 1.074 GB)
    """
    try:
        if not mem_str:
            return 0.0
        value = float(mem_str.split()[0])
        unit = mem_str.split()[1].lower()
        if "gib" in unit:
            # Convert GiB to GB
            return value * 1.074
        return value
    except (IndexError, ValueError) as e:
        print(f"Error parsing memory value '{mem_str}': {e}")
        return 0.0


def parse_cpu_value(cpu_str: str) -> float:
    """Parse CPU value from string with units."""
    try:
        if not cpu_str:
            return 0.0
        return float(cpu_str.split()[0])
    except (IndexError, ValueError) as e:
        print(f"Error parsing CPU value '{cpu_str}': {e}")
        return 0.0


def parse_worker_type(worker_type: Any) -> tuple[str, float, float]:
    """Parse worker type into machine type, CPU, and memory.

    Input can be one of:
    1. {'machinetype': 'm5.xlarge'} (cloud deployment)
    2. {'Memory': '4 GiB', 'CPU': '2 vCPU'} (software deployment)
    3. 'm5.xlarge' (direct machine type string)
    4. 'Memory 4 GiB, CPU 2 vCPU' (software deployment string)

    Returns:
        tuple[str, float, float]: (machine_type, cpu_cores, memory_gb)
    """
    machine_type = ""
    cpu = 0.0
    memory = 0.0

    if not worker_type:
        return machine_type, cpu, memory

    if isinstance(worker_type, dict):
        # Handle dictionary format
        if "machinetype" in worker_type and worker_type["machinetype"]:
            # Cloud deployment with non-empty machine type
            machine_type = worker_type["machinetype"]
        elif "Memory" in worker_type or "CPU" in worker_type:
            # Software deployment
            memory = parse_memory_value(worker_type.get("Memory", ""))
            cpu = parse_cpu_value(worker_type.get("CPU", ""))
    elif isinstance(worker_type, str):
        # Handle string format (legacy)
        if "Memory" in worker_type and "CPU" in worker_type:
            # Software deployment format: "Memory 4 GiB, CPU 2 vCPU"
            try:
                mem_str = worker_type.split(",")[0].replace("Memory", "").strip()
                memory = parse_memory_value(mem_str)

                cpu_str = worker_type.split(",")[1].replace("CPU", "").strip()
                cpu = parse_cpu_value(cpu_str)
            except (IndexError, ValueError) as e:
                print(f"Error parsing worker type string: {e}")
        else:
            # Cloud deployment format: direct machine type
            machine_type = worker_type.strip()

    print(f"Parsed worker type: machine_type='{machine_type}', cpu={cpu}, memory={memory}")
    return machine_type, cpu, memory


def extract_data_from_json(namespace_report: dict[str, Any]) -> dict[str, Any]:
    """Extract both string and numerical data from a namespace report."""
    data = {"Deployment Name": namespace_report["name"], "Deployment Name Space": namespace_report["namespace"], "executor": namespace_report["executor_type"]}

    # Process metrics
    for metric in namespace_report.get("metrics", []):
        metric_name = metric["metric_name"].lower().replace(" ", "_")

        # Handle scheduler metrics
        if metric_name == "scheduler_cpu":
            data.update({
                "scheduler_metrics.avg_scheduler_cpu (vCPU)": metric["mean_value"],
                "scheduler_metrics.max_scheduler_cpu (vCPU)": metric["max_value"],
                "scheduler_metrics.p90_scheduler_cpu (vCPU)": metric["p90_value"],
            })
        elif metric_name == "scheduler_memory":
            data.update({
                "scheduler_metrics.avg_scheduler_mem (GB)": metric["mean_value"],
                "scheduler_metrics.max_scheduler_mem (GB)": metric["max_value"],
                "scheduler_metrics.p90_scheduler_mem (GB)": metric["p90_value"],
            })
        # Handle worker metrics
        elif metric_name == "ke_cpu":
            data.update({
                "worker_metrics.avg_worker_cpu (vCPU)": metric["mean_value"],
                "worker_metrics.max_worker_cpu (vCPU)": metric["max_value"],
                "worker_metrics.p90_worker_cpu (vCPU)": metric["p90_value"],
            })
        elif metric_name == "ke_memory":
            data.update({
                "worker_metrics.avg_worker_mem (GB)": metric["mean_value"],
                "worker_metrics.max_worker_mem (GB)": metric["max_value"],
                "worker_metrics.p90_worker_mem (GB)": metric["p90_value"],
            })
        # Handle task metrics
        elif metric_name == "total_task_success":
            data["Total Task Success"] = metric["last_value"]
        elif metric_name == "total_task_failure":
            data["Total Task Failure"] = metric["last_value"]

    # Add other numerical fields
    if namespace_report.get("scheduler_replicas"):
        data["scheduler_replicas"] = namespace_report["scheduler_replicas"]

    # Convert scheduler_au to CPU and Memory
    if namespace_report.get("scheduler_au"):
        cpu_value, mem_value = parse_scheduler_au(namespace_report["scheduler_au"])
        data["Scheduler Conf CPU (vCPU)"] = cpu_value
        data["Scheduler Conf Mem (GiB)"] = mem_value
    else:
        data["Scheduler Conf CPU (vCPU)"] = 0.0
        data["Scheduler Conf Mem (MiB)"] = 0.0

    return data


def create_worker_queue_stats(stat_dict: dict[str, Any]) -> WorkerQueueStats:
    """Convert dictionary to WorkerQueueStats object."""
    return WorkerQueueStats(
        queue_name=stat_dict["queue_name"],
        mean_value=stat_dict["mean_value"],
        median_value=stat_dict["median_value"],
        max_value=stat_dict["max_value"],
        min_value=stat_dict["min_value"],
        p90_value=stat_dict["p90_value"],
        worker_type=stat_dict.get("worker_type"),
        worker_concurrency=stat_dict.get("worker_concurrency"),
        min_workers=stat_dict.get("min_workers"),
        max_workers=stat_dict.get("max_workers"),
    )


def create_pod_stats(stat_dict: dict[str, Any]) -> PodStats:
    """Convert dictionary to PodStats object."""
    return PodStats(
        pod_type=stat_dict["pod_type"],
        mean_value=stat_dict["mean_value"],
        median_value=stat_dict["median_value"],
        max_value=stat_dict["max_value"],
        min_value=stat_dict["min_value"],
        p90_value=stat_dict["p90_value"],
    )


def create_metric_calculation(metric_dict: dict[str, Any]) -> MetricCalculation:
    """Convert dictionary to MetricCalculation object."""
    # Convert worker queue stats if present
    worker_queue_stats = None
    if metric_dict.get("worker_queue_stats"):
        worker_queue_stats = [create_worker_queue_stats(stat) for stat in metric_dict["worker_queue_stats"]]

    # Convert pod stats if present
    pod_stats = None
    if metric_dict.get("pod_stats"):
        pod_stats = [create_pod_stats(stat) for stat in metric_dict["pod_stats"]]

    return MetricCalculation(
        metric_name=metric_dict["metric_name"],
        mean_value=metric_dict.get("mean_value", 0.0),
        median_value=metric_dict.get("median_value", 0.0),
        max_value=metric_dict.get("max_value", 0.0),
        min_value=metric_dict.get("min_value", 0.0),
        p90_value=metric_dict.get("p90_value", 0.0),
        last_value=metric_dict.get("last_value", 0.0),
        worker_queue_stats=worker_queue_stats,
        pod_stats=pod_stats,
    )


def create_namespace_report(report_dict: dict[str, Any]) -> NamespaceReport:
    """Convert dictionary to NamespaceReport object."""
    # Convert metrics to MetricCalculation objects
    metrics = [create_metric_calculation(metric) for metric in report_dict.get("metrics", [])]

    return NamespaceReport(
        name=report_dict["name"],
        namespace=report_dict["namespace"],
        executor_type=report_dict["executor_type"],
        scheduler_replicas=report_dict.get("scheduler_replicas"),
        scheduler_au=report_dict.get("scheduler_au"),
        metrics=metrics,
    )


def generate_raw_data(json_path: str, csv_path: str, output_path: str):
    """Generate raw data CSV from JSON and CSV template."""
    # Read input files
    json_data = read_json_file(json_path)
    csv_headers = read_csv_headers(csv_path)

    # Required string columns
    string_columns = ["Deployment Name", "Deployment Name Space", "executor"]

    # Filter headers to keep only numerical columns and required string columns
    numerical_headers = [header for header in csv_headers if any(metric in header.lower() for metric in ["metrics", "replicas", "success", "failure"])]

    # Add new scheduler configuration columns
    scheduler_conf_headers = ["Scheduler Conf CPU (vCPU)", "Scheduler Conf Mem (GiB)"]

    # Add worker-related columns
    worker_columns = [
        "Worker Type",  # For cloud deployments (e.g. m5.xlarge)
        "Worker Conf CPU",  # CPU cores (from either machine type or software config)
        "Worker Conf Mem",  # Memory in GB (from either machine type or software config)
        "Worker Queue Name",
        "Worker Concurrency",
        "Min Worker",
        "Max Workers",
        "Worker Size Hosted",
        "Worker Count",
    ]
    required_headers = string_columns + numerical_headers + scheduler_conf_headers + worker_columns

    # Prepare output rows
    rows = []
    for namespace_dict in json_data["namespace_reports"]:
        # Convert dict to NamespaceReport
        namespace_report = create_namespace_report(namespace_dict)
        data = extract_data_from_json(namespace_dict)

        # Create base row with all deployment info
        base_row = {}
        for header in required_headers:
            if header in string_columns:
                base_row[header] = data.get(header, "")
            else:
                base_row[header] = data.get(header, 0.0)

        if data.get("executor") == "CELERY":
            # Get all rows for this deployment (default queue, additional queues, KPO)
            deployment_rows = []

            # Add worker queue rows
            worker_rows = get_worker_rows(namespace_report, base_row)
            if worker_rows:
                # For each worker row, ensure it has all deployment info
                for worker_row in worker_rows:
                    full_row = base_row.copy()

                    # Get worker type from Celery CPU metric
                    celery_cpu_metric = next((m for m in namespace_report.metrics if m.metric_name == "Celery CPU"), None)
                    if celery_cpu_metric and celery_cpu_metric.worker_queue_stats:
                        queue_stat = next((qs for qs in celery_cpu_metric.worker_queue_stats if qs.queue_name == worker_row.get("Worker Queue Name")), None)
                        if queue_stat and hasattr(queue_stat, "worker_type"):
                            # Parse worker type into separate fields
                            machine_type, sw_cpu, sw_memory = parse_worker_type(queue_stat.worker_type)

                            # Get CPU and memory specs from worker_map.json if machine type exists
                            machine_cpu, machine_memory = get_machine_specs(machine_type) if machine_type else (0.0, 0.0)

                            # For software deployment, find closest machine type
                            # For cloud deployment, use provided machine type
                            if not machine_type and (sw_cpu > 0 or sw_memory > 0):
                                # Find closest machine type based on CPU and memory
                                machine_type = find_closest_machine_type(sw_cpu, sw_memory)
                                if machine_type:
                                    machine_cpu, machine_memory = get_machine_specs(machine_type)
                                    worker_row.update({"Worker Type": machine_type, "Worker Conf CPU": machine_cpu, "Worker Conf Mem": machine_memory})
                                else:
                                    # No matching machine type found
                                    worker_row.update({"Worker Type": "", "Worker Conf CPU": sw_cpu, "Worker Conf Mem": sw_memory})
                            else:
                                # Cloud deployment or empty
                                worker_row.update({"Worker Type": machine_type, "Worker Conf CPU": machine_cpu, "Worker Conf Mem": machine_memory})
                    else:
                        # Default values if no worker type found
                        worker_row.update({
                            "Worker Type": "",  # Keep original key from queues.py
                            "Worker Conf CPU": 0.0,
                            "Worker Conf Mem": 0.0,
                        })

                    full_row.update(worker_row)  # Override only worker-specific metrics
                    deployment_rows.append(full_row)
            else:
                # Just add base row with default queue
                base_row.update({"Worker Type": "", "Worker Conf CPU": 0.0, "Worker Conf Mem": 0.0})
                deployment_rows.append(base_row)

            # Add KPO rows if they exist
            kpo_rows = post_process_kpo_pod_stats(namespace_report)
            if kpo_rows:
                # For each KPO row, ensure it has all deployment info
                for kpo_row in kpo_rows:
                    full_row = base_row.copy()
                    full_row.update(kpo_row)  # Override only KPO-specific metrics
                    deployment_rows.append(full_row)

            rows.extend(deployment_rows)
        else:
            # For non-CELERY executors, just add the base row
            rows.append(base_row)

    # Write output CSV
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=required_headers)
        writer.writeheader()
        writer.writerows(rows)


def _find_csv_and_json_file(directory: str) -> tuple[str, str]:
    """Walk the directory and find all CSV and JSON files."""
    csv_files = ""
    json_files = ""

    for file in glob.glob(os.path.join(directory, "**/*.*"), recursive=True):
        if file.endswith(".csv") and not csv_files:
            csv_files = file
        elif file.endswith(".json") and not json_files:
            json_files = file
        if csv_files and json_files:
            break

    return csv_files, json_files


def post_process(output_path: str):
    """Post-process the raw data CSV."""

    csv_files, json_files = _find_csv_and_json_file(output_path)
    print("CSV Files:", csv_files)
    print("JSON Files:", json_files)
