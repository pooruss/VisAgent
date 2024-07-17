import os
import json

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

# 使用方法
base_directory = 'history_data_gpt-4o/'
ratio = count_null_feedback(base_directory)
print(f"代码执行出错的 action 占比: {ratio:.2%}")
