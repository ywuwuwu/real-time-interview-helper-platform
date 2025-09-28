from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OpenAI.api_key =  OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)
prompt = f"请你自我介绍"
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)
print(response.choices[0].message.content)


models = client.models.list()
for m in models.data:
    print(m.id)

try:
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input="Today is a wonderful day to build something people love!",
        instructions="Speak in a cheerful and positive tone.",
    )
    print("你的API Key可以用OpenAI TTS API！")
except Exception as e:
    print("调用失败：", e)


