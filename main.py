import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq

load_dotenv()

app = FastAPI()

# This allows your frontend to talk to your backend later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# This defines what the incoming request should look like
class VideoRequest(BaseModel):
    url: str

def get_transcript(video_url):
    video_id = video_url.split("v=")[-1].split("&")[0]
    ytt = YouTubeTranscriptApi()
    transcript_data = ytt.fetch(video_id)
    full_transcript = " ".join([chunk.text for chunk in transcript_data])
    return full_transcript

def summarize(transcript):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"""You are a smart note-taking assistant.

Given the following YouTube video transcript, create structured notes with:
- A short summary (3-4 sentences)
- Key points (bullet list)
- Important terms or concepts mentioned

Transcript:
{transcript}"""
            }
        ]
    )
    return response.choices[0].message.content

@app.get("/")
def root():
    return {"message": "YouTube Notes API is running!"}

@app.post("/summarize")
def summarize_video(request: VideoRequest):
    try:
        transcript = get_transcript(request.url)
        notes = summarize(transcript)
        return {"notes": notes}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))