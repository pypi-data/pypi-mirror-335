from concurrent.futures import Future

import ext_llm
from ext_llm.llm.response import Response
from ext_llm.llm.stream import Stream

#read config yaml file
config : str = open("config.yaml").read()

#initialize extllm library
extllm = ext_llm.init(config)

#request a client via user defined presets. In this instance it's "groq-llama"
llm_client = extllm.get_client("groq-llama")

#you can request e concurrent client, based on the same preset. This will allow for non blocking concurrent requests.
llm_concurrent_client = extllm.get_concurrent_client("groq-llama")

#Non blocking call. This will return a future object that will be resolved when the request is completed.
future1: Future [Response | Stream] = llm_concurrent_client.generate_text("You are an helpful assistant", "Recite the first article of the Italian Constitution")

#Blocking call. This will return the result of the request. The result can be either a Response or a Stream object.
#Response or Stream are defined by the user in the config file.
#If the "invocation_method" is "converse" then the result is a Response.
#If the "invocation_method" is "converse_stream" then the result is a Stream.
#A stream has to be handled differently from a response.
result: Response | Stream = llm_client.generate_text("You are an helpful assistant", "Recite the first amendment of the American constitution")


print(result.metadata)
print(result)

print(future1.result().metadata)
print(future1.result())
