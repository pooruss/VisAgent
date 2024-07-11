import os
import json
from VAgent.engine import EvalEngine
from VAgent.environment import CodeEnvironment
from VAgent.memory import BaseMemory
from VAgent.config import CONFIG


if __name__ == '__main__':

    data_root = "/Users/user/Downloads/git_clone/VisAgent/history_data"
    for record in os.listdir(data_root):
        if "http" not in record:
            continue
        print(record)

        trajectory_dir = os.path.join(data_root, record, "Trajectory")
        result_path = os.path.join(trajectory_dir, "eval_result.json")
        if os.path.exists(result_path):
            continue

        max_step = 0
        for step_name in os.listdir(trajectory_dir):
            step_cnt = int(step_name[-1])
            max_step = max(max_step, step_cnt)
        
        step_dir = os.path.join(trajectory_dir, f"Step_{max_step}")

        max_action = 0
        for action_name in os.listdir(step_dir):
            action_cnt = int(action_name.replace(".json", "")[-1])
            max_action = max(max_action, action_cnt)

        action_result_path = os.path.join(step_dir, f"action_{max_action}.json")
        # print(action_result_path)
        action_result = json.load(open(action_result_path, "r"))
        image_path = action_result["arguments"]["output_path"]
        task = action_result["task"]

        if not os.path.exists(image_path):
            results = {
                "score": 0,
                "is_pass": False,
                "reason": "Do not have image output."
            }
        else:
            eval_engine = EvalEngine(CONFIG)
            results = eval_engine.run(task, image_path)
            results = results.to_json()
            print(results)

        if results is not None:            
            json.dump(results, open(result_path, "w"), indent=4)
        