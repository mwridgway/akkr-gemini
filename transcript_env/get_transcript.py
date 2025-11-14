import json
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# Configuration
VIDEO_ID = "GAEwE7BgjMs"
JSON_FILENAME = "IEM_Melbourne_2025_Full.json"
TXT_FILENAME = "IEM_Melbourne_2025_Readable.txt"

def main():
    print(f"--- Fetching transcript for Video ID: {VIDEO_ID} ---")
    
    try:
        # 1. Instantiate the API
        api = YouTubeTranscriptApi()

        # 2. Fetch the raw transcript object
        fetched_transcript = api.fetch(VIDEO_ID)
        
        # 3. Save as Structured JSON (Best for analysis/parsing)
        # Manually convert snippet objects to a list of dictionaries using dot notation
        raw_transcript = [
            {'text': snippet.text, 'start': snippet.start, 'duration': snippet.duration}
            for snippet in fetched_transcript
        ]
        with open(JSON_FILENAME, 'w', encoding='utf-8') as json_file:
            json.dump(raw_transcript, json_file, indent=4)
        print(f"✅ Success! Structured JSON saved to: {JSON_FILENAME}")

        # 4. Save as Readable Text (Best for reading)
        formatter = TextFormatter()
        text_formatted = formatter.format_transcript(fetched_transcript)
        
        with open(TXT_FILENAME, 'w', encoding='utf-8') as text_file:
            text_file.write(text_formatted)
        print(f"✅ Success! Readable Text saved to: {TXT_FILENAME}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Note: This video might not have captions enabled, or they might be auto-generated only.")

if __name__ == "__main__":
    main()
