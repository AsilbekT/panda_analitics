# yourapp/management/commands/restart_celery.py

from django.core.management.base import BaseCommand
import subprocess

class Command(BaseCommand):
    help = 'Restarts Celery workers for analytics service with custom hostname and queue'

    def handle(self, *args, **kwargs):
        # Define the custom hostname and queue for analytics service
        custom_hostname = "analitics_worker@%h"  # %h will be replaced with the actual host
        custom_queue = "analitics_queue"

        # Stop existing Celery workers if needed
        # Note: Implement a way to gracefully stop your existing workers.
        # It could be using PID files, supervisord, or any other method suitable for your deployment

        # Start new Celery workers for analytics service
        subprocess.run(["screen", "-d", "-m", "celery", "-A", "analitics_service",
                        "worker", "-l", "info",
                        "--hostname", custom_hostname,
                        "-Q", custom_queue])
        self.stdout.write(self.style.SUCCESS(
            'Successfully restarted Celery workers for analytics service'))
