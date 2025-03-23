# tools.py
# Copyright (c) 2025 zedmoster

import logging
from typing import List
from mcp.server.fastmcp import Context

logger = logging.getLogger("RevitTools")


def call_func(ctx: Context, method: str = "CallFunc", params: List[str] = None) -> List[int]:
    """
    Calls a specified function asynchronously based on the given method and parameters.

    This function handles the execution of various Revit API functions, such as "ClearDuplicates",
    based on the method provided. It sends a command to Revit, which is then executed
    asynchronously, and returns the list of element IDs affected by the function.

    Supported Functions:
    - "ClearDuplicates": Removes duplicate elements located at the same position, preventing
      double counting in schedules. This is useful when unintended duplicate instances
      of the same family are placed on top of each other.

    Parameters:
    - ctx (Context): The current FastMCP context for managing Revit operations.
    - method (str): The name of the function to call. Default is "CallFunc".
    - params (List[str]): A list of parameters required for the function. For "ClearDuplicates",
      no additional parameters are required.

    Returns:
    - List[int]: A list of element IDs affected by the function call. When using "ClearDuplicates",
      it returns the IDs of the elements that were removed.

    Exceptions:
    - Raises ValueError if `params` is not a list of strings.
    - Logs and returns an empty list in case of errors during function execution.
    """
    try:
        # 参数验证，确保params为一个包含字符串的列表
        if params is not None and (not isinstance(params, list) or not all(isinstance(param, str) for param in params)):
            raise ValueError("Invalid input: 'params' should be a list of strings or None.")

        # 获取Revit连接实例
        from .server import get_Revit_connection
        revit = get_Revit_connection()

        # 发送命令并等待结果
        result = revit.send_command(method, params or [])

        # 返回执行结果
        return result

    except Exception as e:
        # 记录异常信息并返回空列表
        logging.error(f"Error in call_func: {str(e)}", exc_info=True)
        return []


def find_elements(ctx: Context, method: str = "FindElements", params: List[dict[str, object]] = None) -> List[int]:
    """
    Finds elements in the Revit scene using categoryId or categoryName.

    Parameters:
    - ctx (Context): The current FastMCP context for managing Revit operations.
    - method (str): The Revit API method to call. Default is "FindElements".
    - params (List[dict[str, object]]): A list of dictionaries specifying search parameters.
      - categoryId (int, optional): The ID of the category to search.
      - categoryName (str, optional): The name of the category to search.
      - isInstance (bool, optional): Whether to search for instances or types.

    Returns:
    - List[int]: A list of matching element IDs.
    """
    try:
        if not isinstance(params, list) or not all(isinstance(param, dict) for param in params):
            raise ValueError("Invalid input: 'params' should be a list of dictionaries.")

        from .server import get_Revit_connection
        revit = get_Revit_connection()
        result = revit.send_command(method, params)
        return result

    except Exception as e:
        logger.error(f"Error finding elements. {str(e)}", exc_info=True)
        return []


def update_elements(ctx: Context, method: str = "UpdateElements", params: list[dict[str, str]] = None) -> str:
    """
    Updates the parameters of elements in the Revit model.

    Parameters:
    - ctx (Context): The FastMCP context.
    - method (str): The Revit API method to call. Default is "UpdateElements".
    - params (List[dict[str, str]]): List of dictionaries with update data:
      - elementId (int or str): The ID of the element to be updated.
      - parameterName (str): The parameter name to update.
      - parameterValue (str): The new parameter value.

    Returns:
    - str: Result message indicating success or failure.
    """
    try:
        from .server import get_Revit_connection
        revit = get_Revit_connection()
        result = revit.send_command(method, params)
        return f"Successfully updated element(s). Result: {result}"

    except Exception as e:
        logger.error(f"Error updating elements. {str(e)}", exc_info=True)
        return f"Error: {str(e)}"


def delete_elements(ctx: Context, method: str = "DeleteElements", params: List[dict[str, str]] = None) -> str:
    """
    Deletes elements from the Revit model using their IDs.

    Parameters:
    - ctx (Context): The FastMCP context.
    - method (str): The Revit API method to call. Default is "DeleteElements".
    - params (List[int]): List of element IDs to delete.

    Returns:
    - str: Result message indicating success or failure.
    """
    try:
        if not params or not all(isinstance(el_id, int) for el_id in params):
            raise ValueError("Invalid input: 'params' should be a list of element IDs (int).")

        from .server import get_Revit_connection
        revit = get_Revit_connection()
        result = revit.send_command(method, params)
        return f"Successfully deleted element(s). Result: {result}"

    except Exception as e:
        logger.error(f"Error deleting elements. {str(e)}", exc_info=True)
        return f"Error: {str(e)}"


