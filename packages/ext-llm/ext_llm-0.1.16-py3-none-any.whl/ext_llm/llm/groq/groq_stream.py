from ext_llm.llm.response import Response
from ext_llm.llm.stream import Stream

class GroqStream(Stream):

    def __init__(self, stream, preset_name, model_id, temperature, max_tokens):
        super().__init__()
        self.stream = stream
        self.preset_name = preset_name
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens

    def __iter__(self):
        for event in self.stream:
            # Create metadata for each chunk in the stream
            stop_reason = event.choices[0].finish_reason

            completion_tokens = 0
            prompt_tokens = 0
            total_tokens = 0
            chunk_metadata = None
            if event.x_groq is not None and event.x_groq.usage is not None:
                if event.x_groq.usage.completion_tokens is not None:
                    completion_tokens = event.x_groq.usage.completion_tokens
                else:
                    completion_tokens = 0
                if event.x_groq.usage.prompt_tokens is not None:
                    prompt_tokens = event.x_groq.usage.prompt_tokens
                else:
                    prompt_tokens = 0
                total_tokens = completion_tokens + prompt_tokens
                chunk_metadata = {
                    "preset_name": self.preset_name,
                    "model_id": self.model_id,
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "finish_reason": stop_reason,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "chunk_type": "metadata"
                }
            # Extract text content if present
            content = event.choices[0].delta.content
            if content is None:
                content = ""

            yield Response(content, chunk_metadata)