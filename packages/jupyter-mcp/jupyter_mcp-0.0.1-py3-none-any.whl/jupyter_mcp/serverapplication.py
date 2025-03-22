# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

"""The Jupyter MCP Server application."""

import os

from traitlets import Unicode

from jupyter_server.utils import url_path_join
from jupyter_server.extension.application import ExtensionApp, ExtensionAppJinjaMixin

from jupyter_mcp.__version__ import __version__

from jupyter_mcp.handlers.index.handler import IndexHandler
from jupyter_mcp.handlers.config.handler import ConfigHandler
from jupyter_mcp.handlers.oauth.handler import OAuth2Callback


DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "./static")

DEFAULT_TEMPLATE_FILES_PATH = os.path.join(os.path.dirname(__file__), "./templates")


class JupyterIamExtensionApp(ExtensionAppJinjaMixin, ExtensionApp):
    """The Jupyter MCP Server extension."""

    name = "jupyter_mcp"

    extension_url = "/jupyter_mcp"

    load_other_extensions = True

    static_paths = [DEFAULT_STATIC_FILES_PATH]
    template_paths = [DEFAULT_TEMPLATE_FILES_PATH]

    config_a = Unicode("", config=True, help="Config A example.")
    config_b = Unicode("", config=True, help="Config B example.")
    config_c = Unicode("", config=True, help="Config C example.")

    def initialize_settings(self):
        self.log.debug("Jupyter MCP Config {}".format(self.config))

    def initialize_templates(self):
        self.serverapp.jinja_template_vars.update({"jupyter_mcp_version" : __version__})

    def initialize_handlers(self):
        self.log.debug("Jupyter MCP Config {}".format(self.settings['jupyter_mcp_jinja2_env']))
        handlers = [
            ("jupyter_mcp", IndexHandler),
            (url_path_join("jupyter_mcp", "config"), ConfigHandler),
            (url_path_join("jupyter_mcp", "oauth2", "callback"), OAuth2Callback),
        ]
        self.handlers.extend(handlers)


# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------

main = launch_new_instance = JupyterIamExtensionApp.launch_instance
