from ext_llm import LlmClient


class MyLlmClient(LlmClient):
    def __init__(self, config: dict, preset_name: str):
        super().__init__()
        self.preset_name = preset_name
        self.config = config

    def generate_text(self, system_prompt: str, prompt: str, max_tokens=None, temperature=None):
        return "Hello, world!"