from dotenv import load_dotenv
import os
import subprocess
import pandas as pd
from pyspark.sql import SparkSession, DataFrame
from IPython.display import display as ipython_display
from IPython.core.display import HTML as ipython_HTML
import ipywidgets as widgets

load_dotenv()

pd.set_option("display.width", 1000)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_rows", 100)
pd.set_option("display.max_columns", 100)


def _create_spark() -> SparkSession:
    log_level = "ERROR"

    spark = (
        SparkSession.builder.config(
            "spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension"
        )
        .config("spark.sql.catalogImplementation", "hive")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0")
        .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.3.0")
        .config("spark.jars.packages", "io.delta:delta-sharing-spark_2.12:3.3.0")
        .config("spark.sql.sources.default", "delta")
        .config("spark.sql.default.tableFormat", "delta")
        .config(
            "spark.driver.extraJavaOptions", "-Dlog4j.logger.org.apache=" + log_level
        )
        .config("spark.sql.autoBroadcastJoinThreshold", -1)
        .config("spark.driver.memory", "25g")
        .config("spark.executor.memory", "25g")
        .config("spark.driver.maxResultsSize", "0")
        # .config("spark.executor.memoryOverhead", "2048")
        # .config("spark.memory.fraction", "0.9")      # Allocate more memory for execution
        # .config("spark.memory.storageFraction", "0.8")      # Adjust storage fraction
        .config("spark.dynamicAllocation.enabled", "true")  # Enable dynamic allocation
        .config("spark.dynamicAllocation.minExecutors", "1")
        .config("spark.dynamicAllocation.maxExecutors", "10")
        .config("spark.sql.shuffle.partitions", "200")  # Increase shuffle partitions
        .config("spark.memory.offHeap.enabled", "true")  # Enable off-heap memory usage
        .config("spark.memory.offHeap.size", "10g")  # Assign off-heap memory
        .master("local[*]")
        .enableHiveSupport()
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel(log_level)

    return spark


_spark = None


def get_platform():
    return "local"


def get_spark():
    global _spark

    if _spark is None:
        _spark = _create_spark()

    return _spark


def display(df, limit=20):
    if isinstance(df, pd.DataFrame):
        pandas_df = df
    elif isinstance(df, DataFrame):
        pandas_df = df.limit(limit).toPandas()
    else:
        pandas_df = pd.DataFrame([row for row in df])

    return pandas_df.head(limit)


def display_html(val):
    ipython_display(ipython_HTML(val))


def _find_project_dir(input_path: str):
    if os.path.exists(input_path + "/pyproject.toml") or os.path.exists(
        input_path + "/requirements.txt"
    ):
        return input_path

    return _find_project_dir(os.path.dirname(input_path))


_project_dir = _find_project_dir(os.getcwd())


def run_notebook(name, params=None, timeout=6000):
    script_path = get_project_dir() + "/notebooks/" + name + ".py"

    print("Running " + script_path)

    result = subprocess.run(["python", script_path], capture_output=True, text=True)

    print(result.stdout)

    if result.stderr:
        print(result.stderr)

    # Check if script ran successfully
    if result.returncode == 0:
        print(f"Finished successfully: {script_path}")
    else:
        print(f"Execution failed: {script_path}")
        raise Exception(f"Execution failed with code: {result.returncode}")


def get_project_dir():
    return _project_dir


_widgets = {}


def create_text_widget(name, label, default_value=""):
    global _widgets

    _widgets[name] = widgets.Text(
        value=default_value, description=label, disabled=False
    )

    ipython_display(_widgets[name])


def create_combobox_widget(name, options, label, default_value=""):
    global _widgets

    _widgets[name] = widgets.Combobox(
        placeholder="- select -",
        options=options,
        description=label,
        value=default_value,
        ensure_option=True,  # Only allow values from the list
        disabled=False,
    )

    ipython_display(_widgets[name])


def get_widget_value(name):
    global _widgets

    if name not in _widgets:
        raise Exception(f'Widget with name "{name}" does not exist')

    return _widgets[name].value


def get_secret(scope, key):
    path = scope + "__" + key

    if path not in os.environ:
        raise Exception("env variable {path} for secret not defined")

    return os.environ[path]


class Filesystem:
    @classmethod
    def cp(cls, from_: str, to: str, recurse: bool = False):
        raise Exception("Not implemented")

    @classmethod
    def exists(cls, path: str):
        raise Exception("Not implemented")

    @classmethod
    def head(cls, file: str, maxbytes: int = 65536):
        raise Exception("Not implemented")

    @classmethod
    def ls(cls, path: str):
        raise Exception("Not implemented")

    @classmethod
    def mkdirs(cls, path: str):
        raise Exception("Not implemented")

    @classmethod
    def mv(cls, from_: str, to: str, recurse: bool = False):
        raise Exception("Not implemented")

    @classmethod
    def put(cls, file: str, contents: str, overwrite: bool = False):
        raise Exception("Not implemented")

    @classmethod
    def rm(cls, path: str, recursive: bool = False):
        raise Exception("Not implemented")
