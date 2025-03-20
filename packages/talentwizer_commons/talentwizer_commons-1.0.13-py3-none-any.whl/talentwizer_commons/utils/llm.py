from dotenv import load_dotenv
load_dotenv()
import os
from llama_index.llms.openai import OpenAI

# finetuning_handler = OpenAIFineTuningHandler()
# callback_manager = CallbackManager([finetuning_handler])

llm = OpenAI(model="gpt-4", temperature=0)
