import json
import os
import base64
from io import BytesIO
from PIL import Image
from VAgent.config import CONFIG
from VAgent.models import EnvState, Action
from VAgent.agent.base import BaseAgent
from VAgent.environment.base import BaseEnvironment
from VAgent.memory import BaseMemory
from VAgent.llm import (
    openai_chatcompletion_request, 
    openai_vision_chatcompletion_request
)

from VAgent.agent.prompt.data_visulization import (
    SYSTEM_PROMPT as VIS_SYSTEM_PROMPT,
    USER_PROMPT as VIS_USER_PROMPT,
    RESPONSE_FORMAT as VIS_FORMAT
)
from VAgent.utils.parser import react_parser, react_parser_json, code_parser
from VAgent.utils.image import img_to_base64, base64_to_image
from VAgent.log import logger
from colorama import Fore

class VisAgent(BaseAgent):
    def __init__(self, config: CONFIG):
        super().__init__(config=config)

    def predict(
            self,
            task: str,
            action_schemas: list,
            data: str,
            history_code : str = "",
            image: Image = None,
            additional_message: str = ""
        ) -> Action:

        system_prompt = VIS_SYSTEM_PROMPT
        user_prompt = VIS_USER_PROMPT
        format_prompt = VIS_FORMAT
        # DEBUGGING
        available_actions_msg = ""
        for action_schame in action_schemas:
            action_name = action_schame["name"]
            available_actions_msg += f"{action_name}: {action_schame}\n"
        
        while True:
            if image is None:
                messages = [
                    {
                        "role": "system", 
                        "content": system_prompt
                    }, 
                    {
                        "role": "user", 
                        "content": system_prompt + user_prompt.format(
                task=task,
                data=data,
                history_code=history_code,
                available_actions=available_actions_msg,
                additional_message=additional_message
            ) + format_prompt
                    }
                ]
                response = openai_chatcompletion_request(
                    model=self.config.request.default_model,
                    messages=messages
                )
                response = response["choices"][0]["message"]["content"]
                (response)
            else:
                messages = [
                    {
                        "role": "system", 
                        "content": system_prompt
                    }, 
                    {
                        "role": "user", 
                        "content": user_prompt.format(
                            task=task,
                            data=data,
                            history_code=history_code,
                            available_actions=available_actions_msg,
                            additional_message=additional_message
                        ) + format_prompt
                    }
                ]
                response = openai_vision_chatcompletion_request(messages, img_to_base64(image))
            # print(response)
            thought, code, output_path = code_parser(response)
            if code:
                break
        
        vagent_actions = []

        action = Action(
            thought=thought,
            name="execute_shell",
            arguments={"code": code, "output_path": output_path}
        )
        vagent_actions.append(action)
        return vagent_actions
            