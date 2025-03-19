from ext_llm.llm.response import Response
from ext_llm.llm.stream import Stream


class LlmClient:
    def __init__(self):
        pass

    def generate_text(self, system_prompt : str, prompt : str, max_tokens=None, temperature=None) -> Response | Stream :
        raise NotImplementedError("This method should be implemented by subclasses.")

    def get_config(self):
        raise NotImplementedError("This method should be implemented by subclasses.")

