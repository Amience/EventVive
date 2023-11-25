"""
StreamLit gives error:
RuntimeError: Your system has an unsupported version of sqlite3. Chroma
requires sqlite3 >= 3.35.0.

Follow instructions here: https://discuss.streamlit.io/t/issues-with-chroma-and-sqlite/47950/4

Solution: need to rewrite sqlite3 with new pysqlite3.
Also added to requirements.txt: pysqlite3-binary==0.5.2.post1
"""
#__import__('pysqlite3')
#import sys
#sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# End of solution

import streamlit as st
from langchain import ConversationChain, PromptTemplate
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationEntityMemory, ConversationBufferMemory, CombinedMemory, \
    ConversationSummaryMemory
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough
from langchain.text_splitter import MarkdownHeaderTextSplitter

from Agent.prompts import ENTITY_EXTRACTION_PROMPT, ENTITY_SUMMARIZATION_PROMPT, ENTITY_MEMORY_CONVERSATION_PROMPT

from Agent.Tools import create_your_own, eventvive, create_summary

from langchain.tools.render import format_tool_to_openai_function

import openai
# ---------------------------------------------------
import os
from dotenv import load_dotenv, find_dotenv
# ---------------------------------------------------
# ---------------------------------------------------
# ---------------------------------------------------

# Initialize session states
if "stored_session" not in st.session_state:
    st.session_state.stored_session = []


# Define function to start a new chat
def new_chat():
    """
    Clears session state and starts a new chat.
    """
    st.session_state.stored_session.append(st.session_state.messages)
    st.session_state.entity_memory.entity_store.clear()
    st.session_state.entity_memory.buffer.clear()
    st.session_state.messages = []


# Get API key
#_ = load_dotenv(find_dotenv())  # read local .env file
#openai.api_key = os.environ['OPENAI_API_KEY']

# Set up sidebar with various options
openai_api_key = st.sidebar.text_input(label="Enter the password", type="password", value=st.session_state['OPENAI_API_KEY'] if 'OPENAI_API_KEY' in st.session_state else '', placeholder="...")
if openai_api_key:
    #openai_api_key = 'sk-'
    st.session_state['OPENAI_API_KEY'] = openai_api_key
    os.environ['OPENAI_API_KEY'] = openai_api_key
    openai.api_key = st.session_state['OPENAI_API_KEY']
else:
    st.error("You must enter the correct password to continue.")
    #st.info("Obtain your password here: ")
    st.stop()

st.sidebar.write('''<p style="font-family:sans-serif; color:Black; font-size: 12px;">
    EventVive represents a breakthrough in how we interact with knowledge from significant events, \
    like the Royal Academy of Engineering's "Critical Conversations" on "Future Telecommunications - \
    A Critical Technology for a Critical Time?". Unlike traditional methods of information consumption, \
    this agent allows you to have a conversation with the event itself, making the experience more personal \
    and engaging. This level of interaction not only personalises the knowledge but also aligns it with your \
    specific interests and queries, offering a unique and valuable learning experience.
    </p>''',
    unsafe_allow_html=True)

# Add a button to start a new chat
st.sidebar.button("New Chat", on_click=new_chat, type='primary')

# Allow the user to clear all stored conversation sessions
if st.session_state.stored_session:
    if st.sidebar.checkbox("Clear-all"):
        st.session_state.stored_session = []
        st.session_state.stored_session.append(st.session_state.messages)
        st.session_state.entity_memory.entity_store.clear()
        st.session_state.entity_memory.buffer.clear()
        st.session_state.messages = []

# Set up the Streamlit app layout
st.title("️🐝 EventVive")
#st.subheader("""We're creating AI agents that think, reason, and reference like the best human \
#experts, but with the speed and scalability that only AI can offer.""")
st.markdown(
    '''<p style="font-family:sans-serif; color:Green; font-size: 12px;"> \
    Revive the Conference. Converse with it. Query it. Integrate its insights into your daily work flows.
    </p>''',
    unsafe_allow_html=True)

