"""
StreamLit gives error:
RuntimeError: Your system has an unsupported version of sqlite3. Chroma
requires sqlite3 >= 3.35.0.

Follow instructions here: https://discuss.streamlit.io/t/issues-with-chroma-and-sqlite/47950/4

Solution: need to rewrite sqlite3 with new pysqlite3.
- no need for pip install because this error is fixed on StreamLit server by adding to requirements
- Add to requirements.txt: pysqlite3-binary==0.5.2.post1
"""
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# End of solution

import streamlit as st
from Agent.Tools import create_your_own, TelecomFuture, TelecomFuture_create_summary, TelecomFuture_summarise_presenters, GreenReport2023, GreenReport2023_create_summary
from Agent.Agent import Agent
from langchain.tools.render import format_tool_to_openai_function
import hmac
from gsheet import create_gsheet_connection, save_data_to_sheet, save_login_to_sheet, save_feedback_to_sheet
import openai
import os
# ---------------------------------------------------

from dotenv import load_dotenv, find_dotenv


def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            # del st.session_state["username"]

            # If login is successful, save the record to Google Sheets
            spreadsheet = create_gsheet_connection()
            login_data_sheet = spreadsheet.worksheet("login_data")
            save_login_to_sheet(login_data_sheet, st.session_state["username"])
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()

st.session_state.username = st.session_state["username"]
# ---------------------------------------------------
# ---------------------------------------------------
# ---------------------------------------------------
# Main Streamlit app starts here
# ---------------------------------------------------
# ---------------------------------------------------
# ---------------------------------------------------




# Define function to start a new chat
def new_chat():
    """
    Clears session state and starts a new chat.
    """
    st.session_state.stored_session.append(st.session_state.messages)
    #st.session_state.entity_memory.entity_store.clear()
    #st.session_state.entity_memory.buffer.clear()
    if 'agent' in st.session_state:
        st.session_state.pop('agent') # To remove 'agent' from session_state
    st.session_state.messages = []





# Get API key
#_ = load_dotenv(find_dotenv())  # read local .env file
#openai.api_key = os.environ['OPENAI_API_KEY']

# Set up sidebar with various options
# openai_api_key = st.sidebar.text_input(label="Enter the password", type="password", value=st.session_state['OPENAI_API_KEY'] if 'OPENAI_API_KEY' in st.session_state else '', placeholder="...")
#if openai_api_key:
#    st.session_state['OPENAI_API_KEY'] = openai_api_key
#    os.environ['OPENAI_API_KEY'] = openai_api_key
#    openai.api_key = st.session_state['OPENAI_API_KEY']
#else:
#    st.error("You must enter the correct password to continue.")
#    #st.info("Obtain your password here: ")
#    st.stop()




#st.sidebar.write('''<p style="font-family:sans-serif; color:Black; font-size: 12px;">
#    EventVive represents a breakthrough in how we interact with knowledge from significant events, \
#    like the Royal Academy of Engineering's "Critical Conversations" on "Future Telecommunications - \
#    A Critical Technology for a Critical Time?". Unlike traditional methods of information consumption, \
#    this agent allows you to have a conversation with the event itself, making the experience more personal \
#    and engaging. This level of interaction not only personalises the knowledge but also aligns it with your \
#    specific interests and queries, offering a unique and valuable learning experience.
#   </p>''',
#    unsafe_allow_html=True)

# Add a button to start a new chat
st.sidebar.button("New Chat", on_click=new_chat, type='primary')

# Allow the user to clear all stored conversation sessions
#if st.session_state.stored_session:
#    if st.sidebar.checkbox("Clear-all"):
#        st.session_state.stored_session = []
#        st.session_state.stored_session.append(st.session_state.messages)
#        st.session_state.entity_memory.entity_store.clear()
#        st.session_state.entity_memory.buffer.clear()
#        st.session_state.messages = []



# Set up the Streamlit app layout
st.title("️🐝 EventVive")
#st.subheader("""We're creating AI agents that think, reason, and reference like the best human \
#experts, but with the speed and scalability that only AI can offer.""")
st.markdown(
    '''<p style="font-family:sans-serif; color:Green; font-size: 12px;"> \
    Revive the Conference. Converse with it. Query it. Integrate its insights into your daily work flows.
    </p>''',
    unsafe_allow_html=True)

#st.markdown('''<p style="font-family:sans-serif; color:Black; font-size: 12px;">
#    Dive into an interactive adventure with EventVive! If you're not sure where to begin, \
#    just throw a question my way. Try asking, "What's the scope on this event?", \
#    "Hit me with the hottest topics discussed!", "Zoom into the 5G tech talks, will you?", \
#    "Did they chat about climate impacts at all?" or better yet, tell me about what you're working on, and \
#    let's explore how this event's insights can spice up your project. \
#    Let's deep dive into the details and uncover some hidden gems!
#    </p>''',
#    unsafe_allow_html=True)

