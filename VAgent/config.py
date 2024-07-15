"""Configuration module for VAgent.

This module should be loaded after the environment variables are set,
and before any other VAgent modules are loaded.

The module initializes the global configuration for VAgent.
"""


import os
import yaml
import time
import uuid
from copy import deepcopy
from typing import Literal, Optional
from pydantic import BaseModel, Field

ARGS = {}


class VAgentConfig(BaseModel):
    """
    VAgent configuration class.
    """
    max_retry_times: int = 3
    workspace_root: str = "./running_workspace"
    api_keys: dict[str, list[dict]] = {
        "gpt-3.5-turbo-16k": [{
            "api_key": "sk-xxx",
            "model": "gpt-3.5-turbo-16k",
        }],
        "gpt-4": [{
            "api_key": "sk-xxx",
            "model": "gpt-4",
        }],
        "gpt-4-vision-preview": [{
            "api_key": "sk-xxx",
            "model": "gpt-4-vision-preview",
        }],
    }

    class RequestConfig(BaseModel):
        lib: Literal["openai", "VAgent"] = 'openai'
        format: Literal[
            "chat",
            "tool_call",
            "function_call",
            "objlink"] = "tool_call"
        json_mode: bool = False
        schema_validation: bool = True

        default_model: str = "gpt-4"
        
        default_timeout: int = 600

        class GPTConfig(BaseModel):
            api_key: str = ""
            base_url: str = ""
            max_tokens: int = 1000
            temperature: float = 0.8

        gpt: GPTConfig = GPTConfig()

        class AdaEmbeddingConfig(BaseModel):
            embedding_model: str = "text-embedding-ada-002"
            api_key: str = ""
            base_url: str = ""
            
        ada_embedding: AdaEmbeddingConfig = AdaEmbeddingConfig()

        class GPT4VConfig(BaseModel):
            api_key: str = ""
            base_url: str = ""
            max_tokens: int = 1000
            temperature: float = 0.8
        
        gpt4v: GPT4VConfig = GPT4VConfig()

    request: RequestConfig = RequestConfig()

    class LoggerConfig(BaseModel):
        record_in_database: bool = True
        logger: Optional[str] = None
        level: Literal["DEBUG", "INFO", "WARNING",
                       "ERROR", "CRITICAL"] = "INFO"

        reload: bool = False
        # only support file now
        reload_source: Literal["database", "file"] = "file"
        reload_id: Optional[str] = None

        record_in_files: bool = True
        record_dir: str = Field(
            default_factory=lambda: os.path.relpath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "running_records",
                    str(time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(
                        int(round(time.time()))))) + '_' + uuid.uuid4().hex[:8]
                ))
        )

    logger: LoggerConfig = LoggerConfig()

    class RecorderConfig(BaseModel):
        record_dir: str = "running_records"

    recorder: RecorderConfig = RecorderConfig()

    class EngineConfig(BaseModel):
        max_step: int = 5
        max_self_reflexion_step: int = 3
        code_model: str = "gpt-4o"
        feedback_model: str = "gpt-4o"
        code_temperature: float = 0.8
        feedback_temperature: float = 0.8
        enable_feedback: bool = True
        json_mode: bool = True

    engine: EngineConfig = EngineConfig()

    class CodeEnvConfig(BaseModel):
        work_directory: str = "code_workspace"
        max_entry_nums_for_level: int = 20
        timeout: int = 300
        save_name: str = "python_notebook.ipynb"
        data_path: str = "/Users/user/Downloads/git_clone/VisAgent/assets/vis_data/McDonald_financial_statements/McDonalds_Financial_Statements.csv"
    
    code_env: CodeEnvConfig = CodeEnvConfig()

    class OCRConfig(BaseModel):
        method: Literal["easyocr", "pytesseract", "surya"] = 'easyocr'

    ocr: OCRConfig = OCRConfig()

    class DocumentConfig(BaseModel):
        document_path: str = "assets/documents"

    document: DocumentConfig = DocumentConfig()

    def to_dict(self):
        return self.model_dump(exclude=['api_keys'])

    def reload(self, config_file=None):
        if config_file is None:
            config_file = os.getenv('CONFIG_FILE', "assets/config.yml")
        print('# Config File\n'+str(config_file))
        new_config_dict = yaml.load(
            open(config_file, 'r'), Loader=yaml.FullLoader)
        new_config = VAgentConfig(**new_config_dict)
        self.__init__(**new_config.model_dump())

        if len(ARGS) > 0:
            print('# Args\n'+str(ARGS))
            self.set_value_with_args(ARGS)

    def set_value_with_args(self, args=ARGS):
        if "model" in args:
            self.request.default_model = args['model']
        if "max_retry_times" in args:
            self.max_retry_times = args['max_retry_times']

    def get_model_name(self, model_name: str = None) -> Literal[
        "gpt-4-turbo",
        "gpt-4-vision",
        "gpt-4",
        "gpt-4-32k",
        "gpt-3.5-turbo-16k",
        "VAgentllm",]:
        """
        Get the normalized model name for a given input model name.

        Args:
            model_name (str, optional): Input model name. Default is None.

        Returns:
            str: Normalized model name.

        Raises:
            Exception: If the model name is not recognized.
        """

        if model_name is None:
            model_name = self.request.default_model

        normalized_model_name = ''
        match model_name.lower():
            case 'gpt-4-turbo':
                normalized_model_name = 'gpt-4-turbo'
            case 'gpt-4-vision':
                normalized_model_name = 'gpt-4-vision'
            case 'gpt-4v':
                normalized_model_name = 'gpt-4-vision'

            case 'gpt-4':
                normalized_model_name = 'gpt-4'
            case 'gpt-4-32k':
                normalized_model_name = 'gpt-4-32k'
            case 'gpt-3.5-turbo-16k':
                normalized_model_name = 'gpt-3.5-turbo-16k'

            case 'gpt4':
                normalized_model_name = 'gpt-4'
            case 'gpt4-32':
                normalized_model_name = 'gpt-4-32k'
            case 'gpt-35-16k':
                normalized_model_name = 'gpt-3.5-turbo-16k'
            case 'VAgentllm':
                normalized_model_name = 'VAgentllm'
            case _:
                normalized_model_name = model_name

        return normalized_model_name

    def get_apiconfig_by_model(self, model_name: str) -> dict:
        """
        Get API configuration for a model by its name.
        Return default model if the given model name is not found.

        The function first normalizes the name, then fetches the API keys for this model
        from the CONFIG and rotates the keys.

        Args:
            model_name (str): Name of the model.

        Returns:
            dict: Dictionary containing the fetched API configuration.
        """
        normalized_model_name = self.get_model_name(model_name)
        if normalized_model_name not in self.api_keys:
            normalized_model_name = self.get_model_name(self.request.default_model)
        apiconfig = deepcopy(self.api_keys[normalized_model_name][0])
        self.api_keys[normalized_model_name].append(
            self.api_keys[normalized_model_name].pop(0))
        return apiconfig


CONFIG = VAgentConfig()
CONFIG.reload()