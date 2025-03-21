# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

"""Config handler."""

import json

import tornado

from jupyter_server.base.handlers import APIHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin

from jupyter_iam.__version__ import __version__


# pylint: disable=W0223
class ConfigHandler(ExtensionHandlerMixin, APIHandler):
    """The handler for configurations."""

    @tornado.web.authenticated
    def get(self):
        """Returns the configurations of the server extensions."""
        res = json.dumps({
            "extension": "jupyter_iam",
            "version": __version__
        })
        self.finish(res)
