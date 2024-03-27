"""This script is used to create a worker that listens for tasks from the
gearman server."""
import json

from python3_gearman import GearmanWorker

from app.core.config import settings
from scripts.service_entry import process_start

# Initialize gearman worker
worker = GearmanWorker([f"{settings.GEARMAN_HOST}:{settings.GEARMAN_PORT}"])


def import_task_listener(task_id: str, gearman_job: str):
    """This function listens for tasks from the gearman server and processes
    them.

    Args:
        task_id (str): The task id
        gearman_job (str): The gearman job

    Returns:
        str: The status of the task
    """
    print(task_id)
    file_id = json.dumps(gearman_job.data)

    process_start(file_id)

    print("Completed!!!")
    return "success"


worker.set_client_id("imports-worker")
worker.register_task("imports", import_task_listener)


def main():
    """This function starts the worker."""
    print("Starting worker...")
    worker.work()


if __name__ == "__main__":
    main()
