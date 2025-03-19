from ext_llm.llm.response import Response
from ext_llm.llm.stream import Stream
class AwsStream(Stream):

    def __init__(self, stream):
        super().__init__()
        self.stream = stream

    def __iter__(self):
        for event in self.stream:
            # Create metadata for each chunk in the stream
            chunk_metadata = None
            if 'usage' in event:
                chunk_metadata = {
                    "prompt_tokens": event['usage'].get('inputTokenCount', 0),
                    "completion_tokens": event['usage'].get('outputTokenCount', 0),
                    "chunk_type": "metadata"
                }

            # Extract text content if present
            content = ""
            if 'delta' in event and 'content' in event['delta'] and len(event['delta']['content']) > 0:
                content = event['delta']['content'][0]['text']

            yield Response(content, chunk_metadata)