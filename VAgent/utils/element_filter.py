""" 
Element Filter Script:
- functions
    - filter_by_area
        - remove too small elements
    - filter_by_view
        - remove elements not in the current view port
    - filter_by_interoperable
        - remove elements is not interoperable
    - filter_by_features
        - remove elements with unexpected text
    - filter_by_nms
        - remove bounding boxes that overlap more than the threshold with the current bounding box

- inputs
    - source-elements, rules
- outputs
    - target-elements
- description
    - this is script will filter source elements by text, area, view-port, iou, etc.
    
"""
import numpy as np

def filter_by_area(rect, min_side=10, min_area=300):
    if rect["width"] < min_side or rect["height"] < min_side or rect["width"] * rect["height"] < min_area:
        return True
    return False

def filter_by_view(rect, view_port):
    x1, y1, x2, y2 = 0, 0,  view_port["width"], view_port["height"]

    if rect["left"] < x1 or rect["top"] < y1 or rect["right"] > x2 or rect["bottom"] > y2:
        return True
    return False

def filter_by_interoperable(e):
    return not e["is_interoperable"]

def filter_by_text(e):
    return not (e["text"] and e["text"] != "undefined")

def iou(box1, box2):
    """
    计算两个边界框的IOU（Intersection over Union）
    """
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    # 计算相交区域的坐标
    x_left = max(x1, x2)
    y_top = max(y1, y2)
    x_right = min(x1 + w1, x2 + w2)
    y_bottom = min(y1 + h1, y2 + h2)

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    # 计算相交区域的面积
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # 计算并集区域的面积
    box1_area = w1 * h1
    box2_area = w2 * h2
    union_area = box1_area + box2_area - intersection_area
    iou = intersection_area / union_area
    return iou

def nms_by_area(bboxes, areas, iou_threshold=0.5):
    """
    非极大值抑制（NMS）算法
    """
    # 根据置信度排序
    sorted_indices = np.argsort(areas)
    keep = []

    while len(sorted_indices) > 0:
        # 选择置信度最高的边界框
        best_idx = sorted_indices[0]
        keep.append(best_idx)

        # 计算当前边界框与其余边界框的IOU
        current_bbox = bboxes[best_idx]
        rest_indices = sorted_indices[1:]

        rest_bboxes = [bboxes[i] for i in rest_indices]
        ious = np.array([iou(current_bbox, bbox) for bbox in rest_bboxes])

        # 移除与当前边界框重叠度高于阈值的边界框
        no_overlapping_indices = np.where(ious < iou_threshold)[0]
        sorted_indices = rest_indices[no_overlapping_indices]

    return keep


def filter_elements(elements, view_port, 
                    is_sort=True,
                    is_filter_by_view=True, 
                    is_filter_by_interoperable=False,
                    is_filter_by_text=False,
                    is_filter_by_area=False,
                    is_filter_by_overlapping=True,
                    overlap_iou_threshold = 0.5
                    ):
    med_results = []
    areas = []
    bboxes = []
    cut1, cut2, cut3, cut4, cut5 = 0, 0, 0, 0, 0
    for e in elements:
        if is_filter_by_view and filter_by_view(e["bbox"], view_port):
            cut1 += 1
            continue
        if is_filter_by_interoperable and filter_by_interoperable(e):
            cut2 += 1
            continue
        if is_filter_by_text and filter_by_text(e):
            cut3 += 1
            continue
        if is_filter_by_area and filter_by_area(e["bbox"]):
            cut4 += 1
            continue
        
        med_results.append(e)
        areas.append(e["bbox"]["width"] * e["bbox"]["height"])
        bboxes.append((e["bbox"]["x"], e["bbox"]["y"], e["bbox"]["width"], e["bbox"]["height"]))
    
    # filter by nsm
    if is_filter_by_overlapping:
        keep = nms_by_area(bboxes, areas, overlap_iou_threshold)
        cut5 = len(med_results) - len(keep)
        results = []
        for i in keep:
            results.append(med_results[i])
    else:
        results = med_results
    
    # sort
    if is_sort:
        results = sorted(results, key=lambda item: (item["bbox"]["top"]//10, item["bbox"]["left"]//10))
   
    # done 
    final_results = []
    for i, item in enumerate(results):
        item["uid"] = i+1
        final_results.append(item)

    return final_results

def clean_elements(elements):
    """
    'text': {'0': 'P', '1': 'r', '2': 'o', '3': 't', '4': 'e', '5': 'c', '6': 't', '7': ' ', '8': 'Y', '9': 'o', '10': 'u', '11': 'r', '12': ' ', '13': 'A', '14': 'c', '15': 'c', '16': 'o', '17': 'u', '18': 'n', '19': 't', '20': ' ', '21': 'I', '22': 'n', '23': 'f', '24': 'o', '25': 'r', '26': 'm', '27': 'a', '28': 't', '29': 'i', '30': 'o', '31': 'n'}
    'text": Prot...
    """
    for e in elements:
        if "text" in e and isinstance(e["text"], dict):
            e["text"] = "".join(list(e["text"].values()))
    return elements