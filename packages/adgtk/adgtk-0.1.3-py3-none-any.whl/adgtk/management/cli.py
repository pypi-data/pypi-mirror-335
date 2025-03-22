"""Handlers for the CLI tools for this project
"""

import logging
from typing import Literal, Union
import datetime
import argparse
import sys
import os
import shutil
import signal
import tarfile
import importlib.resources
import http.server
from http.server import HTTPServer
import socketserver
import toml
import yaml
from jinja2 import Environment, FileSystemLoader
from adgtk.common import (
    DEFAULT_SETTINGS,
    DEFAULT_EXP_DEF_DIR,
    DEFAULT_BATCH_DIR)
from adgtk.scenario import ScenarioManager
from adgtk.experiment import ExperimentBuilder
from adgtk.utils import (
    get_user_input,
    start_logging,
    clear_screen,
    create_line,
    load_settings)
from adgtk import __version__ as adgtk_ver
from .intro import intro

# ----------------------------------------------------------------------
# Module configuration
# ----------------------------------------------------------------------
WIZARD_OPTIONS = ("agent", "environment", "policy", "scenario", "custom")

# ----------------------------------------------------------------------
# Module variables
# ----------------------------------------------------------------------
httpd: Union[HTTPServer, None] = None
http_dir = "html"
# ----------------------------------------------------------------------
# Signal handlers
# ----------------------------------------------------------------------


def signal_handler(signum, frame):
    """Handles the signal from the OS

    :param signum: The signal number
    :type signum: int
    :param frame: the frame object
    :type frame: stack frame
    """
    global httpd
    # https://docs.python.org/3/library/signal.html
    if signal.SIGINT == signum:
        print('\nRecievd Ctrl+C! Canceling action.')
        if httpd is not None:
            httpd.server_close()
            print("Server stopped")
    sys.exit(0)

# ----------------------------------------------------------------------
# Web Server
# ----------------------------------------------------------------------


class Handler(http.server.SimpleHTTPRequestHandler):
    """Handler for the web server

    :param http: _description_
    :type http: _type_
    """
    global http_dir

    def __init__(self, *args, directory=http_dir, **kwargs):
        super().__init__(*args, directory=http_dir, **kwargs)


def start_web_server(port: int = 8000, directory: str = "html") -> None:
    """Starts a web server.

    :param port: The port to listen on, defaults to 8000
    :type port: int, optional
    :param directory: The directory to serve, defaults to "html"
    :type directory: str, optional
    """
    global httpd
    global http_dir
    http_dir = directory
    addr = ('', port)
    try:
        # TODO: Fix the type hinting
        httpd = socketserver.TCPServer(addr, Handler)   # type: ignore
        print(f"serving at port {port}")
        if httpd is not None:
            httpd.serve_forever()
        else:
            print("Failed to start server")
            sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)


