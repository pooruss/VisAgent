import json
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
    openai_vision_chatcompletion_request,
    claude_chatcompletion_request,
    claude_vision_chatcompletion_request
)
from VAgent.record import recorder
from VAgent.agent.prompt.text_mode_react import SYSTEM_PROMPT as TEXT_REACT_SYSTEM_PROMPT
from VAgent.agent.prompt.text_mode_react import USER_PROMPT as TEXT_REACT_USER_PROMPT
from VAgent.agent.prompt.image_mode_react import (
    SYSTEM_PROMPT as IMAGE_REACT_SYSTEM_PROMPT,
    USER_PROMPT as IMAGE_REACT_USER_PROMPT,
    RESPONSE_FORMAT as IMAGE_REACT_FORMAT
)
from VAgent.agent.prompt.image_mode_pipeline import (
    SYSTEM_PROMPT as IMAGE_PIPELINE_SYSTEM_PROMPT,
    USER_PROMPT as IMAGE_PIPELINE_USER_PROMPT,
    RESPONSE_FORMAT as IMAGE_PIPELINE_FORMAT
)
from VAgent.utils.parser import react_parser, react_parser_json
from VAgent.utils.image import img_to_base64, base64_to_image
from VAgent.log import logger
from colorama import Fore

class ActionAgent(BaseAgent):
    def __init__(self, config: CONFIG):
        super().__init__(config=config)

    def predict(
            self,
            task: str,
            action_schemas: list,
            env_state: EnvState,
            memory: BaseMemory,
            mode: str = "text",
            additioanl_message: str = "",
            enable_pipeline: bool = False,
            llm_query_id: int = 0
        ) -> Action:

        # DEBUGGING
        available_actions_msg = ""
        for action_schame in action_schemas:
            action_name = action_schame["name"]
            available_actions_msg += f"{action_name}: {action_schame}\n"

        while True:
            if mode == "image":
                if enable_pipeline:
                    system_prompt = IMAGE_PIPELINE_SYSTEM_PROMPT
                    user_prompt = IMAGE_PIPELINE_USER_PROMPT
                else:
                    system_prompt = IMAGE_REACT_SYSTEM_PROMPT
                    user_prompt = IMAGE_REACT_USER_PROMPT

                if "gpt" in self.config.request.default_model:
                    messages = [
                        {
                            "role": "system", 
                            "content": system_prompt
                        }, 
                        {
                            "role": "user", 
                            "content": user_prompt.format(
                                task=task,
                                screenshot_description=env_state.get_descirption(),
                                history=memory.to_str(),
                                available_actions=available_actions_msg,
                                additioanl_message=additioanl_message
                            ) + IMAGE_REACT_FORMAT
                        }
                    ]
                    response = openai_vision_chatcompletion_request(messages, img_to_base64(env_state.screenshot))
                elif "claude" in self.config.request.default_model:
                    messages = [
                        {
                            "role": "system", 
                            "content": system_prompt
                        },
                        {
                            "role": "user", 
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/jpeg",
                                        "data": img_to_base64(env_state.screenshot)
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": user_prompt.format(
                                                    task=task,
                                                    screenshot_description=env_state.get_descirption(),
                                                    history=memory.to_str(),
                                                    available_actions=available_actions_msg,
                                                    additioanl_message=additioanl_message
                                                ) + IMAGE_REACT_FORMAT
                                }
                            ]
                        }
                    ]
                    response = claude_vision_chatcompletion_request(messages=messages)
                
                actions = react_parser_json(response)
                
            else:
                messages = [
                    {
                        "role": "system", 
                        "content": TEXT_REACT_SYSTEM_PROMPT
                    }, 
                    {
                        "role": "user", 
                        "content": TEXT_REACT_USER_PROMPT.format(
                            task=task,
                            screenshot_description=env_state.get_descirption(),
                            history=memory.to_str(),
                            available_actions=available_actions_msg)\
                        + IMAGE_REACT_FORMAT
                    }
                ]

                response = claude_chatcompletion_request(
                    model=self.config.request.default_model,
                    messages=messages
                )

                if "gpt" in self.config.request.default_model:
                    response = response["choices"][0]["message"]["content"]
                elif "claude" in self.config.request.default_model:
                    response = response.content[0].text
                    # print(response)
                actions = react_parser_json(response)

            if actions:
                break

        vagent_actions = []
        for action in actions:
            action = Action(
                thought=action["thought"],
                name=action["action"],
                arguments=action["arguments"]
            )
            vagent_actions.append(action)
        
        recorder.save_llm_inout(llm_query_id=llm_query_id, messages=messages, output_data=response)
        
        return vagent_actions
            