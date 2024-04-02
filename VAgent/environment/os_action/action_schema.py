ACTION_SCHEMA = \
{
    "keyboard_write": {
        "action_name": "keyboard_write",
        "action_schema": {
            "name": "keyboard_write",
            "description": "Type out a string of characters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The string to be typed out.",
                        "default": "hello world"
                    },
                    "interval": {
                        "type": "string",
                        "description": "The delay between pressing each character key. Defaults to 0.1.",
                        "default": "0.1"
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
            "description": "Press a key with the number of times specified by presses. If the keys is a single key after splitting by the delimiter, it is treated as a single key and is pressed the number of times specified by presses. If keys is a sequence of keys split by the delimiter, each key in the list is pressed once.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "string",
                        "description": "The key(s) to be pressed.",
                        "default": ""
                    },
                    "delimiter": {
                        "type": "string",
                        "description": "The character used to split the keys into a list of keys. Note that the delimiter should not be one of the keys.",
                        "default": "/"
                    },
                    "presses": {
                        "type": "integer",
                        "description": "The number of times to press the key. Defaults to 1.",
                        "default": 1
                    },
                    "interval": {
                        "type": "string",
                        "description": "The delay between each key press. Defaults to 0.1.",
                        "default": "0.1"
                    }
                }
            },
            "required": ["keys"]
        }
    },
    "keyboard_hotkey": {
        "action_name": "keyboard_hotkey",
        "action_schema": {
            "name": "keyboard_hotkey",
            "description": "Press a sequence of keys in the order they are provided, and then release them in reverse order. Provide delimiter every time you use hotkey.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "string",
                        "description": "The keys to be pressed. Specified in string format, and will be split by a split character into a list of keys. For example, ' /command' means pressing ' ' and 'command' for a spotlight search on mac ios system.",
                        "default": " /command"
                    },
                    "delimiter": {
                        "type": "string",
                        "description": "The character used to split the keys into a list of keys. Include this every time you use keyboard hotkey.",
                        "default": "/"
                    }
                }
            },
            "required": ["keys", "delimiter"]
        }
    },
    "mouse_scroll": {
        "action_name": "mouse_scroll",
        "action_schema": {
            "name": "mouse_scroll",
            "description": "Scrolls down. If you don't find some text on screen that you expected to be there, you probably want to do this",
            "parameters": {
                "type": "object",
                "properties": {
                    "clicks": {
                        "type": "integer",
                        "description": "The amount of scrolling to perform.",
                        "default": "-10"
                    }
                }
            },
            "required": ["clicks"]
        }
    },
    "mouse_click": {
        "action_name": "mouse_click",
        "action_schema": {
            "name": "mouse_click",
            "description": "Performs pressing a mouse button down and then immediately releasing it. Can receive 1.text or 2.(x,y) coordinate or 3.bounding box index to locate the click position. Very useful if want to open a link on a web page, or operating on an app.",
            "parameters": {
                "text": {
                    "type": "string",
                    "description": "The text used to find out the position in the screenshot, by matching with the OCR text results of the screenshot, and then click with the button. Priority higher than the `icon` parameter. Use this very often if you want to click.",
                    "default": ""
                },
                "button": {
                    "type": "string",
                    "description": "one of the constants ``left``, ``middle``, ``right``, ``primary``, or ``secondary``. It defaults to ``primary`` (which is the left mouse button, unless the operating system has been set for left-handed users.)",
                    "default": "primary"
                },
                "clicks": {
                    "type": "integer",
                    "description": "an int of how many clicks to make, and defaults to ``1``",
                    "default": 1
                },
                "interval": {
                    "type": "string",
                    "description": "how many seconds to wait in between each click, if ``clicks`` is greater than ``1``. It defaults to ``0.0`` for no pause in between clicks.",
                    "default": "0.1"
                },
                "x": {
                    "type": "integer",
                    "description": "The x coordinate of the mouse to move to. Optional, and if parameter `text` is set, this parameter will be ignored.",
                    "default": ""
                },
                "y": {
                    "type": "integer",
                    "description": "The y coordinate of the mouse to move to. Optional, and if parameter `text` is set, this parameter will be ignored.",
                    "default": ""
                },
                "index": {
                    "type": "integer",
                    "description": "The bounding box index to click on. Highly recommended if bounding box indexes are provided.",
                    "default": ""
                },
                "click_type": {
                    "type": "string",
                    "description": "Single click or double click or triple click or right click. Default to single click. If set to double or triple, the `clicks` parameter will be ignored. If set to right, the `button` parameter will be ignored.",
                    "default": "single"
                }
            },
            "required": []
        }
    }
}
