import json
import base64
import pickle
import itertools
import math
import numpy as np
from typing import List
from PIL import Image
from VAgent.utils.image import img_to_base64, base64_to_image

HASH_MOD = 2147483647
FACT_POWER = [17**i for i in range(20)]
RATIO_CONST = 11.8

def hash_float(x):
    """
    Hash a float by top-3 binary digits.
    """
    sign = 1 if (x >= 0) else -1
    x = abs(x)
    if x <= 8:
        return round(x) * sign
    x, p = int(x), 20
    while (x >> p) & 1 == 0:
        p = p - 1
    return ((x & (7<<(p-2))) + (0 if (x>>(p-3)) & 1 == 0 else (1<<(p-2)))) * sign

class BoundingBox:
    def __init__(self, identifier, description, coordinates):
        """
        Initialize a BoundingBox instance.

        :param identifier: A unique identifier for the bounding box.
        :param description: Natural language description of the bounding box.
        """
        self.identifier = identifier
        self.description = description
        self.coordinates = coordinates

    def __eq__(self, other):
        """
        Check if two BoundingBox instances are equal based on their identifiers and descriptions.

        :param other: Another BoundingBox instance.
        :return: True if they have the same identifier, False otherwise.
        """
        return hash(self.coordinates["top"]) + hash(self.coordinates["bottom"]) + hash(self.coordinates["left"]) + hash(self.coordinates["right"]) + hash(self.description) == hash(other.coordinates["top"]) + hash(other.coordinates["bottom"]) + hash(other.coordinates["left"]) + hash(other.coordinates["right"]) + hash(other.description)

    def __lt__(self, other):
        """
        Compare two BoundingBox instances based on their description.

        :param other: Another BoundingBox instance.
        :return: True if this instance's description is less than the other, False otherwise.
        """
        return self.description < other.description
    
    def __hash__(self):
        """
        Return the hash of the bounding box based on its identifier.
        """
        return hash(self.coordinates["top"]) + hash(self.coordinates["bottom"]) + hash(self.coordinates["left"]) + hash(self.coordinates["right"])

    def __repr__(self):
        """
        Return a string representation of the bounding box.
        """
        return f"BoundingBox(identifier={self.identifier}, description={self.description})"


