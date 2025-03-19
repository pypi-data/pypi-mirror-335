from ._version import __version__
from .handlers import setup_handlers
import os
import sys


def _jupyter_server_extension_paths():
    return [{"module": "escrowai_jupyter"}]


def jupyter_serverproxy_servers():
    """
    Return a dict of server configurations for jupyter-server-proxy.
    This is used by jupyter-server-proxy to start the service.
    """
    return {
        "escrowai-jupyter": {
            "command": [sys.executable, "-m", "escrowai_jupyter.main"],
            "environment": {},
            "launcher_entry": {
                "title": "EscrowAI Jupyter",
                "icon_path": os.path.join(
                    os.path.dirname(__file__), "icons", "escrowai.svg"
                ),
            },
        }
    }


def load_jupyter_server_extension(nbapp):
    setup_handlers(nbapp.web_app)
    nbapp.log.info("EscrowAI Jupyter loaded.")
