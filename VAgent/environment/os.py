import json
import time
import pyautogui
import numpy as np
import warnings
import matplotlib.pyplot as plt
from VAgent.environment.base import BaseEnvironment
from VAgent.models import EnvState
from VAgent.environment.os_action import (
    Clipboard,
    Display,
    Mouse,
    Keyboard,
    Terminal,
    Os,
    ACTION_SCHEMA
)
from VAgent.models import ActionStatusCode

class OSEnvironment(BaseEnvironment):
    def __init__(self, config):
        super().__init__(config)
        self.state = EnvState()
        self.config = config
        self.terminal = Terminal()

        self.offline = False
        self.verbose = False

        self.mouse = Mouse(self)
        self.keyboard = Keyboard(self)
        self.display = Display(self)
        self.clipboard = Clipboard(self)
        self.os = Os(self)

        self.action_schema = ACTION_SCHEMA
        self.update_state()

    def screenshot(self, show: bool=True):
        screenshot = pyautogui.screenshot()
        # IPython interactive mode auto-displays plots, causing RGBA handling issues, possibly MacOS-specific.
        screenshot = screenshot.convert("RGB")
        if show:
            # Show the image using matplotlib
            plt.imshow(np.array(screenshot))

            with warnings.catch_warnings():
                # It displays an annoying message about Agg not being able to display something or WHATEVER
                warnings.simplefilter("ignore")
                plt.show()
        return screenshot

    def step(self, action, use_ocr=True):
        action_name = action.name
        action_inputs = action.arguments
        # try:
        if action_name == "keyboard_write":
            self.keyboard.write(**action_inputs)
        elif action_name == "keyboard_press":
            self.keyboard.press(**action_inputs)
        elif action_name == "keyboard_hotkey":
            self.keyboard.hotkey(**action_inputs)

        elif action_name == "mouse_scroll":
            self.mouse.scroll(**action_inputs)
        elif action_name == "mouse_click":
            self.mouse.click(**action_inputs)

        else:
            raise ValueError(f"Invalid action: {action_name}")
        status_code = ActionStatusCode.SUCCESS

        # Update self state
        self.update_state()
        return status_code, "Operation success."
        
        # except Exception as e:
        #     # raise e
        #     return ActionStatusCode.FAILED, f"Action failed due to error: {e}"
    
    def update_state(self, use_ocr=True):
        # Update self state. Default to ocr for nl description.
        screenshot = self.screenshot(show=False)
        if use_ocr:
            ocr_description = self.ocr(screenshot)
            self.state.ocr_description = ocr_description
        self.state.screenshot = screenshot
        return self.state

if __name__ == '__main__':
    import asyncio
    
