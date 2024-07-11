import os
import json
import time
import uuid
from VAgent.engine import VisEngine
from VAgent.environment import CodeEnvironment
from VAgent.memory import BaseMemory
from VAgent.config import CONFIG
from VAgent.record import Recorder

if __name__ == '__main__':

    data_root = "/Users/user/Downloads/git_clone/VisAgent/datasets"
    for url in os.listdir(data_root):

        for file_name in os.listdir(os.path.join(data_root, url)):
            if ".query.json" not in file_name:
                continue

            csv_file = file_name.replace(".query.json", "")
            csv_path = os.path.join(data_root, url, csv_file)
            
            query_path = os.path.join(data_root, url, file_name)
            query_json = json.load(open(query_path, "r"))

            query = query_json["query"]
            query += "\nCheckpoints to fulfill the demands:\n"
            for checkpoint in query_json["checkpoints"]:
                query += f"- {checkpoint}\n"

            print(f"reinitialize recorder... with url {url}")
            recorder = Recorder(CONFIG, url)

            print(f"Running query:\n{query}\n for data {csv_path}...")
            engine = VisEngine(config=CONFIG, recorder=recorder)

            # Initialize environment
            CONFIG.code_env.data_path = csv_path
            env = CodeEnvironment(config=CONFIG)

            # Initialize memory
            short_memory = BaseMemory()

            try:
                # Run the task
                image = engine.run(task=query, env=env, memory=short_memory)
                break
            except Exception as e:
                print(f"Error {e} when running data {csv_path}.")

