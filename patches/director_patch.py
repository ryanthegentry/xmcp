"""
Monkey-patch for FastMCP's RequestDirector._unflatten_arguments.

Problem: LLMs sometimes serialize nested tool parameters (like the `reply` object
in X API's createPosts) as JSON strings instead of native dicts. FastMCP passes
these through to the HTTP request body, causing errors like:
  "$.reply: string found, object expected"

Fix: After assembling body_props from flat tool arguments, coerce any string values
that look like JSON objects into native dicts via json.loads().

This patch is applied at import time by patches/__init__.py and survives pip
reinstalls of FastMCP (unlike editing site-packages directly).
"""

import json
import functools

_applied = False


def apply():
    """Apply the body param coercion patch to RequestDirector._unflatten_arguments."""
    global _applied
    if _applied:
        return
    _applied = True

    from fastmcp.utilities.openapi.director import RequestDirector

    original = RequestDirector._unflatten_arguments

    @functools.wraps(original)
    def _patched_unflatten(self, route, flat_args):
        path_params, query_params, header_params, body = original(self, route, flat_args)

        # Coerce string-encoded JSON objects in body.
        # Only applies when body is a dict (the normal case for object-typed bodies).
        if isinstance(body, dict):
            for key, val in list(body.items()):
                if isinstance(val, str) and val.startswith("{"):
                    try:
                        body[key] = json.loads(val)
                    except (ValueError, json.JSONDecodeError):
                        pass

        return path_params, query_params, header_params, body

    RequestDirector._unflatten_arguments = _patched_unflatten

