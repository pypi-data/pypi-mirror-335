# Copyright (c) 2021-2024 Datalayer, Inc.
#
# Datalayer License

"""The Datalayer UI Server application."""

import os

from jupyter_server.extension.application import ExtensionApp, ExtensionAppJinjaMixin

from datalayer_ui.handlers.index.handler import IndexHandler

from datalayer_ui._version import __version__


DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "./static")

DEFAULT_TEMPLATE_FILES_PATH = os.path.join(os.path.dirname(__file__), "./templates")


class DatalayerUIExtensionApp(ExtensionAppJinjaMixin, ExtensionApp):
    """The Datalayer UI Server extension."""

    name = "datalayer_ui"

    extension_url = "/datalayer_ui"

    load_other_extensions = True

    static_paths = [DEFAULT_STATIC_FILES_PATH]
    template_paths = [DEFAULT_TEMPLATE_FILES_PATH]

    def initialize_handlers(self):
        handlers = [
            ("/", IndexHandler),
            (self.name, IndexHandler),
        ]
        self.handlers.extend(handlers)


# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------

main = launch_new_instance = DatalayerUIExtensionApp.launch_instance
