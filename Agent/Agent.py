from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ConversationEntityMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough
from langchain.tools.render import format_tool_to_openai_function

from Agent.prompts import ENTITY_EXTRACTION_PROMPT, ENTITY_SUMMARIZATION_PROMPT
import param
from langchain.schema import FunctionDefinition

import pydantic

# Ensure LangChain uses Pydantic v2
if pydantic.VERSION.startswith("2"):
    from langchain.pydantic_v1 import ValidationError
else:
    from pydantic import ValidationError

class Agent(param.Parameterized):

    def __init__(self, tools, llm, llm_temp, verbose, **params):
        super(Agent, self).__init__(**params)
        self.answer = None
        self.panels = []

        self.functions = [FunctionDefinition.from_tool(f) for f in tools]
        self.model = ChatOpenAI(model_name=llm, temperature=llm_temp, functions=self.functions)

        #self.functions = [format_tool_to_openai_function(f) for f in tools]
        #self.model = ChatOpenAI(model_name=llm, temperature=llm_temp).bind(functions=self.functions)
        self.memory = ConversationBufferMemory(return_messages=True, memory_key="history")
        # self.memory = ConversationEntityMemory(
        #    llm=ChatOpenAI(model_name=llm, temperature=llm_temp),
        #    entity_extraction_prompt=ENTITY_EXTRACTION_PROMPT,
        #    entity_summarization_prompt=ENTITY_SUMMARIZATION_PROMPT,
        #    return_messages=True,
        #    memory_key="chat_history",
        #)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant whose knowledge and \
    expertise are specifically focused on one event. Keep your language professional but informal. \
    Your role is to assist in discussions about various aspects of this event, \
    providing information and insights based on what was discussed there. Your assistance is confined to the \
    topics, data, and discussions that took place during this event. Your name is Eve and you work for EventVive."""),
            MessagesPlaceholder(variable_name="history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        self.chain = RunnablePassthrough.assign(
            agent_scratchpad=lambda x: format_to_openai_functions(x["intermediate_steps"])
        ) | self.prompt | self.model | OpenAIFunctionsAgentOutputParser()
        #self.qa = AgentExecutor(
        #    agent=self.chain,
        #    tools=tools,
        #    verbose=verbose,
        #    memory=self.memory,
        #    return_intermediate_steps=False,
        #)
        self.qa = AgentExecutor(
            agent=self.chain,
            tools=tools,
            verbose=verbose,
            memory=self.memory
        )

    def convchain(self, query):
        if not query:
            return
        result = self.qa.invoke({"input": query})
        self.answer = result['output']
        return self.answer


    def clr_history(self ,count=0):
        self.chat_history = []
        return


