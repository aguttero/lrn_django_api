"""
Test custom Django management commands.
"""

from unittest.mock import patch  # To MocK DB behaviour

from django.core.management import call_command  # call the custom command
from django.db.utils import OperationalError
from django.test import SimpleTestCase
from psycopg2 import (
    OperationalError as Psycopg2OpError,
)

# OpError -> django error DB table is not ready
# Psycop error DB is not ready to receive connections,


@patch(
    "core.management.commands.wait_for_db.Command.check"
)  # check method checks if the DB is active -@patch mocks the db behaviour
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready.
        And that the custom command is ok and can be called"""
        patched_check.return_value = (
            True  # The mock returns true,
            # as if the DB service and DB table are up
        )

        call_command("wait_for_db")

        patched_check.assert_called_once_with(
            databases=["default"]
        )  # check that is called once with the
        # these are the parameters to use with the call to the mocked object
        # (which is the .check in this case)

    @patch(
        "time.sleep"
    )  # wait for a set period of time before calling the command each time
    # We are moking sleep so it does not actually wait to test the test
    # it returns a 'None' value every time we call it
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError."""
        # side effect returns different values that handle differently
        # depending on their type: exception -> exception / Boolean -> Boolean
        patched_check.side_effect = (
            [Psycopg2OpError] * 2 + [OperationalError] * 3 + [True]
        )
        # simulates DB service +  DB table startaup.
        # First 2 times - Raises Psycop2Op Error
        # Postgres nos ready to receive connections
        # Next 3 times - Raises Operational Error
        # Postgres ready to receive connections but has not setup the
        # test DB yet
        # 6th time - returns True: DB service and Test DB ready
        # These numbers are arbitray (2, 3, 1) but intend to simulate
        # what actually happens while postgres is starting up

        call_command("wait_for_db")

        self.assertEqual(
            patched_check.call_count, 6
        )  # Validates that we call the check method only 6 times.
        # If we call it any more than 6 it was not necessary.
        # If we calling less than 5 then we are not checking
        # the exceptions properly in the test
        patched_check.assert_called_with(
            databases=["default"]
        )  # checks that is called with the correct value
