"""For ease of working with the results folder. This module provides
a class to manage the folder structure for an experiment.
"""

import logging
import os
import shutil
import csv
from typing import Union, Any
import yaml
import toml
from adgtk.utils import load_settings

# ----------------------------------------------------------------------
#
# ----------------------------------------------------------------------
# py -m pytest -s test/common/test_results.py

# ----------------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------------
DEBUG = False

METRICS_FOLDER = "metrics"
METRICS_IMG_FOLDER = "images"
METRICS_DATA_FOLDER = "data"
DATASET_FOLDER = "datasets"
AGENT_FOLDER = "agent"
PERFORMANCE_FOLDER = "performance"

# ----------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------


def collect_batch_results(exp_prefix: str, results_dir: str) -> list:
    """Retrieves the results and the configuration of an experiment and
    puts it into a dictionary for processing.

    :param experiment_name: The name of the experiment
    :type experiment_name: str
    :return: a tuple of filename and a dict that contains results
    :rtype: dict
    """
    experiments = os.listdir(results_dir)
    results = []
    for experiment in experiments:
        if experiment.startswith(exp_prefix):
            folder_manager = FolderManager(experiment)
            results.append((experiment, folder_manager.collect_results()))

    return results

# ----------------------------------------------------------------------
# Classes
# ----------------------------------------------------------------------


