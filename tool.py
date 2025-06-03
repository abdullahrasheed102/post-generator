import os, json
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from langchain_core.tools import tool
from requests import post
from io import BytesIO
from langchain_tavily import TavilySearch
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
import re
from instagrapi import Client


load_dotenv()


processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

username = os.getenv("username")
password = os.getenv("password")


@tool
def analyze_image(image_path: str) -> str:
    """
    Generate detailed scene description (including subjects, environment, mood, style, colors, and composition
    Args:
        image_path (str): Full path to a local image file
    Returns:
        str: Generated caption/description for the similar image but unique.
    """
    if not os.path.exists(image_path):
        return "Error: Image file not found at the specified path."

    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(image, return_tensors="pt")

        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)

        return f" Description: {caption}"

    except Exception as e:
        return f" Error during image analysis: {str(e)}"
    



@tool
def generate_image(prompt: str) -> str:
    """
    Generate an image using the Hugging Face image generation API (e.g., FLUX.1-dev model).

    Args:
        prompt (str): The text prompt describing the unique image.

    Returns:
        str: Path to the saved image or error message.
    """
    api_token = os.getenv("HF_TOKEN")
    headers = {
        "Authorization": f"Bearer {api_token}"
    }

    model_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
    payload = {"inputs": prompt}

    try:
        response = post(model_url, headers=headers, json=payload)

        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image_path = "generated_image.png"
            image.save(image_path)
            
            return f"Image generate successfuly {image_path}"
        else:
            return f"Image generation failed: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Exception occurred during image generation: {str(e)}"


@tool
def search_web(query: str) ->  str:
    """
    Search the web using Tavily API for the given query.

    Args:
        query (str): The search query.

    Returns:
        str: Search results or error message.
    """
    try:
        tavily_search = TavilySearch()
        results = tavily_search.search(query)
        return f"Search results: {results}"
    except Exception as e:
        return f"Error during web search: {str(e)}"
    

@tool
def extract_instagram_post(url: str) -> dict:
    """
    Extract caption text, hashtags, and image URL from a public Instagram post.
    """

    # Setup headless Chrome
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    try:
        # Load Instagram post
        driver.get(url)
        driver.implicitly_wait(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # --- Extract Caption ---
        caption = ""
        hashtags = []

        og_desc = soup.find("meta", attrs={"property": "og:description"})
        if og_desc:
            desc = og_desc.get("content", "")
            # Get caption inside quotes
            match = re.search(r'“(.+?)”', desc) or re.search(r'"(.+?)"', desc)
            if match:
                caption = match.group(1).strip()
            # Extract hashtags
            hashtags = re.findall(r'#\w+', desc)

        # --- Extract Image URL ---
        og_img = soup.find("meta", attrs={"property": "og:image"})
        image_url = og_img["content"] if og_img else None

        # --- Download Image (optional) ---
        image_path = None
        if image_url:
            img_data = requests.get(image_url).content
            image_path = "instagram_image.jpg"
            with open(image_path, "wb") as f:
                f.write(img_data)

        return {
            "caption": caption,
            "hashtags": hashtags,
            "image_url": image_url,
            "image_path": image_path
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        driver.quit()

@tool
def upload_post(caption: str , image_path: str)-> str:
    """get generated data and upload post on instagram"""
    cl = Client()
    cl.login(username, password)

    try:
        cl.photo_upload(path=image_path, caption=caption)
        return("Image uploaded successfully")
    except Exception as e:
        return(f"Error uploading image: {e}")
    
@tool
def humman_approval(caption:str) ->str:
    """Show user caption and ask for the approval """
    input_msg = (
        f"Do you approve of the following post content\n\n{caption}\n\n"
        "Anything except 'Y'/'Yes' (case-insensitive) will be treated as a no.\n >>>"
    )
    response = input(input_msg)
    if response.lower() in ("yes", "y"):
        return f"Caption approved by the user"
    else:
        return f"Caption not approved by the user"