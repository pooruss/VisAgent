import os
import time
from PIL import Image
from VAgent.config import CONFIG
from VAgent.models import EnvState, Action, ActionStatusCode
from VAgent.engine.base import BaseEngine
from VAgent.agent import VisAgent, FeedBackAgent
from VAgent.environment import CodeEnvironment
from VAgent.memory import BaseMemory
from VAgent.log import logger
from VAgent.record import Recorder
from colorama import Fore, Style

class VisEngine(BaseEngine):
    def __init__(self, config: CONFIG, recorder: Recorder):
        super().__init__(config=config)
        self.code_agent = VisAgent(config)
        self.feedback_agent = FeedBackAgent(config)
        self.recorder = recorder
        
    def run(self, task: str, env: CodeEnvironment, memory: BaseMemory=None):
        
        data = f"Data overview:\n{env.data}\nData path: {env.data_path}"
        history_code = ""
        image = None
        step_count = 0
        feedback = ""
        error_msgs = ""
        while step_count < self.config.engine.max_step:
            
            # Get current environment state and executable actions
            action_names, action_schemas = env.get_available_actions()
            logger.typewriter_log(f"Current available actions for step {step_count}:\n", Fore.YELLOW, f"{Fore.GREEN}{action_names}{Style.RESET_ALL}")

            # Insert env state to agent memory
            # memory.insert(step_count, env_state=env_state)

            # Store env state to local memory
            # self.recorder.save_trajectory(step_count, env_state=env_state)

            # Predict code action. TODO: output action directly or call gpt4v again to do it
            max_try = 0
            visual_result = None
            while True and max_try < self.config.engine.max_self_reflexion_step:

                try:
                    actions = self.code_agent.predict(
                        task,
                        action_schemas, 
                        data=data,
                        image=None,
                        history_code=history_code,
                        additional_message=f"{feedback}\n\nCode Execution Message:\n{error_msgs}",
                        model_name=self.config.engine.code_model,
                        json_mode=self.config.engine.json_mode
                    )
                except Exception as e:
                    print(f"Error when generation code: {e}")
                    max_try += 1
                    continue
                    
                action = actions[0]

                logger.typewriter_log(f"Next Step Thoughts:", Fore.YELLOW, f"{Fore.RED}{action.thought}{Style.RESET_ALL}")
                logger.typewriter_log(f"Next Step Action:", Fore.YELLOW, f"{Fore.RED}{action.name}, {action.arguments}{Style.RESET_ALL}")

                if action.name == "exit":
                    # Save action locally
                    self.recorder.save_trajectory(step_count=step_count, action=action, task=task)
                    return env
                
                try:
                    action_status, visual_result = env.step(action)
                except:
                    max_try += 1
                    continue

                if action_status == ActionStatusCode.SUCCESS:
                    time.sleep(5)
                    if os.path.exists(visual_result):
                        break
                else:
                    action.observation = visual_result
                    self.recorder.save_trajectory(step_count=step_count, action=action, task=task)
                    logger.typewriter_log(f"Action Status for try {max_try}:", Fore.YELLOW, f"{Fore.GREEN}{action_status}, {visual_result}{Style.RESET_ALL}")
                    error_msgs = visual_result
                    history_code = action.arguments["code"]
                    max_try += 1
            
            if visual_result is None or not os.path.exists(visual_result):
                raise RuntimeError(f"Can not find output path, might due to parsing error or code running error: {visual_result}")
            
            history_code = action.arguments["code"]
            action.status = action_status
            action.observation = visual_result
            logger.typewriter_log(f"Action Observation:", Fore.YELLOW, f"{Fore.GREEN}{action_status}{Style.RESET_ALL}")

            # Insert action to agent memory
            memory.insert(
                step_count,
                action=action,
                action_status=action_status,
                observation=visual_result
            )
            
            if self.config.engine.enable_feedback:
                image = Image.open(visual_result)

                # Predict feedback action. # TODO
                feedback_action = self.feedback_agent.predict(
                    task,
                    action_schemas, 
                    data=data,
                    image=image,
                    history_code=history_code,
                    additional_message=feedback,
                    model_name=self.config.engine.feedback_model
                )

                feedback = feedback_action[0].arguments["text"]

                self.recorder.save_trajectory(step_count=step_count, action=action, feedback=feedback, task=task)

                if action.name == "exit" or "Feedback: exit" in feedback:
                    logger.typewriter_log(f"Query completed. Exiting...", Fore.YELLOW, f"{Fore.GREEN}{feedback}{Style.RESET_ALL}")
                    return env
                
                logger.typewriter_log(f"Action Feedback:", Fore.YELLOW, f"{Fore.GREEN}{feedback}{Style.RESET_ALL}")

            else:
                self.recorder.save_trajectory(step_count=step_count, action=action, task=task)
                
            step_count += 1
            
        return image
            