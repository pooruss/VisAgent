import os
import re
import abc
import nbformat
from nbclient import NotebookClient
from typing import List, Tuple, Dict, Any
from PIL import Image
from nbclient.exceptions import CellExecutionError,DeadKernelError
from VAgent.config import CONFIG
from VAgent.environment.code_action.action_schema import ACTION_SCHEMA
from VAgent.utils.ocr import easyocr_get_text, pytesseract_get_text, surya_get_text
from VAgent.models import EnvState, Action, ActionStatusCode
from VAgent.environment.base import BaseEnvironment

class CodeEnvironment(BaseEnvironment):
    """Python Notebook Environment. Provide a notebook interface to run python code."""
    def __init__(self, config: CONFIG):
        super().__init__(config)
        self.config = config
        self.state = EnvState()
        self.action_schema = dict()

        self.work_directory = self.config.code_env.work_directory
        self.data_path = self.config.code_env.data_path
        if not os.path.exists(self.data_path):
            raise RuntimeError
        self.data = open(self.data_path, "r")
        self.data = self.data.read()[:500]
        print(self.data)

        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory,mode=0o777)

        # make a new notebook
        self.nb = nbformat.v4.new_notebook(
            metadata = {'kernelspec': {'name': 'python', 'language': 'python', 'display_name': 'python'}})
        self.nbc = NotebookClient(self.nb,timeout=self.config.code_env.timeout)
        self.action_schema = ACTION_SCHEMA

    def _running(self):
        if self.nbc.kc is not None:
            return self.nbc.kc.is_alive()
        return False
    
    def _reset(self):
        if self._running():
            self.nbc.cleanup_kernel()
        self.nbc.create_kernel_manager()
        self.nbc.start_new_kernel(cwd=self.work_directory)
        self.nbc.start_new_kernel_client()

    @staticmethod
    def _fix_escape(problematic_code: str) -> str:
        for str_sign in ['"', "'", '"""', "'''"]:

            pattern = rf'{str_sign}(.*?){str_sign}'
            in_line_strs = re.findall(pattern, problematic_code, re.DOTALL)
            replaced_in_line_strs = []
            for in_line_str in in_line_strs:
                replaced_in_line_strs.append(in_line_str.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t'))
            for original_str, modified_str in zip(in_line_strs, replaced_in_line_strs):
                fixed_code = problematic_code.replace(f'{str_sign}' + original_str + f'{str_sign}',
                                                            f'{str_sign}' + modified_str + f'{str_sign}')

        return fixed_code
    
    def print_notebook(self)->str:
        """print all notebook cells' content and output.
        
        :return string: all notebook cells description.
        """
        ret = ''
        for i,cell in enumerate(self.nb.cells):
            ret += f'= Cell {i} =\n'
            if cell['cell_type'] == 'code':
                ret += f'{cell["source"]}\n'
                if len(cell['outputs']) != 0:
                    ret += f'= Output {i} =\n'
                    ret += f'{self._format_outputs(cell["outputs"])}\n'
        return ret
    def _format_outputs(self,outputs,cell_index=None,reraise=False,return_binary=False):
        ret = None
        if len(outputs) == 0:
            ret = '' if cell_index is None else f'cell_index: {cell_index}'
        elif len(outputs) == 1:
            if cell_index is not None:
                ret = {
                    'type':'composite',
                    'data':[
                        f'cell_index: {cell_index}',
                        self._format_output(outputs[0],cell_index,reraise,return_binary)
                    ]
                }
            else:
                ret = self._format_output(outputs[0],cell_index,reraise,return_binary)
        else:
            ret = {
                'type':'composite',
                'data':[
                    self._format_output(output,cell_index,reraise,return_binary) for output in outputs
                ]
            }
            if cell_index is not None:
                ret['data'].insert(0,f'cell_index: {cell_index}')
        return ret
        
    def _format_output(self,output,cell_index=None,reraise=False,return_binary=False):
        def format_single_data(data,data_type:str):
            if data_type.startswith('image/'):
                return {
                    'type': 'binary',
                    'media_type':data_type,
                    'data': data if return_binary else '`Wrapped`'
                }
            elif data_type.startswith('text/'):
                return ''.join(data)
            elif data_type.startswith('application/'):
                return data
            return data
            
        ret = None
        match output['output_type']:
            case 'execute_result' | 'display_data':
                keys = list(output['data'].keys())
                if 'text/html' in keys and 'text/plain' in keys:
                    keys.remove('text/html') # remove html
                if len(keys) == 1:
                    ret = format_single_data(output['data'][keys[0]],keys[0])
                elif len(keys) > 1:
                    ret = {
                        'type': 'composite',
                        'data':[]
                    }
                    for k in keys:
                        ret['data'].append(format_single_data(output['data'][k],k))
                    
            case 'error':
                if reraise:
                    raise RuntimeWarning(f'cell_index: {cell_index}\n'+'\n'.join(output['traceback']))
                else:
                    return '\n'.join(output['traceback'])
            case 'stream':
                ret = output['text']
            case _:
                ret = output
        return ret

    def screenshot(self,) -> Image.Image:
        pass
    
    def step(self, action: Action) -> Tuple[ActionStatusCode, str]:
        """Execute code cell."""
        if action.name == "execute_shell":
            code = action.arguments["code"]
            if "cell_index" in action.arguments:
                cell_index = action.arguments["cell_index"]
            else:
                cell_index = None
            if "reset" in action.arguments:
                reset = action.arguments["reset"]
            else:
                reset = False
            
            output_path = action.arguments["output_path"]

            # code = self._fix_escape(code)
            if reset or not self._running():
                self._reset()
            if cell_index is None or cell_index == len(self.nb.cells) or len(self.nb.cells) == 0:
                self.nb.cells.append(nbformat.v4.new_code_cell(code))
                cell_index = len(self.nb.cells) - 1
            else:
                self.nb.cells[cell_index] = nbformat.v4.new_code_cell(code)

            try:
                self.nbc.execute_cell(self.nb.cells[-1], len(self.nb.cells) - 1)
            except CellExecutionError as e:
                return ActionStatusCode.FAILED, str(e)[-500:]
            except DeadKernelError as e:
                return ActionStatusCode.FAILED, str(e)[-500:]

            nbformat.write(self.nb, os.path.join(self.work_directory, self.config.code_env.save_name))

            return ActionStatusCode.SUCCESS, output_path
        
        elif action.name == "feedback":
            feedback = action.arguments["text"]
            return ActionStatusCode.SUCCESS, feedback

        else:
            raise RuntimeError(f"Unrecognized action: {action.name}")


if __name__ == '__main__':
    code_env = CodeEnvironment(CONFIG)
    code_str = """import pandas as pd\nimport matplotlib.pyplot as plt\n\n# Data loading\ndata = pd.read_csv('data.csv')\n\n# Data visualization\nplt.figure(figsize=(10, 6))\nplt.plot(data['name'], data['age'], marker='o') # Add markers\nplt.xlabel('Name')\nplt.ylabel('Age')\nplt.title('Age by Name') # Updated title\nplt.xticks(rotation=45) # Rotate x-axis labels\nplt.grid(axis='y') # Add grid to y-axis\nplt.tight_layout() # Adjust layout to prevent clipping of tick-labels\n\n# Save the figure and show plot\nplt.savefig('improved_linear_plot.png')\nplt.show()\nplt.close()\n"""
    action = Action(name="execute_shell", arguments={"code": code_str, "output_path": "./1.jpg"})
    ret = code_env.step(action=action)
    print(ret)
    
