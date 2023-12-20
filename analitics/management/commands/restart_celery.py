# yourapp/management/commands/restart_celery.py

from django.core.management.base import BaseCommand
import subprocess


class Command(BaseCommand):
    help = 'Restarts Celery workers with new names'

    def handle(self, *args, **kwargs):
        # Stop existing workers
        subprocess.run(["pkill", "-9", "celery"])

        # Start new workers with new names
        subprocess.run(["celery", "-A", "analitics_service",
                       "worker", "-l", "info", "--hostname=new_worker_name@%h"])

        self.stdout.write(self.style.SUCCESS(
            'Successfully restarted Celery workers with new names'))
