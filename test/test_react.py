from VAgent.engine import ReActEngine
from VAgent.environment import WebEnvironment, OSEnvironment
from VAgent.memory import BaseMemory
from VAgent.config import CONFIG


if __name__ == '__main__':

    engine = ReActEngine(config=CONFIG)

    # Initialize environment
    env = WebEnvironment(config=CONFIG)

    # Initialize memory
    short_memory = BaseMemory()

    # User task
    query = "搜索最近三天发表的与AI Agent 相关的论文，获取到论文名、作者、摘要、链接。"
    _ = env.goto("https://arxiv.org/")

    # Run the task
    env = engine.run(task=query, env=env, memory=short_memory)
    
    # Show results
    import matplotlib.pyplot as plt
    import numpy as np
    print(env.state.documentation)
    # Show the image using matplotlib
    plt.imshow(np.array(env.state.screenshot))
    plt.show()