st.markdown('''<p style="font-family:sans-serif; color:Black; font-size: 12px;">
    Dive into an interactive adventure with EventVive! If you're not sure where to begin, \
    just throw a question my way. Try asking, "What's the scope on this event?", \
    "Hit me with the hottest topics discussed!", "Zoom into the 5G tech talks, will you?", \
    "Did they chat about climate impacts at all?" or better yet, tell me about what you're working on, and \
    let's explore how this event's insights can spice up your project. \
    Let's deep dive into the details and uncover some hidden gems!
    </p>''',
    unsafe_allow_html=True)


# ################################################
# ## AI MODEL
MODEL = 'gpt-4-1106-preview'
llm_temp = 0
verbose = True
tools = [create_your_own, eventvive, create_summary]
functions = [format_tool_to_openai_function(f) for f in tools]
llm = ChatOpenAI(model_name=MODEL, temperature=llm_temp)
model = llm.bind(functions=functions)
# Create a ConversationEntityMemory object if not already created
if 'entity_memory' not in st.session_state:
    st.session_state.entity_memory = ConversationEntityMemory(
        llm=llm,
        entity_extraction_prompt=ENTITY_EXTRACTION_PROMPT,
        entity_summarization_prompt=ENTITY_SUMMARIZATION_PROMPT,
        return_messages=True,
        memory_key="chat_history",
    )
# DEFINITION BUT NOT USED IN THE CODE YET. MEMORY KEY ISSUES
if 'summary_memory' not in st.session_state:
    st.session_state.summary_memory = ConversationSummaryMemory(
        llm=llm,
        input_key="input",
        memory_key="chat_history",
    )
if 'combined_memory' not in st.session_state:
    st.session_state.combined_memory = CombinedMemory(
        memories=[st.session_state.entity_memory, st.session_state.summary_memory]
    )

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful but sassy assistant whose knowledge and expertise are specifically \
    focused on [Name of Event]. Your role is to assist in discussions about various aspects of this event, \
    providing information and insights based on what was discussed there. Your assistance is confined to the \
    topics, data, and discussions that took place during this event. Your name is Maya and you work for EventVive"""),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])
chain = RunnablePassthrough.assign(
    agent_scratchpad=lambda x: format_to_openai_functions(x["intermediate_steps"])
) | prompt | model | OpenAIFunctionsAgentOutputParser()
qa = AgentExecutor(
    agent=chain,
    tools=tools,
    verbose=verbose,
    memory=st.session_state.entity_memory,
    return_intermediate_steps=False,
)


# read the text file into string
text_file = open("KnowledgeBase.txt", "r")  # open text file in read mode
KnowledgeBase = text_file.read()  # read whole file to a string
text_file.close()  # close file

headers_to_split_on = [
    ("#", "Headline")
]

markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on
)
md_header_splits = markdown_splitter.split_text(KnowledgeBase)  # markdown header splits


# ################################################
# ## FRONT INTERFACE


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if user_message := st.chat_input("How can I help?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(user_message)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_message})
    # Retrieve relevant knowledge from knowledge base
    # retrieved_knowledge_base = vectordb.max_marginal_relevance_search(user_message, k=1)
    # Create the response to user message
    # response = Conversation(
    #    {"input_documents": retrieved_knowledge_base, "human_input": user_message},
    #    return_only_outputs=True
    # )['output_text']
    if len(user_message) >= 200:
        user_message = "Tell me that my query was way to long in a sassy way, and advise it should be less than 200 characters long"

    AI_response = qa.invoke({"input": user_message})
    AI_output = AI_response['output']
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(AI_output)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": AI_output})

#st.sidebar.download_button(
#    label="Download the conversation",
#    data=st.session_state.entity_memory.buffer,
#    file_name='LeanBoost_ConversationHistory.txt',
#    mime='text',
#)


st.sidebar.write('''<p style="font-size:10px; color:black;"><i>
<b>Disclaimer:</b> We do not take responsibility for any misuse or unintended consequences arising \
from the use of the results suggested by 🐝 <u>EventVive</u>. Users are advised to exercise discretion and judgment while \
interpreting and using the results provided by the app. We are not liable for any consequences, whether direct or \
indirect, that may arise from the use or misuse of the app
</i></p>''', unsafe_allow_html=True)

st.sidebar.write('<p style="font-size:10px; color:black;">Powered by 🦜LangChain + OpenAI + Streamlit</p>', unsafe_allow_html=True)

