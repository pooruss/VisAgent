import os
import time
from PIL import Image
from VAgent.config import CONFIG
from VAgent.models import EnvState, Action, ActionStatusCode
from VAgent.engine.base import BaseEngine
from VAgent.agent import ActionAgent, AnalyzeAgent, VisAgent, FeedBackAgent
from VAgent.environment import CodeEnvironment
from VAgent.memory import BaseMemory
from VAgent.log import logger
from VAgent.record import recorder
from colorama import Fore, Style

class VisEngine(BaseEngine):
    def __init__(self, config: CONFIG):
        super().__init__(config=config)
        self.agent = VisAgent(config)
        self.code_agent = VisAgent(config)
        self.feedback_agent = FeedBackAgent(config)
        
    def run(self, task: str, env: CodeEnvironment, memory: BaseMemory=None):
        
        data = f"Data overview:\n{env.data}\nData path: {env.data_path}"
        history_code = ""
        image = None
        step_count = 0
        feedback = ""
        error_msgs = ""
        while True and step_count <= self.config.engine.max_step:
            
            # Get current environment state and executable actions
            action_names, action_schemas = env.get_available_actions()
            logger.typewriter_log(f"Current available actions:\n", Fore.YELLOW, f"{Fore.GREEN}{action_names}{Style.RESET_ALL}")

            # Insert env state to agent memory
            # memory.insert(step_count, env_state=env_state)

            # Store env state to local memory
            # recorder.save_trajectory(step_count, env_state=env_state)

            # Predict code action. TODO: output action directly or call gpt4v again to do it
            max_try = 3
            while True and max_try > 0:
                actions = self.code_agent.predict(
                    task,
                    action_schemas, 
                    data=data,
                    image=None,
                    history_code=history_code,
                    additional_message=f"{feedback}\n\nCode Execution Message:\n{error_msgs}"
                )
                
                action = actions[0]

                logger.typewriter_log(f"Next Step Thoughts:", Fore.YELLOW, f"{Fore.RED}{action.thought}{Style.RESET_ALL}")
                logger.typewriter_log(f"Next Step Action:", Fore.YELLOW, f"{Fore.RED}{action.name}, {action.arguments}{Style.RESET_ALL}")

                if action.name == "exit":
                    # Save action locally
                    recorder.save_trajectory(step_count=step_count, action=action)
                    return env
                
                action_status, visual_result = env.step(action)

                if action_status == ActionStatusCode.SUCCESS:
                    time.sleep(5)
                    if os.path.exists(visual_result):
                        break
                else:
                    logger.typewriter_log(f"Action Status:", Fore.YELLOW, f"{Fore.GREEN}{action_status}, {visual_result}{Style.RESET_ALL}")
                    error_msgs = visual_result
                    history_code = action.arguments["code"]
                    max_try -= 1
            
            if not os.path.exists(visual_result):
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
            
            image = Image.open(visual_result)
            image.show()
            # Save action locally
            recorder.save_trajectory(step_count=step_count, action=action)

            # Predict feedback action. # TODO
            feedback_action = self.feedback_agent.predict(
                task,
                action_schemas, 
                data=data,
                image=image,
                history_code=history_code,
                additional_message=feedback
            )

            feedback = feedback_action[0].arguments["text"]

            if action.name == "exit":
                logger.typewriter_log(f"Query completed. Exiting...", Fore.YELLOW, f"{Fore.GREEN}{feedback}{Style.RESET_ALL}")
                # Save action locally
                recorder.save_trajectory(step_count=step_count, action=action)
                return env
            
            logger.typewriter_log(f"Action Feedback:", Fore.YELLOW, f"{Fore.GREEN}{feedback}{Style.RESET_ALL}")


            step_count += 1
            
        return image
    
    def run_one_step(self, task, env: CodeEnvironment, memory, history_code, feedback, step_count):
        data = f"Data overview:\n{env.data}\nData path: {env.data_path}"
        error_msgs = ""
        
        # 获取当前环境状态和可执行动作
        action_names, action_schemas = env.get_available_actions()
        logger.typewriter_log("Current available actions:", Fore.YELLOW, Fore.GREEN + str(action_names) + Style.RESET_ALL)

        max_try = 3
        while True and max_try > 0:
            # 预测代码动作
            actions = self.code_agent.predict(
                task,
                action_schemas,
                data=data,
                image=None,
                history_code=history_code,
                additional_message=f"{feedback}\n\nCode Execution Message:\n{error_msgs}"
            )

            action = actions[0]  # 假设predict方法返回一个动作列表，我们取第一个动作
            
            logger.typewriter_log("Next Step Thoughts:", Fore.YELLOW, Fore.RED + action.thought + Style.RESET_ALL)
            logger.typewriter_log("Next Step Action:", Fore.YELLOW, Fore.RED + action.name + ", " + str(action.arguments) + Style.RESET_ALL)

            if action.name == "exit":
                recorder.save_trajectory(step_count=step_count, action=action)
                return action.thought, visual_result, str(action.arguments), "Exit"
            
            # 执行动作
            action_status, visual_result = env.step(action)
            print(action_status)
            print(visual_result)
            action.status = action_status
            action.observation = visual_result
            recorder.save_trajectory(step_count=step_count, action=action)

            
            if action_status == ActionStatusCode.SUCCESS:
                if os.path.exists(visual_result):
                    logger.typewriter_log(f"Action Observation:", Fore.YELLOW, f"{Fore.GREEN}{action_status}{Style.RESET_ALL}")
                    

                    # Predict feedback action. # TODO
                    image = Image.open(visual_result)
                    feedback_action = self.feedback_agent.predict(
                        task,
                        action_schemas, 
                        data=data,
                        image=image,
                        history_code=history_code,
                        additional_message=feedback
                    )

                    feedback = feedback_action[0].arguments["text"]
                    logger.typewriter_log(f"Action Feedback:", Fore.YELLOW, f"{Fore.GREEN}{feedback}{Style.RESET_ALL}")
                    return action.thought, visual_result, action.arguments["code"], feedback
                else:
                    # raise RuntimeError(f"Cannot find output path, might due to parsing error or code running error: {visual_result}")
                    feedback = f"Cannot find output path, might due to parsing error or code running error: {visual_result}"
                    max_try -= 1
                    # return visual_result, action.arguments["code"], f"Cannot find output path, might due to parsing error or code running error: {visual_result}"
            else:
                logger.typewriter_log(f"Action Status:", Fore.YELLOW, f"{Fore.GREEN}{action_status}, {visual_result}{Style.RESET_ALL}")
                error_msgs = visual_result
                max_try -= 1
                
                # raise RuntimeError(f"Error in action execution: {error_msgs}")
                # return visual_result, action.arguments["code"], f"Error in action execution: {error_msgs}"
        return "", visual_result, action.arguments["code"], f"Error in action execution: {error_msgs}"
                