import os
import sys
import json
import argparse

from loguru import logger


def _spark_parallelize(sc, func, iterable, num_slices=None, collect=True):
    """
    Run a spark for each safely with logging and exitlogs report if options
    are provided.
    """
    if num_slices is None:
        num_slices = len(iterable)

    if num_slices == 0:
        logger.warning("Nothing to process")
        return None

    try:
        logger.info(f"Starting parallelization of {len(iterable)} tasks.")

        if collect:
            rdd = sc.parallelize(iterable, num_slices).map(func).collect()
        else:
            rdd = sc.parallelize(iterable, num_slices).foreach(func)  # None

        logger.success("Spark processing completed.")

        return rdd

    except Exception as e:
        e_msg = str(e)
        if len(e_msg) > 4096:
            # when using telegram this causes an error because text is too long
            # so this prints the full error to the MEP logs
            print(e_msg)
            e_msg = e_msg[:4096]
        logger.error(f"ERROR - Task interrupted:\n{e}")
        # raise e # causes threadlock
        return e

    finally:
        sc.stop()


def spark_foreach(sc, func, iterable, num_slices=None):
    return _spark_parallelize(sc, func, iterable, num_slices=num_slices, collect=False)


def spark_collect(sc, func, iterable, num_slices=None):
    return _spark_parallelize(sc, func, iterable, num_slices=num_slices, collect=True)


def spark_context(local=False, threads="*", spark_version=None):
    """
    Returns SparkContext for local run.
    if local is True, conf is ignored.

    Customized for VITO MEP
    """
    if spark_version is None:
        spark_version = 2 if sys.version_info.minor < 8 else 3
    sv = spark_version

    spark_home = {2: "/usr/hdp/current/spark2-client", 3: "/opt/spark3_2_0"}

    env_vars = {"SPARK_MAJOR_VERSION": str(sv), "SPARK_HOME": spark_home[sv]}

    py4j_v = {2: "py4j-0.10.7", 3: "py4j-0.10.9.2"}

    spark_py_path = [
        f"{spark_home[sv]}/python",
        f"{spark_home[sv]}/python/lib/{py4j_v[sv]}-src.zip",
    ]

    for k, v in env_vars.items():
        logger.info(f"Setting env var: {k}={v}")
        os.environ[k] = v

    logger.info(f"Prepending {spark_py_path} to PYTHONPATH")
    sys.path = spark_py_path + sys.path

    import py4j

    logger.info(f"py4j: {py4j.__file__}")

    import pyspark

    logger.info(f"pyspark: {pyspark.__file__}")

    from pyspark import SparkContext, SparkConf

    import cloudpickle
    import pyspark.serializers

    pyspark.serializers.cloudpickle = cloudpickle

    if local:
        logger.info(f"Setting env var: PYSPARK_PYTHON={sys.executable}")
        os.environ["PYSPARK_PYTHON"] = sys.executable

        conf = SparkConf()
        conf.setMaster(f"local[{threads}]")
        conf.set("spark.driver.bindAddress", "127.0.0.1")

        sc = SparkContext(conf=conf)
    else:
        sc = SparkContext()

    return sc


def get_local_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--local", action="store_true")
    return parser


def get_telegram_handler(config_filename, chat_id=None):
    with open(config_filename, "r") as f:
        config = json.load(f)

    TELEGRAM_TOKEN = config["telegram"].get("token")

    if chat_id is None:
        TELEGRAM_CHAT_ID = config["telegram"].get("chat_id")
    else:
        TELEGRAM_CHAT_ID = chat_id

    # Add telegram sink for loguru notifications
    if (TELEGRAM_TOKEN is None) | (TELEGRAM_CHAT_ID is None):
        logger.warning(
            "Telegram notifications cannot be sent. "
            "TELEGRAM_TOKEN and/or TELEGRAM_CHAT_ID chat_id "
            "variables not set."
        )
    else:
        params = dict(token=TELEGRAM_TOKEN, chat_id=TELEGRAM_CHAT_ID)
        from notifiers.logging import NotificationHandler

        telegram_handler = NotificationHandler("telegram", defaults=params)
        return telegram_handler
