import hashlib
from VAgent.utils.image import img_to_base64
from VAgent.utils.parser import box_explore_parser
from VAgent.utils.utils import generate_url_id
from VAgent.llm.openai_api import openai_vision_chatcompletion_request
from VAgent.agent.prompt.document_labeling import UNCERTAIN_BOX, CERTAIN_BOX, API_BOX, API_BOX_USER
import time
import json
import os
import re
from copy import deepcopy
from colorama import Fore, Style

class DocumentLabeler:
    def __init__(self, root_dir: str, web_env, max_steps=5):
        self.root_dir = root_dir
        self.env = web_env
        self.visited_box = set()
        self.explored_document = set()
        self.max_steps = max_steps
    
    def generate_document(self, env_state, history, selected_bbox_description, last_element, mode="uncertain", additional_img=None):
        img_64 = img_to_base64(env_state.screenshot)
        if additional_img:
            additional_img_64 = img_to_base64(additional_img)
            base64_capture_bbox = [img_64, additional_img_64]
        # bbox_description = env_state.bbox_description
        bbox_description = selected_bbox_description
        if mode == "uncertain":
            prompt = UNCERTAIN_BOX.format(
                bbox_description=bbox_description,
                history=history
            )
        elif mode == "api":
            prompt = API_BOX
            user_prompt = API_BOX_USER.format(
                bbox_description=bbox_description,
                history=history,
                last_element=last_element
            )
        else:
            prompt = CERTAIN_BOX.format(
                bbox_description=bbox_description,
                history=history
            )

        try:
            messages = [
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        }
                    ]
                }
            ]
            response = openai_vision_chatcompletion_request(messages=messages, base64_capture_bbox=base64_capture_bbox)
        except Exception as e:
            print(f"Error when requesting gpt4v: {e}")
            return None
        
        max_try_times = 3
        while max_try_times > 0:
            try:
                overview, reason, box, query, element_prediction, element_description, thought = box_explore_parser(response)
                result = {
                    "overview": overview,
                    "reason": reason,
                    "box": int(box),
                    "query": query,
                    "element_description": element_description,
                    "box_prediction": element_prediction,
                    "thought": thought
                }
                return result
            except Exception as e:
                print(f"Error when parsing gpt4v response: {e}\nResponse: {response}")
                max_try_times -= 1
        return None

    def detect_new_state(self, cur_bboxes):
        new_state = False
        newly_added_box = set()
        for bbox in cur_bboxes:
            if bbox.description == "":
                continue
            if bbox not in self.visited_box:
                # print(f"newly added bbox: {bbox}")
                newly_added_box.add(bbox)
                self.visited_box.add(bbox)
                new_state = True
        return new_state, newly_added_box

    def explore_element(self, element_index, url_id):
        last_screenshot = deepcopy(self.env.state.screenshot_bbox)

        # Record last env document
        last_document = deepcopy(self.env.state.document)

        # Click next element
        self.env.click(element_index=element_index)

        # Record explored document for filtering
        cur_document = deepcopy(self.env.state.document)
        self.explored_document.add(cur_document)

        # Detect unique document, only depends on new box
        new_state, newly_added_box = self.detect_new_state(cur_bboxes=self.env.state.document.bounding_boxes)
        
        # TODO: Notice, we assume the first round exploration is new state
        new_state = True
        
        # Explore box
        explored_bbox_num = [element_index]

        # Build history operations
        history = ""
        last_element = ""
        for box in last_document.bounding_boxes:
            if int(box.identifier) == int(element_index):
                last_element = f"{box.identifier}:{box.description}"
                history += f"-> {last_element}"

        # Only explore on those newly added bboxes
        selected_bbox_description = f"Bounding Boxes:\n"
        for box in newly_added_box:
            selected_bbox_description += f"{box.identifier}: {box.description}\n"

        # Explore while in new page state
        step_cnt = 0
        while new_state and step_cnt < self.max_steps:
            bbox_str = ""
            for bbox_index in explored_bbox_num:
                bbox_str += f"_box_{bbox_index}"
            
            # Generate main document content here
            explore_result = self.generate_document(self.env.state, history, selected_bbox_description, last_element, mode="api", additional_img=last_screenshot)
            if not explore_result:
                break
            target_box = explore_result["box"]
            ocr_description = self.env.ocr(self.env.state.screenshot)
            explore_result["ocr_description"] = ocr_description

            # Save current state document
            os.makedirs(os.path.join(self.root_dir, url_id, bbox_str), exist_ok=True)
            if not os.path.exists(os.path.join(self.root_dir, url_id, bbox_str, f"document.json")):

                self.env.state.screenshot.save(os.path.join(self.root_dir, url_id, bbox_str, f"screenshot.png"))
                with open(
                os.path.join(self.root_dir, url_id, bbox_str, f"xml_content.json"), "w", encoding="utf-8") as writer:
                    json.dump(self.env.state.xml_content, writer, indent=2, ensure_ascii=False)
                with open(
                os.path.join(self.root_dir, url_id, bbox_str, f"document.json"), "w", encoding="utf-8") as writer:
                    json.dump(explore_result, writer, indent=2, ensure_ascii=False)

            for box in self.env.state.document.bounding_boxes:
                if int(box.identifier) == int(target_box):
                    last_element = f"{box.identifier}:{box.description}"
                    history += f"-> {last_element}"

            print(f"{Fore.LIGHTYELLOW_EX}[Explore History]{Style.RESET_ALL}: {history}")

            # Click to explore target box
            try:
                self.env.click(target_box)
            except:
                print("Clicking on non-exist bbox...")
                break

            target_document = deepcopy(self.env.state.document)

            # Record explored bbox
            explored_bbox_num.append(target_box)
            
            # Detect new state
            new_state, cur_newly_added_box = self.detect_new_state(cur_bboxes=target_document.bounding_boxes)

            # Only explore on those newly added bboxes
            selected_bbox_description = f"Bounding Boxes:\n"
            for box in cur_newly_added_box:
                selected_bbox_description += f"{box.identifier}: {box.description}\n"
            
            step_cnt += 1

    def run(self, url):

        # Prepare directories
        url_id = generate_url_id(url)
        os.makedirs(os.path.join(self.root_dir, url_id), exist_ok=True)
        with open(os.path.join(self.root_dir, url_id, "url.txt"), "w", encoding="utf-8") as writer:
            writer.write(url)
        writer.close()

        print(f"{Fore.LIGHTGREEN_EX}[Process Url]{Style.RESET_ALL}: {url}, id: {url_id}")

        # Initial env
        _ = self.env.goto(url)

        # Traverse all the element in the initial page
        for element_index in range(len(self.env.page_elements)):
            
            if element_index == 0:
                # Initial page state, named with _box_0
                os.makedirs(os.path.join(self.root_dir, url_id, f"_box_{element_index}"), exist_ok=True)
                self.env.state.screenshot.save(os.path.join(self.root_dir, url_id, f"_box_{element_index}", "screenshot.png"))
                with open(
                os.path.join(self.root_dir, url_id, f"_box_{element_index}", "xml_content.json"), "w", encoding="utf-8") as writer:
                    json.dump(self.env.state.xml_content, writer, indent=2, ensure_ascii=False)

                continue

            for bbox in self.env.state.document.bounding_boxes:
                if bbox not in self.visited_box:
                    self.visited_box.add(bbox)

            if element_index-1 > len(self.env.page_elements):
                break

            print(f"{Fore.LIGHTRED_EX}[Exploring Element]{Style.RESET_ALL}: {element_index}, box: {self.env.page_elements[element_index]}")
            self.explore_element(element_index=element_index, url_id=url_id)

            # Go back to original page
            _ = self.env.goto(url)
            

if __name__ == '__main__':
    pass
