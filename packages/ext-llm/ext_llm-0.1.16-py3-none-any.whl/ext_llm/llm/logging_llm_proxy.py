from concurrent.futures import Future
import time

from ext_llm import LlmClient
from ext_llm.llm.llm_client import Response, Stream
from ext_llm.llm.logging_stream_proxy import LoggingStreamProxy
from ext_llm.llm.response_repository import ResponseRepository


class LlmClientLoggingProxy(LlmClient):
    def __init__(self, llm, db_path, logging):
        super().__init__()
        self.llm = llm
        self.db_path=db_path
        self.logging=logging
        self.repository = ResponseRepository(db_path)

    def log(self, result, system_prompt: str, prompt: str, max_tokens=None, temperature=None):
        self.repository.save(result, system_prompt, prompt)

    def generate_text(self, system_prompt: str, prompt: str, max_tokens=None, temperature=None) -> Response | Stream:
        start_time = time.time()
        result = self.llm.generate_text(system_prompt, prompt, max_tokens, temperature)

        if isinstance(result, Stream):
            if self.logging:
                # Wrap the stream in a logging proxy
                return LoggingStreamProxy(result, self.repository, system_prompt, prompt)
            return result
        else:
            # Handle regular Response objects as before
            end_time = time.time()
            latency = end_time - start_time
            result.metadata['latency'] = latency

            if self.logging:
                self.log(result, system_prompt, prompt, max_tokens, temperature)

            return result

    def get_config(self):
        return self.llm.get_config()