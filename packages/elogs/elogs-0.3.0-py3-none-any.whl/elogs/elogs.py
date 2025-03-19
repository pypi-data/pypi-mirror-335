import functools
import json
import os
import signal
import threading
import getpass
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict

from boto3.dynamodb.conditions import Attr

from elogs import check_env_vars_if_none, clean
from elogs.dynamo import DynamoClient, DynamoError
from elogs.s3 import S3BucketReader

TERMINATION_SIGNALS = [signal.SIGQUIT, signal.SIGTERM, signal.SIGINT]

# ELOGS_LEVEL = 70
# logger.level("ELOGS", no=ELOGS_LEVEL, color="<magenta>")
# logger.__class__.elogs = functools.partialmethod(
#     logger.__class__.log, "ELOGS")

# aliases
DONE = "done"
ERROR = "error"
RUNNING = "running"
SCHEDULED = "scheduled"
PROC = "proc"
MEM = "mem"


def thread_id():
    return threading.current_thread().ident


def app_table_name(app_id):
    return f"elogs-{app_id}"


def check_dynamo_response(r):
    if r["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise DynamoError(f"Failed operation. Response: {r}")
    else:
        return True


class ElogsTask:
    """Task object to feed to the elogs wrappers.
    The task_id is the unique identifier of the task.
    The args and kwargs are the arguments to be passed to the wrapped function.
    If only the task_id is provided, it will be passed as the first argument
    to the wrapped function."""

    def __init__(self, task_id: str, *args, **kwargs) -> None:
        if not isinstance(task_id, str):
            raise TypeError("task_id should be of type 'str'.")
        self.task_id = task_id

        if (len(args) == 0) and (len(kwargs) == 0):
            args = (task_id,)
        self.args = args
        self.kwargs = kwargs

    def __repr__(self) -> str:
        return (
            f"<ElogsTask - "
            f"task_id: {self.task_id} - "
            f"args: {self.args} - "
            f"kwargs: {self.kwargs}>"
        )

    @classmethod
    def tasks_from_iterable(cls, iterable):
        """Return a list of tasks from an iterable of task_ids.
        Only works if the task_id is the only argument to be passed to the wrapped function."""
        return [cls(i) for i in iterable]


class ElogsApps:
    _table_name = "elogs-apps-registry"

    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None):
        aws_access_key_id, aws_secret_access_key, _ = check_env_vars_if_none(
            aws_access_key_id, aws_secret_access_key
        )

        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

    def entries(self, status=None):
        apps_entries = self.dynamo.dump_table(self._table_name)
        if status is not None:
            apps_entries = [
                e for e in apps_entries if e.get("status") == status
            ]
        return apps_entries

    @property
    def dynamo(self):
        return DynamoClient.from_credentials(
            self.aws_access_key_id, self.aws_secret_access_key
        )

    @property
    def table(self):
        return self.dynamo.get_table(self._table_name)

    def master(self, app_id):
        return ElogsMaster(
            app_id, self.aws_access_key_id, self.aws_secret_access_key
        )


