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

This function should return a comprehensive and structured scene description, including:

Subjects: Who or what is in the image (e.g., a woman, a couple, a dog, etc.).

Facial features and identity markers (if people are present): Describe hair, face orientation, expressions, ethnicity if evident, and any unique characteristics.

Environment/Background: Where the scene is set (e.g., brick wall, beach, urban street).

Mood and Tone: Emotional atmosphere (e.g., calm, confident, energetic).

Artistic Style: Realism, editorial, cinematic, street photography, etc.

Colors and Lighting: Dominant color palette, lighting type (e.g., soft daylight, studio light, warm evening glow).

Composition and Camera Angle: Full-body vs. close-up, angle (eye-level, low, high), background blur, symmetry, etc.

Create a New Social Media Post

Use the image analysis and caption to:

Write a new caption that reflects a similar idea, theme, or emotion, but uses fresh wording.

Generate at least 15 to 20 relevant and engaging hashtags related to the new caption and theme.

Avoid using hashtags in the caption itself.

Image Generation:
Using the image analysis, generate a detailed prompt for creating a new image that closely resembles the original. The generated image should feel like a fresh but visually faithful twin to the original.

Your prompt must include:

Visual Elements: Clearly describe the main subjects, background, and any notable objects in the scene.

Art Style: Specify the style (e.g., realistic photography, cinematic, editorial, cartoonish, etc.).

Color and Lighting: Mention dominant color tones and lighting conditions (e.g., soft natural light, cool tones, golden hour, etc.).

Mood and Tone: Convey the emotional feel of the image (e.g., confident, calm, stylish, dramatic, serene).

Camera Perspective and Composition: Include details like full-body vs. close-up, angle, depth of field, etc.

Important Note:
If the image contains a person, describe their appearance in precise detail, and make it explicit in the prompt that their facial features, identity, and core appearance must remain unchanged. Only the setting, outfit, or lighting may vary subtly to make the new image unique but still clearly based on the same individual.



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