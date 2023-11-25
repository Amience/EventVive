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

import streamlit as st


class Agent(param.Parameterized):

    def __init__(self, tools, llm, llm_temp, verbose, **params):
        super(Agent, self).__init__(**params)
        self.answer = None
        self.panels = []
        self.functions = [format_tool_to_openai_function(f) for f in tools]
        self.model = ChatOpenAI(model_name=llm, temperature=llm_temp).bind(functions=self.functions)
        # self.memory = ConversationBufferMemory(return_messages=True ,memory_key="chat_history")
        self.memory = ConversationEntityMemory(
            llm=ChatOpenAI(model_name=llm, temperature=llm_temp),
            entity_extraction_prompt=ENTITY_EXTRACTION_PROMPT,
            entity_summarization_prompt=ENTITY_SUMMARIZATION_PROMPT,
            return_messages=True,
            memory_key="chat_history",
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are helpful but sassy assistant"),
            MessagesPlaceholder(variable_name="history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        self.chain = RunnablePassthrough.assign(
            agent_scratchpad=lambda x: format_to_openai_functions(x["intermediate_steps"])
        ) | self.prompt | self.model | OpenAIFunctionsAgentOutputParser()
        self.qa = AgentExecutor(
            agent=self.chain,
            tools=tools,
            verbose=verbose,
            memory=self.memory,
            return_intermediate_steps=False,
        )

    def convchain(self, query):
        if not query:
            return
        result = self.qa.invoke({"input": query})

        #self.answer = result['output']
        return result


    def clr_history(self ,count=0):
        self.chat_history = []
        return


