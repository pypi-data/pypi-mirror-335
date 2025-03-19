from datetime import datetime, timedelta
from contextlib import contextmanager

from loguru import logger

import boto3
import botocore.exceptions
from botocore.waiter import WaiterModel, create_waiter_with_client


_DELAY = 1
_MAX_ATTEMPTS = 60
_WAITER_CONFIG = {
    "version": 2,
    "waiters": {
        "TableExists": {
            "delay": _DELAY,
            "operation": "DescribeTable",
            "maxAttempts": _MAX_ATTEMPTS,
            "acceptors": [
                {
                    "expected": "ACTIVE",
                    "matcher": "path",
                    "state": "success",
                    "argument": "Table.TableStatus",
                },
                {
                    "expected": "ResourceNotFoundException",
                    "matcher": "error",
                    "state": "retry",
                },
            ],
        },
        "TableNotExists": {
            "delay": _DELAY,
            "operation": "DescribeTable",
            "maxAttempts": _MAX_ATTEMPTS,
            "acceptors": [
                {
                    "expected": "ResourceNotFoundException",
                    "matcher": "error",
                    "state": "success",
                }
            ],
        },
    },
}


_LOCK_KEY_SCHEMA = [
    {"AttributeName": "id", "KeyType": "HASH"},
]
_LOCK_ATTRIBUTE_DEFINITIONS = [
    {"AttributeName": "id", "AttributeType": "S"},
]


class DynamoError(Exception): ...


class DynamoLockError(Exception): ...