def show_elements(ctx: Context, method: str = "ShowElements", params: List[dict[str, str]] = None) -> str:
    """
    Makes elements visible in the Revit view using their IDs.

    Parameters:
    - ctx (Context): The FastMCP context.
    - method (str): The Revit API method to call. Default is "ShowElements".
    - params (List[dict[str, str]]): List of dictionaries specifying element IDs:
      - elementId (int or str): The ID of the element to be shown.

    Returns:
    - str: Result message indicating success or failure.
    """
    try:
        if not params or not all(isinstance(param.get("elementId"), (int, str)) for param in params):
            raise ValueError("Invalid input: 'params' should be a list of dictionaries with 'elementId' (int or str).")

        from .server import get_Revit_connection
        revit = get_Revit_connection()
        result = revit.send_command(method, params)
        return f"Successfully shown element(s). Result: {result}"

    except Exception as e:
        logger.error(f"Error showing elements. {str(e)}", exc_info=True)
        return f"Error: {str(e)}"


def parameter_elements(ctx: Context, method: str = "ParameterElements", params: List[dict[str, str]] = None) -> str:
    """
    Retrieves parameter names and values for specified Revit elements.

    Parameters:
    - ctx (Context): The FastMCP context.
    - method (str): The Revit API method to call. Default is "ParameterElements".
    - params (List[dict[str, str]]): List of dictionaries specifying element IDs and optional parameter names.
      Example: [{"elementId": 123456}, {"elementId": 123456, "parameterName": "Comments"}]

    Returns:
    - str: Result message with parameter data or error.
    """
    try:
        if not params or not all(isinstance(param.get("elementId"), (int, str)) for param in params):
            raise ValueError("Invalid input: 'params' should be a list of dictionaries with 'elementId' (int or str).")

        from .server import get_Revit_connection
        revit = get_Revit_connection()
        result = revit.send_command(method, params)
        return f"Unexpected result format: {result}"

    except Exception as e:
        logger.error(f"Error retrieving element parameters: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"


def create_elements(ctx: Context, method: str, params: List[dict[str, object]] = None) -> str:
    """
    Create various types of elements in the Revit scene.

    Parameters:
    - ctx (Context): The FastMCP context.
    - method (str): The Revit API method for creating elements.
        Examples: "CreateWalls", "CreateFamilyInstances", "CreateFloors", "CreateGrids", "CreateLevels".
    - params (List[dict[str, object]]): A list of dictionaries specifying creation parameters.

    Supported Methods and Required Parameters:
    - CreateWalls: {startX, startY, endX, endY, height, width, elevation (optional)}
    - CreateFloors: {boundaryPoints: List[dict[str, float]], floorTypeName (optional): str, structural (optional): bool}
    - CreateFamilyInstances:  {categoryName, startX, startY, startZ, name,
        familyName (optional), endX (optional), endY (optional), endZ (optional),
        hostId (optional), viewName (optional), rotationAngle (optional), offset (optional)}
    - CreateGrids: {name, startX, startY, endX, endY, centerX (optional), centerY (optional)}
    - CreateLevels: {name, elevation}

    Returns:
    - str: Result message indicating success or failure.
    """
    try:
        # Validate parameters
        if not isinstance(params, list) or not all(isinstance(param, dict) for param in params):
            raise ValueError("Invalid input: 'params' should be a list of dictionaries.")

        valid_methods = ["CreateWalls", "CreateFamilyInstances", "CreateFloors", "CreateGrids", "CreateLevels"]
        if method not in valid_methods:
            raise ValueError(f"Invalid method: '{method}'. Supported methods: {', '.join(valid_methods)}")

        # Validate required parameters for each method
        required_params = {
            "CreateWalls": ["startX", "startY", "endX", "endY", "height", "width"],
            "CreateFloors": ["boundaryPoints"],  # boundaryPoints is required for CreateFloors
            "CreateFamilyInstances": ["categoryName", "startX", "startY", "startZ", "name"],
            "CreateGrids": ["name", "startX", "startY", "endX", "endY"],
            # For grid lines, start and end coordinates are required
            "CreateLevels": ["name", "elevation"],  # For levels, name and elevation are required
        }

        missing_keys = []
        for param in params:
            if method in required_params:
                missing_keys += [key for key in required_params[method] if key not in param]

        if missing_keys:
            raise ValueError(f"Missing required parameters for {method}: {', '.join(set(missing_keys))}")

        # Specifically handle "CreateGrids" to ensure the correct structure
        if method == "CreateGrids":
            for param in params:
                if "centerX" in param and "centerY" in param:
                    # It's an arc grid, so we need centerX, centerY
                    if "startX" not in param or "startY" not in param or "endX" not in param or "endY" not in param:
                        raise ValueError(
                            f"Missing required parameters for arc grid: startX, startY, endX, endY must be provided.")
                else:
                    # It's a line grid, so just startX, startY, endX, endY
                    if "startX" not in param or "startY" not in param or "endX" not in param or "endY" not in param:
                        raise ValueError(
                            f"Missing required parameters for line grid: startX, startY, endX, endY must be provided.")

        # Handle levels (CreateLevels)
        if method == "CreateLevels":
            for param in params:
                if "name" not in param or "elevation" not in param:
                    raise ValueError(f"Missing required parameters for level: name and elevation must be provided.")

        # Proceed with sending the command to Revit
        from .server import get_Revit_connection
        revit = get_Revit_connection()
        result = revit.send_command(method, params)
        return f"Successfully created element(s). Result: {result}"

    except Exception as e:
        logger.error(f"Error creating elements: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"
