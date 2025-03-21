import yaml

class ExtLlmContext:
    config_map = {} # type: dict
    def __init__(self, content: str):
        #read yaml file with nested properties
        self.config_map = yaml.safe_load(content)

    def get_configs(self) -> dict:
        return self.config_map["config"]

    def get_config(self, key:str):
        return self.config_map["config"][key]