class DynamoClient:
    def __init__(self, client, resource):
        self.client = client
        self.resource = resource

    @classmethod
    def from_credentials(
        cls, aws_access_key_id, aws_secret_access_key, region_name="eu-central-1"
    ):
        client = boto3.client(
            "dynamodb",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        resource = boto3.resource(
            "dynamodb",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        return cls(client, resource)

    def waiter(self, waiter_name):
        waiter_model = WaiterModel(_WAITER_CONFIG)
        return create_waiter_with_client(waiter_name, waiter_model, self.client)

    def _create_table(
        self, name, key_schema, attribute_definitions, billing_mode="PAY_PER_REQUEST"
    ):
        # Create the DynamoDB table.
        table = self.resource.create_table(
            TableName=name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            BillingMode=billing_mode,
        )

        logger.debug("Waiting for table creation")
        waiter = self.waiter("TableExists")
        waiter.wait(TableName=name)  # wait that table is created
        logger.debug(f"Table {name} created.")

        return table

    def delete_table(self, name):
        table = self.resource.Table(name)
        table.delete()
        logger.debug(f"Waiting for table {name} deletion.")
        waiter = self.waiter("TableNotExists")
        waiter.wait(TableName=name)  # wait that table is deleted
        logger.debug(f"Table {name} deleted.")

    def create_table(
        self,
        name,
        key_schema,
        attribute_definitions,
        billing_mode="PAY_PER_REQUEST",
        overwrite=False,
    ):
        """Create table. If it exists and overwrite==True, delete it
        and re-create it.

        Returns DynamoDB table object"""
        if self.table_exists(name):
            if not overwrite:
                raise ValueError(f"Table {name} already exists")
            else:
                logger.warning(f"Overwriting table {name}")
                self.delete_table(name)

        return self._create_table(name, key_schema, attribute_definitions, billing_mode)

    def table_exists(self, table_name):
        try:
            _ = self.client.describe_table(TableName=table_name)
            return True
        except self.client.exceptions.ResourceNotFoundException:
            return False

    def get_table(self, name):
        if self.table_exists(name):
            return self.resource.Table(name)
        else:
            raise ValueError(f"Table {name} does not exist")

    def get_item(self, table, **item):
        response = table.get_item(Item=item)
        items = response["Items"]

        if len(items):
            return items[0]
        else:
            return {}

    def put_item(self, table, entry):
        import json
        from decimal import Decimal

        entry = json.loads(json.dumps(entry), parse_float=Decimal)
        response = table.put_item(Item=entry)
        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise DynamoError("Failed put")
        return response

    def dump_table(self, table_name, attributes=None):
        results = []
        last_evaluated_key = None
        table = self.get_table(table_name)

        while True:
            query = {}
            if last_evaluated_key:
                query["ExclusiveStartKey"] = last_evaluated_key

            if attributes is not None:
                query["AttributesToGet"] = attributes

            response = table.scan(**query)
            last_evaluated_key = response.get("LastEvaluatedKey")

            results.extend(response["Items"])

            if not last_evaluated_key:
                break
        return results

    def _acquire_lock(self, resource_id, lock_table_name, expiration_time=5):
        """Lock resource for atomic operations.
        When acquiring a lock, the update operation has 'expiration_time'
        seconds to be executed.
        If a lock is already acquired but it's expiration time passed, we
        force the new lock acquisition, which will set a new timestamp.

        When unlocking, we make sure that the current lock is the same that was
        acquired, if yes we release it deleting the entry, otherwise we try to
        acquire a new lock
        """

        if self.table_exists(lock_table_name):
            table = self.get_table(lock_table_name)
        else:
            table = self.create_table(
                lock_table_name, _LOCK_KEY_SCHEMA, _LOCK_ATTRIBUTE_DEFINITIONS
            )

        # try to get lock: if lock doesn't exist
        # create lock entry and insert it making sure it was not created

        try:
            # Put item with conditional expression to acquire the lock
            creation_time = datetime.now()
            expiration_time = creation_time + timedelta(seconds=expiration_time)
            table.put_item(
                Item={
                    "id": resource_id,
                    "creation_time": creation_time.isoformat(),
                    "expiration_time": expiration_time.isoformat(),
                },
                ConditionExpression="attribute_not_exists(#r)",
                ExpressionAttributeNames={"#r": "id"},
            )
            # Lock acquired
            return True

        except botocore.exceptions.ClientError as e:
            # Another exception than ConditionalCheckFailedException
            # was caught, raise as-is
            if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
                raise
            else:
                # Else, lock cannot be acquired because already locked
                self._delete_expired_lock(resource_id)  # if expired
                return False

    def _delete_expired_lock(self, resource_id, lock_table_name):
        _ = self.get_table(lock_table_name)
        raise NotImplementedError

    def _unlock(self, resource_id, lock_table_name):
        """Unlock resource for atomic operations"""

        if self.table_exists(lock_table_name):
            table = self.get_table(lock_table_name)
        else:
            table = self.create_table(
                lock_table_name, _LOCK_KEY_SCHEMA, _LOCK_ATTRIBUTE_DEFINITIONS
            )

        try:
            # Put item with conditional expression to acquire the lock
            table.delete_item(
                Item={"id": resource_id},
                ConditionExpression="attribute_exists(#r)",
                ExpressionAttributeNames={"#r": "id"},
            )
            # Unlocked successfully
            return True
        except botocore.exceptions.ClientError as e:
            # Another exception than ConditionalCheckFailedException
            # was caught, raise as-is
            if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
                raise
            else:
                # Else, lock cannot be acquired because already locked
                return True  # resource already unlocked, return True anyway

    @contextmanager
    def lock(
        self, resource_id, lock_table_name="elogs_lock", timeout=20, retry_time=0.5
    ):
        import time

        start_time = time.time()

        while (time.time() - start_time) < timeout:
            locked = self._lock(resource_id, lock_table_name)
            if locked is True:
                break
            else:
                logger.warning(
                    f"Failed to acquire lock on {resource_id}. "
                    f"Retrying in {retry_time} s."
                )
                time.sleep(retry_time)

        if locked is False:
            raise DynamoLockError(f"Failed to acquire lock for {resource_id}")

        try:
            yield
        finally:
            self._unlock(resource_id, lock_table_name)


class DynamoLockCtx:
    def __init__(self, file_name, method):
        self.file_obj = open(file_name, method)

    def __enter__(self):
        return self.file_obj

    def __exit__(self, type, value, traceback):
        self.file_obj.close()


class NoProductsError: ...


class L2AProductsDB:
    _db_attributes = [
        "date",
        "path",
        "data_coverage_percentage",
        "timestamp",
        "cloudy_pixel_percentage",
        "tile",
        "product_id",
    ]
    _db_attributes_mapping = {f"#{a}": a for a in _db_attributes}
    _table_name = "s2products_v2"

    def __init__(self, aws_access_key_id, aws_secret_access_key):
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key

    @property
    def dynamo(self):
        return DynamoClient.from_credentials(
            self._aws_access_key_id, self._aws_secret_access_key
        )

    @property
    def table(self):
        return self.dynamo.get_table(self._table_name)

    def _query_tile(
        self,
        tile,
        start_date=20160101,
        end_date=20990101,
        last_evaluated_key=None,
        items=None,
    ):
        from boto3.dynamodb.conditions import Key

        if items is None:
            items = []

        params = dict(
            KeyConditionExpression=(
                Key("tile").eq(tile) & Key("date").between(start_date, end_date)
            ),
            ProjectionExpression=",".join(self._db_attributes_mapping.keys()),
            ExpressionAttributeNames=self._db_attributes_mapping,
        )

        if last_evaluated_key is not None:
            params["ExclusiveStartKey"] = last_evaluated_key

        response = self.table.query(**params)
        last_evaluated_key = response.get("LastEvaluatedKey")
        items.extend(response.get("Items"))

        if last_evaluated_key is not None:
            logger.debug(f"LastEvaluatedKey: {last_evaluated_key}")
            return self._query_tile(
                tile, start_date, end_date, last_evaluated_key, items
            )
        else:
            return items

    def query_tile(
        self,
        tile,
        start_date=20160101,
        end_date=20990101,
        max_cloud_cover=0.9,
        max_1product_per_day=True,
    ):
        import pandas as pd

        items = self._query_tile(tile, start_date, end_date)
        if len(items) == 0:
            raise NoProductsError

        df = pd.DataFrame(items)

        # filter cloudy
        df = df[df["cloudy_pixel_percentage"] <= (max_cloud_cover * 100)]

        if max_1product_per_day:
            df = self._filter_daily(df)

        return df

    def query_tile_year(
        self, tile, year, max_cloud_cover=0.9, max_1product_per_day=True
    ):
        products_df = self.query_tile(
            tile, "20160101", "20250101", max_cloud_cover, max_1product_per_day
        )

        products_df["year"] = products_df["timestamp"].apply(lambda x: x[:4])
        products_df = products_df[products_df["year"] == str(year)]

        return products_df

    @staticmethod
    def _acquisition_id(row):
        def _day(row):
            return row["timestamp"][:10]

        def _orbit(row):
            return row.product_id.split("_")[4]

        return f"{row.tile}_{_day(row)}_{_orbit(row)}"

    @staticmethod
    def _abs_cloudfree(row):
        return (
            row.data_coverage_percentage
            / 100
            * (100 - row.cloudy_pixel_percentage)
            / 100
        )

    def _filter_daily(self, df):
        """Keep 1 observation per day. Can be 2 when there are 2 ground segments.
        Keep the best cloudfree product, considering available pixels
        """
        import decimal

        df = df.copy()
        cols = ["data_coverage_percentage", "cloudy_pixel_percentage"]

        # fill missing data_coverage values sometimes
        df[cols] = df[cols].fillna(decimal.Decimal(0))

        df["acquisition_id"] = df.apply(self._acquisition_id, axis=1)
        df["abs_cloudfree"] = df.apply(self._abs_cloudfree, axis=1)
        score = (
            df[["acquisition_id", "abs_cloudfree"]]
            .groupby("acquisition_id")["abs_cloudfree"]
            .sum()
            .to_frame()
            .reset_index()
        )
        score["day"] = score["acquisition_id"].apply(lambda x: x.split("_")[1])
        score = score.sort_values(["day", "abs_cloudfree"], ascending=[True, False])
        keep_ids = score.drop_duplicates("day")["acquisition_id"].values
        df = df[df["acquisition_id"].isin(keep_ids)].drop(
            columns=["acquisition_id", "abs_cloudfree"]
        )
        return df
