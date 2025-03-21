# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

import sys
import warnings
from pathlib import Path

from traitlets import Bool, Unicode

from jupyter_kernels.__version__ import __version__

from datalayer_core.application import (
    DatalayerApp, NoStart, base_aliases, base_flags
)


HERE = Path(__file__).parent


jupyter_iam_aliases = dict(base_aliases)
jupyter_iam_aliases["cloud"] = "JupyterKernelsApp.cloud"

jupyter_iam_flags = dict(base_flags)
jupyter_iam_flags["dev-build"] = (
    {"JupyterKernelsApp": {"dev_build": True}},
    "Build in development mode.",
)
jupyter_iam_flags["no-minimize"] = (
    {"JupyterKernelsApp": {"minimize": False}},
    "Do not minimize a production build.",
)


class ConfigExportApp(DatalayerApp):
    """An application to export the configuration."""

    version = __version__
    description = """
   An application to export the configuration
    """

    def initialize(self, *args, **kwargs):
        """Initialize the app."""
        super().initialize(*args, **kwargs)

    def start(self):
        """Start the app."""
        if len(self.extra_args) > 1:  # pragma: no cover
            warnings.warn("Too many arguments were provided for workspace export.")
            self.exit(1)
        self.log.info("JupyterKernelsConfigApp %s", self.version)


class JupyterKernelsConfigApp(DatalayerApp):
    """A config app."""

    version = __version__
    description = """
    Manage the configuration
    """

    subcommands = {}
    subcommands["export"] = (
        ConfigExportApp,
        ConfigExportApp.description.splitlines()[0],
    )

    def start(self):
        try:
            super().start()
            self.log.error("One of `export` must be specified.")
            self.exit(1)
        except NoStart:
            pass
        self.exit(0)


class JupyterKernelsShellApp(DatalayerApp):
    """A shell app."""

    version = __version__
    description = """
    Run predefined scripts.
    """

    def start(self):
        super().start()
        args = sys.argv
        self.log.info(args)


class JupyterKernelsApp(DatalayerApp):
    name = "jupyter_iam"
    description = """
    Import or export a JupyterLab workspace or list all the JupyterLab workspaces

    You can use the "config" sub-commands.
    """
    version = __version__

    aliases = jupyter_iam_aliases
    flags = jupyter_iam_flags

    minimize = Bool(True, config=True, help="")

    subcommands = {
        "config": (JupyterKernelsConfigApp, JupyterKernelsConfigApp.description.splitlines()[0]),
        "sh": (JupyterKernelsShellApp, JupyterKernelsShellApp.description.splitlines()[0]),
    }

    def initialize(self, argv=None):
        """Subclass because the ExtensionApp.initialize() method does not take arguments"""
        super().initialize()

    def start(self):
        super(JupyterKernelsApp, self).start()
        self.log.info("Jupyter Kernels - Version %s", self.version)


# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------

main = launch_new_instance = JupyterKernelsApp.launch_instance

if __name__ == "__main__":
    main()