class ElogsMaster:
    _table_name = "elogs-apps-registry"
    _key_schema = [
        {"AttributeName": "app_id", "KeyType": "HASH"},
    ]
    _attribute_definitions = [
        {"AttributeName": "app_id", "AttributeType": "S"},
    ]

    def __init__(
        self,
        app_id,
        username,
        aws_access_key_id,
        aws_secret_access_key,
        overwrite_entry=False,
    ):
        from loguru import logger

        self.app_id = app_id
        self.app_table_name = app_table_name(app_id)
        self.username = username
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

        self._overwrite_entry = overwrite_entry
        _ = self._init_master_table()

        if overwrite_entry:
            if self.has_running_tasks() > 0:
                logger.warning(
                    "The table will not be overwritten because at least one task is running."
                )
            else:
                self.delete_entry()

        _ = self.entry  # init empty app_id entry

    @property
    def entry(self):
        from loguru import logger

        r = self.table.get_item(Key={"app_id": self.app_id})
        entry = r.get("Item")
        username = self.username

        if entry is None:
            if username is None:
                username = os.getenv("ELOGS_USERNAME")
                if username is not None:
                    logger.info(
                        f"ELOGS_USERNAME found in environment variables: {username}"
                    )
                else:
                    logger.info(
                        "ELOGS_USERNAME not found in environment variables. Trying to get USER from os..."
                    )
                    username = getpass.getuser()

            entry = {
                "app_id": self.app_id,
                "app_table_name": app_table_name(self.app_id),
                "username": username,  # NOTE
                DONE: Decimal(0),
                ERROR: Decimal(0),
                RUNNING: Decimal(0),
                "total": Decimal(0),
                "creation_time": datetime.now().isoformat(),
            }
            self.entry = entry  # update entry in db
        else:
            if "username" not in entry:
                entry["username"] = None
                self.entry = entry  # update entry in db
        return entry

    @entry.setter
    def entry(self, entry):
        if entry.get("app_id") is None:
            raise ValueError('Missing key: "app_id" in entry')
        response = self.table.put_item(Item=entry)
        check_dynamo_response(response)

    @property
    def dynamo(self):
        return DynamoClient.from_credentials(
            self.aws_access_key_id, self.aws_secret_access_key
        )

    @property
    def table(self):
        return self.dynamo.get_table(self._table_name)

    def _init_master_table(self):
        """Create or init Table holding metadata of the apps tables:
        - tasks to do
        - start time
        - app_id
        - app_table_name
        - state: 'done', 'running', 'stopped'
        """

        # check app table exists
        dynamo = self.dynamo
        table_exists = dynamo.table_exists(self._table_name)

        if table_exists:
            table = dynamo.get_table(self._table_name)
        else:
            table = dynamo.create_table(
                self._table_name,
                key_schema=self._key_schema,
                attribute_definitions=self._attribute_definitions,
                overwrite=False,
            )

        return table

    def delete_entry(self):
        r = self.table.delete_item(Key={"app_id": self.app_id})
        return r

    def _update_status(self, status, value=1):
        response = self.table.update_item(
            Key={"app_id": self.app_id},
            UpdateExpression="SET #s = #s + :val",
            ExpressionAttributeNames={"#s": status},
            ExpressionAttributeValues={":val": Decimal(value)},
        )
        check_dynamo_response(response)

    def update_status(self, status):
        self._update_status(status, 1)
        if status in (DONE, ERROR):
            self._update_status(RUNNING, -1)

    def set_status(self, status, value):
        response = self.table.update_item(
            Key={"app_id": self.app_id},
            UpdateExpression="SET #s = :val",
            ExpressionAttributeNames={"#s": status},
            ExpressionAttributeValues={":val": Decimal(value)},
        )
        check_dynamo_response(response)

    def set_interrupted_status(self, **kwargs):
        # update dello status a DONE / ERROR
        entry = self.entry
        entry[RUNNING] = 0
        entry["status"] = "interrupted"
        entry["end_date"] = "-"

        entry = {**entry, **kwargs}
        self.entry = entry

    def has_running_tasks(self):
        """Check if there are any tasks with RUNNING status."""
        response = self.table.scan(
            FilterExpression=Attr("status").eq(RUNNING),
            ProjectionExpression="task_id",
        )
        return len(response["Items"]) > 0


