import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import boto3
import botocore
from loguru import logger


def compute_md5(file_path):
    """Compute the MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@dataclass
class S3File:
    uri: str
    size: int
    last_modified: datetime

    def __str__(self):
        return f"{self.uri}"

    def __repr__(self):
        return f"S3File(uri={self.uri}, size={self.size}, last_modified={self.last_modified})"


class S3BucketReader:
    """
    Helper class to browse AWS S3 buckets using boto3
    """

    def __init__(self, client: boto3.client, bucket, requester_pays=False):
        self.client = client
        self.bucket = bucket
        self._params = dict(Bucket=bucket)
        self._pag = client.get_paginator("list_objects_v2")
        self._requester_pays = requester_pays

        if requester_pays:
            self._params.update(RequestPayer="requester")

    @classmethod
    def from_credentials(
        cls,
        aws_access_key_id,
        aws_secret_access_key,
        bucket,
        requester_pays=False,
        aws_region="eu-central-1",
        max_pool_connections=100,
        endpoint_url=None,
    ):
        client_config = botocore.config.Config(
            max_pool_connections=max_pool_connections,
        )

        client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region,
            config=client_config,
            endpoint_url=endpoint_url,
        )

        return cls(client, bucket, requester_pays)

    @property
    def params(self):
        return self._params.copy()

    def read_text(self, key):
        """
        Load a text file from S3
        """
        client = self.client
        params = self.params
        params.update(Key=key)

        fileobj = client.get_object(**params)

        filedata = fileobj["Body"].read()
        return filedata.decode("utf-8")

    def read_json(self, key):
        """
        Load a JSON file from S3
        """
        contents = json.loads(self.read_text(key))
        return contents

    def list_contents(
        self,
        prefix="",
        recursive=False,
        folders=True,
        files=True,
        files_metadata=False,
        sort_by_date=False,
    ):
        """
        Returns a dictionary of 'folders' and 'files' at the given prefix.
        Fetches data per page and sorts using date of creation if sort_by_date is True.
        """
        pag = self._pag
        params = self.params
        params.update(Prefix=prefix)
        if not recursive:
            params.update(Delimiter="/")

        dirs_meta, files_meta = [], []
        for subset in pag.paginate(**params):
            if ("CommonPrefixes" in subset.keys()) and folders:
                dirs_meta.extend(subset.get("CommonPrefixes"))
            if ("Contents" in subset.keys()) and files:
                files_meta.extend(subset.get("Contents"))

        dirs = [d["Prefix"] for d in dirs_meta]

        # Sort files by LastModified date if sort_by_date is True
        if sort_by_date:
            files_meta.sort(key=lambda x: x["LastModified"], reverse=True)

        if files_metadata:
            files = files_meta
        else:
            files = [f["Key"] for f in files_meta]

        contents = {"folders": dirs, "files": files}

        return contents

    def list_dirs(self, prefix=""):
        return self.list_contents(prefix=prefix, files=False)["folders"]

    def list_files(self, prefix="", recursive=False):
        return self.list_contents(
            prefix=prefix, recursive=recursive, folders=False
        )["files"]

    def list_files_matching_pattern(self, prefix, pattern):
        """
        List S3 keys matching a given regex pattern.

        :param prefix: The S3 prefix to start listing from.
        :param pattern: The regex pattern to match keys.
        :return: List of keys matching the pattern.
        """
        keys = []
        regex = re.compile(pattern)

        files = self.list_files(prefix, recursive=True)
        for obj in files:
            if regex.match(obj):
                keys.append(obj)
        return keys

    def download(self, key, filename, verbose=False, overwrite=False):
        if self._requester_pays:
            extra_args = dict(RequestPayer="requester")
        else:
            extra_args = {}

        filename = Path(filename)

        if filename.is_file():
            if verbose:
                logger.info(f"{filename} exists already.")
        else:
            if verbose:
                logger.info(
                    f"Downloading s3://{self.bucket}/{key} to {filename}"
                )
            self.client.download_file(
                Bucket=self.bucket,
                Key=key,
                Filename=str(filename),
                ExtraArgs=extra_args,
            )

    def delete(self, key, verbose=True):
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
        except Exception as e:
            if verbose:
                logger.error(f"Failed to delete {key}: {e}")

    def download_folder(
        self,
        key,
        output_folder,
        regex_pattern=None,
        verbose=False,
        overwrite=False,
    ):
        output_folder = Path(output_folder)
        contents = self.list_contents(key)
        folders, files = contents["folders"], contents["files"]

        for file in files:
            if regex_pattern is not None:
                if re.compile(f"{regex_pattern}").search(file) is None:
                    continue

            output_filename = output_folder / Path(file).name
            output_filename.parent.mkdir(parents=True, exist_ok=True)

            self.download(
                file, output_filename, verbose=verbose, overwrite=overwrite
            )

        for fold in folders:
            if verbose:
                logger.info(f"Downloading folder: s3://{self.bucket}/{key}")
            self.download_folder(
                fold,
                output_folder / Path(fold).name,
                regex_pattern=regex_pattern,
                verbose=verbose,
                overwrite=overwrite,
            )

    def exists(self, key):
        import botocore

        client = self.client
        params = self.params
        params.update(Key=key)

        try:
            client.head_object(**params)
            return True
        except botocore.exceptions.ClientError as e:
            if e.response["ResponseMetadata"]["HTTPStatusCode"] == 404:
                return False
            else:
                raise

    def upload(
        self,
        fn,
        key,
        overwrite=True,
        metadata=None,
        add_md5=True,
        multipart_threshold_mb=200,
    ):
        from boto3.s3.transfer import TransferConfig
        from botocore.exceptions import ClientError

        # Configure multipart upload threshold and concurrency for uploads only
        transfer_config = TransferConfig(
            multipart_threshold=multipart_threshold_mb
            * 1024
            * 1024,  # 10MB threshold
        )
        metadata = metadata or {}
        if add_md5:
            metadata["md5"] = compute_md5(fn)

        fn = str(fn)
        key = str(key)

        if not overwrite and self.exists(key):
            logger.info(f"File {key} already exists. Skipping upload.")
            return

        try:
            logger.debug(f"Uploading {fn} to {key}")
            response = self.client.upload_file(
                Filename=fn,
                Bucket=self.bucket,
                Key=key,
                Config=transfer_config,
                ExtraArgs={"Metadata": metadata},
            )
        except ClientError as e:
            logger.error(f"Failed to upload: {fn}: {e}")
            raise e
        return response

    def head_object(self, key, cheksum_mode="ENABLED"):
        return self.client.head_object(
            Bucket=self.bucket, Key=key, ChecksumMode=cheksum_mode
        )

    def upload_folder(
        self,
        folder,
        folder_key_prefix,
        overwrite=True,
        metadata=None,
        add_md5=True,
        multipart_threshold_mb=200,
    ):
        from elogs.utils import iglob_files

        folder = Path(folder).absolute()
        files_gen = iglob_files(folder)
        for fn in files_gen:
            key = str(Path(folder_key_prefix) / Path(fn).relative_to(folder))
            self.upload(
                fn,
                key,
                metadata=metadata,
                overwrite=overwrite,
                add_md5=add_md5,
                multipart_threshold_mb=multipart_threshold_mb,
            )

    def md5(self, key):
        """Return md5sum of key"""
        # TODO: differentiate between md5 and etag
        head = self.head_object(key)

        try:
            metadata = head.get("Metadata", {})
            if "md5" in metadata.keys():
                return metadata["md5"]

            etag = head["ETag"][1:-1]
            return etag

        except botocore.exceptions.ClientError:
            md5sum = None

        return md5sum

    def md5_file(self, fn):
        """Return md5sum of local file"""
        return compute_md5(fn)

    def check_md5(self, key, fn):
        """check md5sum of key with md5sum of local file"""
        return self.md5(key) == self.md5_file(fn)

    def url(self, key):
        region = self.client.meta.region_name
        if region == "us-east-1":
            region_prefix = "s3"
        else:
            region_prefix = f"s3-{region}"
        return f"http://{region_prefix}.amazonaws.com/{self.bucket}/{key}"

    def size(self, key):
        """Returns the size of the object in bytes"""
        return self.client.head_object(Bucket=self.bucket, Key=key)[
            "ContentLength"
        ]


class AWSL2ABucket(S3BucketReader):
    def __init__(self, client, bucket="sentinel-s2-l2a"):
        super().__init__(client, bucket, requester_pays=True)

    @classmethod
    def from_credentials(
        cls, aws_access_key_id, aws_secret_access_key, max_pool_connections=50
    ):
        client_config = botocore.config.Config(
            max_pool_connections=max_pool_connections,
        )

        AWS_REGION = "eu-central-1"  # L2A bucket location
        client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=AWS_REGION,
            config=client_config,
        )
        return cls(client)

    @staticmethod
    def _get_utm_lat_grid(tile):
        utm = tile[:2].lstrip("0")
        lat = tile[2]
        grid = tile[3:]
        return utm, lat, grid

    def get_yearly_products(self, tile, year=2019, max_workers=10):
        utm, lat, grid = self._get_utm_lat_grid(tile)

        months = list(range(1, 13))

        def get_products_days(utm, lat, grid, year, month):
            prefix = f"tiles/{utm}/{lat}/{grid}/{year}/{month}/"
            return self.list_dirs(prefix)

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            mapper = ex.map(
                lambda x: get_products_days(utm, lat, grid, year, x), months
            )
            products_days = [r for nr in mapper for r in nr]

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            mapper = ex.map(self.list_dirs, products_days)
            products_paths = [r for nr in mapper for r in nr]

        return products_paths

    def _get_tile_products(
        self,
        tile,
        start_date="2019-01-01",
        end_date="2020-01-01",
        max_workers=10,
    ):
        utm, lat, grid = self._get_utm_lat_grid(tile)

        years_months = self._get_years_months(start_date, end_date)

        def get_products_days(utm, lat, grid, year, month):
            prefix = f"tiles/{utm}/{lat}/{grid}/{year}/{month}/"
            return self.list_dirs(prefix)

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            mapper = ex.map(
                lambda year_month: get_products_days(
                    utm, lat, grid, year_month[0], year_month[1]
                ),
                years_months,
            )
            products_days = [r for nr in mapper for r in nr]

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            mapper = ex.map(self.list_dirs, products_days)
            products_paths = [r for nr in mapper for r in nr]

        products_paths = list(
            map(lambda x: f"s3://{self.bucket}/" + x, products_paths)
        )
        return products_paths

    @staticmethod
    def _convert_dates(*dates):
        new_dates = []
        fmt = "%Y-%m-%d"

        for d in dates:
            if isinstance(d, str):
                new_dates.append(datetime.strptime(d, fmt))
            elif isinstance(d, datetime):
                new_dates.append(d)
            else:
                raise ValueError(
                    "Type of date not recognized. Should be "
                    "a string in the format '%Y-%m-%d' or a "
                    "'datetime.datetime' instance. Instead is: "
                    f"type({d}): {type(d)}"
                )
        return new_dates

    def _get_years_months(self, start_date, end_date):
        """
        Returns a tuple (year, month) for all the months in the dates interval.
        Dates should be strings with format %Y-%m-%d
        """

        s, e = self._convert_dates(start_date, end_date)

        years = list(range(s.year, e.year + 1))

        start_month = s.month
        end_month = e.month

        year_months = []
        for y in years:
            if len(years) == 1:
                year_months += [
                    (y, m) for m in range(start_month, end_month + 1)
                ]
                return year_months

            if y == years[0]:
                year_months += [(y, m) for m in range(start_month, 13)]

            elif y == years[-1]:
                year_months += [(y, m) for m in range(1, end_month + 1)]

            else:
                year_months += [(y, m) for m in range(1, 13)]

        return year_months

    @staticmethod
    def _get_product_date(x):
        s = x.strip("/").split("/")
        year, month, day = int(s[-4]), int(s[-3]), int(s[-2])
        return datetime(year, month, day)

    def get_tile_products(
        self,
        tile,
        start_date="2019-01-01",
        end_date="2020-01-01",
        max_workers=10,
    ):
        import numpy as np

        start_date, end_date = self._convert_dates(start_date, end_date)

        products = self._get_tile_products(
            tile, start_date, end_date, max_workers
        )

        products = np.array(products)
        products_dates = np.array(
            [self._get_product_date(x) for x in products]
        )

        valid_ids = np.where(
            (products_dates >= start_date) & (products_dates < end_date)
        )[0]

        valid_products = products[valid_ids].tolist()

        return valid_products

    def download_product(
        self,
        product_key,
        download_folder,
        max_workers=4,
        verbose=False,
        overwrite=False,
    ):
        r10_files = [f"R10m/B{n:02d}.jp2" for n in [2, 3, 4, 8]]
        r20_files = [f"R20m/B{n:02d}.jp2" for n in [5, 6, 7, 11, 12]] + [
            "R20m/SCL.jp2"
        ]
        r60_files = ["R60m/SCL.jp2"]

        basenames = r10_files + r20_files + r60_files
        keys = [f"{product_key}/{f}" for f in basenames]

        download_folder = Path(download_folder)
        product_folder = download_folder

        for f in ["R10m", "R20m", "R60m"]:
            sub_folder = product_folder / f
            sub_folder.mkdir(parents=True, exist_ok=True)

        dst_filenames = [product_folder / b for b in basenames]

        kd_tuples = list(zip(keys, dst_filenames))

        def _download(tup):
            k, d = tup
            self.download(k, d, verbose=verbose, overwrite=overwrite)

        # parallel downloads
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            _ = list(ex.map(_download, kd_tuples))
