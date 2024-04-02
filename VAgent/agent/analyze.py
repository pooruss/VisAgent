from VAgent.config import CONFIG
from VAgent.models import EnvState, Action
from VAgent.agent.base import BaseAgent
from VAgent.environment.base import BaseEnvironment
from VAgent.memory import BaseMemory
from VAgent.agent.prompt.image_analyze import SYSTEM_PROMPT, USER_PROMPT
from VAgent.llm.openai_api import openai_vision_chatcompletion_request
from VAgent.utils.image import img_to_base64
from VAgent.log import logger
from colorama import Fore

class AnalyzeAgent(BaseAgent):
    def __init__(self, config: CONFIG):
        super().__init__(config=config)

    def predict(self, task: str, env_state: EnvState, memory: BaseMemory, additioanl_message: str="") -> str:

        # TODO: DEBUGGING
        prompt = SYSTEM_PROMPT + USER_PROMPT.format(
                task=task,
                ocr_description=env_state.ocr_description,
                history=memory.to_str(),
                additioanl_message=additioanl_message
            )
        response = openai_vision_chatcompletion_request(prompt, img_to_base64(env_state.screenshot))
        return response
