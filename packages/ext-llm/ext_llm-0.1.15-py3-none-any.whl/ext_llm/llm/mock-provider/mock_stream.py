from ext_llm.llm.stream import Stream


class MockStream(Stream):
    def __init__(self, stream, preset_name, model_id, temperature, max_tokens):
        super().__init__()
        pass