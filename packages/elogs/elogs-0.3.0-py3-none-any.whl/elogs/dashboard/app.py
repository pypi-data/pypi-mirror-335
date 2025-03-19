from math import ceil
from pathlib import Path
from urllib.parse import quote, unquote

import geopandas as gpd
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session

from elogs import check_env_vars_if_none
from elogs._version import __version__
from elogs.dashboard import latlon_read_s3, ls, random_string, remove_file, static_path
from elogs.dashboard.labels import label_to_rgb
from elogs.s3 import S3BucketReader

global s3, dyn

# AWS_ENV = Path(__file__).resolve().parent.parent / 'tests' / 'aws.env'
TXT_TYPE = ["txt", "log", "json"]
GEOTIFF_TYPE = ["tif", "jp2"]
S2GRID = gpd.read_file(Path(__file__).resolve().parent / "static" / "s2grid.fgb")
DEFAULT_PORT = 18080

app = Flask(__name__)
app.secret_key = "secret_key_generate"

# Configure server-side session storage
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./.flask_session/"
app.config["SESSION_PERMANENT"] = False
Session(app)


@app.context_processor
def inject_version():
    return dict(version=__version__)


@app.template_global()
def encode_prefix(prefix):
    return quote(prefix.replace("/", " "))


@app.route("/browse/<prefix>/", methods=["GET"])
def browse_folder(prefix):
    prefix = unquote(prefix).replace(" ", "/")  # gets removed by html

    page = request.args.get("page", 1, type=int)
    per_page = 20

    if prefix == "root":
        prefix = ""

    q = request.args.get("q", "")

    if "all_keys" not in session or session.get("current_prefix") != prefix:
        folders, files = ls(s3, prefix, sort_by_date=True)
        session["all_keys"] = {"folders": folders, "files": files}
        session["current_prefix"] = prefix

    else:
        folders = session["all_keys"]["folders"]
        files = session["all_keys"]["files"]

    if q:
        folders = [f for f in folders if q.lower() in f.lower()]
        files = [f for f in files if q.lower() in f.lower()]

    items = folders + files
    total_items = len(items)
    total_pages = ceil(total_items / per_page)

    start = (page - 1) * per_page
    end = start + per_page

    paginated_items = items[start:end]

    # Separate paginated items back into folders and files
    paginated_folders = [item for item in paginated_items if item in folders]
    paginated_files = [item for item in paginated_items if item in files]

    return render_template(
        "browse.html",
        folders=paginated_folders,
        files=paginated_files,
        page=page,
        total_pages=total_pages,
        q=q,
        prefix=prefix,
    )


@app.route("/clear_session")
def clear_session():
    session.pop("all_keys", None)
    session.pop("current_prefix", None)
    return redirect(url_for("browse_folder", prefix="root"))


@app.route("/view/<prefix>/")
def browse_file(prefix):
    ext = prefix.split(".")[-1]

    if ext in TXT_TYPE:
        return redirect(url_for("txt", prefix=prefix))

    elif ext in GEOTIFF_TYPE:
        return redirect(url_for("tif", prefix=prefix))

    else:
        txt = "ERROR: Not supported"
        return render_template("txt.html", prefix=prefix, txt=txt)


@app.route("/read/<prefix>/")
def txt(prefix):
    prefix = unquote(prefix).replace(" ", "/").strip("/")
    txt = s3.read_text(prefix).strip()
    return render_template("txt.html", prefix=prefix, txt=txt)


@app.route("/tif/<prefix>/")
def tif(prefix):
    import atexit
    from threading import Timer

    import numpy as np
    from skimage.io import imsave

    prefix = unquote(prefix).replace(" ", "/").strip("/")

    png_path = static_path(Path(random_string(10)).with_suffix(".png"))

    # arr, bounds = load_geotiff(s3, prefix)
    arr, bounds = latlon_read_s3(s3, prefix)

    if "_prediction.tif" in prefix:
        rgb = label_to_rgb(arr[0])
    elif arr.shape[0] in (1, 2):
        rgb = arr[0]
    elif arr.shape[0] >= 3:
        rgb = np.transpose(arr[:3], (1, 2, 0))

    xmin, ymin, xmax, ymax = bounds
    imsave(png_path, rgb)

    # clean after 30 secs or at exit
    atexit.register(remove_file, png_path)
    Timer(60, lambda: remove_file(png_path)).start()

    return render_template(
        "leaflet.html",
        url=url_for("static", filename=png_path.name),
        xmin=xmin,
        ymin=ymin,
        xmax=xmax,
        ymax=ymax,
    )


@app.route("/")
def index():
    from elogs.dashboard.tables import df_html_to_bootstrap, get_apps_df

    elogs_apps_table_name: str = "elogs-apps-registry"
    df = get_apps_df(dyn, elogs_apps_table_name)
    df_table = df_html_to_bootstrap(df)
    # Add an ID to the table for DataTables
    df_table = df_table.replace("<table", '<table id="dataframe-table"')
    return render_template("index.html", df_table=df_table)


def get_tile_centroid(tile):
    tile_gdf = S2GRID[S2GRID.tile == tile]
    if tile_gdf.shape[0] == 0:
        lat, lon = 44, 10
    else:
        c = tile_gdf.iloc[0].geometry.centroid
        lat, lon = c.y, c.x

    return lat, lon


@app.route("/s2gridc/<lat>/<lon>/<zoom>/")
def s2gridc(lat, lon, zoom):
    fn = "s2grid.fgb"
    return render_template(
        "s2grid.html", fgb=url_for("static", filename=fn), lat=lat, lon=lon, zoom=zoom
    )


@app.route("/s2grid/", methods=["GET"])
def s2grid():
    tile = request.args.get("tile")
    if tile is not None:
        lat, lon = get_tile_centroid(tile)
        zoom = 8
    else:
        lat = 44
        lon = 10
        zoom = 6

    fn = "s2grid.fgb"
    return render_template(
        "s2grid.html", fgb=url_for("static", filename=fn), lat=lat, lon=lon, zoom=zoom
    )


@app.route("/tile", methods=["GET"])
def tile():
    tile = request.args["tile"]
    lat, lon = get_tile_centroid(tile)
    zoom = 8
    return redirect(url_for("s2gridc", lat=lat, lon=lon, zoom=zoom))


@app.route("/s2grid_tile/<tile>/")
def s2grid_tile(tile):
    lat, lon = get_tile_centroid(tile)
    return redirect(url_for("s2gridc", lat=lat, lon=lon, zoom=8))


def main():
    global s3, dyn
    # add parser for aws.env
    import argparse

    from elogs.dynamo import DynamoClient

    parser = argparse.ArgumentParser()
    parser.add_argument("--aws-env")
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    aws_env = args.aws_env

    if aws_env is not None:
        load_dotenv(aws_env)

    (aws_access_key_id, aws_secret_access_key, bucket) = check_env_vars_if_none(
        None, None, None
    )

    # upload auxdata bundle for ewoco
    s3 = S3BucketReader.from_credentials(
        aws_access_key_id, aws_secret_access_key, bucket
    )

    dyn = DynamoClient.from_credentials(aws_access_key_id, aws_secret_access_key)

    app.run(host="0.0.0.0", port=args.port, debug=True)


if __name__ == "__main__":
    main()