# ----------------------------------------------------------------------
# Management
# ----------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """Parses the command line arguments

    Returns:
        argparse.Namespace: The command line input
    """
    parser = argparse.ArgumentParser()

    # modifiers
    parser.add_argument(
        '-f', '--file',
        type=str,
        help="override the settings file with this file")
    parser.add_argument(
        '--version', action='version', version=f"ADGTK {adgtk_ver}")
    parser.add_argument(
        '--sample',
        action='store_true',
        help="Creates a project with sample code.")
    parser.add_argument(
        "--yaml",
        help="Use YAML format when creating the project settings.file.",
        action="store_true")

    # now positional
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands")

    # Project
    project_parser = subparsers.add_parser("project", help="Project actions")
    project_parser.add_argument(
        "action",
        choices=["create", "destroy"],
        help="Available project actions")
    project_parser.add_argument(
        "name",
        type=str,
        nargs="?",
        help="The project name")

    # Experiment
    exp_parser = subparsers.add_parser(
        "experiment", help="Experiment actions")
    exp_parser.add_argument(
        "action",
        choices=["create", "destroy", "list", "run", "preview", "report"],
        help="Available experiment actions")
    exp_parser.add_argument(
        "name",
        type=str,
        nargs="?",
        help="The experiment name")

    # Factory
    factory_parser = subparsers.add_parser(
        "factory", help="Factory actions")
    factory_parser.add_argument(
        "name",
        type=str,
        nargs="?",
        help="The group name")

    # Batch
    batch_parser = subparsers.add_parser(
        "batch", help="Batch actions")
    batch_parser.add_argument(
        "action",
        choices=["run", "preview", "list", "create"],
        help="Available batch actions")
    batch_parser.add_argument(
        "name",
        type=str,
        nargs="?",
        help="The batch name")

    args = parser.parse_args()
    return args


def build_folders_from_settings():
    """Builds out the folders based on settings"""
    settings = load_settings()
    if not os.path.exists(settings.experiment["data_dir"]):
        os.makedirs(name=settings.experiment["data_dir"], exist_ok=True)
    if not os.path.exists(settings.experiment["results_dir"]):
        os.makedirs(name=settings.experiment["results_dir"], exist_ok=True)
    if not os.path.exists(settings.experiment["tensorboard_dir"]):
        os.makedirs(name=settings.experiment["tensorboard_dir"], exist_ok=True)
    if not os.path.exists(settings.experiment["definition_dir"]):
        os.makedirs(name=settings.experiment["definition_dir"], exist_ok=True)
    if not os.path.exists(settings.logging["log_dir"]):
        os.makedirs(name=settings.logging["log_dir"], exist_ok=True)


def create_settings_file(
    project_name: str,
    data_format: Literal["toml", "yaml"] = "toml",
    clean: bool = False
) -> None:
    """Creates the settings file on project creation. It uses a template
    to create the settings file.

    :param project_name: The project name to be created
    :type project_name: str
    :param data_format: The format of the settings file,
        defaults to "toml"
    :type data_format: Literal[&quot;toml&quot;, &quot;yaml&quot;],
        optional
    :param clean: _description_, defaults to False
    :type clean: bool, optional        
    """

    filename = "project.toml"
    options = "Invalid file type"

    settings_data = DEFAULT_SETTINGS.copy()
    if clean:
        settings_data["user_modules"] = []

    if data_format == "toml":
        options = toml.dumps(settings_data)
    elif data_format == "yaml":
        filename = "project.yaml"
        options = yaml.safe_dump(
            settings_data, sort_keys=False, default_flow_style=False)

    # now craft the file
    env = Environment(loader=FileSystemLoader(
        os.path.join(project_name, 'templates')))
    template = env.get_template("settings.jinja")
    output = template.render(version=adgtk_ver, options=options)

    target_file = os.path.join(project_name, filename)
    with open(file=target_file, encoding="utf-8", mode="w") as outfile:
        outfile.write(output)


def build_experiment(
    experiment_definition_dir: str,
    load_user_modules: list,
    use_formatting: bool = True,
    name: Union[str, None] = None
) -> None:
    """Builds an experiment and saves to disk


    :param name: The name of the experiment, defaults to None
    :type name: Union[str, None], optional
    """
    # Just in case. Build folder(s)
    build_folders_from_settings()

    # and now build the experiment
    builder = ExperimentBuilder(
        experiment_definition_dir=experiment_definition_dir,
        load_user_modules=load_user_modules,
        scenario_manager=None)

    builder.build_interactive(name)

# ---------------------------------------------------------------------
# Project functions
# ---------------------------------------------------------------------


def create_project(
    name: str,
    file_format: Literal["yaml", "toml"] = "toml",
    sample: bool = False
) -> bool:
    """Creates a project

    :param name: The project/directory name to create
    :type name: str
    :param file_format: the format of the settings, defaults to "toml"
    :type file_format: Literal[&quot;yaml&quot;, &quot;toml&quot;], optional
    :param sample: Include sample files, defaults to False
    :type sample: bool, optional
    :return: True if successful, else False
    :rtype: bool
    """
    print(f"Creating project: {sample}")

    if name is None:
        return False

    if os.path.exists(name):
        print("Unable to create a project. remove the other first!")
    elif name is None:
        print("Please specify a name of your project")
    else:
        print(f"Attempting to create {name}")
        if not sample:
            # the clean.tar doesn't have the sample code. See Makefile
            filestream = importlib.resources.files(
                "adgtk").joinpath("clean.tar").open("rb")
        else:
            filestream = importlib.resources.files(
                "adgtk").joinpath("template.tar").open("rb")

        archive = tarfile.open(fileobj=filestream)
        archive.extractall("./")
        archive.close()

        # and rename
        os.rename("project_template", name)

        # safety check
        if os.path.exists(name):
            # now create the settings.py
            clean = True
            if sample:
                clean = False

            create_settings_file(name, data_format=file_format, clean=clean)
            # and let the user know it worked
            print(f"Successfully created project {name}")
            print(f"`cd {name}` to work with the project")
            return True

    print(f"Error creating {name}")
    return False


def destroy_project(name: str) -> bool:
    """Destroys a folder and all its contents

    Args:
        name (str): The folder to destroy
    """
    if name is not None:
        if os.path.exists(name):
            exp_file = os.path.join(name, "project.toml")
            if not os.path.exists(exp_file):
                print("Does not appear to be an ADGTK project. Cancelling")
                return False
            ask_to_remove = f": Please type [{name}] to confirm deleting this project: "
            confirmation = input(ask_to_remove)
            if confirmation.lower() == name.lower():
                shutil.rmtree(name)
                if os.path.exists(name):
                    print("Failed to remove. Please check case")
                else:
                    print(f"Successfully destroyed {name}")
            else:
                print("No action taken.")
            return True
        else:
            print(f"Unable to find project {name} to destroy")
            return True

    return False


def execute(
    experiment: str,
    load_user_modules: list,
    batch_mode: bool = False
) -> None:
    """Runs an experiment

    Args:
        experiment (str): The experiment-definition to run. This is the
            file located in the definition folder as outlined in the
            settings.py file.
    """
    if os.path.exists("project.toml") or os.path.exists("project.yaml"):
        start_logging(name=experiment, surpress_chatty=True, preview=False)
    else:
        print("Execution is unable to find the settings file")
        sys.exit(0)

    loader = ScenarioManager(
        load_user_modules=load_user_modules,
        experiment_definition_dir=DEFAULT_EXP_DEF_DIR)
    loader.load_experiment(experiment)
    if loader.active_scenario is not None:
        loader.run_experiment()
    else:
        msg = "Failure establishing scenario from file"
        logging.error(msg)
        print(msg)
    if not batch_mode:
        sys.exit(0)


def run_batch(batch: str, load_user_modules: list) -> None:
    """Runs a batch of exeperiments

    :param batch: the batch to run
    :type batch: str
    :param load_user_modules: the user modules to load
    :type load_user_modules: list
    """

    if os.path.exists("project.toml") or os.path.exists("project.yaml"):
        start_logging(name=batch, surpress_chatty=True, preview=False)
    else:
        print(
            f"{datetime.datetime.now()} - ERROR: Batch process is unable to "
            "find the settings file")
        sys.exit(0)

    settings = load_settings()
    # create if it doesn't exist
    os.makedirs(settings.batch_dir, exist_ok=True)

    batch_file = os.path.join(settings.batch_dir, f"{batch}.yaml")
    if not os.path.exists(batch_file):
        print(f"Batch file {batch_file} not found")
        sys.exit(0)

    with open(batch_file, "r", encoding="utf-8") as infile:
        batch_data = yaml.safe_load(infile)
        msg = f"{datetime.datetime.now()} - Starting batch {batch} : "\
            f"{batch_data['comments']}"
        print(msg)
        print(create_line(msg, char="="))
        for exp in batch_data["experiments"]:
            print(f"{datetime.datetime.now()} - Starting experiment {exp}")
            execute(
                experiment=exp,
                load_user_modules=load_user_modules,
                batch_mode=True)
            print(create_line(msg, char="-"))
    sys.exit(0)


def preview(experiment: str) -> None:
    """Previews an experiment

    :param experiment: The experiment to preview.
    :type experiment: str
    """
    start_logging(name=experiment, surpress_chatty=True, preview=True)
    loader = ScenarioManager(
        experiment_definition_dir=DEFAULT_EXP_DEF_DIR)
    loader.load_experiment(experiment)
    if loader.active_scenario is not None:
        loader.preview_experiment()
    else:
        print("Failure establishing scenario from file")

    sys.exit(0)


def print_title(clear_screen_first: bool = True) -> None:
    """Clears the screen and prints to console the title

    :param clear_screen_first: Clear screen first, defaults to True
    :type clear_screen_first: bool, optional
    """

    title_string = f"ADGTK - Version {adgtk_ver}"
    line = create_line(title_string)
    if clear_screen_first:
        clear_screen()

    print(line)
    print(title_string)
    print(line)
    print()


# ---------------------------------------------------------------------
# interacting with files and folders
# ---------------------------------------------------------------------
def get_exp_comments_w_basename(file_w_path: str) -> tuple:
    title = os.path.basename(file_w_path)
    comments = "Not set"
    error_found = False
    exp_def = {}
    if file_w_path.lower().endswith(".toml"):
        with open(file_w_path, "r", encoding="utf-8") as infile:
            exp_def = toml.load(infile)
    elif file_w_path.lower().endswith(".yaml"):
        with open(file_w_path, "r", encoding="utf-8") as infile:
            try:
                exp_def = yaml.safe_load(infile)
            except yaml.parser.ParserError as e:
                error_found = True
                comments = f"INVALID: {e}"

    if title.endswith(".toml") or title.endswith(".yaml"):
        title = title[:-5]

    if not error_found:
        if "comments" in exp_def:
            if len(exp_def["comments"]) > 0:
                comments = exp_def["comments"]

    return title, comments


def get_experiment_list(exp_def_dir: Union[str, None] = None) -> list:
    if exp_def_dir is None:
        # try the default
        exp_def_dir = DEFAULT_EXP_DEF_DIR
    try:
        in_files = os.listdir(exp_def_dir)
        files = sorted(in_files)
    except FileNotFoundError:
        print(
            "ERROR: experiment definition directory not found. Check the path.")
        print("Unable to list experiments")
        return []

    return files


def get_exp_to_run(exp_def_dir: Union[str, None] = None) -> str:

    if exp_def_dir is None:
        exp_def_dir = DEFAULT_EXP_DEF_DIR

    experiments = get_experiment_list(exp_def_dir=exp_def_dir)
    if len(experiments) == 0:
        print(f"No experiments found. Please check path for {exp_def_dir}")
        sys.exit(1)

    title = "Experiment"
    comments = "Comments"
    msg = "  Select which experiment to run:"
    line = create_line("", char="-", modified=79)
    print(msg)
    print(line)
    choices = []

    for file in experiments:
        file_w_path = os.path.join(exp_def_dir, file)
        title, comments = get_exp_comments_w_basename(file_w_path)
        choices.append(title)
        print(f"{title:<40} | {comments}")

    print()
    val = get_user_input(
        configuring="experiment",
        request="Which experiment to run?",
        choices=choices,
        requested="str")

    return str(val)


def list_experiments(exp_def_dir: Union[str, None] = None) -> list:

    if exp_def_dir is None:
        exp_def_dir = DEFAULT_EXP_DEF_DIR

    experiments = get_experiment_list(exp_def_dir=exp_def_dir)
    if len(experiments) == 0:
        return []

    title = "Experiment"
    comments = "Comments"
    msg = "  Available experiments"
    line = create_line("", char="-", modified=79)
    print(msg)
    print(line)

    experiments = []

    for file in experiments:
        file_w_path = os.path.join(exp_def_dir, file)
        title, comments = get_exp_comments_w_basename(file_w_path)
        experiments.append(title)
        print(f"{title:<40} | {comments}")

    print(line)
    return experiments


# --------------------------------------------------------------------
# for batch listing
# --------------------------------------------------------------------
def cleanup_name(name: str):
    name = name.replace('.yaml', '')
    name = name.replace('.yml', '')
    name = name.replace('.toml', '')
    return name


def count_results(exp_names: list):
    all_results = os.listdir('results')
    count = 0
    for name in exp_names:
        if name in all_results:
            count += 1
    return count


def list_batch_experiments(batch_dir: str, filename: str) -> tuple:
    batch_file = os.path.join(batch_dir, filename)
    completed_count = 0
    expected_count = 0

    with open(batch_file) as file:
        config = yaml.safe_load(file)
        exp_list = config["experiments"]
        completed_count = count_results(exp_list)
        expected_count = len(exp_list)
        comments = config["comments"]

    return (completed_count, expected_count, comments)


def list_batches(batch_dir: str, show_completed=True) -> list:

    msg = "Available batches"
    line = create_line("", char="-", modified=79)
    print(msg)
    print(line)

    batch_listing = os.listdir(batch_dir)
    batch_names = []
    for batch in batch_listing:
        c_count, e_count, comments = list_batch_experiments(
            batch_dir=batch_dir, filename=batch)
        batch_name = cleanup_name(batch)
        if show_completed:
            batch_names.append(batch_name)
            print(f"- {batch_name:<20} {comments:<60} [{c_count}/{e_count}]")
        elif c_count < e_count:
            batch_names.append(batch_name)
            print(f"- {batch_name:<20} {comments:<60} [{c_count}/{e_count}]")

    return batch_names


def get_batch_to_run(batch_dir: Union[str, None] = None) -> str:

    if batch_dir is None:
        batch_dir = DEFAULT_BATCH_DIR

    batches = list_batches(batch_dir=batch_dir, show_completed=False)
    if len(batches) == 0:
        print(f"No available batches found. Please check path for {batch_dir}")
        sys.exit(1)

    title = "Batch"
    comments = "Comments"
    msg = "  Select which batch to run:"
    line = create_line("", char="-", modified=79)
    print(msg)
    print(line)

    val = get_user_input(
        configuring="batch",
        request="Which batch to run?",
        choices=batches,
        requested="str")

    return str(val)

# --------------------------------------------------------------------
# --------------------------------------------------------------------
#          !!! MANAGER !!! THIS IS THE MAIN FUNCTION
# --------------------------------------------------------------------
# --------------------------------------------------------------------


def manager() -> None:
    """provides a CLI management"""

    signal.signal(signal.SIGINT, signal_handler)

    args = parse_args()
    inside_a_project = False
    # using local variables with a fallback to default for safety

    try:
        if args.file is not None:
            print(f"ADGTK: Loading settings from file {args.file}")
            settings = load_settings(args.file)
        else:
            settings = load_settings()
        exp_def_dir = settings.experiment["definition_dir"]
        batch_def_dir = settings.batch_dir
        user_modules = settings.user_modules
        inside_a_project = True
    except FileNotFoundError:
        exp_def_dir = None
        user_modules = []
    except ValueError:
        msg = f"""
