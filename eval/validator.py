# eval/validator.py
import types
import traceback

def validate_cadquery_code(py_src: str):
    """
    Executes a model's Python output and verifies:
      - it imports cadquery as cq
      - defines a variable `result`
      - `result` is a cadquery.Workplane (solid)
    Returns: (ok: bool, info: dict)
    """
    info = {"error": None, "has_import": False, "has_result": False, "is_workplane": False}

    # Quick checks
    info["has_import"] = ("import cadquery as cq" in py_src)

    # Minimal sandbox — WARNING: exec is dangerous; keep this local.
    # We explicitly restrict builtins.
    safe_globals = {"__builtins__": {}}
    safe_locals = {}

    # Allow only what we need after import inside the code
    try:
        exec(py_src, safe_globals, safe_locals)
    except Exception as e:
        info["error"] = "exec_failure:\n" + "".join(traceback.format_exc())
        return False, info

    # Was result produced?
    info["has_result"] = ("result" in safe_locals)

    if not info["has_result"]:
        info["error"] = "missing_result_variable"
        return False, info

    result = safe_locals["result"]

    # Try to import cadquery here and check type
    try:
        import cadquery as cq
        from cadquery import Workplane
    except Exception:
        info["error"] = "cadquery_not_installed"
        return False, info

    # Workplane check
    info["is_workplane"] = isinstance(result, Workplane)

    if not info["is_workplane"]:
        info["error"] = f"result_not_workplane_got_{type(result)}"
        return False, info

    # Optional: additional geometry sanity checks could go here

    return True, info