# Initialize session states
if "stored_session" not in st.session_state:
    st.session_state.stored_session = []



# ################################################
# ## AI MODEL
# Define the options for the select box
with st.sidebar:
    # Define the options and their descriptions
    options = {
        "TelecomFuture": "Future telecommunications - a critical technology for a critical time? by Royal Academy of Engineering",
        "GreenReport2023": "ANNUAL REPORT 2022-2023 by Greener by Design"
    }
    # Display the title for the selection
    #st.write("Select an option")
    # Single radio button group for options
    selected_option = st.radio("", list(options.keys()), key="user_selection")
    # Check if the selection has changed
    if 'last_selection' in st.session_state and st.session_state.last_selection != selected_option:
        if 'agent' in st.session_state:
            # Perform any cleanup if necessary
            # st.session_state.agent.cleanup()
            st.session_state.pop('agent')
            st.session_state.messages = []
    # Update the last_selection in the session state
    st.session_state.last_selection = selected_option
    # Display the description for the selected option
    st.caption(options[selected_option])

openai_api_key = st.secrets["openAI"]["OPENAI_API_KEY"]
st.session_state['OPENAI_API_KEY'] = openai_api_key
os.environ['OPENAI_API_KEY'] = openai_api_key
openai.api_key = st.session_state['OPENAI_API_KEY']

MODEL = 'gpt-4-1106-preview'
llm_temp = 0
verbose = True
tools = [create_your_own]
if selected_option == "TelecomFuture":
    tools = [TelecomFuture, TelecomFuture_create_summary, TelecomFuture_summarise_presenters]
elif selected_option == "GreenReport2023":
    tools = [GreenReport2023, GreenReport2023_create_summary]

# Add to session state Agent and all of its properties and states, including the memory component
if 'agent' not in st.session_state:
    st.session_state.agent = Agent(
                                    tools=tools,
                                    llm=MODEL,
                                    llm_temp=llm_temp,
                                    verbose=verbose)

# functions = [format_tool_to_openai_function(f) for f in tools]
# llm = ChatOpenAI(model_name=MODEL, temperature=llm_temp)
# model = llm.bind(functions=functions)
# # Create a ConversationEntityMemory object if not already created
# if 'entity_memory' not in st.session_state:
#     st.session_state.entity_memory = ConversationEntityMemory(
#         llm=llm,
#         entity_extraction_prompt=ENTITY_EXTRACTION_PROMPT,
#         entity_summarization_prompt=ENTITY_SUMMARIZATION_PROMPT,
#         return_messages=True,
#         memory_key="chat_history",
#     )
# # DEFINITION BUT NOT USED IN THE CODE YET. MEMORY KEY ISSUES
# if 'summary_memory' not in st.session_state:
#     st.session_state.summary_memory = ConversationSummaryMemory(
#         llm=llm,
#         input_key="input",
#         memory_key="chat_history",
#     )
# if 'combined_memory' not in st.session_state:
#     st.session_state.combined_memory = CombinedMemory(
#         memories=[st.session_state.entity_memory, st.session_state.summary_memory]
#     )
#
# prompt = ChatPromptTemplate.from_messages([
#     ("system", """You are a helpful assistant whose knowledge and \
#     expertise are specifically focused on one event. Keep your language professional but informal. \
#     Your role is to assist in discussions about various aspects of this event, \
#     providing information and insights based on what was discussed there. Your assistance is confined to the \
#     topics, data, and discussions that took place during this event. Your name is Eve and you work for EventVive."""),
#     MessagesPlaceholder(variable_name="history"),
#     ("user", "{input}"),
#     MessagesPlaceholder(variable_name="agent_scratchpad")
# ])
# chain = RunnablePassthrough.assign(
#     agent_scratchpad=lambda x: format_to_openai_functions(x["intermediate_steps"])
# ) | prompt | model | OpenAIFunctionsAgentOutputParser()
# qa = AgentExecutor(
#     agent=chain,
#     tools=tools,
#     verbose=verbose,
#     memory=st.session_state.entity_memory,
#     return_intermediate_steps=False,
# )


