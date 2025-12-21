import time
from django.core.management import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        connected = False
        while not connected:
            try:
                db_conn = connections["default"]
                # This is the line that actually checks the connection
                db_conn.ensure_connection()
                connected = True
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Successfully connected to PostgreSQL"))
