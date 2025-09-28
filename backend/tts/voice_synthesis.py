# backend/tts/tts_service.py
import openai
from openai import OpenAI
import os
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) 

def stream_and_save_tts(text, voice="alloy", model="tts-1", save_path="tts_output.mp3"):
    try:
        with client.audio.speech.with_streaming_response.create(
            model=model,
            voice=voice,
            input=text
        ) as response:
            with open(save_path, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
                    yield chunk
    except Exception as e:
        import traceback
        print("TTS流式生成异常：", str(e))
        traceback.print_exc()
        # 必须raise，否则生成器提前终止，StreamingResponse会挂
        raise