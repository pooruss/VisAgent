import os
import time
import json
from PIL import Image
from VAgent.config import CONFIG
from VAgent.models import EnvState, Action, ActionStatusCode
from VAgent.engine.base import BaseEngine
from VAgent.agent import EvaluationAgent
from VAgent.environment import CodeEnvironment
from VAgent.memory import BaseMemory
from VAgent.log import logger
from colorama import Fore, Style

class EvalEngine(BaseEngine):
    def __init__(self, config: CONFIG):
        super().__init__(config=config)
        self.agent = EvaluationAgent(config)
        
    def run(self, query: str, image_path: str):

        image = Image.open(image_path)

        max_retry = 3
        success = False
        while True and max_retry > 0:
            try:
                results = self.agent.predict(
                    query=query,
                    image=image
                )
                success = True
                break
            except Exception as e:
                print(f"Error when evaluating: {e}")
                max_retry -= 1

        if not success:
            results = None

        return results
            