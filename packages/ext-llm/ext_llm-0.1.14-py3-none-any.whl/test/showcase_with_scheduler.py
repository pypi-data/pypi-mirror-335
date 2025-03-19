import ext_llm
from ext_llm.scheduler import RequestScheduler

#read config yaml file
config : str = open("config.yaml").read()
#initialize extllm library
extllm = ext_llm.init(config)

#request client instatiation based on user defined preset
llm_client = extllm.get_client("groq-llama")

#request a scheduler
scheduler = extllm.get_scheduler(llm_client, max_workers=2)
#Start scheduler thread
scheduler.start()

trivia_questions=[]
answers=[]
requests_amount=10
for i in range(requests_amount):
    trivia_questions.append(scheduler.submit_request("You're a helpful assistant","Generate a short and interesting trivia question!"))

for i in range(requests_amount):
    trivia_question = scheduler.get_result(trivia_questions[i]).content
    print(trivia_question)
    answers.append(scheduler.submit_request("Answer to trivia question in one line", trivia_question))

for i in range(requests_amount):
    answer = scheduler.get_result(answers[i]).content
    print(answer)

#stop scheduler thread
scheduler.stop()