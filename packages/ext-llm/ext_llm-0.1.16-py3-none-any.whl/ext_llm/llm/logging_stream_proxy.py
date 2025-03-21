from ext_llm.llm.response import Response
from ext_llm.llm.stream import Stream
import time


class LoggingStreamProxy(Stream):
    def __init__(self, stream, repository, system_prompt, user_prompt):
        super().__init__()
        self.stream = stream
        self.repository = repository
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.start_time = time.time()
        self.content_buffer = []
        self.metadata = None

    def __iter__(self):
        for resp in self.stream:
            # Collect content and metadata
            self.content_buffer.append(resp.content)
            if resp.metadata and self.metadata is None:
                self.metadata = resp.metadata

            # Pass through the response to the caller
            yield resp

        # After the stream completes, log the consolidated response
        self._log_complete_response()

    def _log_complete_response(self):
        end_time = time.time()
        #last element of the buffer has None value
        full_content = "".join(self.content_buffer[:-1])

        # Create complete metadata
        complete_metadata = self.metadata or {}
        complete_metadata['latency'] = end_time - self.start_time

        # Log the complete response
        complete_response = Response(full_content, complete_metadata)
        self.repository.save(complete_response, self.system_prompt, self.user_prompt)