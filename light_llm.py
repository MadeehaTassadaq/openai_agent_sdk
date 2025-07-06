from litellm import completion
import os
from dotenv import load_dotenv
load_dotenv()
gemini_api_key=os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("Gemini_api_key is not defined")

response=completion(model="gemini/gemini-2.0-flash",
                    api_key=gemini_api_key,
                    messages=[
                        {"role":"user",
                         "content":"hello ,how are you"}
                    ],
                    temperature=0.5,
                    max_tokens=100)

print(response.choices[0].message.content)