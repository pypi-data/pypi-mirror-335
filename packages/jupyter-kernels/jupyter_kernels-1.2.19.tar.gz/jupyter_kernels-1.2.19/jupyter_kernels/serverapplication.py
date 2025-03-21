# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

"""The Jupyter Kernels Server application."""

import os

from traitlets import CInt

from jupyter_server.utils import url_path_join
from jupyter_server.extension.application import ExtensionApp, ExtensionAppJinjaMixin

from jupyter_kernels.handlers.index.handler import IndexHandler
from jupyter_kernels.handlers.config.handler import ConfigHandler
from jupyter_kernels.handlers.jump.handler import JumpHandler
from jupyter_kernels.handlers.content.handler import ContentHandler
# from .handlers.jump.keys import setup_keys


from jupyter_kernels.__version__ import __version__


DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "./static")

DEFAULT_TEMPLATE_FILES_PATH = os.path.join(
    os.path.dirname(__file__), "./templates")


class JupyterKernelsExtensionApp(ExtensionAppJinjaMixin, ExtensionApp):
    """The Jupyter Kernels Server extension."""

    name = "jupyter_kernels"

    extension_url = "/jupyter_kernels"

    load_other_extensions = True

    static_paths = [DEFAULT_STATIC_FILES_PATH]
    template_paths = [DEFAULT_TEMPLATE_FILES_PATH]

    max_notebook_kernels = CInt(
        5,
        config=True,
        help="Maximal number of Notebook Remote Kernels that can be spawned by an user."
    )

    max_cell_kernels = CInt(
        3,
        config=True,
        help="Maximal number of Cell Remote Kernels that can be spawned by an user. They are not taking into account in the max_notebook_kernels limit."
    )

    def initialize_settings(self):
        settings = dict(
            max_notebook_kernels=self.max_notebook_kernels,
            max_cell_kernels=self.max_cell_kernels
        )
        self.settings.update(**settings)

    def initialize_templates(self):
        self.serverapp.jinja_template_vars.update(
            {
                "jupyter_kernels_version": __version__,
            })

    def initialize_handlers(self):
        pod_name_regex = r"(?P<pod_name>[\w\.\-%]+)"
        handlers = [
            ("jupyter_kernels", IndexHandler),
            (url_path_join("jupyter_kernels", "config"), ConfigHandler),
            (url_path_join("jupyter_kernels", "content"), ContentHandler),
            (r"/jupyter_kernels/jump/%s" % pod_name_regex, JumpHandler),
        ]
        self.handlers.extend(handlers)


# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------

main = launch_new_instance = JupyterKernelsExtensionApp.launch_instance
