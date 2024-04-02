from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_not_exception_type, wait_chain, wait_none
from VAgent.config import CONFIG
from VAgent.log import logger
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from anthropic import AuthenticationError, PermissionDeniedError, BadRequestError
RETRY_ERRORS = (AuthenticationError, PermissionDeniedError,
                BadRequestError, AssertionError)
from colorama import Fore, Style


# @retry(
#     retry=retry_if_not_exception_type(RETRY_ERRORS),
#     stop=stop_after_attempt(3),
#     wait=wait_chain(
#         *[wait_none() for _ in range(3)] + [wait_exponential(min=61, max=293)]
#     ),
#     reraise=True,
# )
def claude_chatcompletion_request(*, max_lenght_fallback=True, **kwargs):
    model_name = CONFIG.get_model_name(
        kwargs.pop("model", CONFIG.request.default_model)
    )
    logger.debug("Completion using: " + model_name)
    chatcompletion_kwargs = {
        "model": CONFIG.request.default_model,
        "max_tokens": CONFIG.request.claude.max_tokens,
        "temperature": CONFIG.request.claude.temperature
    }
    request_timeout = kwargs.pop("request_timeout", 60)
    chatcompletion_kwargs.update(kwargs)
    client = Anthropic(
        api_key=CONFIG.request.claude.api_key,
        timeout=request_timeout
    )
    new_messages = []
    system_prompt = ''
    for message in chatcompletion_kwargs['messages']:
        if message["role"] == "system":
            system_prompt = message["content"]
        else:
            new_messages.append(message)
    chatcompletion_kwargs["messages"] = new_messages
    chatcompletion_kwargs["system"] = system_prompt
    print(chatcompletion_kwargs.keys())
    try:
        completions = client.messages.create(**chatcompletion_kwargs)
        response = completions

    except BadRequestError as e:
        raise e
    return response


def claude_vision_chatcompletion_request(**kwargs):
    model_name = "claude-3-opus-20240229"
    logger.debug("Completion using: " + model_name)
    chatcompletion_kwargs = {
        "model": CONFIG.request.default_model,
        "max_tokens": CONFIG.request.claude.max_tokens,
        "temperature": CONFIG.request.claude.temperature
    }
    
    chatcompletion_kwargs.update(kwargs)
    client = Anthropic(
        api_key=CONFIG.request.claude.api_key,
        timeout=CONFIG.request.claude.request_timeout
    )
    new_messages = []
    system_prompt = ''
    for message in chatcompletion_kwargs['messages']:
        if message["role"] == "system":
            system_prompt = message["content"]
        else:
            new_messages.append(message)
    chatcompletion_kwargs["messages"] = new_messages
    chatcompletion_kwargs["system"] = system_prompt
    print(chatcompletion_kwargs.keys())
    try:
        completions = client.messages.create(**chatcompletion_kwargs)
        response = completions

    except BadRequestError as e:
        raise e
    return response

# messages = [
#             {
#                     "role": "user",
#                     "content": f"{HUMAN_PROMPT} how does a court case get to the Supreme Court? {AI_PROMPT}",
#             }
# ]
# response = claude_chatcompletion_request(messages=messages, max_tokens=1000)
# print(response)