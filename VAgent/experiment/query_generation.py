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
        api_key='api_key',
        base_url="https://aihubmix.com/v1"
    )

    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4o",
        response_format={"type":"json_object" if use_json else "text"},
        max_tokens=4096
    )
    
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
    max_query = 60
    query_cnt = 0
    for url in os.listdir(data_root):

        csv_files = []

        has_query = False
        for csv_file in os.listdir(os.path.join(data_root, url)):
            if csv_file.endswith(".query.json"):
                query_cnt += 1
                has_query  = True
            if not csv_file.endswith(".csv"):
                continue

            csv_files.append(csv_file)
        
        if has_query:
            continue
        
        if len(csv_files) <= 0:
            continue

        csv_file = random.sample(csv_files, k=1)[0]
        
        if query_cnt >= max_query:
            continue
        
        try:
            data_path = os.path.join(data_root, url, csv_file)
            data = open(data_path, "r")
            data_overview = data.read()[:500]
            query_path = data_path + ".query.json"
            if os.path.exists(query_path):
                query_data = json.load(open(query_path, "r"))
                print(query_data)
                if "query" in query_data:
                    continue

            print(query_path)
            query_data = generate(url, data_overview)
            json.dump(query_data, open(data_path + ".query.json", "w"), indent=4)
            query_cnt += 1
            # print(query_data)
            print(query_cnt)

        except Exception as e:
            print(f"Error: {e}")
            continue