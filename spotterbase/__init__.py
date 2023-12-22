from importlib.metadata import version

__version__ = version('spotterbase')


from spotterbase.utils.plugin_loader import load_plugins

load_plugins()
