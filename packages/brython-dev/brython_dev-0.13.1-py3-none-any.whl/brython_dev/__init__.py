import importlib.metadata
import logging
import pkgutil
import sysconfig
from copy import deepcopy
from pathlib import Path

import yaml
from flask import (
    Flask,
    jsonify,
    render_template,
    render_template_string,
    request,
    send_from_directory,
)
from jinja2.exceptions import TemplateNotFound
from yaml import YAMLError

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"


INDEX_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>{{ config["NAME"] }}</title>
    {%- for metatag in config["METATAGS"] %}
    <meta{{ metatag|xmlattr }}>
    {%- endfor %}
    {%- for stylesheet in config["STYLESHEETS"] %}
    <link{{ stylesheet|xmlattr }}>
    {%- endfor %}
</head>
<body>
    {{ load_template()|safe }}
    <brython-options{{ config["BRYTHON_OPTIONS"]|xmlattr }}></brython-options>
    {%- for script in config["SCRIPTS"] %}
    <script{{ script|xmlattr }}></script>
    {%- endfor %}
    {%- for pyscript in config["PYSCRIPTS"] %}
    <script{{ pyscript|xmlattr }}></script>
    {%- endfor %}
</body>
</html>
"""


def read_config_file(config_file):
    logger = logging.getLogger(f"{__name__}.config")
    try:
        if config_file.is_file():
            return {
                k.upper(): v for k, v in yaml.safe_load(config_file.read_text()).items()
            }
        else:
            logger.info(f"File {config_file.name} not found, use default values")
    except YAMLError:
        logger.info(f"YAML error in {config_file.name}, use default values")
    return {}


def create_app(__config__: dict = {}) -> Flask:
    config_file = Path(__config__.pop("CONFIG_FILE", "brython.yml")).resolve()

    config = read_config_file(config_file)
    config.update(__config__)

    config.setdefault("NAME", Path().resolve().name.lower())
    config.setdefault(
        "PROYECT",
        (
            config["NAME"].lower().replace("-", "_")
            if Path(config["NAME"].lower().replace("-", "_")).is_dir()
            else "."
        ),
    )
    config.setdefault("APP", "app.py")
    config.setdefault("TEMPLATE", "app.html")
    config.setdefault("PROYECT_TESTS", "tests")
    config.setdefault("APP_TESTS", "tests.py")
    config.setdefault("TEMPLATE_TESTS", "tests.html")
    config.setdefault("CONSOLE", False)
    config.setdefault("METATAGS", [])
    config.setdefault("STYLESHEETS", [])
    config.setdefault("EXTENSIONS", {})
    config["EXTENSIONS"].setdefault("brython", True)
    config["EXTENSIONS"].setdefault("brython_stdlib", False)
    config.setdefault("SCRIPTS", [])
    config.setdefault("PYSCRIPTS", [])
    config.setdefault("BRYTHON_URL_PREFIX", "/")
    config.setdefault("BRYTHON_OPTIONS", {})
    config.setdefault("STATIC_URL", "/")

    for key in ("METATAGS", "STYLESHEETS", "SCRIPTS", "PYSCRIPTS"):
        if not isinstance(config[key], list):
            config[key] = [config[key]]

    if config["EXTENSIONS"]["brython"]:
        config["SCRIPTS"].append("/brython.js")
    if config["EXTENSIONS"]["brython_stdlib"]:
        config["SCRIPTS"].append("/brython_stdlib.js")
    if config["APP"]:
        config["PYSCRIPTS"].append(config["APP"])
    if config["CONSOLE"] and config["EXTENSIONS"]["brython_stdlib"]:
        config["PYSCRIPTS"].append("/console.py")

    for i in range(len(config["METATAGS"])):
        if isinstance(config["METATAGS"][i], str):
            config["METATAGS"][i] = {
                k: v
                for k, v in map(
                    lambda i: i.split("=", 1), config["METATAGS"][i].split()
                )
            }

    for i in range(len(config["STYLESHEETS"])):
        if isinstance(config["STYLESHEETS"][i], str):
            config["STYLESHEETS"][i] = {
                "rel": "stylesheet",
                "href": config["STYLESHEETS"][i],
            }

    for i in range(len(config["SCRIPTS"])):
        if isinstance(config["SCRIPTS"][i], str):
            config["SCRIPTS"][i] = {
                "type": "text/javascript",
                "src": config["SCRIPTS"][i],
            }

    for i in range(len(config["PYSCRIPTS"])):
        if isinstance(config["PYSCRIPTS"][i], str):
            _id = (
                config["PYSCRIPTS"][i]
                .split("//", 1)[-1]
                .rsplit(".", 1)[0]
                .replace(":", "_")
                .replace("/", "_")
                .replace(".", "_")
            )
            config["PYSCRIPTS"][i] = {
                "id": _id,
                "type": "text/python3",
                "src": config["PYSCRIPTS"][i],
            }

    app = Flask(
        __name__,
        static_folder=Path(config["PROYECT"]).resolve(),
        static_url_path=config["STATIC_URL"],
        template_folder=Path(config["PROYECT"]).resolve(),
    )

    app.config.from_mapping(config)

    @app.template_global()
    def load_template():
        if request.path.startswith("/tests") and app.config["TEMPLATE_TESTS"]:
            filename = Path(app.config["PROYECT_TESTS"]) / app.config["TEMPLATE_TESTS"]
        elif not request.path.startswith("/tests") and app.config["TEMPLATE"]:
            filename = Path(app.config["PROYECT"]) / app.config["TEMPLATE"]
        else:
            return ""

        if not filename.exists():
            return f"The template <strong>{str(filename)}</strong> not exist"

        return "\n    ".join(filename.read_text().splitlines())

    @app.route("/")
    def index():
        try:
            return render_template("index.html")
        except TemplateNotFound:
            return render_template_string(INDEX_TEMPLATE)

    @app.route(f"/{app.config['NAME'].lower().replace('-', '_')}/<path:filename>")
    def proyect(filename: str):
        return send_from_directory(
            Path(app.config["NAME"].lower().replace("-", "_")).resolve(), filename
        )

    @app.route(f"{app.config['BRYTHON_URL_PREFIX']}brython.js")
    def brythonjs():
        return send_from_directory(
            pkgutil.resolve_name("brython").__path__[0], "data/brython.js"
        )

    @app.route(f"{app.config['BRYTHON_URL_PREFIX']}brython_stdlib.js")
    def brythonstdlibjs():
        return send_from_directory(
            pkgutil.resolve_name("brython").__path__[0], "data/brython_stdlib.js"
        )

    @app.route("/console.py")
    def console():
        return "from interpreter import Interpreter;Interpreter()"

    @app.route("/Lib/site-packages/<path:filename>")
    def site_packages(filename: str):
        return send_from_directory(sysconfig.get_path("purelib"), filename)

    @app.route("/tests")
    @app.route("/tests/files")
    def tests():
        if "files" in request.args or request.path == "/tests/files":
            return jsonify(
                [str(path).replace("\\", "/") for path in Path("tests").iterdir()]
            )

        tests_config = deepcopy(app.config)

        if not tests_config["EXTENSIONS"]["brython_stdlib"]:
            tests_config["SCRIPTS"].append(
                {"type": "text/javascript", "src": "/brython_stdlib.js"}
            )

        if tests_config["APP"]:
            del tests_config["PYSCRIPTS"][-1]

        if tests_config["CONSOLE"]:
            tests_config["PYSCRIPTS"].append(
                {"id": "console", "type": "text/python3", "src": "/console.py"}
            )

        if tests_config["APP_TESTS"]:
            _id = (
                tests_config["APP_TESTS"]
                .rsplit(".", 1)[0]
                .replace(":", "_")
                .replace("/", "_")
                .replace(".", "_")
            )
            tests_config["PYSCRIPTS"].append(
                {
                    "id": _id,
                    "type": "text/python3",
                    "src": f"/{tests_config['PROYECT_TESTS']}/{tests_config['APP_TESTS']}",
                }
            )

        template = render_template_string(INDEX_TEMPLATE, config=tests_config)
        return template

    @app.route("/tests/<path:filename>")
    def tests_lib(filename: str):
        return send_from_directory(Path("tests").resolve(), filename)

    return app
