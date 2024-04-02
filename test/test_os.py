from VAgent.engine import ReActEngine
from VAgent.environment import WebEnvironment, OSEnvironment
from VAgent.models import Action
from VAgent.memory import BaseMemory
from VAgent.config import CONFIG


if __name__ == '__main__':

    engine = ReActEngine(config=CONFIG)

    # Initialize environment
    env = OSEnvironment(config=CONFIG)

    status, obs = env.step(action=Action(name="mouse_click", arguments={"text": "screenshot"}))
    print(status, obs)
    
