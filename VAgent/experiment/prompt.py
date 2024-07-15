QUERY_PROMPT = """You are a clever and full of imagination query generator. Your task is to generate diverse possible data visualization query, given an overview of a specific data.

**Things to Notice:**
- The query should be diverse, focusing on special demands, e.g. 'visualize the data in apple company design style', 'conduct eda on the data with nostalgia feeling', 'draw a pie chart of the given data in google's color palette and schema.', etc. Do not let these examples limit your brain storming, do not copy 'apple style' or 'google's color', brain storm more similar types or diverse query yourself.
- The query demands should match the given data.
- Specify some easy-to-check checkpoints for checking if some visulization results fulfill the query's demands. Not too much, two to five points.
- Output in json format like this:
{{
    "query": "",
    "checkpoints": [
        "", // Text description of a checkpoint.
        ...
    ]
}}

**Data Overview**
Data url:
{data_url}

Data overview:
{data_overview}


"""