#!/usr/bin/env python
# encoding: utf-8

"""
ConfLoggingModel.py

Python logging configuration data model.

author  : stefan schablowski
contact : stefan.schablowski@desmodyne.com
created : 2025-03-18
"""


# python > logging > configuration:
#   https://docs.python.org/3/library/logging.config.html
# python > logging > configuration > data model:
#   https://docs.python.org/3/library/logging.config.html#dictionary-schema-details


# TODO: add validators to ensure logging objects reference valid other objects
# TODO: support user-defined objects ?
#   https://docs.python.org/3/library/logging.config.html#user-defined-objects


from typing import Any, Dict, List, Literal, Optional

# https://pypi.org/project/pydantic
from pydantic import BaseModel, ConfigDict, Field


# -----------------------------------------------------------------------------
# supporting types

class ConfLoggingFilterModel(BaseModel):
    """
    Pydantic helper model that defines logging filter conf attrbutes.
    """

    # https://docs.python.org/3/library/logging.html#logging.Filter

    model_config = ConfigDict(extra='forbid')
    name:          Optional[str]   = None


class ConfLoggingFormatterModel(BaseModel):
    """
    Pydantic helper model that defines logging formatter conf attrbutes.
    """

    # https://docs.python.org/3/library/logging.html#logging.Formatter

    model_config = ConfigDict(extra='forbid')
    # NOTE: 'class' obviously is a python keyword; use alias to work around:
    #   https://stackoverflow.com/a/70584815
    #   https://docs.pydantic.dev/latest/concepts/fields/#field-aliases
    # TODO: restrict to dot notation / valid class names ?
    class_:        Optional[str]  = Field(alias = 'class', default = None)
    # TODO: verify this is a valid date format ?
    datefmt:       Optional[str]               = None
    defaults:      Optional[Dict[str, Any]]    = None
    # TODO: verify this is a valid log message format ?
    format:        Optional[str]               = None
    # TODO: restrict to '%', '{' or '$'
    style:         Optional[str]               = None
    # NOTE: 'validate' is a BaseModel method; see class_ above
    validate_:     Optional[bool] = Field(alias = 'validate', default = None)


class ConfLoggingHandlerModel(BaseModel):
    """
    Pydantic helper model that defines logging handler conf attrbutes.
    """

    # https://docs.python.org/3/library/logging.html#logging.Handler
    # however, most useful info is in the handlers section at
    #   https://docs.python.org/3/library/logging.config.html ...
    #    ... #dictionary-schema-details

    # from above page:
    # > All other keys are passed through as keyword
    # > arguments to the handler’s constructor.
    # --> do not forbid extra attributes as usual
    model_config = ConfigDict(extra='allow')
    class_:        Optional[str]  = Field(alias = 'class', default = None)
    filters:       Optional[List[str]] = None
    formatter:     Optional[str]       = None
    # TODO: restrict to python log levels (?) in upper case (?)
    level:         Optional[str]       = None


class ConfLoggingLoggerModel(BaseModel):
    """
    Pydantic helper model that defines logging logger conf attrbutes.
    """

    # https://docs.python.org/3/library/logging.html#logging.Logger
    # however, most useful info is in the loggers section at
    #   https://docs.python.org/3/library/logging.config.html ...
    #    ... #dictionary-schema-details and at
    #   https://docs.python.org/3/library/logging.config.html ...
    #    ... #object-connections

    model_config = ConfigDict(extra='forbid')
    filters:       Optional[List[str]] = None
    handlers:      Optional[List[str]] = None
    level:         Optional[str]       = None
    propagate:     Optional[bool]      = None


# -----------------------------------------------------------------------------
# public types

class ConfLoggingModel(BaseModel):
    """
    Pydantic model that defines python logging configuration attributes.
    """

    # TODO: python's interpretation of 'optional' seems inconsistent:
    # + python logging configuration docs say attributes are optional:
    #     https://docs.python.org/3/library/logging.config.html ...
    #      ... #dictionary-schema-details > 'All other keys are optional'
    # + from python typing docs at
    #     https://docs.python.org/3/library/typing.html#typing.Optional:
    #   > Optional[X] is equivalent to X | None (or Union[X, None]).
    # however, using `Optional[...] = None` below as in e.g.
    #   formatters:    Optional[Dict[str, ConfLoggingFormatterModel]]  = None
    # fails because python code seems to expect empty dictionaries:
    #     File ".../lib/python3.13/logging/config.py", line 581, in configure
    #       for name in formatters:
    #                   ^^^^^^^^^^
    #   TypeError: 'NoneType' object is not iterable
    # workaround: use {} as default value instead of None

    model_config = ConfigDict(extra='forbid')
    # NOTE: attribute order not alphabetical, but follows documentation at
    #   https://docs.python.org/3/library/logging.config.html ...
    #    ... #dictionary-schema-details
    version:       Literal[1]
    formatters:    Optional[Dict[str, ConfLoggingFormatterModel]]  = {}
    filters:       Optional[Dict[str, ConfLoggingFilterModel]]     = {}
    handlers:      Optional[Dict[str, ConfLoggingHandlerModel]]    = {}
    loggers:       Optional[Dict[str, ConfLoggingLoggerModel]]     = {}
    # TODO: from https://docs.python.org/3/library/logging.config.html:
    #   > configuration will be as for any logger,
    #   > except that the propagate setting will not be applicable
    root:          Optional[ConfLoggingLoggerModel]                = None
    incremental:   Optional[bool]                                  = None
    disable_existing_loggers:  Optional[bool]                      = None
