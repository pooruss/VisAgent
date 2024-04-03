from VAgent.engine import VisEngine
from VAgent.environment import WebEnvironment, OSEnvironment, CodeEnvironment
from VAgent.models import Action
from VAgent.memory import BaseMemory
from VAgent.config import CONFIG


if __name__ == '__main__':

    engine = VisEngine(config=CONFIG)

    # Initialize environment
    env = CodeEnvironment(config=CONFIG)

    # Initialize memory
    short_memory = BaseMemory()

    action = Action(name="execute_shell", arguments={"code": """import pandas as pd\nimport matplotlib.pyplot as plt\n\ndata = pd.read_csv('assets/vis_data/demo.csv') # reading the CSV file\n\nplt.figure(figsize=(10, 6)) \nplt.plot(data['name'], data['age'], marker='o') \nplt.title('Linear Plot of Age')\nplt.xlabel('Name') \nplt.ylabel('Age') \n\nplt.savefig('assets/vis_data/demo_plot.png') # saving the plot\n\nplt.show()\n""", "output_path": "./1.jpg"})

    env = env.step(action)
    
