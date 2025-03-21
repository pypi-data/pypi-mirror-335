# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

"""Run handler."""

import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin

from ...__version__ import __version__


# pylint: disable=W0223
class ContentHandler(ExtensionHandlerMixin, APIHandler):
    """The content handler."""

    @tornado.web.authenticated
    def get(self):
        """Returns the content."""
        pass
