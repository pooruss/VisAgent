"""Recorder for VAgent.

This module provides the recorder for VAgent, which responsible for recording the running process of VAgent.

Functionalities:
- Log run records and store them locally.
"""

import re
import os
import time
import uuid
import json
from copy import deepcopy

from .config import CONFIG
from VAgent.utils.single import Singleton

def dump_common_things(object):
    if type(object) in [str, int, float, bool]:
        return object
    if type(object) == dict:
        return {dump_common_things(key): dump_common_things(value) for key, value in object.items()}
    if type(object) == list:
        return [dump_common_things(cont) for cont in object]
    method = getattr(object, 'to_json', None)
    if callable(method):
        return method()
    

class Recorder():
    """Recorder that records the running process of VAgent.

    Functionalities:
    - print log to console.
    - store running records to database and file.
    """

    def __init__(self, config: CONFIG, strip=None):
        
        """Initialize files."""
        now = int(round(time.time() * 1000))
        if strip is None:
            strip = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(now / 1000)) + uuid.uuid4().hex[:8]
        else:
            strip += ("_" + time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(now / 1000)) + uuid.uuid4().hex[:8])

        self.root_dir = os.path.join(config.recorder.record_dir, strip)
        os.makedirs(self.root_dir, exist_ok=True)
        os.makedirs(os.path.join(self.root_dir, "LLM_input_output_pair"), exist_ok=True)
        os.makedirs(os.path.join(self.root_dir, "Trajectory"), exist_ok=True)
        self.query_count = 0
    
    def get_query_id(self):
        query_id = deepcopy(self.query_count)
        self.query_count += 1
        return query_id
    
    def save_trajectory(self, step_count, **kwargs):
        os.makedirs(os.path.join(self.root_dir, "Trajectory", f"Step_{step_count}"), exist_ok=True)

        feedback = kwargs.pop("feedback", None)
        
        action = kwargs.pop("action", None)
        if action:
            action_cnt = 0
            while os.path.exists(os.path.join(self.root_dir, "Trajectory", f"Step_{step_count}", f"action_{action_cnt}.json")):
                action_cnt += 1

            task = kwargs.pop("task", None)
            with open(
                os.path.join(self.root_dir, "Trajectory", f"Step_{step_count}", f"action_{action_cnt}.json"), "w", encoding="utf-8") as writer:
                action = action.to_json()
                action["feedback"] = feedback
                action["task"] = task
                json.dump(action, writer, indent=2, ensure_ascii=False)

        env_state = kwargs.pop("env_state", None)
        if env_state:
            screenshot = env_state.screenshot
            screenshot_bbox = env_state.screenshot_bbox
            documentation = env_state.documentation
            ocr_description = env_state.ocr_description
            bbox_description = env_state.bbox_description
            document = env_state.document
            xml_content = env_state.xml_content
            if screenshot:
                screenshot.save(os.path.join(self.root_dir, "Trajectory", f"Step_{step_count}", "screenshot.png"))
            if screenshot_bbox:
                screenshot_bbox.save(os.path.join(self.root_dir, "Trajectory", f"Step_{step_count}", "screenshot_bbox.png"))
            if documentation or ocr_description or bbox_description:
                with open(
                os.path.join(self.root_dir, "Trajectory", f"Step_{step_count}", "screenshot_description.json"), "w", encoding="utf-8") as writer:
                    nl_description = {
                        "documentation": documentation,
                        "ocr_description": ocr_description,
                        "bbox_description": bbox_description
                    }
                    json.dump(nl_description, writer, indent=2, ensure_ascii=False)
            if document:
                env_state.document.save(os.path.join(self.root_dir, "Trajectory", f"Step_{step_count}", "document.pkl"))
            if xml_content:
                with open(
                os.path.join(self.root_dir, "Trajectory", f"Step_{step_count}", "xml_content.json"), "w", encoding="utf-8") as writer:
                    json.dump(env_state.xml_content, writer, indent=2, ensure_ascii=False)

    def save_llm_inout(self, llm_query_id, messages, functions=None, function_call=None, model=None, stop=None, output_data=None,**other_args):
        with open(os.path.join(self.root_dir, "LLM_input_output_pair", f"{llm_query_id:05d}.json"),"w",encoding="utf-8") as writer:
            llm_inout_record = {
                "input": {
                    "messages": dump_common_things(messages),
                    "functions": dump_common_things(functions),
                    "function_call": dump_common_things(function_call),
                    "model": dump_common_things(model),
                    "stop": dump_common_things(stop),
                    "other_args": dump_common_things(other_args),
                },
                "output": dump_common_things(output_data),
                "llm_interface_id": llm_query_id,
            }
            json.dump(llm_inout_record, writer, indent=2, ensure_ascii=False)
        
# recorder = Recorder(CONFIG)
