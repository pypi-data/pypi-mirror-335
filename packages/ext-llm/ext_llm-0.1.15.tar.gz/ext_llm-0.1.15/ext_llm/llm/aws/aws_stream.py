from ext_llm.llm.response import Response
from ext_llm.llm.stream import Stream
class AwsStream(Stream):

    counter = 0

    def __init__(self, stream, preset_name, model_id, temperature, max_tokens):
        super().__init__()
        self.stream = stream
        self.preset_name = preset_name
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stop_reason = None

    def __iter__(self):
        for event in self.stream:
            if self.counter != 0:
                self.counter += 1
                content = ""
                chunk_metadata = None
                if 'contentBlockDelta' in event:
                    content = event['contentBlockDelta']['delta']['text']
                if 'messageStart' in event or 'contentBlockStop' in event:
                    continue
                if 'messageStop' in event:
                    self.stop_reason = event['messageStop']['stopReason']
                if 'metadata' in event:
                    prompt_tokens = event['metadata']['usage']['inputTokens']
                    completion_tokens = event['metadata']['usage']['outputTokens']
                    total_tokens = prompt_tokens + completion_tokens
                    chunk_metadata = {
                        "preset_name": self.preset_name,
                        "model_id": self.model_id,
                        "max_tokens": self.max_tokens,
                        "temperature": self.temperature,
                        "finish_reason": self.stop_reason,
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens,
                        "chunk_type": "metadata"
                    }
                yield Response(content, chunk_metadata)
            else:
                self.counter += 1
                continue