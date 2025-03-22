"""Impairment Engine is responsible for impairing the data. It follows
a similar pattern as the measurement engine."""

from typing import Protocol, Union, Literal, runtime_checkable
from adgtk.common import DuplicateFactoryRegistration, InvalidConfigException
from adgtk.components import PresentableRecord, PresentableGroup, State
# ----------------------------------------------------------------------
#
# ----------------------------------------------------------------------
# py -m pytest -s test/impairment/test_engine.py


@runtime_checkable
class Impairment(Protocol):
    """Impairment is a protocol for impairing data"""

    impairs: set[
        Literal["PresentableGroup", "PresentableRecord", "dict", "str", "State"]
    ]
    label: str
    skipped_counter: int
    executed_counter: int

    def impair(
        self,
        data: Union[PresentableGroup, PresentableRecord, dict, str, State],
        key: Union[str, None] = None,
        idx: Union[int, None] = None
    ) -> dict:
        """Impair the data

        :param data: The data to impair
        :type data: Union[PresentableGroup, PresentableRecord, dict, str, State]
        :param key: If a specific key is requested to impair, defaults to None
        :type key: Union[str, None], optional
        :param idx: If a group then the record to impair, defaults to None
        :type idx: Union[int, None], optional
        :return: the data impaired
        :rtype: dict
        """


class ImpairmentEngine:
    """Impairment Engine is responsible for impairing the data. It follows
    a similar pattern as the measurement engine."""

    def __init__(self):
        """Initializes a new instance of the Impairment Engine."""
        self._impairments: dict[str, Impairment] = {}

    def add_impairment(self, impairment: Impairment) -> None:
        """Adds an impairment to the engine.

        :param impairment: The impairment to add
        :type impairment: Impairment
        """
        if not isinstance(impairment, Impairment):
            msg = "Impairment must be an instance of Impairment"
            raise ValueError(msg)

        if impairment.label not in self._impairments:
            self._impairments[impairment.label] = impairment
        else:
            msg = f"Impairment {impairment.label} exists"
            raise DuplicateFactoryRegistration(msg)

    def __len__(self) -> int:
        """Returns the number of impairments in the engine

        :return: The number of impairments
        :rtype: int
        """
        return len(self._impairments)

    def _can_impair(
        self,
        impairs: set[
            Literal[
                "State",
                "PresentableGroup",
                "PresentableRecord",
                "dict",
                "str"]],
        data: Union[PresentableGroup, PresentableRecord, dict, str, State]
    ) -> bool:
        """Internal function to check if the data can be impaired

        :param impairs: The types of data that can be impaired
        :type impairs: list[Literal["PresentableGroup", "PresentableRecord", "dict", "str", "State"]]
        :param data: The data to check
        :type data: Union[PresentableGroup, PresentableRecord, dict, str, State]
        :return: True if the data can be impaired
        :rtype: bool
        """
        for imp in impairs:
            if self._check_type(imp, data):
                return True
        return False

    def _check_type(
        self,
        impairs:
            Literal[
                "State",
                "PresentableGroup",
                "PresentableRecord",
                "dict",
                "str"],
        data: Union[PresentableGroup, PresentableRecord, dict, str, State]
    ) -> bool:
        """Checks against a specific type. Used by _can_impair

        :param impairs: The type of data that can be impaired
        :type impairs: Literal[ "PresentableGroup", "PresentableRecord", "dict", "str", "State"]
        :param data: The data to check
        :type data: Union[PresentableGroup, PresentableRecord, dict, str, State]
        :return: True if the data can be impaired
        :rtype: bool
        """
        match impairs:
            case "PresentableGroup":
                return isinstance(data, PresentableGroup)
            case "PresentableRecord":
                return isinstance(data, PresentableRecord)
            case "dict":
                return isinstance(data, dict)
            case "str":
                return isinstance(data, str)
            case _:
                return False

    def impair(
        self,
        impairment_label: str,
        data: Union[PresentableGroup, PresentableRecord, dict, str, State],
        key: Union[str, None] = None,
        idx: Union[int, None] = None
    ) -> dict:
        """Impair the data. Assumes working off a copy.

        :param impairment_label: The label of the impairment to use
        :type impairment_label: str
        :param data: The data to impair
        :type data: Union[PresentableGroup, PresentableRecord, dict, str]
        :param key: If a specific key is requested to impair, defaults to None
        :type key: Union[str, None], optional
        :param idx: If a group then the record to impair, defaults to None
        :type idx: Union[int, None], optional
        :return: a copy of the data impaired
        :rtype: dict
        """
        if impairment_label in self._impairments:
            impair_type = self._impairments[impairment_label].impairs
            if self._can_impair(impair_type, data):
                return self._impairments[impairment_label].impair(
                    data=data, key=key, idx=idx)
            msg = f"Impairment {impairment_label} cannot impair {type(data)}"
            raise InvalidConfigException(msg)
        else:
            msg = f"Impairment {impairment_label} does not exist"
            raise ValueError(msg)

    def get_impairment_labels(
        self,
        impairs: Literal[
            "PresentableGroup",
            "PresentableRecord",
            "dict",
            "str",
            "all"]
    ) -> list[str]:
        """Returns the labels of the registered impairments. Usage
        includes for generating reports and needing to iterate the
        impairment engine.
        :param impairs: The type of impairments to return
        :type impairs: Literal["PresentableGroup", "PresentableRecord", "dict", "str", "all"]

        :return: A list of the impairment labels
        :rtype: list
        """
        if impairs == "all":
            return list(self._impairments.keys())
        else:
            return_list = []
            for label, imp in self._impairments.items():
                if impairs in imp.impairs:
                    return_list.append(label)
            return return_list

        return []

    def get_impairment(self, label: str) -> Impairment:
        """Returns the impairment associated with the label

        :param label: The label of the impairment
        :type label: str
        :return: The impairment
        :rtype: Impairment
        """
        if label in self._impairments:
            return self._impairments[label]
        else:
            msg = "Impairment %s does not exist", label
            raise ValueError(msg)

    def get_skip_count(self, label: str) -> int:
        """Gets the number of times the impairment was skipped

        :param label: the label of the impairment
        :type label: str
        :return: the counter value
        :rtype: int
        """
        if label in self._impairments:
            return self._impairments[label].skipped_counter

        raise KeyError(f"Impairment {label} does not exist")

    def get_execution_count(self, label: str) -> int:
        """Gets the number of times the impairment was executed

        :param label: the label of the impairment
        :type label: str
        :return: the counter value
        :rtype: int
        """
        if label in self._impairments:
            return self._impairments[label].executed_counter

        raise KeyError(f"Impairment {label} does not exist")

    def reset_counters(self, label: Union[str, None] = None) -> None:
        """Resets the counters for the impairments

        :param label: filter the impairment counter to reset, defaults to None
        :type label: Union[str, None], optional
        """

        if label is not None:
            if label in self._impairments:
                self._impairments[label].skipped_counter = 0
                self._impairments[label].executed_counter = 0
        else:
            for key in self._impairments.keys():
                self._impairments[key].skipped_counter = 0
                self._impairments[key].executed_counter = 0
