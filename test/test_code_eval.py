import os
import json
import threading
from VAgent.engine import EvalEngine
from VAgent.environment import CodeEnvironment
from VAgent.memory import BaseMemory
from VAgent.config import CONFIG

def process_trajectory(record, data_root):
    url = record.split("_2024_07")[0]
    trajectory_dir = os.path.join(data_root, record, "Trajectory")
    result_path = os.path.join(trajectory_dir, "eval_result.json")
    if os.path.exists(result_path):
        results = json.load(open(result_path, "r"))
    else:
        max_step = 0
        for step_name in os.listdir(trajectory_dir):
            if "Step" in step_name:
                step_cnt = int(step_name[-1])
                max_step = max(max_step, step_cnt)
        
        step_dir = os.path.join(trajectory_dir, f"Step_{max_step}")
        if not os.path.exists(step_dir):
            return 0, 0, 0, 0
        
        max_action = 0
        for action_name in os.listdir(step_dir):
            action_cnt = int(action_name.replace(".json", "")[-1])
            max_action = max(max_action, action_cnt)

        action_result_path = os.path.join(step_dir, f"action_{max_action}.json")
        action_result = json.load(open(action_result_path, "r"))
        image_path = action_result["arguments"]["output_path"]
        task = action_result["task"]

        if image_path is None or not os.path.exists(image_path) or action_result["status"] != 0:
            results = {
                "score": 0,
                "is_pass": False,
                "reason": "Do not have image output."
            }
        else:
            eval_engine = EvalEngine(CONFIG)
            results = eval_engine.run(task, image_path)
            if results is not None:
                results = results.to_json()
            # print(results)

        if results is not None:
            json.dump(results, open(result_path, "w"), indent=4)

        else:
            return 0, 0, 0, 0

    score = results["score"]
    is_pass = 1.0 if results["is_pass"] else 0.0
    code_error = 1.0 if results["score"] == 0 else 0

    return 1, score, is_pass, code_error

def process_records(records, data_root, results):
    total_cnt = 0
    score_sum = 0
    pass_sum = 0
    code_error_sum = 0

    for record in records:
        if "http" not in record:
            continue
        # print(record)
        
        cnt, score, is_pass, code_error = process_trajectory(record, data_root)
        total_cnt += cnt
        score_sum += score
        pass_sum += is_pass
        code_error_sum += code_error
    
    results.append((total_cnt, score_sum, pass_sum, code_error_sum))


def count_null_feedback(base_directory):
    total_actions = 0
    null_feedback_count = 0
    
    for sub_dir in os.listdir(base_directory):
        sub_dir_path = os.path.join(base_directory, sub_dir)
        trajectory_path = os.path.join(sub_dir_path, 'Trajectory')
        # print(trajectory_path)
        if os.path.isdir(trajectory_path):
            for root, dirs, files in os.walk(trajectory_path):
                for file in files:
                    # print(file)
                    if file.endswith('.json') and "action" in file:
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # print(data)
                            total_actions += 1
                            # print(data.get('feedback'))
                            status = data["status"]
                            if status != 0:
                                null_feedback_count += 1
    
    if total_actions == 0:
        return 0.0
    
    null_feedback_ratio = null_feedback_count / total_actions
    return null_feedback_ratio


if __name__ == '__main__':
    root_names = [
        # "/Users/user/Downloads/git_clone/VisAgent/history_data_claude-3-5-sonnet-20240620",
        # "/Users/user/Downloads/git_clone/VisAgent/history_data_gpt-4o_visagent",
        "/Users/user/Downloads/git_clone/VisAgent/history_data_gpt-4o",
        # "/Users/user/Downloads/git_clone/VisAgent/history_data_gpt-4o_sr",
        # "/Users/user/Downloads/git_clone/VisAgent/history_data_gpt-4o_react",
        # "/Users/user/Downloads/git_clone/VisAgent/history_data_gpt-3.5-turbo-16k",
        # "/Users/user/Downloads/git_clone/VisAgent/history_data_qwen-turbo",
        # "/Users/user/Downloads/git_clone/VisAgent/history_data_deepseek-chat",
        # "/Users/user/Downloads/git_clone/VisAgent/history_data_gemini-pro",
        # "/Users/user/Downloads/git_clone/VisAgent/history_data_glm-3-turbo",
    ]

    result_dict = {}
    for root_name in root_names:
        data_root = root_name
        records = [record for record in os.listdir(data_root) if "http" in record]

        num_threads = 5
        records_per_thread = len(records) // num_threads

        threads = []
        results = []
        for i in range(num_threads):
            start_index = i * records_per_thread
            end_index = None if i == num_threads - 1 else (i + 1) * records_per_thread
            thread_records = records[start_index:end_index]

            thread = threading.Thread(target=process_records, args=(thread_records, data_root, results))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Combine results from all threads
        total_cnt = sum(result[0] for result in results)
        score_sum = sum(result[1] for result in results)
        pass_sum = sum(result[2] for result in results)
        code_error_sum = sum(result[3] for result in results)

        score_avg = float(score_sum / total_cnt) if total_cnt else 0
        pass_avg = float(pass_sum / total_cnt) if total_cnt else 0
        code_error_avg = float(code_error_sum / total_cnt) if total_cnt else 0

        print(total_cnt)
        print(score_avg, pass_avg, code_error_avg)

        # error rate
        ratio = count_null_feedback(data_root)
        print(f"代码执行出错的 action 占比: {ratio:.2%}")

        result_dict[data_root] = {
            "score": score_avg,
            "pass": pass_avg,
            "error": ratio
        }
    print(result_dict)