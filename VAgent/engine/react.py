from VAgent.config import CONFIG
from VAgent.models import EnvState, Action
from VAgent.engine.base import BaseEngine
from VAgent.agent import ActionAgent, AnalyzeAgent
from VAgent.environment.base import BaseEnvironment
from VAgent.memory import BaseMemory
from VAgent.log import logger
from VAgent.record import recorder
from colorama import Fore, Style

class ReActEngine(BaseEngine):
    def __init__(self, config: CONFIG):
        super().__init__(config=config)
        self.action_agent = ActionAgent(config)
        if self.config.engine.inference_mode == "mix":
            self.analyze_agent = AnalyzeAgent(config)

    def run(self, task: str, env: BaseEnvironment, memory: BaseMemory=None):

        step_count = 0
        llm_query_id = 0
        while True and step_count <= self.config.engine.max_step:
            
            env_state = env.get_current_state()

            if self.config.engine.inference_mode == "mix":
                logger.typewriter_log(f"Start analyzing current screenshot...", Fore.YELLOW)
                # Use gpt4v to analyze current env
                documentation = self.analyze_agent.predict(task, env_state, memory)
                env.state.documentation = documentation
            
            ocr_description = env.ocr(env_state.screenshot)
            env_state.ocr_description = ocr_description

            logger.typewriter_log(f"Current screenshot text info:\n", Fore.YELLOW, f"{Fore.GREEN}{env_state.documentation}...\n{env_state.ocr_description[:100]}...\n{env_state.bbox_description}...{Style.RESET_ALL}")

            # Get current environment state and executable actions
            action_names, action_schemas = env.get_available_actions()
            logger.typewriter_log(f"Current available actions:\n", Fore.YELLOW, f"{Fore.GREEN}{action_names}{Style.RESET_ALL}")

            # Insert env state to agent memory
            memory.insert(step_count, env_state=env_state)

            # Store env state to local memory
            recorder.save_trajectory(step_count, env_state=env_state)

            # Predict next action. TODO: output action directly or call gpt4v again to do it
            actions = self.action_agent.predict(
                task,
                action_schemas, 
                env_state, 
                memory,
                self.config.engine.inference_mode,
                llm_query_id
            )
            llm_query_id += 1
            
            # Execution action combo
            for action in actions:
                logger.typewriter_log(f"Next Step Thoughts:", Fore.YELLOW, f"{Fore.RED}{action.thought}{Style.RESET_ALL}")
                logger.typewriter_log(f"Next Step Action:", Fore.YELLOW, f"{Fore.RED}{action.name}, {action.arguments}{Style.RESET_ALL}")

                if action.name == "exit":
                    # Save action locally
                    recorder.save_trajectory(step_count=step_count, action=action)
                    return env
                
                # Act in environment and get action status
                action_status, observation = env.step(action)
                action.status = action_status
                action.observation = observation
                logger.typewriter_log(f"Action Observation:", Fore.YELLOW, f"{Fore.GREEN}{action_status}, {observation}{Style.RESET_ALL}")

                # Insert action to agent memory
                memory.insert(
                    step_count,
                    action=action,
                    action_status=action_status,
                    observation=observation
                )

                # Save action locally
                recorder.save_trajectory(step_count=step_count, action=action)

            step_count += 1
            
        return env
            