from ext_llm import ExtLlmContext, LlmClient
from ext_llm.llm.concurrent_llm_client import ConcurrentLlmClient
from ext_llm.llm.logging_llm_proxy import LlmClientLoggingProxy
from ext_llm.scheduler import RequestScheduler
from ext_llm.scheduler_statistic_repository import SchedulerStatisticRepository


class ExtLlm:

    provider_dict = {
        "groq" : ["ext_llm.llm.groq.groq_llm_client", "GroqLlmClient"],
        "aws" : ["ext_llm.llm.aws.aws_llm_client", "AwsLlmClient"]
    }

    def __init__(self, context: ExtLlmContext):
        self.context = context

    def list_available_presets(self):
        return self.context.get_configs()["presets"]

    def get_client(self, preset_name: str) -> LlmClient:
        class_name = None
        module_name = None
        if preset_name not in self.context.get_configs()["presets"]:
            raise Exception("Preset not found")

        if "provider" in self.context.get_configs()["presets"][preset_name]:
            class_name = self.provider_dict[self.context.get_configs()["presets"][preset_name]["provider"]][1]
            module_name = self.provider_dict[self.context.get_configs()["presets"][preset_name]["provider"]][0]
        else:
            class_name = self.context.get_configs()["presets"][preset_name]["class_name"]
            module_name=self.context.get_configs()["presets"][preset_name]["module_name"]

        try:
            module = __import__(module_name, fromlist=[class_name])
        except KeyError:
            module = __import__(module_name, fromlist=[class_name])
        if hasattr(module, class_name):
            return LlmClientLoggingProxy(getattr(module, class_name)(self.context.get_configs()["presets"][preset_name], preset_name), self.context.get_configs()['db_path'], bool(self.context.get_configs()['logging']))
        else:
            raise Exception("Class not found")

    def get_concurrent_client(self, preset_name: str) -> ConcurrentLlmClient:
        return ConcurrentLlmClient(self.get_client(preset_name))

    def get_scheduler(self,
                      client: LlmClient,
                      max_workers: int = 4,
                      max_retries: int = 5,
                      retry_delay: int = 4.0,
                      initial_rate_limit: int = 60,
                      min_rate_limit: int = 5,
                      max_rate_limit: int = 120,
                      ):
        scheduler_statistic_repository = SchedulerStatisticRepository(db_path=self.context.get_configs()["db_path"])
        return RequestScheduler(client, scheduler_statistic_repository, max_workers, max_retries, retry_delay, initial_rate_limit, min_rate_limit, max_rate_limit)
