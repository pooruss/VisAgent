from VAgent.environment import WebEnvironment
from VAgent.document.labeler import DocumentLabeler

if __name__ == '__main__':
    from VAgent.config import CONFIG
    web_env = WebEnvironment(CONFIG)

    urls = ["https://www.youtube.com/"]
    document_labeler = DocumentLabeler(root_dir=f"assets/document", web_env=web_env, max_steps=5)
    
    for url in urls:
        document_labeler.run(url=url)
        input()