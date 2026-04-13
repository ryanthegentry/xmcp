"""
Patches for FastMCP OpenAPI utilities.

Import this module before FastMCP creates tools to apply all patches.
Currently patches:
  - _unflatten_arguments: coerces string-encoded JSON objects in body params
    to native dicts, fixing LLM double-serialization of nested params like `reply`.
"""

from patches.director_patch import apply  # noqa: F401

apply()