class Document:
    _hash: int = None 

    def __init__(self, state_description):
        """
        Initialize a Document instance.

        :param state_description: Natural language description of the document state.
        """
        self.state_description = state_description
        self.bounding_boxes = []

    def add_bounding_box(self, new_box):
        """
        Add a BoundingBox to the document. The identifiers are reassigned based on description order.

        :param description: Natural language description of the bounding box.
        """
        self.bounding_boxes.append(new_box)

    def is_unique(self, other_document):
        """
        Check if this document is unique compared to another document.

        :param other_document: Another Document instance.
        :return: True if the set of bounding boxes are different, False otherwise.
        """
        if len(self.bounding_boxes) == len(other_document.bounding_boxes):
            return hash(self) != hash(other_document)
        ### TODO: Extra boudning boxes? 
        return True

    def is_unique_bbox(self, other_document):
        other_bbox = other_document.bounding_boxes
        for bbox in self.bounding_boxes:
            if bbox not in other_bbox:
                return True
        return False

    def calculate_similarity(self, other_document) -> float:
        same_cnt = 0
        other_bbox = other_document.bounding_boxes
        for bbox in self.bounding_boxes:
            if bbox in other_bbox:
                same_cnt += 1
        similarity = same_cnt / max(len(other_bbox), len(self.bounding_boxes))
        return similarity
            
    def __hash__(self) -> int:
        """
        Calculate hash value for current page.
        Three features are calculated for bounding boxes and pairs of bounding boxes.

        :return: int value.
        """
        if self._hash is not None:
            return self._hash
        _hash = 0
        for box in self.bounding_boxes:
            height, width = abs(box.coordinates["top"] - box.coordinates["bottom"]), abs(box.coordinates["left"] - box.coordinates["right"])
            f0, f1 = hash_float(height), hash_float(width)
            f2 = hash_float(math.log(height/width)*RATIO_CONST)
            _hash = (_hash + np.dot([f0, f1, f2], FACT_POWER[:3]) % HASH_MOD) % HASH_MOD

        for box_a, box_b in itertools.pairwise(self.bounding_boxes):
            l = min(box_a.coordinates["left"], box_b.coordinates["left"])
            t = max(box_a.coordinates["top"], box_b.coordinates["top"])
            r = max(box_a.coordinates["right"], box_b.coordinates["right"])
            b = min(box_a.coordinates["bottom"], box_b.coordinates["bottom"])
            height, width = abs(t-b), abs(r-l)
            f0, f1 = hash_float(height), hash_float(width)
            try:
                f2 = hash_float(math.log(height/width)*RATIO_CONST)
            except:
                print(height, width)
                print(box_a, box_b)
                continue
            _hash = (_hash + np.dot([f0, f1, f2], FACT_POWER[:3]) % HASH_MOD) % HASH_MOD

        self._hash = int(_hash)
        return self._hash

    def __repr__(self):
        """
        Return a string representation of the document.
        """
        return f"Document(state_description={self.state_description}, bounding_boxes={self.bounding_boxes})"
    
    def save(self, file_path):
        with open(file_path, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def load(file_path):
        with open(file_path, 'rb') as file:
            return pickle.load(file)


class EnvState():
    documentation: str = ""
    ocr_description: str = ""
    bbox_description: str = ""
    screenshot: Image.Image | str = None
    screenshot_bbox: Image.Image | str = None
    document: Document = Document(state_description="")
    xml_content: None

    def to_json(self) -> dict:
        state_json = dict()
        if isinstance(self.screenshot, Image.Image):
            screenshot_base64 = img_to_base64(self.screenshot)
        else:
            screenshot_base64 = self.screenshot
        if isinstance(self.screenshot_bbox, Image.Image):
            screenshot_bbox_base64 = img_to_base64(self.screenshot_bbox)
        else:
            screenshot_bbox_base64 = self.screenshot_bbox
        state_json["screenshot"] = screenshot_base64
        state_json["screenshot_bbox_base64"] = screenshot_bbox_base64

        if self.documentation != "":
            state_json["nl_description"] = self.documentation
        elif self.bbox_description != "":
            state_json["nl_description"] = self.bbox_description
        elif self.ocr_description != "":
            state_json["nl_description"] = self.bbox_description
        else:
            state_json["nl_description"] = ""
        return state_json
    
    def get_descirption(self):
        overall_description = f"Bounding Boxes:\n"
        for bbox in self.document.bounding_boxes:
            overall_description += f"{bbox.identifier+1}: {bbox.description}\n"
        if self.ocr_description != "":
            overall_description += f"\nOCR Information:{self.ocr_description}\n"
        if self.document != "":
            overall_description += f"\nPage Document Information:{self.document}\n"
        return overall_description
    

def add_noise(bbox, percent=1):
    w, h = bbox[2] - bbox[0], bbox[1]-bbox[3]
    return np.array((bbox[0]+np.random.uniform(0, percent*w/100), bbox[1]+np.random.uniform(0, percent*h/100),
                    bbox[2]+np.random.uniform(0, percent*w/100), bbox[3]+np.random.uniform(0, percent*h/100)))

if __name__ == '__main__':
    # Bounding Boxes
    bbox1 = np.array((30, 100, 40, 80))
    bbox2 = np.array((20, 30, 100, 20))
    # Example of creating and comparing documents
    per = 3.4
    sample_count = 10000
    ans = 0
    for _ in range(sample_count):
        doc1 = Document("State 1 of a web page")
        doc1.add_bounding_box(BoundingBox(0, "A submit button", add_noise(bbox1, per)))
        doc1.add_bounding_box(BoundingBox(1, "A hyperlink to a different page", add_noise(bbox2, per)))

        doc2 = Document("State 2 of the same web page")
        doc2.add_bounding_box(BoundingBox(3, "A hyperlink to a different page", add_noise(bbox2, per)))
        doc2.add_bounding_box(BoundingBox(2, "A submit button", add_noise(bbox1, per)))

        # Checking if the documents are unique
        doc1_unique = doc1.is_unique(doc2)
        if doc1_unique:
            ans += 1
    print("True Equal Rate:", ans / sample_count)
    ans = 0
    for _ in range(sample_count):
        doc1 = Document("State 1 of a web page")
        doc1.add_bounding_box(BoundingBox(0, "A submit button", add_noise(bbox1, per)))
        doc1.add_bounding_box(BoundingBox(1, "A hyperlink to a different page", add_noise(bbox2, per)))

        doc2 = Document("State 2 of the same web page")
        doc2.add_bounding_box(BoundingBox(3, "A hyperlink to a different page", add_noise(bbox1, per)))
        doc2.add_bounding_box(BoundingBox(2, "A submit button", add_noise(bbox1, per)))

        # Checking if the documents are unique
        doc1_unique = doc1.is_unique(doc2)
        # if not doc1_unique:
        #     exit(0)
        if doc1_unique:
            ans += 1

    print("False Equal Rate: (Collision)", ans / sample_count)
    #print(doc1_unique)  # This should be True, as the documents have different bounding boxes
    #print(doc2)
    #print(doc1)
    # print(doc2.bounding_boxes)