from .markerpath import marker_main
from .markerpath_global import markerpath_global_initialize, inject_logger_member, markerpath_global,change_logging_level
# Run marker_main on package import.
marker_main()

__all__ = [
    "markerpath_global_initialize",
    "inject_logger_member",
    "markerpath_global",
    "change_logging_level"
]