class Elogs:
    # default elogs app table schema
    _key_schema = [
        {"AttributeName": "task_id", "KeyType": "HASH"},
    ]
    _attribute_definitions = [
        {"AttributeName": "task_id", "AttributeType": "S"},
    ]

    def __init__(
        self,
        app_id,
        username=getpass.getuser(),
        logs_bucket=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        region_name="eu-central-1",
        logs_folder=None,
        skip_done=True,
        skip_errors=False,
        overwrite_table=False,
        custom_entry_builder=None,
        proc_logs=True,
        proc_logs_level="INFO",
        force_process_termination=False,
        register_signal_handlers=False,
    ) -> None:
        if logs_folder is None:
            """If logs folder is not provided store in temporary folder"""
            self.logs_folder = Path(".elogs") / app_id
            self._clean = True
        else:
            self.logs_folder = Path(logs_folder)
            self._clean = False

        (aws_access_key_id, aws_secret_access_key, logs_bucket) = (
            check_env_vars_if_none(
                aws_access_key_id, aws_secret_access_key, logs_bucket
            )
        )

        self.logs_subfolders = {
            k: self.logs_folder / k for k in (ERROR, MEM, PROC)
        }
        self.logs_bucket = logs_bucket

        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name

        self.skip_done = skip_done
        self.skip_errors = skip_errors
        self.app_id = app_id
        self.app_table_name = app_table_name(app_id)
        self.username = username
        self._overwrite = overwrite_table
        self._custom_entry_builder = custom_entry_builder
        self._proc_logs = proc_logs
        self._proc_logs_level = proc_logs_level
        self._proc_sinks = {}
        self._force_process_termination = force_process_termination
        self._register_signal_handlers = register_signal_handlers
        # initialize table
        _ = self._init_table()

        self.master = ElogsMaster(
            self.app_id,
            self.username,
            self.aws_access_key_id,
            self.aws_secret_access_key,
            overwrite_entry=overwrite_table,
        )

    @property
    def dynamo(self):
        return DynamoClient.from_credentials(
            self.aws_access_key_id,
            self.aws_secret_access_key,
            self.region_name,
        )

    @property
    def bucket(self):
        if self.logs_bucket is None:
            raise ValueError("'logs_bucket' parameter was not provided.")
        return S3BucketReader.from_credentials(
            self.aws_access_key_id,
            self.aws_secret_access_key,
            self.logs_bucket,
        )

    def _init_table(self):
        from loguru import logger

        """Return Dynamo Table object for given app_id"""
        app_table_name = self.app_table_name

        # check app table exists
        dynamo = self.dynamo
        table_exists = dynamo.table_exists(app_table_name)

        if table_exists and not self._overwrite:
            logger.info(f"Found app table: {app_table_name}.")
            table = dynamo.get_table(app_table_name)
        else:
            table = dynamo.create_table(
                app_table_name,
                key_schema=self._key_schema,
                attribute_definitions=self._attribute_definitions,
                overwrite=self._overwrite,
            )

        return table

    @property
    def table(self):
        return self.dynamo.get_table(self.app_table_name)

    def items(self, attributes=None):
        """Returns dictionary of the tasks status"""
        items = self.dynamo.dump_table(
            self.app_table_name, attributes=attributes
        )
        return items

    @property
    def status(self):
        """Returns dictionary of the tasks status"""
        attributes = ["task_id", "status", "processing_time"]
        items = self.items(attributes)

        done_ids = []
        error_ids = []
        running_ids = []
        proc_time = {}

        for t in items:
            t_id = t["task_id"]
            if t["status"] == DONE:
                done_ids.append(t_id)
                proc_time[t_id] = t["processing_time"]
            elif t["status"] == ERROR:
                error_ids.append(t_id)
            elif t["status"] == RUNNING:
                running_ids.append(t_id)

        return {
            DONE: done_ids,
            ERROR: error_ids,
            RUNNING: running_ids,
            "proc_time": proc_time,
        }

    def report(self):
        import numpy as np
        from loguru import logger

        status = self.status
        ptime = np.array(list(map(float, status["proc_time"].values())))

        for s in (DONE, ERROR, RUNNING):
            self.master.set_status(s, len(status[s]))
            logger.info(f"{s.upper()}: {len(status[s])}")

        if ptime.size > 0:
            logger.info(
                f"processing time: "
                f"mean={ptime.mean():.2f} s, "
                f"min={ptime.min():.2f} s, "
                f"max={ptime.max():.2f} s."
            )
        return status

    def filter_done(self, tasks, done_ids=None):
        if done_ids is None:
            done_ids = self.status[DONE]
        tasks = [t for t in tasks if t.task_id not in done_ids]
        return tasks

    @staticmethod
    def task(task_id, *args, **kwargs):
        return ElogsTask(task_id, *args, **kwargs)

    def get_task(self, task_id):
        response = self.table.get_item(Key={"task_id": task_id})
        return response.get("Item", {})

    def update_task(self, **entry):
        entry = json.loads(json.dumps(entry), parse_float=Decimal)
        response = self.table.put_item(Item=entry)
        check_dynamo_response(response)
        # update status counters on master table
        self.master.update_status(entry["status"])

        return response

    def skip_task(self, task_id):
        from loguru import logger

        task = self.get_task(task_id)
        status = task.get("status", None)

        if status == DONE:
            if self.skip_done:
                logger.warning(f"Task {task_id} status: '{DONE}'. Skipping.")
                return True
            else:
                self.master._update_status(DONE, -1)
                return False

        if status == ERROR:
            if self.skip_errors:
                logger.warning(f"Task {task_id} status: '{ERROR}'. Skipping.")
                return True
            else:
                self.master._update_status(ERROR, -1)
                return False

        if status == RUNNING:
            logger.warning(
                f"Task {task_id} status: '{RUNNING}', task will be restarted."
            )
            # the runnings counter is already resetted by start method
            # self.master._update_status(RUNNING, -1)

        return False

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper_exitlog(task: ElogsTask):
            from loguru import logger

            if not isinstance(task, ElogsTask):
                raise TypeError(
                    "Inputs of the elogs wrapped function should "
                    "be of type: elogs.elogs.ElogsTask"
                )

            task_id = task.task_id

            if self.skip_task(task_id):
                # returns true if conditions to skip processing are met
                return None

            # make sure logs are uploaded on termination
            def _upload_task_logs():
                return self.upload_logs(task_id)

            def _clean_running_entry():
                # s = self.get_task(task_id).get('status')
                # if s == RUNNING:
                #     self.delete_item(task_id)
                try:
                    self.table.delete_item(
                        Item={"task_id": task_id},
                        ConditionExpression="#r = :v",
                        ExpressionAttributeNames={"#r": "status"},
                        ExpressionAttributeValues={":v": RUNNING},
                    )

                    # if task was running, also decrease master counter
                    # the delete doesn't raise and we get here
                    self.master._update_status(RUNNING, -1)
                except Exception:
                    # do not raise in the elogs context
                    pass

            def _termination_handler(sig, frame):
                _upload_task_logs()
                _clean_running_entry()

            if self._register_signal_handlers:
                for s in TERMINATION_SIGNALS:
                    signal.signal(s, _termination_handler)

            # get base entry (task id and custom entries)
            base_entry = self.base_entry(task)

            # run wrapped function and time it
            try:
                # setup db entry for starting task
                start_date = datetime.now()
                start_time = start_date.timestamp()

                entry = dict(
                    status=RUNNING,
                    start_date=start_date.isoformat(),
                    end_date="",
                    processing_time=0,
                )
                entry = {**base_entry, **entry}
                self.update_task(**entry)

                self._add_proc_sink(task_id)
                logger.info(f"Starting processing of {task_id}.")

                value = func(*task.args, **task.kwargs)

                end_date = datetime.now()
                end_time = end_date.timestamp()
                processing_time = end_time - start_time
                logger.success(
                    f"Processing of {task_id} completed in "
                    f"{processing_time / 60:.2f} minutes."
                )

                entry = dict(
                    status=DONE,
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat(),
                    processing_time=processing_time,
                )
                entry = {**base_entry, **entry}
                self.update_task(**entry)

            except Exception as e:
                # get end time
                end_date = datetime.now()
                end_time = end_date.timestamp()
                processing_time = end_time - start_time

                err_sink = self._add_error_sink(task_id)
                logger.exception(
                    "Error occurred while processing task "
                    f"with task id '{task_id}':\n\n{e}"
                )
                logger.remove(err_sink)

                # update db
                entry = dict(
                    status=ERROR,
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat(),
                    processing_time=processing_time,
                )
                entry = {**base_entry, **entry}
                self.update_task(**entry)

                value = None

            finally:
                self._remove_proc_sink(task_id)
                self.upload_logs(task_id)
                self._clean_logs(task_id)

                if self._force_process_termination:
                    import sys

                    sys.exit()

            return value

        return wrapper_exitlog

    def _remove_proc_sink(self, task_id):
        from loguru import logger

        s = self._proc_sinks.get(task_id)
        if s is not None:
            logger.remove(s)

    def _add_sink(self, task_id, tag):
        from loguru import logger

        sink = logger.add(
            self._log_fn(task_id, tag),
            filter=lambda record: record["thread"].id == thread_id(),
        )
        return sink

    def _add_proc_sink(self, task_id):
        if self._proc_logs:
            # add processing log
            sink = self._add_sink(task_id, PROC)
            self._proc_sinks[task_id] = sink
            return sink

    def _add_error_sink(self, task_id):
        return self._add_sink(task_id, ERROR)

    def upload_logs(self, task_id):
        for tag in [ERROR, PROC]:
            log_fn = self._log_fn(task_id, tag)
            log_key = self._log_key(task_id, tag)
            if log_fn.is_file():
                self.bucket.upload(log_fn, log_key)
            else:
                # if the error log was not created, task
                # processed well, delete old error logs from bucket if any
                self.bucket.delete(log_key, verbose=False)

    def _clean_logs(self, task_id):
        if self._clean:
            for tag in [ERROR, PROC]:
                log_fn = self._log_fn(task_id, tag)
                clean(log_fn)

    def read_error_log(self, task_id):
        key = self._log_key(task_id, ERROR)
        return self.bucket.read_text(key)

    def read_proc_log(self, task_id):
        key = self._log_key(task_id, PROC)
        return self.bucket.read_text(key)

    def _log_fn(self, task_id, log_tag=ERROR):
        folder = self.logs_subfolders[log_tag]
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"elogs_{log_tag}_{task_id}.log"

    def _log_key(self, task_id, log_tag=ERROR):
        return f"elogs/{self.app_id}/{log_tag}/{log_tag}_{task_id}.log"

    def base_entry(self, task):
        if self._custom_entry_builder is not None:
            custom_entry = self._custom_entry_builder(task)
        else:
            custom_entry = {}
        entry = {"task_id": task.task_id, **custom_entry}
        return entry

    def delete_items(self, task_ids):
        # to be tested
        with self.table.batch_writer() as batch:
            for task_id in task_ids:
                content = {
                    "task_id": task_id,
                }
                batch.delete_item(Item=content)

    def delete_item(self, task_id):
        r = self.table.delete_item(Key={"task_id": task_id})
        return r

    @contextmanager
    def start(self, tasks):
        # if the app is already marked as running - raise
        # force status to stopped?
        status = self.status

        task_ids = set([t.task_id for t in tasks])
        task_ids_done = set(status[DONE])
        task_ids_error = set(status[ERROR])

        # task_ids_running = set(status[RUNNING])
        # if there are running tasks:
        # delete those items
        # self.delete_items(task_ids_running)

        total = task_ids | task_ids_done | task_ids_error

        todo_ids = task_ids
        if self.skip_done:
            todo_ids -= task_ids_done
        if self.skip_errors:
            todo_ids -= task_ids_error

        todo_tasks = [t for t in tasks if t.task_id in todo_ids]

        entry = self.master.entry
        entry["app_id"] = self.app_id

        # reset master running counter
        entry[RUNNING] = 0

        # reset done and errors counters
        entry[DONE] = len(task_ids_done)
        entry[ERROR] = len(task_ids_error)
        entry["total"] = len(total)
        entry["start_date"] = datetime.now().isoformat()
        entry["status"] = RUNNING
        entry["end_date"] = ""
        self.master.entry = entry

        yield todo_tasks

        # exit
        # update dello end_date
        status = self.status

        task_ids_done = set(status[DONE])
        task_ids_error = set(status[ERROR])
        n_running = len(status[RUNNING])
        # clean 'running' tasks and raise, there should be no running tasks...

        # if tasks are not all done -> failed
        if len(task_ids_done) + len(task_ids_error) != len(total):
            end_status = "failed"
        else:
            end_status = "completed"

        # update dello status a DONE / ERROR
        entry = self.master.entry
        entry["status"] = end_status
        entry["end_date"] = datetime.now().isoformat()
        entry[RUNNING] = n_running
        self.master.entry = entry

    def set_interrupted_status(self):
        # update dello end_date
        status = self.status

        task_ids_done = set(status[DONE])
        task_ids_error = set(status[ERROR])

        status = "interrupted"

        # update dello status a DONE / ERROR
        self.master.set_interrupted_status(
            **{DONE: len(task_ids_done), ERROR: len(task_ids_error)}
        )

    def __getitem__(self, task_id: str) -> Dict:
        return self.get_task(task_id)


