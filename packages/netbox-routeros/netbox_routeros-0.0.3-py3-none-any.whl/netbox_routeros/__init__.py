from typing import Any, Dict, List

from netbox.plugins import PluginConfig

from . import __version__ as plugin_meta

version = plugin_meta.__version__


# TODO: try importlib.metadata
class RouterOSConfig(PluginConfig):
    name = plugin_meta.__plugin_name__
    verbose_name = plugin_meta.__title__
    description = plugin_meta.__description__
    version = plugin_meta.__version__
    author = plugin_meta.__author__
    author_email = plugin_meta.__author_email__
    base_url = "netbox-routeros"
    required_settings: List[str] = []
    min_version = "4.2.0"
    max_version = "4.2.99"
    default_settings: Dict[str, Any] = {}


config = RouterOSConfig