ERROR: Unable to load settings from {args.file}
Reminder: File must end with .toml or .yaml and be properly formatted.
"""
        print(msg)
        sys.exit(1)

    # ----- Project command ------
    if args.command == 'project':
        if args.name is None:
            print("Name of the project is required")
            sys.exit()
        print(args)
        sample = False

        if args.action == "create":
            if args.sample:
                sample = False
                if args.sample:
                    sample = True

            if args.yaml:
                result = create_project(
                    name=args.name, file_format="yaml", sample=sample)
            else:
                result = create_project(
                    name=args.name, file_format="toml", sample=sample)
            if not result:
                print("Error processing\n")
        elif args.action == "destroy":
            if not destroy_project(args.name):
                print("Error processing\n")

        sys.exit(0)
    # ----- batch command ------
    elif args.command == 'batch':
        if not inside_a_project:
            print("No setttings file found. Please check the path")
            sys.exit(0)
        if args.action == "run":
            if args.name is None:
                exp_file = get_batch_to_run(batch_def_dir)
                run_batch(batch=exp_file, load_user_modules=user_modules)
            else:
                # cleanup
                if exp_def_dir in args.name:
                    args.name.replace(exp_def_dir, "")
                    args.name.replace("/", "")
                    args.name.replace("\\", "")
                if args.name.endswith(".toml") or args.name.endswith(".yaml"):
                    args.name = args.run[:-5]

                # and execute
                run_batch(batch=args.name, load_user_modules=user_modules)

        elif args.action == "preview":
            print("Preview not available for a batch. Preview experiments instead")
        elif args.action == "list":
            print_title(clear_screen_first=False)
            _ = list_batches(batch_dir=batch_def_dir, show_completed=True)

        elif args.action == "create":
            print("Batch creation is not supported via the CLI.")

        sys.exit(0)
    # ----- experiment command ------
    elif args.command == 'experiment':
        if not inside_a_project:
            print("No setttings file found. Please check the path")
            sys.exit(0)

        # work the action
        if args.action == "list":
            print_title(clear_screen_first=False)
            _ = list_experiments(exp_def_dir)
        elif args.action == "run":
            if args.name is None:
                exp_file = get_exp_to_run(exp_def_dir)
                execute(experiment=exp_file, load_user_modules=user_modules)
            else:
                # cleanup
                if exp_def_dir in args.name:
                    args.name.replace(exp_def_dir, "")
                    args.name.replace("/", "")
                    args.name.replace("\\", "")
                if args.name.endswith(".toml") or args.name.endswith(".yaml"):
                    args.name = args.run[:-5]

                # and execute
                execute(experiment=args.name, load_user_modules=user_modules)

            sys.exit(0)

        elif args.action == "create":
            print_title(clear_screen_first=True)
            build_experiment(
                experiment_definition_dir=exp_def_dir,
                load_user_modules=user_modules,
                name=args.name)

        elif args.action == "destroy":
            print("Roadmap item. Not implemented yet")
        elif args.action == "preview":
            print_title(clear_screen_first=True)
            preview(args.Preview)
        elif args.action == "report":
            start_web_server(
                port=settings.server["port"],
                directory=settings.experiment["results_dir"])

        sys.exit(0)

    elif args.command == "factory":
        if not inside_a_project:
            print("No setttings file found. Please check the path")
            sys.exit(0)

        print_title(clear_screen_first=False)

        if args.name is not None:
            msg = f"Scenario factory/report for group {args.name}"
            group_label = args.name

            msg = f"Scenario factory/report for group {group_label}"
            line = create_line(msg, char=".")
            print(msg)
            print(line)
            print()
            scenario_mgr = ScenarioManager(load_user_modules=user_modules)
            print(scenario_mgr.group_report(args.name))

            # any problems loading?
            if len(scenario_mgr.load_user_modules_errs) > 0:
                print("ERRORS")
                print("------")
                for err in scenario_mgr.load_user_modules_errs:
                    print(f" - {err}")
        else:
            msg = "Scenario factory/report"
            line = create_line(msg, char=".")
            print(msg)
            print(line)
            print()

            scenario_mgr = ScenarioManager(load_user_modules=user_modules)
            print(scenario_mgr)

            # any problems loading?
            if len(scenario_mgr.load_user_modules_errs) > 0:
                print("ERRORS")
                print("------")
                for err in scenario_mgr.load_user_modules_errs:
                    print(f" - {err}")

        # end of factory option
        sys.exit(0)

    print(intro)
    sys.exit()


if __name__ == '__main__':
    manager()
