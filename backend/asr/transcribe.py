import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import aiofiles
import openai
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

print("DEBUG: OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))
router = APIRouter()

@router.post("/", summary="Transcribe audio file using OpenAI Whisper")
async def transcribe_audio(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("audio/"):
        # 允许 application/octet-stream 也通过
        if file.content_type != "application/octet-stream":
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid file type. Please upload an audio file.")
    try:
        # Save uploaded file to a temporary location
        suffix = os.path.splitext(file.filename)[-1] or ".wav"
        async with aiofiles.tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_path = tmp.name
            content = await file.read()
            await tmp.write(content)
        # Use OpenAI Whisper API for transcription (openai>=1.0.0)
        with open(temp_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        os.remove(temp_path)
        return JSONResponse(content={"transcript": transcript.text})
    except Exception as e:
        print("DEBUG ERROR:", e)  # 打印到终端
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}") 