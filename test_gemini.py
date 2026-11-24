
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
   http_options={"timeout": 60000}
)

print("Connecting to Gemini...")

response = client.models.generate_content(
     model="gemini-3.5-flash-lite",
    contents="Reply with only the word WORKING."
)

print("Gemini response:", response.text)
