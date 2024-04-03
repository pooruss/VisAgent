import re
import json

def feedback_parser(string):
    return string
    
def code_parser(string):
    print(string)
    # 使用正则表达式匹配
    thought_pattern = re.compile(r"Thought: (.*?)\n\nOutput path:", re.DOTALL)
    output_path_pattern = re.compile(r"Output path: (.*?)\n\nCode:", re.DOTALL)
    code_pattern = re.compile(r"Code:\n(.*)", re.DOTALL)

    thought_match = thought_pattern.search(string)
    code_match = code_pattern.search(string)
    output_path_match = output_path_pattern.search(string)

    # 提取匹配的结果
    thought_content = thought_match.group(1).strip() if thought_match else None
    code_content = code_match.group(1).strip() if code_match else None
    output_path_content = output_path_match.group(1).strip() if output_path_match else None
    
    if code_content:
        pattern = r'```python(.*?)```'
        code_content = re.findall(pattern, code_content, re.DOTALL)[0]
    else:
        print(f"Error parsing code: \n{string}")
        code_content = None
    return thought_content, code_content, output_path_content

# For prediction parsing, into ReACT format
def react_parser(string):
    thought = [string[string.find("Thought: ") + len("Thought: "): string.find("\nAction: ")]]
    action = [string[string.find("Action: ") + len("Action: "): string.find("\nAction Input: ")]]
    action_input = [string[string.find("Action Input: ") + len("Action Input: "):]]
    return thought[0], action[0], action_input[0]

def react_parser_json(text) -> dict:
    if "}]" in text:
        pattern_check_keys = r'\[\{(?=.*?"thought":)(?=.*?"action":)(?=.*?"arguments":).*?\}\n\}\]'
    elif "}\n]" in text:
        pattern_check_keys = r'\[\s*\{(?=.*?"thought":)(?=.*?"action":)(?=.*?"arguments":).*?\}*\s*\]'
    elif "},\n]" in text:
        text = text.replace("},\n]", "}\n]")
        pattern_check_keys = r'\[\s*\{(?=.*?"thought":)(?=.*?"action":)(?=.*?"arguments":).*?\}*\s*\]'
    else:
        pattern_check_keys = r'\{(?=.*?"thought":)(?=.*?"action":)(?=.*?"arguments":).*?\}\n\}'

    # Search for the adjusted pattern in the text
    match_check_keys = re.search(pattern_check_keys, text, re.DOTALL)

    # Check if the pattern is found
    extracted_string_check_keys = match_check_keys.group(0) if match_check_keys else "No match found"
    try:
        action = json.loads(extracted_string_check_keys)
        if isinstance(action, dict):
            action = [action]
    except Exception as e:
        print(f"Error parsing action: {e}\n{extracted_string_check_keys}")
        # raise RuntimeError
        action = []
    return action

def box_explore_parser(response):
    overview_pattern = re.compile(r"Overview:\s*((?:(?!Box|Reason|Element Prediction|User Task|Element Summarization|Thought).)*)", re.DOTALL)
    box_pattern = re.compile(r"Box:\s*((?:(?!Reason|Element Prediction|User Task|Element Summarization|Thought).)*)", re.DOTALL)
    reason_pattern = re.compile(r"Reason:\s*((?:(?!Element Prediction|User Task|Element Summarization|Thought).)*)", re.DOTALL)
    element_prediction_pattern = re.compile(r"Element Prediction:\s*((?:(?!User Task|Element Summarization|Thought).)*)", re.DOTALL)
    query_pattern = re.compile(r"User Task:\s*((?:(?!Element Summarization|Thought).)*)", re.DOTALL)
    element_summarization_pattern = re.compile(r"Element Summarization:\s*((?:(?!Thought).)*)", re.DOTALL)
    thought_pattern = re.compile(r"Thought:\s*((?:(?!$).)*)", re.DOTALL)

    # Overview: An overview of the current screenshot.
    # Box: the box index you want to explore for further function.(an integer).
    # Reason: Explain why you choose the element.
    # Element Prediction: Predict the functionality of the element(s) within the chosen box.
    # Function: Possible function to explain the history. Directly give the function.
    # Element Summarization:
    overview_match = overview_pattern.search(response)
    reason_match = reason_pattern.search(response)
    box_match = box_pattern.search(response)
    query_match = query_pattern.search(response)
    element_prediction_match = element_prediction_pattern.search(response)
    element_summarization_match = element_summarization_pattern.search(response)
    thought_match = thought_pattern.search(response)

    return overview_match.group(1).strip(), reason_match.group(1).strip(), box_match.group(1).strip(), query_match.group(1).strip(), element_prediction_match.group(1).strip(), element_summarization_match.group(1).strip(), thought_match.group(1).strip()
