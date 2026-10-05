# Post Generator

An AI agent that takes an Instagram post (or a direct image) and produces a fresh, original "twin" post: a new caption, a set of hashtags, and a newly generated image that is visually faithful to the original. After you approve the caption, the agent uploads the result to Instagram.

Built with LangChain, Google Gemini, Hugging Face, and Selenium.

## How It Works

1. **Input**: you paste the URL of a public Instagram post (or a path to an image).
2. **Extract**: the agent scrapes the post's caption, hashtags, and image using headless Chrome.
3. **Analyze**: the image is described (subjects, setting, mood, colors, composition) using the BLIP image-captioning model.
4. **Write**: Gemini writes a new caption in fresh wording and generates 15-20 relevant hashtags.
5. **Generate**: Gemini builds a detailed image prompt, and FLUX.1-dev (via the Hugging Face Inference API) generates the new image, saved as `generated_image.png`.
6. **Approve**: the agent shows you the caption and asks for approval. If you decline, it writes a new caption and asks again, repeating until you approve.
7. **Upload**: once approved, the image and caption are posted to Instagram.

## Project Structure

| File | Purpose |
| --- | --- |
| `model.py` | Entry point. Sets up the Gemini LLM, the LangChain structured-chat agent, memory, and runs the agent on your input. |
| `prompt.py` | The custom system prompt that defines the agent's workflow and rules. |
| `tool.py` | The agent's tools: `analyze_image`, `generate_image`, `search_web`, `extract_instagram_post`, `upload_post`, `humman_approval`. |
| `requirements.txt` | Python dependencies. |
| `generated_image.png` | Output image from the most recent run. |
| `instagram_image.jpg` | The original image downloaded from the most recent run. |

## Tools

- **`extract_instagram_post`**: scrapes the caption, hashtags, and image from a public post with headless Chrome and saves the image as `instagram_image.jpg`.
- **`analyze_image`**: describes a local image with `Salesforce/blip-image-captioning-base`.
- **`generate_image`**: generates an image with `black-forest-labs/FLUX.1-dev` through the Hugging Face Inference API.
- **`search_web`**: web search via Tavily.
- **`humman_approval`**: asks you in the terminal to approve the caption (`y` / `yes` to approve; anything else counts as a no).
- **`upload_post`**: logs in with `instagrapi` and uploads the photo with its caption.

## Prerequisites

- Python 3.10+
- Google Chrome and a matching ChromeDriver (used by Selenium)
- API keys / accounts:
  - [Google AI Studio](https://aistudio.google.com/) API key (Gemini)
  - [Hugging Face](https://huggingface.co/settings/tokens) access token (image generation)
  - [Tavily](https://tavily.com/) API key (web search)
  - An Instagram account for posting

## Installation

```bash
git clone https://github.com/abdullahrasheed102/post-generator.git
cd post-generator

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

> **Note:** if `pip install` fails on `dotenv` or `BeautifulSoup`, install the correct package names instead: `pip install python-dotenv beautifulsoup4`. The first run also downloads the BLIP model, which needs some disk space and a little time.

## Configuration

Create a `.env` file in the project root (it is already in `.gitignore`, so it won't be committed):

```env
GOOGLE_API_KEY=your_google_gemini_api_key
HF_TOKEN=your_huggingface_token
TAVILY_API_KEY=your_tavily_api_key
username=your_instagram_username
password=your_instagram_password
```

Never commit this file or share these credentials.

## Usage

```bash
python model.py
```

When prompted, enter the Instagram post URL:

```
Enter the path to the post: https://www.instagram.com/p/XXXXXXXXXXX/
```

The agent then runs through the steps above, prints its reasoning (`verbose=True`), and asks you to approve the caption in the terminal before anything is posted.

## Notes and Limitations

- Only **public** Instagram posts can be scraped, and Instagram's page layout can change, which may break extraction.
- Automated logins and uploads through `instagrapi` can trigger Instagram's security checks or violate its terms of service. Consider using a test account.
- Image generation depends on the Hugging Face Inference API, so rate limits, model availability, and access to FLUX.1-dev apply.
- Only repost or recreate content you have the right to use, and respect the original creator's rights.

## Tech Stack

- [LangChain](https://www.langchain.com/) (structured chat agent, tools, memory)
- [Google Gemini](https://ai.google.dev/) (reasoning and copywriting)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers) (BLIP image captioning)
- [FLUX.1-dev](https://huggingface.co/black-forest-labs/FLUX.1-dev) (image generation)
- [Tavily](https://tavily.com/) (web search)
- [Selenium](https://www.selenium.dev/) + [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) (scraping)
- [instagrapi](https://github.com/subzeroid/instagrapi) (Instagram upload)
