class Response:
    def __init__(self, content, metadata):
        self.content = content
        self.metadata = metadata

    def __str__(self) -> str:
        return self.content.__str__()