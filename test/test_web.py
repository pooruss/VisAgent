from VAgent.engine import ReActEngine
from VAgent.environment import WebEnvironment, OSEnvironment
from VAgent.models import Action
from VAgent.memory import BaseMemory
from VAgent.config import CONFIG


if __name__ == '__main__':

    engine = ReActEngine(config=CONFIG)

    # Initialize environment
    env = WebEnvironment(config=CONFIG)

    _ = env.goto("https://arxiv.org/")
    
    env.state.screenshot_bbox.show()

    env.click(element_index=5)

    env.typing(text="AI Agent")

    env.hotkey(press="Enter")

    print(env.state.document.bounding_boxes)

    env.state.screenshot_bbox.show()

