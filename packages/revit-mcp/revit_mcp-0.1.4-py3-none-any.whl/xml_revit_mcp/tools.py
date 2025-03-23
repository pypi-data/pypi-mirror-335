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
    Finds elements in the Revit scene using specified search criteria, such as categoryId or categoryName.

    Parameters:
    - ctx (Context):
      The current FastMCP context, used to manage and track Revit operations.
    - method (str, optional):
      The name of the Revit API method to call. Default is "FindElements".
      This allows flexibility if a different API method is needed for specific search operations.
    - params (List[dict[str, object]], optional):
      A list of dictionaries representing search criteria for finding elements in the model.
      Each dictionary supports the following keys:
        - isInstance (bool, required):
          Set to True to search for instances (actual model elements) or False to search for types (element definitions).
        - categoryId (int, required):
          The numerical ID representing the category of elements to search for (e.g. -2000011, -2000240).
        - categoryName (str, optional):
          The localized name of the category to search for.
          It should match the current language environment of the Revit application.
          If both categoryId and categoryName are provided, categoryId takes precedence. (e.g., 墙, 标高)

      Example `params`:
      ```python
      [
          {"isInstance": True, "categoryId": -2000011},
          {"isInstance": False, "categoryId": -2000011, "categoryName": "墙"}
      ]
      ```
      - This searches for instances in category -2000011 and types in category -2000011 with the localized name "墙".

    Returns:
    - List[int]:
      A list of element IDs that match the search criteria.
      If no elements are found or an error occurs, an empty list is returned.

    Raises:
    - ValueError:
      Raised if `params` is not a list of dictionaries or if its structure is invalid.
    - Exception:
      If any other error occurs during the Revit API call, the error will be logged and an empty list will be returned.

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


def delete_elements(ctx: Context, method: str = "DeleteElements", params: List[dict[str, object]] = None) -> str:
    """
    Deletes elements from the Revit model using their IDs.

 Parameters:
    - ctx (Context): The FastMCP context.
    - method (str): The Revit API method to call. Default is "DeleteElements".
    - params (List[dict[str, object]]): List of dictionaries containing element IDs with the key 'elementId'.
      The 'elementId' can be an integer or a string representing the element ID.

    Returns:
    - str: Result message indicating success or failure.
    """
    try:
        if not params or not all(
                isinstance(param, dict) and 'elementId' in param and isinstance(param['elementId'], (int, str)) for
                param in params):
            raise ValueError(
                "Invalid input: 'params' should be a list of dictionaries with an 'elementId' key (int or str).")

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
