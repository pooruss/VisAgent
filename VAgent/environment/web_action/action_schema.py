ACTION_SCHEMA = \
{
    "mouse_click": {
        "action_name": "mouse_click",
        "action_schema": {
            "name": "mouse_click",
            "description": "Click the target element or position on the web page. Click the element under the mouse cursor if neither element_index nor position is provided.",
            "parameters": {
                "type": "object",
                "properties": {
                    "element_index": {
                        "type": "integer",
                        "description": "The index of the element to click.",
                        "default": 0
                    },
                    "x": {
                        "type": "string",
                        "description": "The x coordinate position to click. Example: 0.5"
                    },
                    "y": {
                        "type": "string",
                        "description": "The y coordinate position to click. Example: 0.5"
                    },
                }
            },
            "required": ["element_index"]
        }
    },
    "keyboard_write": {
        "action_name": "keyboard_write",
        "action_schema": {
            "name": "keyboard_write",
            "description": "Type the given text by triggering keyborad events. Before using this, make sure you have clicked on the target area to ensure the typing message will be sent to the target area, e.g. the search bar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The string to be typed out.",
                        "default": "hello world"
                    }
                }
            },
            "required": ["text"]
        }
    },
    "keyboard_press": {
        "action_name": "keyboard_press",
        "action_schema": {
            "name": "keyboard_press",
            "description": "Press shortcut keys or operations of the keyboard.",
            "parameters": {
                "type": "object",
                "properties": {
                    "press": {
                        "type": "string",
                        "description": "The key to press, can be a combination of any keys. Defaults to 'Enter' . Example: 'Enter', 'Alt+ArrowLeft','Shift+KeyW'.",
                        "default": "Enter"
                    },
                    "times": {
                        "type": "integer",
                        "description": "The times that the key is pressed.",
                        "default": 1
                    }
                }
            },
            "required": ["press"]
        }
    },
    "write_file": {
        "action_name": "write_file",
        "action_schema": {
            "name": "write_file",
            "description": "Write texts to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text content.",
                        "default": ""
                    },
                    "file_path": {
                        "type": "string",
                        "description": "The file path to be stored, including the file name.",
                        "default": "./file.txt"
                    },
                }
            },
            "required": []
        }
    },
    "read_file": {
        "action_name": "read_file",
        "action_schema": {
            "name": "read_file",
            "description": "Read content from a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The file path to read, including the file name.",
                        "default": "./file.txt"
                    }
                }
            },
            "required": []
        }
    },
    "exit": {
        "action_name": "exit",
        "action_schema": {
            "name": "exit",
            "description": "Exit the task if you think the task is completed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Task execution summary and final answer to response to the user.",
                        "default": ""
                    }
                }
            },
            "required": ["text"]
        }
    }
}
