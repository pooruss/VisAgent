from VAgent.engine import VisEngine
from VAgent.environment import WebEnvironment, OSEnvironment, CodeEnvironment
from VAgent.memory import BaseMemory
from VAgent.config import CONFIG


if __name__ == '__main__':

    engine = VisEngine(config=CONFIG)

    # Initialize environment
    env = CodeEnvironment(config=CONFIG)

    # Initialize memory
    short_memory = BaseMemory()

    # User task
    query = "Help me do EDA on the data, with apple's product style, e.g. simple and effective."
    
    # Run the task
    image = engine.run(task=query, env=env, memory=short_memory)
    
    # Show results
    image.show()

