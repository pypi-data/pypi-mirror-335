import os
import IPython

from pyspark.sql import SparkSession


def get_platform():
    return "databricks"


_spark = SparkSession.builder.getOrCreate()
_ipython = IPython.get_ipython()


def get_spark():
    return _spark


def _resolve_dbutils():
    if not hasattr(_ipython, "user_ns") or "dbutils" not in _ipython.user_ns:
        raise Exception("dbutils cannot be resolved")

    return _ipython.user_ns["dbutils"]


_dbutils = _resolve_dbutils()


def _get_notebook_context():
    return _dbutils.notebook.entry_point.getDbutils().notebook().getContext()


def get_dbutils():
    return _dbutils


def create_text_widget(name, label, default_value=""):
    _dbutils.widgets.text(name, default_value, label)


def create_combobox_widget(name, options, label, default_value=""):
    _dbutils.widgets.combobox(name, default_value, options, label)


def get_widget_value(widget_name):
    return _dbutils.widgets.get(widget_name)


def _resolve_display():
    return _ipython.user_ns["display"]


_display = _resolve_display()


def display(*args, **kwargs):
    _display(*args, **kwargs)


def _resolve_display_html():
    if not hasattr(_ipython, "user_ns") or "displayHTML" not in _ipython.user_ns:
        raise Exception("displayHTML cannot be resolved")

    return _ipython.user_ns["displayHTML"]


_display_html = _resolve_display_html()


def display_html(html):
    _display_html(html)


def _find_project_dir(input_path: str):
    current_path = os.path.dirname(input_path)

    if os.path.exists(current_path + "/pyproject.toml") or os.path.exists(current_path + "/requirements.txt"):
        return current_path

    return _find_project_dir(current_path)


_project_dir = _find_project_dir(
    "/Workspace"
    + _dbutils.notebook.entry_point.getDbutils()
    .notebook()
    .getContext()
    .notebookPath()
    .get()
)


def get_project_dir():
    return _project_dir


def run_notebook(name, params=None, timeout=6000):
    params = params or {}

    _dbutils.notebook.run(f"{_project_dir}/notebooks/{name}", timeout, params)


def get_notebook_path():
    return _get_notebook_context().notebookPath().get()


def get_current_username():
    return _get_notebook_context().tags().get("user").get()


def get_secret(scope, key):
    return _dbutils.secrets.get(scope, key)


class Filesystem:
    @classmethod
    def cp(cls, from_: str, to: str, recurse: bool = False):
        return _dbutils.fs.cp(from_, to, recurse)

    @classmethod
    def exists(cls, path: str):
        try:
            _dbutils.fs.head(path)

            return True
        except Exception as e:
            if "Cannot head a directory:" in str(e):
                return True

            if "java.io.FileNotFoundException" in str(e):
                return False

            raise

    @classmethod
    def head(cls, file: str, maxbytes: int = 65536):
        return _dbutils.fs.head(file, maxbytes)

    @classmethod
    def ls(cls, path: str):
        return [item.name for item in _dbutils.fs.ls(path)]

    @classmethod
    def mkdirs(cls, path: str):
        return _dbutils.fs.mkdirs(path)

    @classmethod
    def mv(cls, from_: str, to: str, recurse: bool = False):
        return _dbutils.fs.mv(from_, to, recurse)

    @classmethod
    def put(cls, file: str, contents: str, overwrite: bool = False):
        return _dbutils.fs.put(file, contents, overwrite)

    @classmethod
    def rm(cls, path: str, recursive: bool = False):
        return _dbutils.fs.rm(path, recursive)
