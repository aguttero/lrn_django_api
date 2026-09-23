"""
Django command to wait for the database to be available.
"""

import time

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError  # django error > DB is not ready
from psycopg2 import (
    OperationalError as Psycopg2OpError,
)
# Psycopg2 error when DB is not ready.
# Renamed to OpError avoid name confusion with the django error


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        # pass
        """Entrypoint for command."""
        # stdout -> prints to console
        self.stdout.write("Waiting for database...")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=["default"])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)  # Wait for 1 second

        self.stdout.write(self.style.SUCCESS("Database available!"))
