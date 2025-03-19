from .llm.llm_client import LlmClient
from .context import ExtLlmContext
from ext_llm.extllm import ExtLlm

# This function initializes the ExtLlm object
# It takes in a string containing the yaml configuration
# It returns an ExtLlm object
def init(configs: str) -> ExtLlm:
    ext_llm_context = ExtLlmContext(configs)
    return ExtLlm(ext_llm_context)