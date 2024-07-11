from openai import AuthenticationError, PermissionDeniedError, BadRequestError, OpenAI, AzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_not_exception_type, wait_chain, wait_none
from openai.types.chat import ChatCompletion
from VAgent.config import CONFIG
from VAgent.log import logger
RETRY_ERRORS = (AuthenticationError, PermissionDeniedError,
                BadRequestError, AssertionError)
from colorama import Fore, Style

@retry(
    retry=retry_if_not_exception_type(RETRY_ERRORS),
    stop=stop_after_attempt(3),
    wait=wait_chain(
        *[wait_none() for _ in range(3)] + [wait_exponential(min=61, max=293)]
    ),
    reraise=True,
)
def openai_chatcompletion_request(*, max_lenght_fallback=True, **kwargs):
    """Handle operation of OpenAI v1.x.x chat completion.

    This function operates OpenAI v1.x.x chat completion with provided
    arguments. It gets the model name, applies a JSON web token, if the
    response indicates the context length has been exceeded, it attempts
    to get a higher-capacity language model if it exists in the configuration
    and reattempts the operation. Otherwise, it will raise an error message.

    Args:
        max_lenght_fallback: If True, fallback to a longer model if the context length is exceeded.
        **kwargs: Variable length argument list including (model:str, etc.).

    Returns:
        response (dict): A dictionary containing the response from the Chat API.
        The structure of the dictionary is based on the API response format.

    Raises:
        BadRequestError: If any error occurs during chat completion operation or
        context length limit exceeded and no fallback models available.
    """

    model_name = CONFIG.get_model_name(
        kwargs.pop("model", CONFIG.request.default_model)
    )
    logger.debug("Completion using: " + model_name)
    chatcompletion_kwargs = {"model": CONFIG.request.default_model}
    request_timeout = kwargs.pop("request_timeout", 60)
    if "azure_endpoint" in chatcompletion_kwargs:
        azure_endpoint = chatcompletion_kwargs.pop("azure_endpoint", None)
        api_version = chatcompletion_kwargs.pop("api_version", None)
        api_key = chatcompletion_kwargs.pop("api_key", None)
        organization = chatcompletion_kwargs.pop("organization", None)
        chatcompletion_kwargs.update(kwargs)
        client = AzureOpenAI(
            api_key=api_key,
            organization=organization,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
            timeout=request_timeout
        )
    else:
        if "base_url" in chatcompletion_kwargs:
            base_url = chatcompletion_kwargs.pop("base_url", None)
        else:
            base_url = chatcompletion_kwargs.pop("api_base", None)
        api_key = chatcompletion_kwargs.pop("api_key", None)
        organization = chatcompletion_kwargs.pop("organization", None)
        chatcompletion_kwargs.update(kwargs)
        client = OpenAI(
            api_key=CONFIG.request.gpt.api_key, 
            base_url=CONFIG.request.gpt.base_url,
            timeout=request_timeout
        )

    # chatcompletion_kwargs["model"] = "gpt-4-turbo-preview"
    try:
        completions: ChatCompletion = client.chat.completions.create(**chatcompletion_kwargs)
        response = completions.model_dump()
        # print(response)
        if response["choices"][0]["finish_reason"] == "length":
            raise BadRequestError(
                message="maximum context length exceeded", response=None, body=None
            )

    except BadRequestError as e:
        if "maximum context length" in e.message and max_lenght_fallback:
            if model_name == "gpt-4":
                if "gpt-4-32k" in CONFIG.api_keys:
                    model_name = "gpt-4-32k"
                elif "gpt-3.5-turbo-16k" in CONFIG.api_keys:
                    model_name = "gpt-3.5-turbo-16k"
                else:
                    raise e
            else:
                raise e

            logger.debug(
                f"Context length exceeded. Falling back to {model_name}",
                Fore.YELLOW
            )
            chatcompletion_kwargs["model"] = model_name
            return openai_chatcompletion_request(max_lenght_fallback=False, **chatcompletion_kwargs)

        else:
            print(e)
            raise e

    return response


@retry(
    retry=retry_if_not_exception_type(RETRY_ERRORS),
    stop=stop_after_attempt(CONFIG.max_retry_times + 3),
    wait=wait_chain(
        *[wait_none() for _ in range(3)] + [wait_exponential(min=61, max=293)]
    ),
    reraise=True,
)
def ada_embedding_request(text: str):
    embedding_client = OpenAI(
        api_key = CONFIG.request.ada_embedding.api_key,
        base_url= CONFIG.request.ada_embedding.base_url
    )
    embedding_model = CONFIG.request.ada_embedding.embedding_model
    logger.debug("Embedding completion using: " + embedding_model)
    try:
        response = embedding_client.embeddings.create(
            input = [text],
            model=embedding_model
        )
        embedding = response.data[0].embedding
    except BadRequestError as e:
        logger.debug(
            f"Error when generating embedding: {e}",
            Fore.YELLOW
        )
    return embedding

@retry(
    retry=retry_if_not_exception_type(RETRY_ERRORS),
    stop=stop_after_attempt(CONFIG.max_retry_times + 3),
    wait=wait_chain(
        *[wait_none() for _ in range(3)] + [wait_exponential(min=61, max=293)]
    ),
    reraise=True,
)
def openai_vision_chatcompletion_request(messages: list, base64_capture_bbox):
    # print(CONFIG.request.gpt4v.api_key)
    client = OpenAI(
        api_key=CONFIG.request.gpt4v.api_key,
        base_url=CONFIG.request.gpt4v.base_url
    )

    json_content = []
    
    if isinstance(base64_capture_bbox, list):
        for base64 in base64_capture_bbox:
            image_content = {
                "type": "image_url",
                "image_url":{
                    "url": f"data:image/jpeg;base64,{base64}"
                }
            }
            json_content.append(image_content)
    else:
        image_content = {
            "type": "image_url",
            "image_url":{
                "url": f"data:image/jpeg;base64,{base64_capture_bbox}"
            }
        }
        json_content.append(image_content)
    
    messages[1]["content"].append(image_content)
    
    # messages = messages.append({
    #     "role": "user",
    #     "content": json_content,
    # })

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="gpt-4o",
        max_tokens=CONFIG.request.gpt4v.max_tokens,
        temperature=CONFIG.request.gpt4v.temperature,
    )
    res = ""
    try:
        res = chat_completion.choices[0].message.content
    except Exception as e:
        # print(res)
        logger.debug(
            f"Error when requesting gpt4-v: {e}",
            Fore.YELLOW
        )
    return res