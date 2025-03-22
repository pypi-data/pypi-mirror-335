"""Component Factory is focused on registering, tracking, and creating
instances of user and system defined components. The factory is designed
to be updated at runtime and is used to create components for running
experiments.
"""

from __future__ import annotations
import logging
import os
import sys
import inspect
import toml
import yaml
from typing import Any, Union, List, TYPE_CHECKING
from adgtk.journals import ExperimentJournal
from adgtk.common import (
    DuplicateFactoryRegistration,
    FactoryImplementable,
    FactoryBlueprint,
    ComponentDef,
    InvalidScenarioState, 
    FolderManager)

from adgtk.utils import create_line, load_settings

# py -m pytest -s test/factory/test_component_factory.py

# ----------------------------------------------------------------------
# Module Options
# ----------------------------------------------------------------------
# used for development and troubleshooting.
LOG_FACTORY_CREATE = True

def uses_factory_on_init(component: FactoryImplementable) -> bool:
    """Checks if a component uses the factory on init

    :param component: The component to inspect
    :type component: FactoryImplementable
    :return: T: Uses factory on init, F: Does not use factory on init
    :rtype: bool
    """
    if inspect.isclass(component):
        args = inspect.signature(component).parameters
        if "factory" in args:
            return True
    return False


def uses_journal_on_init(component: FactoryImplementable) -> bool:
    """Checks if a component uses the journal on init

    :param component: The component to inspect
    :type component: FactoryImplementable
    :return: T: Uses journal on init, F: Does not use journal on init
    :rtype: bool
    """
    if inspect.isclass(component):
        args = inspect.signature(component).parameters
        if "journal" in args:
            return True
    return False


# ----------------------------------------------------------------------
# Factory
# ----------------------------------------------------------------------


