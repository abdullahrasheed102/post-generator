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
You are a creative SEO assistant.

Given:
- An image or a URL of an image

Your task:
if you get a link of social media post call extract_instagram_post and get details.
after getting details call analyze_image to analyze the image and generate the detailed  description for similar image.

1. Understand the content of the original post
2. Based on that, create a similar social media post that is fresh but aligned in theme.
3. Write the following:

---

New Social Media Post Content:
call analyze_image tool to analyze the image and generate the description for the similar image
- Caption: (Write a new caption reflecting a similar idea/mood/theme), remember not to add hashtags to the caption
- Hashtags: (Generate relevant and engaging hashtags)

---
after analyzing the caption, you will generate a new image based on the original image
call generate_image with the following prompt:
Write a highly detailed text prompt suitable for an AI image generation model (like Stable Diffusion). It should clearly describe the scene, style, colors, mood, and any key elements to recreate a similar vibe visually.the prompt should be based on the original and very similar to the original image. 

save the new image generated_image.png and show caption and hashtags in the output. if image generation failed show only caption and hashtags and an error message for image generation


---



"""





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