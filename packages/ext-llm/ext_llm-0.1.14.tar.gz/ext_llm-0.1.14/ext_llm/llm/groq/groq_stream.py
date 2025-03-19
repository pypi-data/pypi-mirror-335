from ext_llm.llm.response import Response
from ext_llm.llm.stream import Stream


class GroqStream(Stream):

    def __init__(self, stream):
        super().__init__()
        self.stream = stream

    def __iter__(self):
        for event in self.stream:
            yield Response(event, None)