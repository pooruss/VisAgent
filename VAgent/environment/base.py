import abc
from typing import List, Tuple
from PIL import Image
from VAgent.utils.ocr import easyocr_get_text, pytesseract_get_text, surya_get_text
from VAgent.models import EnvState, Action, ActionStatusCode

class BaseEnvironment(metaclass=abc.ABCMeta):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.state = EnvState()
        self.action_schema = dict()

    def ocr(self, image: Image):
        if self.config.ocr.method == "easyocr":
            return easyocr_get_text(image)
        elif self.config.ocr.method == "pytesseract":
            return pytesseract_get_text(image)
        elif self.config.ocr.method == "surya":
            return surya_get_text(image)
        else:
            # Defaule to easyocr
            return easyocr_get_text(image)
    
    def get_current_state(self) -> EnvState:
        return self.state
    
    def get_available_actions(self) -> Tuple[list, list]:
        action_names = []
        action_schemas = []
        for element in self.action_schema:
            action_json = self.action_schema[element]
            action_name = action_json["action_name"]
            action_schema = action_json["action_schema"]
            action_names.append(action_name)
            action_schemas.append(action_schema)
        return action_names, action_schemas
    
    @abc.abstractmethod
    def screenshot(self,) -> Image.Image:
        """Take a screenshot of current env."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def step(self, action: Action) -> Tuple[ActionStatusCode, str]:
        """Take a step in current env. Return action status code and observation in string."""
        raise NotImplementedError


if __name__ == '__main__':
    import asyncio
    
