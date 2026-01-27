# YouTube Transcript Extractor

A robust Python tool to extract transcripts from YouTube videos using the `youtube-transcript-api`. This tool allows you to fetch transcripts in multiple languages, with or without timestamps, and save them to text files.

## Features

- **Multiple URL Formats**: Supports standard YouTube URLs, short URLs (`youtu.be`), and direct video IDs.
- **Language Support**: Automatically attempts to fetch transcripts in preferred languages (defaulting to English) with a fallback mechanism.
- **Auto-generated & Manual**: Retrieves both manually created captions and auto-generated ones.
- **Formatting**: Output includes timestamps (e.g., `[00:01] Text`) or plain text.
- **Chunking**: Option to split long transcripts into smaller chunks (useful for LLM contexts).
- **CLI & Module**: Can be used as a command-line interface or imported as a Python module.

## Prerequisites

- Python 3.6 or higher
- `pip` package manager

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/youtube-transcript-extractor.git
   cd youtube-transcript-extractor
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Interface

Run the script directly via terminals:

```bash
# Basic usage (defaults to English, saves to file)
python main.py https://www.youtube.com/watch?v=VIDEO_ID

# Get video info and available languages
python main.py VIDEO_ID --info

# Specify preferred languages (e.g., German then English)
python main.py VIDEO_ID -l de en

# Save to specific output file without timestamps
python main.py VIDEO_ID -o transcript.txt --no-timestamps

# Split into chunks of 1000 characters
python main.py VIDEO_ID --chunk-size 1000
```

### Python Module

You can also import and use the extractor in your own Python scripts:

```python
from main import extract_youtube_transcript

# Get transcript data
result = extract_youtube_transcript(
    url="https://www.youtube.com/watch?v=VIDEO_ID",
    languages=['en', 'es'],
    include_timestamps=True
)

print(f"Video ID: {result['video_id']}")
print(f"Language: {result['language']}")
print(result['text'])
```

## Output Format

**With Timestamps:**
```text
[00:01] All right, so here we are, in front of the elephants
[00:05] the cool thing about these guys is that they have really...
```

**Without Timestamps:**
```text
All right, so here we are, in front of the elephants the cool thing about these guys is that they have really...
```

## License

[MIT](LICENSE)