class FolderManager:
    """A simple class to help manage and ensure a consistent folder
    structure for an experiment results. It takes the experiment name
    and the settings file to create the necessary folders and
    sub-folders. It also provides an easy way to access the paths to
    the respective use by reading the attributes.

    The class has the following useful attributes:
        * base_folder: the root folder for the experiment
        * agent: the folder for agent data
        * metrics: the folder for metrics
        * metrics_data: the folder for metrics data
        * metrics_img: the folder for metrics images
        * dataset: the folder for datasets
        * performance: the folder for performance data
        * model_dir: the folder for models
    """

    def __init__(
        self,
        name: str,
        settings_file_override: Union[str, None] = None,
        clear_and_rebuild: bool = False
    ):
        """Initialize and create if needed

        :param name: the experiment name
        :type name: str
        :param clear_and_rebuild: deletes all results, defaults to False
        :type clear_and_rebuild: bool
        :param settings_file_override: redirect settings file location,
            defaults to None
        :type settings_file_override: Union[str, None], optional
        :raises FileNotFoundError: Unable to load the settings file
        """

        # cleanup to ensure consistency
        name = name.lower()
        if name.endswith(".toml") or name.endswith(".yaml"):
            name = name[:-5]

        # now load the settings and set the items to manage
        try:
            settings = load_settings(file_override=settings_file_override)

        except FileNotFoundError as e:
            if settings_file_override is not None:
                msg = f"Unable to locate settings file {settings_file_override}"
            else:
                msg = "Unable to locate settings file from default location"
            logging.error(msg)
            raise FileNotFoundError(msg) from e

        exp_result_dir = os.path.join(settings.experiment["results_dir"], name)
        self.base_folder = exp_result_dir

        if os.path.exists(exp_result_dir) and clear_and_rebuild:
            shutil.rmtree(exp_result_dir)

        if not os.path.exists(exp_result_dir):
            os.makedirs(exp_result_dir, exist_ok=True)
            logging.info(f"Created {exp_result_dir}")
        elif DEBUG:
            msg = f"Folder Manager found {exp_result_dir}. No action taken "\
                "to create additional folders"
            logging.info(msg)

        # Agent data
        self.agent = os.path.join(exp_result_dir, AGENT_FOLDER)
        os.makedirs(self.agent, exist_ok=True)

        # Create metrics sub-folder(s)
        self.metrics = os.path.join(exp_result_dir, METRICS_FOLDER)
        self.metrics_data = os.path.join(
            self.metrics, METRICS_DATA_FOLDER)
        self.metrics_img = os.path.join(self.metrics, METRICS_IMG_FOLDER)

        os.makedirs(self.metrics, exist_ok=True)
        os.makedirs(self.metrics_data, exist_ok=True)
        os.makedirs(self.metrics_img, exist_ok=True)

        # create dataset folder
        self.dataset = os.path.join(exp_result_dir, DATASET_FOLDER)
        os.makedirs(self.dataset, exist_ok=True)

        # Performance
        self.performance = os.path.join(exp_result_dir, PERFORMANCE_FOLDER)
        os.makedirs(self.performance, exist_ok=True)

        # Models - added 0.1.1a1
        self.model_dir = "models"
        try:
            self.model_dir = settings.model_dir
        except AttributeError:
            logging.warning("Using older settings file. No model_dir found")
            self.model_dir = os.path.join(exp_result_dir, "models")

        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir, exist_ok=True)

        # and additional/existing files/folders
        self.logfile = os.path.join(settings.logging["log_dir"], f"{name}.log")
        self.data_dir = settings.experiment["data_dir"]
        self.tensorboard_dir = settings.experiment["tensorboard_dir"]
        self.exp_def_dir = settings.experiment["definition_dir"]
        self.name = name

    def __str__(self) -> str:
        """Creates a string representation of the FolderManager object

        :return: a useful string for UX via a CLI.
        :rtype: str
        """
        to_string = "FolderManager\n"
        to_string += "-------------\n"
        to_string += f" - log: {self.logfile}\n"
        to_string += f" - tensorboard: {self.tensorboard_dir}\n"
        to_string += f" - models: {self.model_dir}\n"
        to_string += f" - Performance: {self.performance}\n"
        to_string += f" - agent: {self.agent}\n"
        to_string += f" - metrics: {self.metrics}\n"
        to_string += f"    - data: {self.metrics_data}\n"
        to_string += f"    - images: {self.metrics_img}\n"
        to_string += f" - dataset: {self.dataset}\n"

        return to_string

    def collect_results(self) -> dict:
        """Collects data created through the course of an experiment. It
        does not collect proprietary data such as tensorboard. It also
        does not attempt to read datasets, only the filenames.

        It does read the logfile, performance data, and metrics data.

        :return: The experiment results
        :rtype: dict
        """
        # building blocks
        definition: dict[str, dict] = {}
        performance: dict[str, dict] = {}
        metrics: dict[str, str] = {}
        datasets: list[str] = []

        # assembly
        data: dict[str, Any] = {
            "definition": definition,
            "performance": performance,
            "metrics": metrics,
            "datasets": datasets,
            "logfile": ""
        }

        # experiment definition
        exp_def_yaml = os.path.join(self.exp_def_dir, f"{self.name}.yaml")
        exp_def_toml = os.path.join(self.exp_def_dir, f"{self.name}.toml")

        if os.path.exists(exp_def_yaml):
            with open(exp_def_yaml, "r") as infile:
                data["definition"] = yaml.safe_load(infile)
        elif os.path.exists(exp_def_toml):
            with open(exp_def_toml, "r") as infile:
                data["definition"] = toml.load(infile)
        else:
            data["definition"] = "No experiment definition found"

        # Logfile
        if os.path.exists(self.logfile):
            with open(self.logfile, "r") as infile:
                data["logfile"] = infile.read()
        else:
            data["logfile"] = "No log file found. Possibly part of a batch"

        # performance
        files = os.listdir(self.performance)
        for file in files:
            with open(os.path.join(self.performance, file), "r") as infile:
                # component, label
                "model-train.test_avg_loss.csv"
                component, label, _ = file.split(".")
                if component not in data["performance"]:
                    data["performance"][component] = {}
                csv_reader = csv.reader(infile, quoting=csv.QUOTE_NONNUMERIC)
                for row in csv_reader:
                    # should only be one row based on performance tracker
                    data["performance"][component][label] = row
        # metrics
        files = os.listdir(self.metrics_data)
        for file in files:
            with open(os.path.join(self.metrics_data, file), "r") as infile:
                data["metrics"][file] = infile.read()

        # dataset filenames
        data["datasets"] = os.listdir(self.dataset)

        return data
