import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

def main():
    url = input("Paste a YouTube URL: ")
    print("\nFetching transcript...")
    transcript = get_transcript(url)
    print("Summarizing with AI...\n")
    notes = summarize(transcript)
    print(notes)

if __name__ == "__main__":
    main()