from orbis.data.models import WorkerQueueStats

"""Worker queue utilities for Orbis.

This module handles worker queue metrics for Celery queues. Unlike pod types,
worker queues are dynamic:
- Number of queues can vary (0 to many)
- Queue names are not known beforehand
- Queue configuration comes from runtime

Due to this dynamic nature, we modify queries to handle all queues within
a single metric rather than creating separate metrics for each queue.
"""


def replace_worker_pattern(base_query: str, queue_name: str) -> str:
    """Replace worker pattern in a query with a specific queue name.

    Since worker queues are dynamic, we use pattern replacement to modify
    queries at runtime rather than creating separate metrics.

    Args:
        base_query: The original query containing 'worker-.*' pattern
        queue_name: Name of the queue to replace with

    Returns:
        str: Query with worker pattern replaced

    Examples:
        >>> replace_worker_pattern('pod=~"namespace-worker-.*"', 'default')
        'pod=~"namespace-worker-default-.*"'
    """
    return base_query.replace("worker-.*", f"worker-{queue_name}-.*")


def update_queries_with_queues(base_query: str, worker_queues: list[WorkerQueueStats]) -> list[str]:
    """Update a base query with worker queue patterns.

    Unlike pod types which have fixed conditions and create separate metrics,
    worker queues are handled by generating multiple queries within the same
    metric. This approach works better for dynamic queue configurations.

    Args:
        base_query: The original query containing 'worker-.*' pattern
        worker_queues: List of worker queue configurations as dicts with queue_name key

    Returns:
        List[str]: List of queries, one for each worker queue

    Examples:
        >>> update_queries_with_queues('pod=~"ns-worker-.*"', [{'queue_name': 'default'}])
        ['pod=~"ns-worker-default-.*"']
    """
    return [replace_worker_pattern(base_query, queue.queue_name) for queue in worker_queues]