# ################################################
# ## FRONT INTERFACE
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Set welcome message based on selection
welcome_message = "Hello, how can I assist you today?"  # Default message
if selected_option == "TelecomFuture":
    welcome_message = """Hello and a warm welcome to EventVive 👋 I'm Eve, your go-to for a nifty bit of banter and \
insight on the world of significant events. Delighted to have you with us! \n\n

Today, we're diving into the rich discussions \
from the Royal Academy of Engineering's "Critical Conversations", \
specifically the thrilling world of telecom's leap towards 6G, blending AI, quantum tech, augmented reality, \
IoT, and more.\n\n

In a nutshell, we've got a panel featuring Dr. Hayaatun Sillem, alongside \
Dr Mallikarjun Tatipamula, Prof. Dimitra Simeonidou, and Dr David Parker, whizzes from Erikson, the \
University of Bristol, and Microsoft, tackling the evolution from 5G to 6G, addressing challenges like \
innovation scaling, workforce skills, and security. There's a lot on the table - from the UK's role in \
global telecom to the societal impacts and the nitty-gritty of technologies like hollow fibre and \
quantum cloud services.\n\n

Curious about the event's speakers, their backgrounds, or the riveting debates \
they engaged in? I'm here to dish \
out all those details. Keen to understand the technical aspects of the technologies discussed? We can explore \
those depths together.\n\n

And here's the cherry on top: if you're wrestling with your own case or project, \
bring it to the table! We'll \
weave in diverse viewpoints and insights from these events, enriching and enhancing your perspectives. It's not \
just about learning what was said, but applying it to your unique situation.\n\n

So, what's on your mind? Let's \
get cracking and make this a conversation to remember! 🕵️‍♀️📚🌟
"""
elif selected_option == "GreenReport2023":
    welcome_message = """Hello and a warm welcome to EventVive 👋 I'm Eve, your go-to for a nifty bit of banter and \
insight on the world of significant events. Delighted to have you with us! \n\n

Today, we're zooming into the Royal Aeronautical Society's "Greener by Design" Annual Report 2022-2023, \
showcasing the aerospace industry's leaps in environmental sustainability. This info-packed session features \
experts tackling climate change forecasts, aviation's decarbonization challenges, and the innovative Sustainable \
Aviation Fuel (SAF). We'll also explore advancements in electric and hybrid aircraft, the potential of hydrogen \
fuel cell hybrid electric aircraft, and the intriguing concept of virtual interlining in airlines.

But there's more! We're delving into Carbon Budgets, the Net Zero Challenge, and the compelling science of \
contrail management. Plus, we'll unravel the impacts of non-CO2 emissions in aviation. Get ready for a journey \
through a blend of challenges, innovative solutions, and forward-thinking strategies! 🌍✈️🔬

So, what's on your mind? Let's \
get cracking and make this a conversation to remember! 🕵️‍♀️📚🌟
"""

# Display AI message on initial launch
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.markdown(welcome_message)
    st.session_state.messages.append({"role": "assistant", "content": welcome_message})

# React to user input
if user_message := st.chat_input("How can I help?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(user_message)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_message})

    # LOG activity in GOOGLE SHEETS
    spreadsheet = create_gsheet_connection()
    save_data_to_sheet(spreadsheet.sheet1, st.session_state.username, user_message, selected_option)

    if len(user_message) >= 200:
        user_message = """Tell me that my query was way to long in a UK style sassy way, and advise it \
        should be less than 200 characters long"""

    #AI_response = qa.invoke({"input": user_message})
    AI_output = st.session_state.agent.convchain(user_message)
    #AI_output = AI_response['output']
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


with st.sidebar:
    with st.form("Feedback Form", clear_on_submit=True):
        username = st.session_state.get("username", "there")  # Fallback to "there" if username is not set
        feedback = st.text_area(f"Hi {username}, we would love to hear your feedback!")
        submit_button = st.form_submit_button("Submit Feedback")

        if submit_button and feedback:
            # Connect to Google Sheets and save the feedback
            spreadsheet = create_gsheet_connection()
            feedback_sheet = spreadsheet.sheet1  # Assuming you're using the first worksheet
            save_feedback_to_sheet(feedback_sheet, st.session_state.username, feedback, selected_option)
            st.success("Feedback submitted successfully!")







st.sidebar.write('''<p style="font-size:10px; color:black;"><i>
<b>Disclaimer:</b> We do not take responsibility for any misuse or unintended consequences arising \
from the use of the results suggested by 🐝 <u>EventVive</u>. Users are advised to exercise discretion and judgment while \
interpreting and using the results provided by the app. We are not liable for any consequences, whether direct or \
indirect, that may arise from the use or misuse of the app
</i></p>''', unsafe_allow_html=True)

st.sidebar.write('<p style="font-size:10px; color:black;">Powered by 🦜LangChain + OpenAI + Streamlit</p>', unsafe_allow_html=True)

