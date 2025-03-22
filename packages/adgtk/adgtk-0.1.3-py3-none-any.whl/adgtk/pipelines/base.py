"""Pipeline provides a consistent set of tools for processing of data."""

import logging
from typing import Union, Protocol, runtime_checkable, Literal, Any
from dataclasses import dataclass
from adgtk.components import PresentableRecord, PresentableGroup


@dataclass
class PipelineConfig:
    """Configuration for the pipeline."""
    version: str
    debug: bool
    log_failures: bool


@dataclass
class PipelineRequest:
    """A request for the pipeline to work"""
    version: str
    data: Any


@runtime_checkable
class Pipeline(Protocol):
    """Provides a consistent set of tools for processing of data."""

    def __init__(self, config: PipelineConfig):
        """Initializes a pipeline.

        :param config: The pipeline configuration
        :type config: PipelineConfig
        """

    def process(self, request: PipelineRequest) -> Any:
        """Processes a pipeline request

        :param request: The request to process
        :type request: PipelineRequest
        :return: The processed data
        :rtype: Any
        """
