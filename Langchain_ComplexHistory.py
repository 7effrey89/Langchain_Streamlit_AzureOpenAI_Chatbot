import streamlit as st
from dotenv import load_dotenv
import os
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, trim_messages
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

#https://www.youtube.com/watch?v=zKGeRWjJlTU

# Load the .env file
load_dotenv()

LANGCHAIN_TRACING_V2="true"
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY=os.getenv("LANGCHAIN_SMITH_API_KEY")
LANGCHAIN_PROJECT="productBenchmark"

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default")

model = AzureChatOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

# Define a function to get the chat history for a given session ID
if "store" not in st.session_state:
    st.session_state.store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in st.session_state.store:
        st.session_state.store[session_id] = InMemoryChatMessageHistory() #ChatMessageHistory()
        st.session_state.session_history = st.session_state.store[session_id]
    return st.session_state.session_history

if "with_message_history" not in st.session_state:
    # Create a runnable that includes the message history
    st.session_state.with_message_history = RunnableWithMessageHistory(model, get_session_history)

if "ui_chat_history" not in st.session_state:
    st.session_state.ui_chat_history = []
    
# Define the initial configuration for
config = {"configurable": {"session_id": "abc3"}}

#Configure amount of history to send to the LLM
#https://python.langchain.com/v0.2/docs/tutorials/chatbot/#managing-conversation-history
trimmer = trim_messages(
    max_tokens=65,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

def get_response(user_query):

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. Answer all questions to the best of your ability in {language}.",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            (
                "human",f"{user_query}"
            )
        ]
    )
      
    #To display the output response only
    outputParser = StrOutputParser()

    #LCEL chain: sequences of calls to the different components of the Langchain
    runnable = (
        # RunnablePassthrough.assign(messages=itemgetter("input") | trimmer) #trim the chat history
        # | 
        prompt 
        | model 
        | outputParser
    )

    # response = chain.invoke({"messages": [HumanMessage(content=user_query)]})
    st.session_state.with_message_history  = RunnableWithMessageHistory(runnable, 
                                                        get_session_history, 
                                                        input_messages_key="input", 
                                                        history_messages_key="chat_history"#, 
                                                        # output_messages_key="answer"
                                                        )

    
    response = st.session_state.with_message_history.invoke(
        {
            "input": f"{user_query}",
            "language": "English"
        },
        config=config,
    )

    #return the LLM completion
    # return chain.stream({
    #     "user_question": user_query,
    # })

    return response

################################################################################################
st.title("Streamlit App")

# Display chat history
for message in st.session_state.ui_chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(f"{message.content}")
    elif isinstance(message, AIMessage):
        with st.chat_message("Assistant"):
            st.write(f"{message.content}")

# Get user input
user_prompt = st.chat_input("Enter your message here")

# Process user input
if user_prompt is not None and user_prompt != "":
    st.session_state.ui_chat_history.append(HumanMessage(user_prompt))

    with st.chat_message("Human"):
        st.write(f"{user_prompt}")

    with st.chat_message("Assistant"):
        ai_completion= str(get_response(user_prompt))
        st.write(ai_completion)
        
    st.session_state.ui_chat_history.append(AIMessage(ai_completion))

def print_chat_history(session_id): #e.g. "abc3"
  for message in st.session_state.store[session_id].messages:
    if isinstance(message, AIMessage):
        prefix = "AI"
    else:
        prefix = "User"

    print(f"{prefix}: {message.content}\n")