class ElogsBlocks(Elogs):
    _key_schema = [
        {"AttributeName": "tile", "KeyType": "HASH"},
        {"AttributeName": "block_id", "KeyType": "RANGE"},
    ]
    _attribute_definitions = [
        {"AttributeName": "tile", "AttributeType": "S"},
        {"AttributeName": "block_id", "AttributeType": "S"},
    ]

    def get_task(self, task_id):
        tile, block_id = task_id.split("_")
        response = self.table.get_item(
            Key={"tile": tile, "block_id": block_id}
        )
        return response.get("Item", {})

    def query_tile_tasks(self, tile):
        from boto3.dynamodb.conditions import Key

        response = self.table.query(
            KeyConditionExpression=(Key("tile").eq(tile))
        )
        items = response["Items"]
        return items

    def base_entry(self, task):
        if self._custom_entry_builder is not None:
            custom_entry = self._custom_entry_builder(task)
        else:
            custom_entry = {}

        task_id = task.task_id
        tile, block_id = task_id.split("_")
        entry = {
            "tile": tile,
            "block_id": block_id,
            "task_id": task_id,
            **custom_entry,
        }
        return entry

    def delete_items(self, task_ids):
        # to be tested
        with self.table.batch_writer() as batch:
            for task_id in task_ids:
                tile, block_id = task_id.split("_")
                content = {"tile": tile, "block_id": block_id}
                batch.delete_item(Item=content)

    def delete_item(self, tile, block_id):
        r = self.table.delete_item(Key={"tile": tile, "block_id": block_id})
        return r
