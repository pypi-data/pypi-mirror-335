from pathlib import Path

import click
import yaml
from flask import current_app, render_template_string
from flask.cli import FlaskGroup

from brython_dev import INDEX_TEMPLATE, __version__, create_app, read_config_file

MAIN_TEMPLATE = """
import argparse

def install(args):
    print(args)

parser = argparse.ArgumentParser()
subparser = parser.add_subparsers()

install = subparser.add_parser('install', help='Install {name} in an empty directory')
install.set_defaults(func=install)

"""

BRYTHON_TEMPLATE = """from browser import document, html\n\ndocument["main"] <= html.SPAN("Hello Brython!")"""
BRYTHON_TEST_TEMPLATE = """from browser import document, html\n\ndocument["tests"] <= html.SPAN("Hello Brython Tests!")"""

HTML_TEMPLATE = """<div id="main"></div>"""
HTML_TEST_TEMPLATE = """<div id="tests"></div>"""

LIST_COMAND = [
    "name",
    "proyect",
    "app",
    "template",
    "proyect_tests",
    "app_tests",
    "template_tests",
    "console",
    "metatags",
    "stylesheets",
    "extensions",
    "scripts",
    "pyscripts",
    "brython_url_prefix",
    "brython_options",
]


@click.group(cls=FlaskGroup, create_app=create_app, add_version_option=False)
@click.version_option(version=__version__)
def cli():
    """Management script for brython developers."""


@cli.command()
@click.argument("key", type=click.Choice(LIST_COMAND), required=False)
@click.argument("values", nargs=-1)
@click.option("-u", "--unset", is_flag=True, help="Unset configuration setting")
@click.option("-l", "--list", "list_", is_flag=True, help="List configuration settings")
@click.option("-a", "--all", "all_", is_flag=True, help="All configuration settings")
@click.option(
    "-b",
    "--brython-config-file",
    default="brython.yml",
    show_default=True,
    type=Path,
    help="The brython config file",
)
def config(key, values, unset, list_, all_, brython_config_file):
    """Manages brython.yml settings."""
    try:
        brython_config = {
            k.lower(): v for k, v in read_config_file(brython_config_file).items()
        }
    except AttributeError:
        brython_config = {}

    if all_:
        _config = create_app({"CONFIG_FILE": brython_config_file}).config
        click.echo(
            yaml.safe_dump(
                {
                    k.lower(): v
                    for k, v in _config.items()
                    if k.lower() in (key or LIST_COMAND)
                }
            )
        )
        return
    elif list_:
        click.echo(
            yaml.safe_dump(
                {k: v for k, v in brython_config.items() if k in (key or LIST_COMAND)}
            )
        )
        click.echo("--all for all configuration settings")
        return

    if key is None:
        return

    if key in (
        "name",
        "proyect",
        "app",
        "template",
        "proyect_tests",
        "app_tests",
        "template_tests",
        "console",
        "brython_url_prefix",
    ):
        if unset:
            try:
                del brython_config[key]
                brython_config_file.write_text(yaml.safe_dump(brython_config))
            except KeyError:
                pass
        elif values:
            if values[0].lower() in ("none", "null") and key in (
                "app",
                "template",
                "app_tests",
                "template_tests",
            ):
                brython_config[key] = None
            elif values[0].lower() in ("0", "no", "false") and key == "console":
                brython_config[key] = False
            elif key == "console":
                brython_config[key] = True
            else:
                brython_config[key] = " ".join(values)
            brython_config_file.write_text(yaml.safe_dump(brython_config))
        else:
            click.echo("Use --list or --all for view configuration settings")
    elif key in ("metatags", "stylesheets", "scripts", "pyscripts"):
        brython_config.setdefault(key, [])
        if not isinstance(brython_config[key], list):
            brython_config[key] = [brython_config[key]]
        if unset:
            if not values:
                del brython_config[key]
                brython_config_file.write_text(yaml.safe_dump(brython_config))
                return
            for i in range(len(brython_config[key])):
                if (
                    isinstance(brython_config[key][i], str)
                    and brython_config[key][i] == " ".join(values)
                ) or (
                    isinstance(brython_config[key][i], dict)
                    and (" ".join(values) in brython_config[key][i].values())
                ):
                    del brython_config[key][i]
                    brython_config_file.write_text(yaml.safe_dump(brython_config))
                    return
        elif values:
            if len(values) == 1 and "=" not in values[0] and key != "metatags":
                brython_config[key].append(values[0])
            else:
                try:
                    brython_config[key].append(
                        {k: v for k, v in map(lambda i: i.split("=", 1), values)}
                    )
                except ValueError:
                    click.echo("Only use key=value")

            brython_config_file.write_text(yaml.safe_dump(brython_config))
        else:
            click.echo("Use --list or --all for view configuration settings")
    else:
        brython_config.setdefault(key, {})
        if unset:
            if not values:
                del brython_config[key]
                brython_config_file.write_text(yaml.safe_dump(brython_config))
            else:
                try:
                    del brython_config[key][values[0]]
                    brython_config_file.write_text(yaml.safe_dump(brython_config))
                except KeyError:
                    pass
            return
        elif values:
            if (
                key == "extensions"
                and len(values) > 1
                and values[1].lower() in ("0", "no", "false")
            ):
                brython_config[key][values[0]] = False
            elif key == "extensions" and len(values) > 1:
                brython_config[key][values[0]] = True
            elif key == "brython_options":
                brython_config[key][values[0]] = values[1]
            brython_config_file.write_text(yaml.safe_dump(brython_config))


@cli.command()
@click.option("--name", prompt=True, help="Proyect name")
@click.option("--app", prompt=True, help="Proyect app", default="app.py")
@click.option("--template", prompt=True, help="Proyect template", default="app.html")
def init(name, app, template):
    """Creates a basic brython.yml file in the current directory."""

    safe_name = Path(name.lower().replace("-", "_"))
    root = safe_name if safe_name.is_dir() else Path.cwd()

    Path("brython.yml").write_text(f"name: {name}\napp: {app}\ntemplate: {template}")
    Path(root / app).write_text(BRYTHON_TEMPLATE)
    Path(root / template).write_text(HTML_TEMPLATE)
    Path("tests").mkdir(exist_ok=True)
    Path("tests/tests.html").write_text(HTML_TEST_TEMPLATE)
    Path("tests/tests.py").write_text(BRYTHON_TEST_TEMPLATE)


@cli.command()
def build():
    """Build the proyect."""

    safe_name = Path(current_app.config["NAME"].lower().replace("-", "_"))
    root = safe_name if safe_name.is_dir() else Path.cwd()

    # Path(root / "__main__.py").write_text(MAIN_TEMPLATE)
    Path(root / "index.html").write_text(render_template_string(INDEX_TEMPLATE))


if __name__ == "__main__":  # pragma: no cover
    cli(prog_name="bython-dev")
