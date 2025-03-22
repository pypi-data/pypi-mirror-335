"""The Presentation module is focused on defining Protocols for 
presenting data. These protocol(s) are intented to be used by the
components responsible for presenting data in a specific format.
"""


from typing import Protocol, runtime_checkable

# ----------------------------------------------------------------------
#
# ----------------------------------------------------------------------
# py -m pytest -s test/data/test_presentation.py


@runtime_checkable
class PresentationFormat(Protocol):
    """Provides a base for a presentation """

    def present(self, data: dict) -> str:
        """Presents data based on its configuration

        :param data: the data to be presented
        :type data: dict
        :return: a string in the format configured
        :rtype: str
        """
