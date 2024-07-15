import os
import json
import time
import uuid
import threading
from VAgent.engine import VisEngine
from VAgent.environment import CodeEnvironment
from VAgent.memory import BaseMemory
from VAgent.config import CONFIG
from VAgent.record import Recorder

def process_queries(urls, data_root, model_name):

    CONFIG.recorder.record_dir = f"history_data_{model_name}"
    CONFIG.engine.code_model = model_name

    for url in urls:
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

            except Exception as e:
                print(f"Error {e} when running data {csv_path}.")

if __name__ == '__main__':

    for model_name in [
        # "glm-3-turbo",
        # "deepseek-chat",
        # "gemini-pro",
        # "gpt-3.5-turbo-16k",
        "gpt-4o",
        # "claude-3-5-sonnet-20240620"
    ]:
        data_root = "/Users/user/Downloads/git_clone/VisAgent/datasets"
        record_root = f"/Users/user/Downloads/git_clone/VisAgent/history_data_{model_name}"
        os.makedirs(record_root, exist_ok=True)
        skip_urls = []
        for url in os.listdir(record_root):
            url = url.split("_2024_07")[0]
            skip_urls.append(url)
        print(skip_urls)

        urls_to_process = [url for url in os.listdir(data_root) if url not in skip_urls and os.path.isdir(os.path.join(data_root, url))]

        # urls_to_process = urls_to_process[:20]
        # Calculate number of threads and split urls evenly
        print(len(urls_to_process))
        num_threads = 10
        urls_per_thread = len(urls_to_process) // num_threads

        threads = []
        for i in range(num_threads):
            start_index = i * urls_per_thread
            end_index = None if i == num_threads - 1 else (i + 1) * urls_per_thread
            thread_urls = urls_to_process[start_index:end_index]

            thread = threading.Thread(target=process_queries, args=(thread_urls, data_root, model_name))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
