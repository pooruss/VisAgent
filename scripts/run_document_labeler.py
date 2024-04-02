import json
import os
from VAgent.environment import WebEnvironment
from VAgent.document.labeler import DocumentLabeler

if __name__ == '__main__':
    from VAgent.config import CONFIG
    web_env = WebEnvironment(CONFIG)

    urls_path = "./assets/urls.json"
    labeled_urls_path = "./assets/labeled_urls.json"

    urls = json.load(open(urls_path, "r"))

    if os.path.exists(labeled_urls_path):
        labeled_urls = json.load(open(labeled_urls_path, "r"))
    else:
        labeled_urls = {}
    document_labeler = DocumentLabeler(root_dir=f"assets/document", web_env=web_env, max_steps=5)
    
    for url_index, url in enumerate(urls):
        if url_index <= 4:
            continue
        document_labeler.run(url=url)
        labeled_urls[url] = 0
        json.dump(labeled_urls, open(labeled_urls_path, "w"), indent=4)
