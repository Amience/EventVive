
from CertiChat.Agent import Agent
from CertiChat.Tools import create_your_own, search_wikipedia, search_cs25_e
import openai
import os
from dotenv import load_dotenv, find_dotenv

# Get API key
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']


tools = [search_wikipedia, create_your_own, search_cs25_e]

cb = Agent(
    tools=tools,
    llm='gpt-4',
    llm_temp=0,
    verbose=True)

cb.convchain("Hello, I'm David and I'm married to Katerina")
cb.convchain("Can you tell me what Langchain is in one sentence?")
cb.convchain("Who is the president of Greece, Mitsotakis?")
cb.convchain("What tools do you have available?")
cb.convchain("What is my name?")
cb.convchain("Call the 'create_your_own' tool with the input 'I love langchain' and return the result")
cb.convchain("What CS25 regulations are relevant to a heat exchanger?")
cb.memory.buffer

cb.memory.entity_store

cb.convchain.tool

cb.convchain._prepare_intermediate_steps

cb.convchain