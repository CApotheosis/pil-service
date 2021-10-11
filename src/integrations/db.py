"""This module contains class, which is the interface to access a database."""
import boto3

from boto3.dynamodb.conditions import Key

ANNOUNCEMENTS_TABLE = "Announcements"
ANNOUNCEMENTS_TABLE_KEYS = ("guid", "created_date")


class DBStorageAccess:
    """Provides accessing to vacancies data."""
    def __init__(self):
        self._db = self._get_dynamo_db()
        self._announcements_table = self._get_table(ANNOUNCEMENTS_TABLE)

    @staticmethod
    def _get_dynamo_db():
        """Creates a dynamodb instance.

        Returns:
            Any: dynamodb instance.
        """
        return boto3.resource("dynamodb")

    def _get_table(self, table_name):
        """Initializes a table by table name or creates new one.

        Args:
            table_name (str)
        """
        if table_name in (table.name for table in self._db.tables.all()):
            table = self._db.Table(table_name)
        else:
            table = self._create_table(table_name)

        return table

    def _create_table(self, table_name):
        """Creates a new table.

        Args:
            table_name (str)
        """
        if table_name == ANNOUNCEMENTS_TABLE:
            key_schema = [
                {
                    "AttributeName": ANNOUNCEMENTS_TABLE_KEYS[0],
                    "KeyType": "HASH",
                },
                {
                    "AttributeName": ANNOUNCEMENTS_TABLE_KEYS[1],
                    "KeyType": "RANGE",
                },
            ]
            attribute_definition = [
                {
                    "AttributeName": "guid",
                    "AttributeType": "S",
                },
                {
                    "AttributeName": "created_date",
                    "AttributeType": "S",
                },
            ]

            return self._db.create_table(
                TableName=table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definition,
                BillingMode="PAY_PER_REQUEST",
            )
        else:
            raise Exception("Wrong table name.")

    @staticmethod
    def _prepare_announcement( announcement):
        for key in ANNOUNCEMENTS_TABLE_KEYS:
            if announcement.get(key) is None:
                raise Exception(f"Key {key} not found")

        return announcement

    def save_announcement(self, announcement):
        """Save announcement into db.

        Args:
            announcement (dict)
        """
        response = self._announcements_table.put_item(Item=self._prepare_announcement(announcement))
        status_code = response["ResponseMetadata"]["HTTPStatusCode"]

        if status_code != 200:
            raise Exception(f"Saving vacancy request is failed with status code {status_code}")

    def get_announcement(self, key_query, search_value):
        """Returns matched announcement.

        Args:
            key_query (str)
            search_value (Any)

        Returns:
            list[dict]
        """
        response = self._announcements_table.query(
            KeyConditionExpression=Key(key_query).eq(search_value)
        )

        return response["Items"]

    def get_announcements(self, page, items_to_show_per_request):
        """Returns announcements in given range.

        Args:
            page (int)
            items_to_show_per_request (int)

        Returns:
            list[dict]
        """
        search_method = self._announcements_table.scan
        scan_kwargs = {
            "Limit": items_to_show_per_request
        }
        items = []
        done = False
        start_key = None
        counter = 0

        while not done:
            if start_key:
                scan_kwargs["ExclusiveStartKey"] = start_key
            response = search_method(**scan_kwargs)
            start_key = response.get("LastEvaluatedKey", None)
            done = start_key is None
            items.extend(response["Items"])
            counter += 1

            if not page or counter == page:
                break

        return items
