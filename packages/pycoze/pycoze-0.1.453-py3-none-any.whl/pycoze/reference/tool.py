import os
import importlib
from .lib import ModuleManager, wrapped_func
from pycoze import utils


params = utils.params


def ref_tools(tool_id, workspace_path=None):
    if workspace_path is None:
        workspace_path = params["workspacePath"]
    tool_base_path = os.path.join(workspace_path, "User/Local/Tool")
    module_path = os.path.join(tool_base_path, tool_id)
    module_path = os.path.normpath(os.path.abspath(module_path))

    if not os.path.exists(module_path):
        print(f"Tool {tool_id} not found")
        return []

    try:
        with ModuleManager(module_path) as manager:
            module = importlib.import_module("tool")
            export_tools = getattr(module, "__all__")

    except Exception as e:
        print(f"Error loading tool {tool_id}: {e}")
        return []

    ret_export_tools = []
    for tool in export_tools:
        tool = wrapped_func(tool, module_path)
        if tool.__doc__ is None:
            tool.__doc__ = "This tool is used to " + tool.__name__.replace("_", " ") + "."
        ret_export_tools.append(tool)

    return ret_export_tools


