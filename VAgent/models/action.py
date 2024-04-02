import uuid
from pydantic import BaseModel, Field
from typing import Any, Union
from pydantic import Field
from VAgent.config import CONFIG
from VAgent.models.enums import ActionStatusCode, ActionType


class Action(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    type: ActionType = ActionType.Default
    thought: str = ""
    name: str = ""
    arguments: Union[str, dict] = {}
    status: ActionStatusCode = ActionStatusCode.PENDING
    observation: Any = ""
    
    def to_json(self) -> dict:
        d = self.model_dump(mode="json")
        return d

    def __setattr__(self, name, value):
        if name == 'output':
            # 对 name 字段执行某些操作
            value = self.unwrap_output(value)  # 例如，转换为大写
        super().__setattr__(name, value)

    def set_tool(self, action_name: str, action_args: dict):
        self.name = action_name
        self.arguments = action_args

    def _wrap_arguments(self, black_list: list[str] = []):
        """
        Wrap arguments in the form of strings.

        Args:
            black_list (list): A list of forbidden or restricted words or keys in the args dictionary.

        Returns:
            str: A string that summarizes the function arguments.
        """
        SINGLE_ACTION_MAX_LENGTH = CONFIG.execution.summary.single_step_max_tokens
        ret = ''
        args_len = 0

        arguments = sorted(self.arguments.items(),
                           key=lambda x: len(str(x[1])),)
        from VAgent.utils.token_count import clip_text

        for k, v in arguments:
            if k in black_list:
                v = '`wrapped`'
            v_str, v_len = clip_text(
                text=str(v),
                max_tokens=SINGLE_ACTION_MAX_LENGTH-args_len,
                clip_end=True)
            if v_len < SINGLE_ACTION_MAX_LENGTH-args_len:
                ret += f'{k}="{v_str}",' if isinstance(
                    v, str) else f'{k}={v_str},'
                args_len += v_len
            else:
                ret += f'{k}="{v_str}...",' if isinstance(
                    v, str) else f'{k}={v_str}...,'
                args_len += SINGLE_ACTION_MAX_LENGTH-args_len

        return ret[:-1]

    def to_str(self, return_output: bool = True, black_list: list[str] = []):
        if "filesystem" in self.name.lower():
            black_list.extend(['content', 'new_content'])

        ret = [
            f'[Tool Call] {self.name}({self._wrap_arguments(black_list)})',
            f'[Status] {self.status.name}'
        ]
        if return_output:
            ret.append(f'[Output] {self.output}')
        from VAgent.utils.token_count import clip_text
        return clip_text('\n'.join(ret), max_tokens=CONFIG.execution.summary.single_step_max_tokens, clip_end=True)[0]

    def __str__(self):
        return self.to_str()