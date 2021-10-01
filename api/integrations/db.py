"""This module contains class, which is the interface to access a database."""
import boto3

from boto3.dynamodb.conditions import Attr, Key


class DBStorageAccess:
    """Provides access to reading and writing announcement data."""
    def __init__(self):
        self._db = self._get_dynamo_db()

    @staticmethod
    def _get_dynamo_db():
        """Creates a dynamodb instance.

        Returns:
            Any: dynamodb instance.
        """
        return boto3.resource("dynamodb")

    def _create_table(self, table_name):
        """Creates a table by table name.

        Args:
            table_name (str)

        Returns:
            Any: a db table.

        Raises:
            DBStorageAccessIncorrectTableName: error occurred when table with received name doesn't exist.
        """

