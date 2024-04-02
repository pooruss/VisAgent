from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from anthropic import AuthenticationError, PermissionDeniedError, BadRequestError
RETRY_ERRORS = (AuthenticationError, PermissionDeniedError,
                BadRequestError, AssertionError)
from colorama import Fore, Style
anthropic = Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="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",
)

completion = anthropic.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=300,
    messages=[
        {
                "role": "user",
                "content": f"{HUMAN_PROMPT} how does a court case get to the Supreme Court? {AI_PROMPT}",
        }
    ]
)
print(completion.content[0].text)