from concurrent.futures import Future

import ext_llm
from ext_llm.llm.response import Response
from ext_llm.llm.stream import Stream

#read config yaml file
config : str = open("config.yaml").read()

#initialize extllm library
extllm = ext_llm.init(config)

#request a client via user defined presets. In this instance it's "groq-llama"
aws_llm_client = extllm.get_client("aws-claude-sonnet")
groq_llm_client = extllm.get_client("groq-llama")

aws_response = aws_llm_client.generate_text("You are an helpful assistant", "Recite the first article of the Italian Constitution")
groq_response = groq_llm_client.generate_text("You are an helpful assistant", "Recite the first article of the Italian Constitution")
print(aws_response.metadata)
print(groq_response.metadata)
