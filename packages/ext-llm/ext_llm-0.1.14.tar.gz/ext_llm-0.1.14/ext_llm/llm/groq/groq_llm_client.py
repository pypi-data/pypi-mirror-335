import os
from ext_llm import LlmClient
import groq
from ext_llm.llm.groq.groq_stream import GroqStream
from ext_llm.llm.response import Response
from ext_llm.llm.stream import Stream


class GroqLlmClient(LlmClient):

    def __init__(self, config: dict, preset_name: str):
        super().__init__()
        self.config = config
        self.preset_name = preset_name
        groq_api_key_env_var_name = config['groq_api_key_variable_name']
        groq_api_key = os.getenv(groq_api_key_env_var_name)
        if groq_api_key is None:
            raise ValueError(f"Environment variable {groq_api_key_env_var_name} not set")
        self.__groq_client = groq.Client(api_key=groq_api_key)

    def __build_metadata(self, chat_completion, max_tokens, temperature):
        preset_name = self.preset_name
        model_id = self.config['model_id']
        max_tokens = max_tokens
        temperature = temperature
        finish_reason = chat_completion.choices[0].finish_reason
        prompt_tokens = chat_completion.usage.prompt_tokens
        completion_tokens = chat_completion.usage.completion_tokens
        total_tokens = prompt_tokens + completion_tokens
        #print(chat_completion)
        return {
            "preset_name": preset_name,
            "model_id": model_id,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "finish_reason": finish_reason,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }

    def __invoke_model(self, system_prompt, prompt, max_tokens: int, temperature: float, top_p=0.9):
        is_stream = self.config['invocation_method'] == 'converse_stream'
        chat_completion = self.__groq_client.chat.completions.create(
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model = self.config['model_id'],
            max_completion_tokens = max_tokens,
            temperature = temperature,
            top_p = top_p,
            stop=None,
            stream=is_stream
        )
        if is_stream:
            return GroqStream(chat_completion)
        else:
            #print(chat_completion)
            return Response(chat_completion.choices[0].message.content, self.__build_metadata(chat_completion, max_tokens, temperature))

    def generate_text(self, system_prompt : str, prompt : str, max_tokens=None, temperature=None) -> Response | Stream :
        if max_tokens is None:
            max_tokens = self.config['max_tokens']

        if temperature is None:
            temperature = self.config['temperature']

        if self.config['invocation_method'] != 'converse' and self.config['invocation_method'] != 'converse_stream':
            raise ValueError("Invalid invocation_method in config")
        return self.__invoke_model(system_prompt, prompt, max_tokens, temperature)

    def get_config(self):
        return self.config