class ObjectFactory:
    """A dynamic factory that creates and manages groups and types"""

    def __init__(
        self,
        journal: ExperimentJournal,
        factory_name: str = "Object Factory",
        settings_file_override: Union[str, None] = None
    ) -> None:
        self.factory_name = factory_name
        # A common place to establish the folder manager
        # should be set before creation. So it is set at experiment run.
        # this way an Agent if designed can run different experiments
        # in parallel or series.
        self.settings_file_override = settings_file_override
        self.folder_manager: FolderManager

        self._journal = journal

        self._registry: dict[str, dict[str, FactoryImplementable]] = {}
        self.registered_count = 0

        self.settings = load_settings()
        # formatting
        self.file_format = self.settings.default_file_format

    def __len__(self) -> int:
        return self.registered_count

    def update_folder_manager(self, name: str) -> None:
        self.folder_manager = FolderManager(
            name=name,
            settings_file_override=self.settings_file_override)

    def __str__(self) -> str:
        title = "Object Factory report"
        report = ""
        report += f"{title}\n"
        report += "---------------------\n"
        for key, group in sorted(self._registry.items()):
            report += f"Group-label: {key}\n"
            for item, _ in sorted(group.items()):
                report += f"  - type: {item}\n"

        return report

    def group_report(self, group_label: str) -> str:
        """Creates a report string for a group. Primary use is in the
        command line interface.

        :param group_label: The group to filter on
        :type group_label: str
        :return: a report showing the group members
        :rtype: str
        """

        title = f"Object Factory report for group1: {group_label}"

        line = create_line(title, "=")
        report = title
        report += f"\n{line}\n"
        if group_label not in self._registry:
            report = f"ERROR: No group {group_label} found\n\n"
            report += "Valid groups are:\n"
            report += create_line("", char=".", modified=17)
            report += "\n"
            for key in self._registry.keys():
                report += f"  - {key}\n"
            return report

        for item, _ in sorted(self._registry[group_label].items()):
            report += f"  - {item:<17}  | "
            desc = self.get_description(
                group_label=group_label, type_label=item)
            report += f"{desc}\n"

        return report

    def get_description(self, group_label: str, type_label: str) -> str:
        """Gets the description of a component that is registed.

        :param group_label: The group the component is a member of
        :type group_label: str
        :param type_label: the member in the group
        :type type_label: str
        :return: a string of the description as defined in the class.
        :rtype: str
        """
        try:
            return self._registry[group_label][type_label].description
        except IndexError:
            return "ERROR. group:type not found"
        except AttributeError:
            # ideally should not happen but if it does keep going!
            return "description not set"

    def register(
        self,
        creator: Any,
        group_label_override: Union[str, None] = None,
        type_label_override: Union[str, None] = None,
        log_entry: bool = True
    ) -> None:
        """Register an object.

        Args:
        :param group_label_overide: The group to which it belongs
        :type group_label_overide: str
        :param type_label_overide: the type within that group
        :type type_label_overide: str
        :param creator: The class to create
        :type creator: Any (implements Protocol FactoryImplementable)
        :raises DuplicateFactoryRegistration: The type label exists
        :raises TypeError: creator does not implement protocol
        """

        group_label: str = creator.blueprint["group_label"]
        type_label: str = creator.blueprint["type_label"]

        if group_label_override is not None:
            group_label = group_label_override
        if type_label_override is not None:
            type_label = type_label_override

        # Safety check
        if not isinstance(creator, FactoryImplementable):
            msg = f"Creator {creator} does not Implement FactoryImplementable"

            raise TypeError(msg)
        if group_label not in self._registry:
            self._registry[group_label] = {}

        # get groups
        c_group = self._registry[group_label]

        # and add to groups
        if type_label in c_group:
            raise DuplicateFactoryRegistration

        c_group[type_label] = creator


        self.registered_count += 1

    def unregister(self, group_label: str, type_label: str) -> None:
        """Unregisters a type from a group

        :param group_label: The group to which it belongs
        :type group_label: str
        :param type_label: the type within that group
        :type type_label: str
        :raises KeyError: Group label not found
        """
        if group_label in self._registry:
            c_group = self._registry[group_label]
            if type_label in c_group:
                c_group.pop(type_label, None)
        else:
            raise KeyError("Group label not found")

        self.registered_count -= 1

    def get_blueprint(
        self,
        group_label: str,
        type_label: str
    ) -> FactoryBlueprint:
        """Gets a blueprint for a component creator

        :param group_label: the group label
        :type group_label: str
        :param type_label: The type label
        :type type_label: str
        :raises KeyError: Group not found
        :raises KeyError: Type not found
        :return: The component blueprint
        :rtype: FactoryBlueprint
        """

        if group_label in self._registry:
            c_group = self._registry[group_label]
        else:
            raise KeyError("Group label not found")

        if type_label in c_group:
            component = c_group[type_label]
            return component.blueprint

        raise KeyError("Type label not found")

    def create(self, component_def: ComponentDef) -> Any:
        """creates a component based on a blueprint

        :param component_def: The item to build
        :type component_def: ComponentDef
        :raises KeyError: unable to find the object
        :return: A created object using the blueprint
        :rtype: Any
        """

        try:
            if "group_label" not in component_def:
                print("--------------------")
                print("COMPONENT DEFINITION")
                print("--------------------")
                print(component_def)
                print("--------------------")
                msg = "Invalid component definition, missing group_label"
                raise KeyError(msg)

            if "type_label" not in component_def:
                msg = "Invalid component definition, missing group_label"
                raise KeyError(msg)

            if component_def["group_label"] not in self._registry:
                msg = f'{component_def["group_label"]} not in factory. '\
                      "Unable to create"
                logging.error(msg)
                print(msg)
                sys.exit(1)
            g_label = component_def["group_label"]
            t_label = component_def["type_label"]
            # get the component_create
            component_create = self._registry[g_label][t_label]
        except KeyError as e:
            msg = "No valid creator found at: "\
                  f"{component_def['group_label']}:{component_def['type_label']}"
            logging.error(e)
            raise KeyError(e) from e

        # do we init w/factory & journal, factory only, or none?
        factory_flag = uses_factory_on_init(component_create)
        j_flag = uses_journal_on_init(component_create)

        if factory_flag and j_flag:
            if LOG_FACTORY_CREATE:
                g_label = component_def["group_label"]
                t_label = component_def["type_label"]
                msg = f"creating {g_label}:{t_label} with Journal and Factory"
                logging.info(msg)
            try:
                if inspect.isclass(component_create):
                    new_component = component_create(
                        factory=self,
                        journal=self._journal,
                        **component_def["arguments"])
                else:
                    msg = f"invalid type in factory for {g_label}|{t_label}"
                    logging.error(msg)
                    raise InvalidScenarioState(msg)
            except TypeError as e:
                msg = f"Invalid settings for {g_label}|{t_label}. "\
                    "Unable to create using the factory. See log for "\
                    "more details."
                logging.error(msg)
                logging.error(e)
                raise TypeError(msg) from e

            return new_component

        elif factory_flag:
            if LOG_FACTORY_CREATE:
                g_label = component_def["group_label"]
                t_label = component_def["type_label"]
                msg = f"creating {g_label}:{t_label} with Factory, no Journal"
                logging.info(msg)
            try:
                if inspect.isclass(component_create):
                    new_component = component_create(
                        factory=self,
                        **component_def["arguments"])
                else:
                    msg = f"invalid type in factory for {g_label}|{t_label}"
                    logging.error(msg)
                    raise InvalidScenarioState(msg)

            except TypeError as e:
                msg = f"Invalid settings for {g_label}|{t_label}. "\
                    "Unable to create using the factory. See log for "\
                    "more details."
                logging.error(msg)
                logging.error(e)
                raise TypeError(msg) from e

            return new_component

        elif j_flag:
            if LOG_FACTORY_CREATE:
                g_label = component_def["group_label"]
                t_label = component_def["type_label"]
                msg = f"creating {g_label}:{t_label} with Journal, no Factory"
                logging.info(msg)

            try:
                if inspect.isclass(component_create):
                    new_component = component_create(
                        journal=self._journal,
                        **component_def["arguments"])
                else:
                    msg = f"invalid type in factory for {g_label}|{t_label}"
                    logging.error(msg)
                    raise InvalidScenarioState(msg)

            except TypeError as e:
                msg = f"Invalid settings for {g_label}|{t_label}. "\
                    "Unable to create using the factory. See log for "\
                    "more details."
                logging.error(msg)
                logging.error(e)
                raise TypeError(msg) from e

            return new_component

        else:
            if LOG_FACTORY_CREATE:
                g_label = component_def["group_label"]
                t_label = component_def["type_label"]
                msg = f"creating {g_label}:{t_label} w/out Factory or journal"
                logging.info(msg)

            try:
                if inspect.isclass(component_create):
                    new_component = component_create(
                        **component_def["arguments"])
                else:
                    msg = f"invalid type in factory for {g_label}|{t_label}"
                    logging.error(msg)
                    raise InvalidScenarioState(msg)
            except TypeError as e:
                msg = f"Invalid settings for {g_label}|{t_label}. "\
                    "Unable to create using the factory. See log for "\
                    "more details."
                logging.error(msg)
                logging.error(e)
                raise TypeError(msg) from e

            return new_component

    def registry_listing(
        self,
        group_label: Union[str, None] = None
    ) -> List[str]:
        """Lists factory entries. if no group listed it returns groups,
        else if a group is entered it returns all types in that group.

        :param group_label: A group label, defaults to None
        :type group_label: Union[str, None], optional
        :return: A listing of types in a group or all groups
        :rtype: List[str]
        """        
        if group_label is None:
            return list(self._registry.keys())
        else:
            try:           
                group = self._registry[group_label]                
                return list(group.keys())
            except KeyError as e:
                msg = f"Invalid group_label: {group_label} not found."
                raise KeyError(msg) from e
