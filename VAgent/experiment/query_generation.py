import os
import re
import csv
import json
from VAgent.experiment.prompt import QUERY_PROMPT
from openai import OpenAI
import random
from math import ceil
random.seed(0)

def clean_json(json_str):
    json_res = json_str.split("```json", 1)[-1].split("```", 1)[0].strip() if "```json" in json_str else json_str
    return json_res

def openai_request(messages, use_json=True):
    client = OpenAI(
        api_key='sk-vAjSo8FwpoiMM01FEfB337D75e6440848e8b89Aa18Ca3810',
        base_url="https://aihubmix.com/v1"
    )

    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4o",
        response_format={"type":"json_object" if use_json else "text"},
        max_tokens=4096
    )
    
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def generate(data_url, data_overview):
    prompt = QUERY_PROMPT
    messages = [
        {
            "role": "system",
            "content": prompt.format(data_url=data_url, data_overview=data_overview)
        }
    ]
    response = openai_request(messages)
    response = json.loads(response)
    return response


if __name__ == "__main__":

    data_root = "datasets"
    for url in os.listdir(data_root):
        for csv_file in os.listdir(os.path.join(data_root, url)):
            if "csv" not in csv_file:
                continue
            
            try:
                data_path = os.path.join(data_root, url, csv_file)
                data = open(data_path, "r")
                data_overview = data.read()[:500]
                query_data = generate(url, data_overview)
                json.dump(query_data, open(data_path + ".query.json", "w"), indent=4)
                print(query_data)
                break
            except Exception as e:
                print(f"Error: {e}")
                continue