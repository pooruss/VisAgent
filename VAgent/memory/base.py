from dataclasses import dataclass

@dataclass
class BaseMemory:

    def __init__(self):
        self.steps = dict()

    def insert(self, step_count, **kwargs):
        if step_count not in self.steps:
            self.steps[step_count] = {}
        if "env_state" in kwargs:
            if kwargs["env_state"].documentation != "":
                self.steps[step_count]["env_state_nl_description"] = kwargs["env_state"].documentation
            elif kwargs["env_state"].bbox_description != "":
                self.steps[step_count]["env_state_nl_description"] = kwargs["env_state"].bbox_description
            elif kwargs["env_state"].ocr_description != "":
                self.steps[step_count]["env_state_nl_description"] = kwargs["env_state"].ocr_description
            else:
                self.steps[step_count]["env_state_nl_description"] = ""
        if "action" in kwargs:
            self.steps[step_count]["action"] = kwargs["action"].to_json()
        if "action_status" in kwargs:
            self.steps[step_count]["action_status"] = kwargs["action_status"]
        if "observation" in kwargs:
            self.steps[step_count]["observation"] = kwargs["observation"]

    def to_json(self):
        pass

    def to_str(self):
        str_message = ""
        for step_idnex, step_memory in self.steps.items():
            str_message += f"\n[Step {step_idnex}]:\n"
            if "action" in step_memory:
                str_message += f'Action: {step_memory["action"]}\n'
            if "action_status" in step_memory:
                str_message += f'Action Status: {step_memory["action_status"]}\n'
            if "observation" in step_memory:
                str_message += f'Observation: {step_memory["observation"]}\n'
            if "env_state" in step_memory:
                str_message += f'Environment State: {step_memory["env_state_nl_description"]}\n'

        return str_message
    
    def save(self, save_path):
        pass

if __name__ == '__main__':
    pass
    
