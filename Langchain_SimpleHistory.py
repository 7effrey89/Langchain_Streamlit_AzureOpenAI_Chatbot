import streamlit as st
from dotenv import load_dotenv
import os
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

#https://www.youtube.com/watch?v=zKGeRWjJlTU

# Load the .env file
load_dotenv()

LANGCHAIN_TRACING_V2="true"
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_PROJECT="productBenchmark"

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default")

MODEL = AzureChatOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

def get_response(user_query, chat_history):

    prompt_template = """
    You are a helpful assistant. Answer the following questions considering the history of the conversation:

    Chat history: {chat_history}

    User question: {user_question}
    """
    print("chat_history", chat_history)
    prompt = ChatPromptTemplate.from_template(prompt_template)
        
    #To display the output response only
    outputParser = StrOutputParser()

    #LCEL chain: sequences of calls to the different components of the Langchain
    chain = prompt | MODEL | outputParser
    
    #return the LLM completion
    return chain.stream({
        "chat_history": chat_history,
        "user_question": user_query,
    })

################################################################################################
st.title("Streamlit App")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for message in st.session_state.chat_history:
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
    st.session_state.chat_history.append(HumanMessage(user_prompt))

    with st.chat_message("Human"):
        st.write(f"{user_prompt}")

    with st.chat_message("Assistant"):
        ai_completion = st.write_stream(get_response(user_prompt, st.session_state.chat_history))
    
    st.session_state.chat_history.append(AIMessage(ai_completion))
