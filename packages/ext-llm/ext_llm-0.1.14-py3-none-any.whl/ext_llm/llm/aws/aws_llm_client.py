import logging
import os
import boto3
from ext_llm import LlmClient
from ext_llm.llm.response import Response
from ext_llm.llm.stream import Stream
from ext_llm.llm.aws.aws_stream import AwsStream


def make_system_prompt(system_prompt):
    return [
        {
            "text": system_prompt
        }
    ]


def make_prompt(prompt):
    return [
        {
            "role": "user",
            "content": [
                {
                    "text": prompt
                }
            ]
        }
    ]


def make_inference_config(max_tokens, temperature, top_p):
    return {
        "maxTokens": max_tokens,
        "temperature": temperature,
        "topP": top_p
    }


class AwsLlmClient(LlmClient):
    logger = logging.getLogger('AwsLlm')

    def __init__(self, config: dict, preset_name: str):
        super().__init__()
        self.config = config
        self.preset_name = preset_name
        access_key_id_env_var_name = config['aws_access_key_id_variable_name']
        secret_access_key_env_var_name = config['aws_secret_access_key_variable_name']
        access_key_id = os.getenv(access_key_id_env_var_name)
        secret_access_key = os.getenv(secret_access_key_env_var_name)
        if access_key_id is None:
            raise ValueError(f"Environment variable {access_key_id_env_var_name} not set")
        if secret_access_key is None:
            raise ValueError(f"Environment variable {secret_access_key_env_var_name} not set")

        region = config['aws_region']
        self.__session = boto3.Session(
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region
        )
        self.__bedrock_client = self.__session.client(service_name='bedrock-runtime')
        self.__model_id = config['model_id']

    def __build_metadata(self, response, max_tokens, temperature):
        preset_name = self.preset_name
        model_id = self.config['model_id']

        # Extract AWS-specific metadata
        # Usage information is in a different format from Groq
        usage = response.get('usage', {})
        prompt_tokens = usage.get('inputTokens', 0)
        completion_tokens = usage.get('outputTokens', 0)
        total_tokens = prompt_tokens + completion_tokens

        # Get finish reason (stop/length/content_filter)
        stop_reason = response.get('stopReason', None)

        return {
            "preset_name": preset_name,
            "model_id": model_id,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "finish_reason": stop_reason,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }

    def __invoke_model(self, system_prompt, prompt, max_tokens: int, temperature: float, top_p=0.9):
        system_prompts = make_system_prompt(system_prompt)
        messages = make_prompt(prompt)
        inference_config = make_inference_config(max_tokens, temperature, top_p)
        response = self.__bedrock_client.converse(
            modelId=self.__model_id,
            messages=messages,
            system=system_prompts,
            inferenceConfig=inference_config
        )

        content = response['output']['message']['content'][0]['text']
        metadata = self.__build_metadata(response, max_tokens, temperature)

        return Response(content, metadata)

    def __invoke_model_stream(self, system_prompt, prompt, max_tokens: int, temperature: float, top_p=0.9):
        system_prompts = make_system_prompt(system_prompt)
        messages = make_prompt(prompt)
        inference_config = make_inference_config(max_tokens, temperature, top_p)
        stream = self.__bedrock_client.converse_stream(
            modelId=self.__model_id,
            messages=messages,
            system=system_prompts,
            inferenceConfig=inference_config
        )

        return AwsStream(stream['stream'])

    def generate_text(self, system_prompt: str, prompt: str, max_tokens=None, temperature=None) -> Response | Stream:
        if max_tokens is None:
            max_tokens = self.config['max_tokens']

        if temperature is None:
            temperature = self.config['temperature']

        self.logger.debug(f"max_tokens: {max_tokens}, temperature: {temperature}")

        if self.config['invocation_method'] == 'converse':
            return self.__invoke_model(system_prompt, prompt, max_tokens, temperature)
        elif self.config['invocation_method'] == 'converse_stream':
            return self.__invoke_model_stream(system_prompt, prompt, max_tokens, temperature)
        else:
            raise ValueError("Invalid invocation method")

    def get_config(self):
        return self.config