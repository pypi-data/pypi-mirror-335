"""
Cotlette's support for templates.

The cotlette.template namespace contains two independent subsystems:

1. Multiple Template Engines: support for pluggable template backends,
   built-in backends and backend-independent APIs
2. Cotlette Template Language: Cotlette's own template engine, including its
   built-in loaders, context processors, tags and filters.

Ideally these subsystems would be implemented in distinct packages. However
keeping them together made the implementation of Multiple Template Engines
less disruptive .

Here's a breakdown of which modules belong to which subsystem.

Multiple Template Engines:

- cotlette.template.backends.*
- cotlette.template.loader
- cotlette.template.response

Cotlette Template Language:

- cotlette.template.base
- cotlette.template.context
- cotlette.template.context_processors
- cotlette.template.loaders.*
- cotlette.template.debug
- cotlette.template.defaultfilters
- cotlette.template.defaulttags
- cotlette.template.engine
- cotlette.template.loader_tags
- cotlette.template.smartif

Shared:

- cotlette.template.utils

"""

# Multiple Template Engines

from .engine import Engine
from .utils import EngineHandler

engines = EngineHandler()

__all__ = ("Engine", "engines")


# Cotlette Template Language

# Public exceptions
from .base import VariableDoesNotExist  # NOQA isort:skip
from .context import Context, ContextPopException, RequestContext  # NOQA isort:skip
from .exceptions import TemplateDoesNotExist, TemplateSyntaxError  # NOQA isort:skip

# Template parts
from .base import (  # NOQA isort:skip
    Node,
    NodeList,
    Origin,
    Template,
    Variable,
)

# Library management
from .library import Library  # NOQA isort:skip

# Import the .autoreload module to trigger the registrations of signals.
# from . import autoreload  # NOQA isort:skip


__all__ += ("Template", "Context", "RequestContext")
