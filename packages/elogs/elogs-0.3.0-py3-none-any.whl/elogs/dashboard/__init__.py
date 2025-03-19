from contextlib import contextmanager
from pathlib import Path

from elogs.dashboard.labels import label_to_rgb


def static_path(basepath):
    return Path(__file__).resolve().parent / "static" / Path(basepath).name


@contextmanager
def named_tmp_staticfile(basepath, clean=True):
    path = static_path(basepath)
    try:
        yield path
    finally:
        if clean:
            print(f"Deleting {path}")
            if path.is_file():
                path.unlink()
            else:
                path.rmdir()


def latlon_read(fn):
    import numpy as np
    import rasterio
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    from rasterio.transform import array_bounds

    dst_crs = "EPSG:4326"

    with rasterio.open(fn) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds
        )

        dst = np.zeros((src.count, height, width))
        dst_bounds = array_bounds(height, width, transform)

        for i in range(src.count):
            reproject(
                source=src.read(i + 1),
                destination=dst[i],
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest,
            )

    return dst, dst_bounds


def latlon_read_s3(bucket, prefix):
    import os
    import numpy as np
    import rasterio
    from rasterio.warp import calculate_default_transform, reproject, Resampling

    from rasterio.transform import array_bounds
    from rasterio.session import AWSSession
    import boto3

    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    bucket = os.getenv("BUCKET")
    region_name = os.getenv("AWS_REGION_NAME", "eu-central-1")

    full_prefix = Path(f"{bucket}/{prefix}")
    fn = f"s3://{full_prefix}"

    boto3_session = boto3.Session(
        aws_access_key_id, aws_secret_access_key, region_name=region_name
    )

    aws_session = AWSSession(boto3_session, aws_unsigned=False)

    with rasterio.Env(session=aws_session):
        with rasterio.open(fn) as src:
            dst_crs = "EPSG:4326"
            transform, width, height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds
            )
            latlon_bounds = array_bounds(height, width, transform)

            dst_crs = "EPSG:3857"
            transform, width, height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds
            )
            dst = np.zeros((src.count, height, width))

            for i in range(src.count):
                reproject(
                    source=src.read(i + 1),
                    destination=dst[i],
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest,
                )

    return dst, latlon_bounds


def remove_file(fn):
    import os

    try:
        os.remove(fn)
    except Exception as e:
        pass


def random_string(length):
    import random
    import string

    # With combination of lower and upper case
    result_str = "".join([random.choice(string.ascii_letters) for i in range(length)])
    # print random string
    return result_str


def ls(s3, prefix="", sort_by_date=True):
    contents = s3.list_contents(prefix, sort_by_date=sort_by_date)
    folders = contents["folders"]
    files = contents["files"]
    return folders, files
