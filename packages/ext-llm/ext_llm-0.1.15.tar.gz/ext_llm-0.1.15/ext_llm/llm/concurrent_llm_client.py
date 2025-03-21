import concurrent.futures
from concurrent.futures import Future

from ext_llm import LlmClient
from ext_llm.llm.response import Response
from ext_llm.llm.stream import Stream


class ConcurrentLlmClient:

    def __init__(self, llm: LlmClient):
        super().__init__()
        self.llm = llm
        self.executor = concurrent.futures.ThreadPoolExecutor()

    def generate_text(self, system_prompt: str, prompt: str, max_tokens=None, temperature=None) -> Future [Response | Stream]:
        future = self.executor.submit(self.llm.generate_text, system_prompt, prompt, max_tokens, temperature)
        return future

    def get_config(self):
        return self.llm.get_config()