ACTION_SCHEMA = \
{
    "execute_shell": {
        "action_name": "execute_shell",
        "action_schema": {
            "name": "execute_shell",
            "description": "Create or replace a notebook cell and execute it, return the output.\nExample:\n```\nIn[0]: code='print(\"hello world\")' # This will create a new cell and execute it.\nIn[1]: code='print(\"hello world\")',cell_index=0 # This will overwrite the first cell and execute it.\nIn[2]: code='print(\"hello world\")',cell_index=-1 # This will overwrite the last cell and execute it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "python code to be executed, make sure it is valid python code with right format."
                    },
                    "cell_index": {
                        "type": "integer",
                        "description": "the index of the cell to be insert and overwrite `code`, default to `None`, which means append new cell.",
                        "default": None
                    },
                    "reset": {
                        "type": "boolean",
                        "description": "whether to reset the kernel before executing the code. Default to `False`.",
                        "default": False
                    },
                },
            "required": ["code"]
            }
        },
    }
}
