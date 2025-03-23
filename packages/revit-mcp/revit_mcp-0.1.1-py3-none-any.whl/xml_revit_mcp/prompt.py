# prompt.py
# Copyright (c) 2025 zedmoster

import mcp.types as types

PROMPTS = {
    "FindElements": types.Prompt(
        name="FindElements",
        description="Find elements in the Revit scene",
        arguments=[
            types.PromptArgument(
                name="categoryId",
                description="Category ID to search (optional) "
                            "* At least one of categoryId or categoryName must be provided.",
                required=False
            ),
            types.PromptArgument(
                name="categoryName",
                description="Category name to search (optional) "
                            "* At least one of categoryId or categoryName must be provided.",
                required=False
            ),
            types.PromptArgument(
                name="isInstance",
                description="Whether to search for instances or types (optional)",
                required=False
            )
        ],
    ),
    "UpdateElements": types.Prompt(
        name="UpdateElements",
        description="Update Revit element parameters",
        arguments=[
            types.PromptArgument(
                name="elementId",
                description="Element ID to update",
                required=True
            ),
            types.PromptArgument(
                name="parameterName",
                description="Name of the parameter to update",
                required=True
            ),
            types.PromptArgument(
                name="parameterValue",
                description="New value for the parameter",
                required=True
            )
        ],
    ),
    "DeleteElements": types.Prompt(
        name="DeleteElements",
        description="Delete elements from Revit",
        arguments=[
            types.PromptArgument(
                name="elementId",
                description="Element ID to delete",
                required=True
            )
        ],
    ),
    "ShowElements": types.Prompt(
        name="ShowElements",
        description="Show elements in Revit",
        arguments=[
            types.PromptArgument(
                name="elementId",
                description="Element ID to show",
                required=True
            )
        ],
    ),
    "CreateElements": types.Prompt(
        name="CreateWalls",
        description="Create walls in Revit",
        arguments=[
            types.PromptArgument(
                name="startX",
                description="Wall start X coordinate (mm)",
                required=True
            ),
            types.PromptArgument(
                name="startY",
                description="Wall start Y coordinate (mm)",
                required=True
            ),
            types.PromptArgument(
                name="endX",
                description="Wall end X coordinate (mm)",
                required=True
            ),
            types.PromptArgument(
                name="endY",
                description="Wall end Y coordinate (mm)",
                required=True
            ),
            types.PromptArgument(
                name="height",
                description="Wall height (mm), must be positive",
                required=True
            ),
            types.PromptArgument(
                name="width",
                description="Wall width (mm), must be positive",
                required=True
            )
        ],
    ),
}


async def list_prompts_response() -> list[types.Prompt]:
    return list(PROMPTS.values())


async def get_prompt_response(
        method: str, arguments: dict[str, str] | None = None
) -> types.GetPromptResult:
    if method not in PROMPTS:
        raise ValueError(f"Prompt not found: {method}. Available prompts: {', '.join(PROMPTS.keys())}")

    params_str = ""

    if method in PROMPTS.keys():
        if arguments:
            params_str = "\n".join(
                f"- {key}: {value}" for key, value in arguments.items()
            )
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Executing '{method}' with the following details:\n\n{params_str}"
                    )
                )
            ]
        )

    raise ValueError("Prompt implementation not found")
