import concurrent.futures
import os
import random
import re
import shutil
import string
from abc import ABC, abstractmethod
from pathlib import Path
from threading import Timer

from dotenv import load_dotenv
from loguru import logger
from tqdm.auto import tqdm

from elogs._version import __version__

__all__ = ["__version__"]


DEFAULT_ELOGS_AWS_LOGS_BUCKET = "vito-worldcover"


def check_env_vars_if_none(
    aws_access_key_id, aws_secret_access_key, aws_logs_bucket=None
):
    if aws_access_key_id is None:
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    if aws_secret_access_key is None:
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if (aws_access_key_id is None) or (aws_secret_access_key is None):
        raise ValueError("AWS credentials not provided and not found as env vars.")

    if aws_logs_bucket is None:
        aws_logs_bucket = os.getenv("AWS_LOGS_BUCKET")
        if aws_logs_bucket is None:
            aws_logs_bucket = DEFAULT_ELOGS_AWS_LOGS_BUCKET

    return aws_access_key_id, aws_secret_access_key, aws_logs_bucket


def parallelize(
    f, my_iter, max_workers=4, progressbar=True, total=None, use_process_pool=False
):
    if total is None:
        try:
            total = len(my_iter)
        except Exception:
            total = None
            progressbar = False

    if use_process_pool:
        Pool = concurrent.futures.ProcessPoolExecutor
    else:
        Pool = concurrent.futures.ThreadPoolExecutor

    with Pool(max_workers=max_workers) as ex:
        if progressbar:
            results = list(tqdm(ex.map(f, my_iter), total=total))
        else:
            results = list(ex.map(f, my_iter))
    return results


def random_string(n=8):
    x = "".join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
        for _ in range(n)
    )
    return x


def _clean(path):
    path = Path(path)
    if path.is_dir():
        cleaner = shutil.rmtree
    elif path.is_file():
        cleaner = os.remove
    else:
        # path doesn't exist
        return

    try:
        logger.debug(f"Deleting {path}")
        cleaner(path)
    except Exception as e:
        logger.error(f"Error cleaning up {path}: {e}")


def clean(*paths):
    for path in paths:
        _clean(path)


def iglob_files(path, pattern=None):
    """
    Generator that finds all subfolders of path containing the regex `pattern`
    """
    try:
        root_dir, folders, files = next(os.walk(path))
    except StopIteration:
        return

    for f in files:
        if (pattern is None) or len(re.findall(pattern, f)):
            file_path = os.path.join(root_dir, f)
            yield file_path

    for d in folders:
        new_path = os.path.join(root_dir, d)
        yield from iglob_files(new_path, pattern)


class BackgroundTask(ABC):
    """Run function in a background thread every N seconds"""

    def __init__(self, interval):
        self.interval = interval
        self.is_running = False
        self._timer = None

    def _run(self):
        self.is_running = False
        self.start()
        self.task()

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        if self.is_running:
            self._timer.cancel()
            self.is_running = False

    @abstractmethod
    def task(self): ...


try:
    from .elogs import Elogs, ElogsBlocks, ElogsMaster, ElogsTask
except Exception as e:
    # install error
    print(f"Error importing elogs: {e}")
