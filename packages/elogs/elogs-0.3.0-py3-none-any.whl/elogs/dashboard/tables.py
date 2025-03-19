from flask import url_for
from urllib.parse import quote


def encode_prefix(prefix):
    return quote(prefix.replace("/", " "))


def _app_link(x):
    # <a href="{{url_for('browse_folder', prefix=encode_prefix(f))}}">{{f}}</a>
    prefix = f"elogs/{x}"
    url = url_for("browse_folder", prefix=encode_prefix(prefix))
    s = f'<a href="{url}">{x}</a>'

    return s


def df_html_to_bootstrap(df):
    display_cols = [
        "app_id",
        "username",
        "creation_time",
        "start_date",
        "end_date",
        "status",
        "done",
        "error",
        "running",
        "total",
    ]

    df = (
        df[display_cols]
        .sort_values("start_date", ascending=False)
        .reset_index(drop=True)
    )

    df["app_id"] = df.app_id.apply(lambda x: _app_link(x))

    # Strip date fields to two milliseconds precision
    for col in ["creation_time", "start_date", "end_date"]:
        df[col] = df[col].apply(lambda x: x[:-3] if isinstance(x, str) else x)

    df_lines = df.to_html(na_rep="").split("\n")

    df_lines[0] = '<table class="table">'

    is_thead = False
    is_body = False
    for i, lin in enumerate(df_lines):
        if "<thead>" in lin:
            is_thead = True
        elif "<tbody>" in lin:
            is_thead = False
            is_body = True

        if is_thead and ("<th>" in lin):
            lin = lin.replace("<th>", '<th scope="col">')
        if is_body and ("<th>" in lin):
            lin = lin.replace("<th>", '<th scope="row">')

        lin = lin.replace("&lt;", "<").replace("&gt;", ">")
        lin = lin.replace("text-align: right;", "text-align: left;")
        df_lines[i] = lin

    return "\n".join(df_lines)


# tables = list(dyn.resource.tables.all())
# for t in tables:
#     print(t.name)
def get_apps_df(dyn, elogs_apps_table_name="elogs-apps-v0.1.1"):
    import pandas as pd

    items = dyn.dump_table(elogs_apps_table_name)
    for item in items:
        if "username" not in item:
            item["username"] = "Unknown"  # or any default value you prefer
    df = pd.DataFrame(items)
    return df
