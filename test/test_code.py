import argparse
from VAgent.engine import VisEngine
from VAgent.environment import CodeEnvironment
from VAgent.memory import BaseMemory
from VAgent.config import CONFIG

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run VisEngine with specified configuration.')
    parser.add_argument('--data_path', required=True, help='Path to the data')
    parser.add_argument('--query', required=True, help='Task query to be performed by the engine')
    args = parser.parse_args()

    # Set the data path in the CONFIG
    CONFIG.code_env.data_path = args.data_path

    # Initialize the engine with the configuration
    engine = VisEngine(config=CONFIG)

    # Initialize environment
    env = CodeEnvironment(config=CONFIG)

    # Initialize memory
    short_memory = BaseMemory()

    # Run the task
    image = engine.run(task=args.query, env=env, memory=short_memory)

    # Show results
    image.show()

if __name__ == '__main__':
    main()