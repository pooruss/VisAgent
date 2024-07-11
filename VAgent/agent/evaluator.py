import json
import base64
from io import BytesIO
from PIL import Image
from VAgent.config import CONFIG
from VAgent.models import EvaluationResult
from VAgent.agent.base import BaseAgent
from VAgent.environment.base import BaseEnvironment
from VAgent.memory import BaseMemory
from VAgent.llm import (
    openai_chatcompletion_request, 
    openai_vision_chatcompletion_request
)

from VAgent.agent.prompt.evaluator import (
    SYSTEM_PROMPT as VIS_SYSTEM_PROMPT,
    USER_PROMPT as VIS_USER_PROMPT,
    RESPONSE_FORMAT as VIS_FORMAT
)
from VAgent.utils.parser import feedback_parser
from VAgent.utils.image import img_to_base64, base64_to_image
from VAgent.utils.utils import clean_json
from VAgent.log import logger
from colorama import Fore

class EvaluationAgent(BaseAgent):
    def __init__(self, config: CONFIG):
        super().__init__(config=config)

    def predict(
            self,
            query: str, 
            image: Image = None,
        ) -> EvaluationResult:

        system_prompt = VIS_SYSTEM_PROMPT
        user_prompt = VIS_USER_PROMPT.format(query=query)
        format_prompt = VIS_FORMAT
        
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }, 
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt + format_prompt
                    }
                ]
            }
        ]
        response = openai_vision_chatcompletion_request(messages, img_to_base64(image))
        response = clean_json(response)
        response = json.loads(response)
        results = EvaluationResult(
            score=response["score"],
            is_pass=response["is_pass"],
            reason=response["reason"]
        )
        return results
            