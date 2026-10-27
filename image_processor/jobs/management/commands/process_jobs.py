import logging
import time

from django.core.management.base import BaseCommand
from jobs.services.job_processor import claim_next_job, process_job

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Process pending image-processing jobs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--once",
            action="store_true",
            help="Process available jobs and exit",
        )

        parser.add_argument(
            "--interval",
            type=int,
            default=10,
            help="Polling interval in seconds",
        )

    def handle(self, *args, **options):
        once = options["once"]
        interval = options["interval"]

        if interval < 1:
            raise ValueError("Interval must be at least 1 second")

        self.stdout.write(
            self.style.SUCCESS(
                "Image processing worker started"
            )
        )

        while True:
            job = claim_next_job()

            if job is not None:
                process_job(job)
                continue

            if once:
                break

            time.sleep(interval)
