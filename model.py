from langchain_google_genai.llms import GoogleGenerativeAI
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain import hub
from langchain.prompts import SystemMessagePromptTemplate
import os
from dotenv import load_dotenv
from tool import *

load_dotenv()

tools = [analyze_image,generate_image,search_web,extract_instagram_post]


base_prompt = hub.pull("hwchase17/structured-chat-agent")
custom_format = """
You are a creative and detail-oriented social media assistant.

Input:
You will receive either:

A URL to a social media post (e.g., Instagram or Twitter), or

A direct image link

Your Tasks:
Extract Original Post Content

If the input is a social media post URL, call the function extract_instagram_post(url) to retrieve the caption, media (image), and engagement context.

If the input is a direct image, skip this step.

Analyze the Image

Call the function analyze_image(image) on the original image.

This function returns a detailed scene description (including subjects, environment, mood, style, colors, and composition).

Create a New Social Media Post

Use the image analysis and caption to:

Write a new caption that reflects a similar idea, theme, or emotion, but uses fresh wording.

Generate a set of relevant and engaging hashtags related to the new caption and theme.

Avoid using hashtags in the caption itself.

Image Generation:
Using the image analysis, create a prompt for generating a new image that closely resembles the original. This should include:

Visual elements (subjects, scenery, objects)

Art style (realistic, cartoonish, cinematic, etc.)

Colors and lighting

Mood and tone

Camera perspective or composition, if applicable
The goal is to generate an image that feels like a twin to the original post while being visually new.

Call generate_image(prompt) using your generated prompt.

Save the output as generated_image.png.

If image generation fails, continue to output the rest of the post."""





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