import sys

from .plugin import plugin_path, dependencies_path, NC, BVC


__all__ = [
    "NC",
    "BVC",
]

_loaded = False

def load():
    global _loaded
    if not _loaded:
        _loaded = True

        from livekit import rtc

        module = sys.modules[__name__]
        module_id = str(id(module))

        plugin = rtc.AudioFilter(module_id, plugin_path(), dependencies_path())

load()
