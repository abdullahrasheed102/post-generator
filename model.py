from langchain_google_genai.llms import GoogleGenerativeAI
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain import hub
from langchain.prompts import SystemMessagePromptTemplate
import os
from dotenv import load_dotenv
from tool import *
from prompt import custom_prompt

load_dotenv()

tools = [analyze_image,generate_image,search_web,extract_instagram_post]


base_prompt = hub.pull("hwchase17/structured-chat-agent")
custom_format = custom_prompt

base_prompt.messages[0] = SystemMessagePromptTemplate.from_template(
custom_format + "\n\n" + base_prompt.messages[0].prompt.template
)
prompt = base_prompt
api_key = os.getenv("GOOGLE_API_KEY")
llm = GoogleGenerativeAI(
model="gemini-2.5-flash-preview-05-20",
api_key=api_key,
temperature=1,
)
agent = create_structured_chat_agent(llm, tools, prompt)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
memory.clear()

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True,
)

url = input("Enter the path to the post: ")

result = agent_executor.invoke({"input": url})
print("AI:", result["output"])