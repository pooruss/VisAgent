import os


for url in os.listdir("datasets"):

    has_query = False
    for file_name in os.listdir(os.path.join("datasets", url)):
        if ".query.json" in file_name:
            has_query = True
    
    if has_query:
        continue
    
    ori_path = os.path.join("datasets", url)
    tgt_path = os.path.join("full_datasets", url)
    os.system(f"mv {ori_path} {tgt_path}")