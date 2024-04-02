from VAgent.engine import PipelineEngine
from VAgent.environment import WebEnvironment, OSEnvironment
from VAgent.memory import BaseMemory
from VAgent.config import CONFIG


if __name__ == '__main__':

    engine = PipelineEngine(config=CONFIG)

    # Initialize environment
    env = WebEnvironment(config=CONFIG)

    # Initialize memory
    short_memory = BaseMemory()

    # User task
    query = "original query：发一条微博，内容是“今天天气真不错”。\nexpanded information："
    _ = env.goto("https://weibo.com/")

    # Run the task
    env = engine.run(task=query, env=env, memory=short_memory)
    
    # Show results
    import matplotlib.pyplot as plt
    import numpy as np
    print(env.state.documentation)
    # Show the image using matplotlib
    plt.imshow(np.array(env.state.screenshot))
    plt.show()

