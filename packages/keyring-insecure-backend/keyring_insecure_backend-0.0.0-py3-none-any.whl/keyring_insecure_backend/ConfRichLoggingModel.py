#!/usr/bin/env python
# encoding: utf-8

"""
ConfRichLoggingModel.py

Rich logging configuration data model.

author  : stefan schablowski
contact : stefan.schablowski@desmodyne.com
created : 2025-03-18
"""


# NOTE: this data model is based on the python logging configuration data model
# and extends it to support configuring logging to file using a rich Console;
# it follows the same concept: similar to formatters, filters, handlers and
# loggers that may reference other logging objects in the python logging conf,
# there is a dict of rich console confs and a dict of rich handler confs that
# may reference entries in said console conf dicts using a textual ID


from pathlib import Path
from typing  import Dict, Optional

# https://pypi.org/project/pydantic
from pydantic import BaseModel, ConfigDict

from .ConfLoggingModel import ConfLoggingHandlerModel, ConfLoggingModel


# -----------------------------------------------------------------------------
# supporting types

class ConfRichConsoleModel(BaseModel):
    """
    Pydantic helper model that defines a subset of rich console conf attrbutes.
    """

    # https://rich.readthedocs.io/en/stable/reference/console.html

    model_config = ConfigDict(extra='forbid')
    # NOTE: rich docs ref'd above say `IO`, but that causes a pyright issue
    #   Expected type arguments for generic class "IO"
    # --> use str type arg, although that assumes all log files contain strings
    # NOTE: using IO[str] or TextIO as in e.g.
    #   file: Optional[IO[str]] = None
    # fails with pydantic.errors.PydanticSchemaGenerationError:
    #   Unable to generate pydantic-core schema for typing.IO[str].
    #   Set `arbitrary_types_allowed=True` in the model_config to
    #   ignore this error or implement `__get_pydantic_core_schema__`
    #   on your type to fully support it.
    #   If you got this error by calling handler(<some type>) within
    #   `__get_pydantic_core_schema__` then you likely need to call
    #   `handler.generate_schema(<some type>)` since we do not call
    #   `__get_pydantic_core_schema__` on `<some type>` otherwise
    #   to avoid infinite recursion.
    #   For further information visit
    #   https://errors.pydantic.dev/2.10/u/schema-for-unknown-type
    # workaround: use file _path_ here, use file object at runtime
    path_to_file:  Optional[Path]  = None


class ConfRichHandlerModel(ConfLoggingHandlerModel):
    """
    Pydantic helper model that defines a subset of rich handler conf attrbutes.
    """

    # https://rich.readthedocs.io/en/stable/reference/logging.html

    # NOTE: need to allow extra attributes as in base class
    model_config = ConfigDict(extra='allow')
    console:       Optional[str]   = None


# -----------------------------------------------------------------------------
# public types

class ConfRichLoggingModel(ConfLoggingModel):
    """
    Pydantic model that defines rich logging configuration attributes.
    """

    model_config = ConfigDict(extra='forbid')
    consoles:      Optional[Dict[str, ConfRichConsoleModel]]   = {}
    # TODO: review supressed pyright issue:
    # "handlers" overrides symbol of same name in class "ConfLoggingModel"
    #   Variable is mutable so its type is invariant
    #     Override type "Dict[str, ConfRichHandlerModel] | None" is not the same
    #      as base type "Dict[str, ConfLoggingHandlerModel] | None"
    handlers:      Optional[Dict[str, ConfRichHandlerModel]]   = {}    # pyright: ignore[reportIncompatibleVariableOverride]
