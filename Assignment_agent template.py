# Necessary Imports
import os

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.memory import ConversationSummaryMemory
from langchain_openai import ChatOpenAI

# Perform necessary imports for creating agents
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_community.chat_message_histories import ChatMessageHistory # Used to store chat history in memory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import OpenAI
import os

## Set the OpenAI API key and model name
# Open_API_Key = os.getenv("Open_API_Key")
# os.environ["OPENAI_API_KEY"] = Open_API_Key
MODEL="gpt-4o-mini"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

## Set the Tavily API key
# os.environ["TAVILY_API_KEY"] = os.getenv("Tavily_API_Key")

## Load the vectorstore
embeddings = OpenAIEmbeddings()
vector = FAISS.load_local(
    ".", embeddings, allow_dangerous_deserialization=True
)


## Create the conversational agent

# Creating a retriever
# See https://python.langchain.com/v0.1/docs/modules/data_connection/retrievers/vectorstore/
retriever = vector.as_retriever(search_kwargs={"k": 5}) # Create retriever from the loaded vector 


from langchain_core.tools import create_retriever_tool

# Create Amazon product search tool from the retriever
amazon_product_search = create_retriever_tool(
    retriever,
    name="amazon_product_search",
    description="Search for information about Amazon products. For any questions related to Amazon products, this tool must be used.",
)

# Tavily web search tool (updated; avoids deprecated langchain_community wrapper)
from langchain_tavily import TavilySearch

search_tavily = TavilySearch(max_results=5)

# Avoid pulling public prompts from the Hub (blocked by default for safety).
# Use a local ReAct prompt instead.
from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template(
    """You are a helpful assistant. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original question

Question: {input}
{agent_scratchpad}"""
)

## Create a list of tools: retriever_tool and search_tool
tools = [amazon_product_search, search_tavily] # TODO: Create a list of tools based on search_tavily and amazon_product_search.

# Initialize OpenAI model with streaming enabled
# Streaming allows tokens to be processed in real-time, reducing response latency.
summary_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0, streaming=True)


# Enable memory optimization with ConversationSummaryMemory
# This ensures that older conversations are summarized instead of keeping full history,
# preventing excessive context length that slows down responses.
 ## Create summary_memory using ConversationSummaryMemory()

summary_memory = ConversationSummaryMemory(llm=summary_llm, max_token_limit=1000)

reasoning_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0, streaming=True)
# Create a ReAct agent
# The agent will reason and take actions based on retrieved tools and memory.
## TODO create a react agent. Check create_react_agent() from langchain
summary_react_agent = create_react_agent(llm=reasoning_llm, tools=tools, prompt=prompt)

def handle_parsing_error(error):
    """Return a message to the agent when output parsing fails, prompting a retry in ReAct format."""
    return "You must respond using the ReAct format with Thought, Action, and Action Input. Try again."


# Configure the AgentExecutor to manage reasoning steps
# Note: memory=None when using RunnableWithMessageHistory for session-based chat history
summary_agent_executor = AgentExecutor(
    agent=summary_react_agent,
    tools=tools,
    memory=None,
    handle_parsing_errors=handle_parsing_error,
    max_iterations=25,
)
# Create an agent executor. Check AgentExecutor() from langchain. Make sure to pass the summary_memory to it



# Building an UI for the chatbot with agents
import gradio as gr

# Initialize session-based chat history
session_memory = {}

def get_memory(session_id):
    """Fetch or create a chat history instance for a given session."""
    if session_id not in session_memory:
        session_memory[session_id] = ChatMessageHistory()
    return session_memory[session_id]
    # Create a new element in the dictionary that corresponds to the session memory if it does not exit

# Wrap AgentExecutor (not the raw agent) with session-based chat history.
# Must use input_messages_key and history_messages_key so RunnablePassthrough.assign
# receives a dict; otherwise the agent's RunnablePassthrough.assign fails.
agent_with_chat_history = RunnableWithMessageHistory(
    summary_agent_executor,
    get_memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)
# Create agent with memory using RunnableWithMessageHistory()

# Define function for Gradio interface
def chat_with_agent(user_input, request: gr.Request):
    """Processes user input and maintains session-based chat history."""
    session_id = getattr(request, "session_hash", None) or "default"
    # Invoke the agent - RunnableWithMessageHistory fetches chat_history from session
    response = agent_with_chat_history.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}}
    )

    # Extract only the 'output' field from the response
    if isinstance(response, dict) and "output" in response:
        output = response["output"]
        # Replace generic iteration-limit message with a friendlier one
        if output == "Agent stopped due to iteration limit or time limit.":
            output = (
                "I wasn't able to complete a full response within the step limit. "
                "Please try asking a simpler or more specific question."
            )
        return output
    else:
        return "Error: Unexpected response format"

# Create Gradio app interface
with gr.Blocks() as app:
    gr.Markdown("# 🤖 Review Genie - Agents & ReAct Framework")
    gr.Markdown("Enter your query below and get AI-powered responses with session memory.")

    with gr.Row():
        input_box = gr.Textbox(label="Enter your query:", placeholder="Ask something...")
        output_box = gr.Textbox(label="Response:", lines=10)

    submit_button = gr.Button("Submit")

    submit_button.click(chat_with_agent, inputs=input_box, outputs=output_box)

# Launch the Gradio app
app.launch(server_name="0.0.0.0", server_port=7860, debug=True, share=False)
