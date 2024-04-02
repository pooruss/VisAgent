import os
import json
import hashlib
from VAgent.models import Document, BoundingBox

class BaseDocument:
    def __init__(self, document_path: str):
        self.path = document_path
        self.documents = self.load_document()
    
    def load_document(self):
        documents = []
        for page_dir in os.listdir(self.path):
            if not os.path.exists(os.path.join(self.path, page_dir, "document.json")):
                continue
            page_document = json.load(open(os.path.join(self.path, page_dir, "document.json"), "r"))
            overview = page_document["overview"]
            xml_content = json.load(open(os.path.join(self.path, page_dir, "xml_content.json"), "r"))
            document = Document(state_description=overview)
            for content in xml_content:
                bbox = BoundingBox(identifier=content["uid"], description=content["text"], coordinates=content["bbox"])
                document.add_bounding_box(bbox)
            documents.append((document, os.path.join(self.path, page_dir)))
        return documents

    def retrieve_documents(self, src_document: Document):
        candidates = []
        src_bboxes = src_document.bounding_boxes
        for document, document_dir in self.documents:
            # Hash match
            # is_unique = src_document.is_unique(document)
            
            # Boxes match
            # is_unique = src_document.is_unique_bbox(document)
            # if not is_unique:
            #     candidates.append((document, document_dir))

            # Similarity calculate
            similarity = src_document.calculate_similarity(document)
            if similarity > 0.75:
                candidates.append((similarity, document, document_dir))
        
        # Sort the candidates by the similarity score in descending order
        sorted_candidates = sorted(candidates, key=lambda x: x[0], reverse=True)
        candidates = []
        for similarity, document, document_dir in sorted_candidates:
            candidates.append((document, document_dir))
        return candidates
    

if __name__ == '__main__':
    pass
