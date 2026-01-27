import os
import sys
import re
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import argparse
from datetime import datetime

class YouTubeTranscriptExtractor:
    def __init__(self):
        self.supported_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh']

    def extract_video_id(self, url):
        """Extract video ID from various YouTube URL formats"""
        # Handle different YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # If it's already just a video ID
        if len(url) == 11 and url.isalnum():
            return url

        raise ValueError("Invalid YouTube URL or video ID")

    def get_transcript(self, video_id, languages=['en']):
        """Get transcript for a video with language preferences"""
        try:
            # Try to get transcript in preferred languages
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # First try manually created transcripts in preferred languages
            for lang in languages:
                try:
                    transcript = transcript_list.find_manually_created_transcript([lang])
                    return transcript.fetch(), lang, 'manual'
                except:
                    continue

            # Then try auto-generated transcripts in preferred languages
            for lang in languages:
                try:
                    transcript = transcript_list.find_generated_transcript([lang])
                    return transcript.fetch(), lang, 'auto-generated'
                except:
                    continue

            # If no preferred language found, get any available transcript
            try:
                transcript = transcript_list.find_transcript(['en'])
                return transcript.fetch(), 'en', 'fallback'
            except:
                # Get first available transcript
                available_transcripts = list(transcript_list)
                if available_transcripts:
                    transcript = available_transcripts[0]
                    return transcript.fetch(), transcript.language_code, 'available'
                else:
                    raise Exception("No transcripts available")

        except Exception as e:
            raise Exception(f"Error fetching transcript: {str(e)}")

    def format_transcript(self, transcript_data, include_timestamps=True, chunk_size=None):
        """Format transcript data into readable text"""
        if include_timestamps:
            formatted_text = []
            for entry in transcript_data:
                timestamp = self.seconds_to_timestamp(entry['start'])
                text = entry['text'].strip()
                formatted_text.append(f"[{timestamp}] {text}")
            result = '\n'.join(formatted_text)
        else:
            # Just concatenate all text
            result = ' '.join([entry['text'].strip() for entry in transcript_data])
            # Clean up extra spaces
            result = re.sub(r'\s+', ' ', result).strip()

        # If chunk_size is specified, split into chunks
        if chunk_size and not include_timestamps:
            chunks = [result[i:i+chunk_size] for i in range(0, len(result), chunk_size)]
            return chunks

        return result

    def seconds_to_timestamp(self, seconds):
        """Convert seconds to MM:SS or HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    def save_to_file(self, text, filename=None, video_id=None):
        """Save transcript to a text file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"youtube_transcript_{video_id}_{timestamp}.txt"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(text)
            return filename
        except Exception as e:
            raise Exception(f"Error saving file: {str(e)}")

    def get_video_info(self, video_id):
        """Get basic video information"""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            available_languages = []
            for transcript in transcript_list:
                lang_info = {
                    'language': transcript.language,
                    'language_code': transcript.language_code,
                    'is_generated': transcript.is_generated
                }
                available_languages.append(lang_info)

            return {
                'video_id': video_id,
                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                'available_languages': available_languages
            }
        except Exception as e:
            raise Exception(f"Error getting video info: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Extract transcripts from YouTube videos')
    parser.add_argument('url', help='YouTube video URL or video ID')
    parser.add_argument('-l', '--languages', nargs='+', default=['en'],
                       help='Preferred languages (default: en)')
    parser.add_argument('-o', '--output', help='Output filename')
    parser.add_argument('--no-timestamps', action='store_true',
                       help='Exclude timestamps from output')
    parser.add_argument('--chunk-size', type=int,
                       help='Split text into chunks of specified size (characters)')
    parser.add_argument('--info', action='store_true',
                       help='Show video info and available languages')

    args = parser.parse_args()

    extractor = YouTubeTranscriptExtractor()

    try:
        # Extract video ID
        video_id = extractor.extract_video_id(args.url)
        print(f"Processing video ID: {video_id}")

        # Show video info if requested
        if args.info:
            info = extractor.get_video_info(video_id)
            print(f"\nVideo URL: {info['video_url']}")
            print("Available transcripts:")
            for lang in info['available_languages']:
                status = "Auto-generated" if lang['is_generated'] else "Manual"
                print(f"  - {lang['language']} ({lang['language_code']}) - {status}")
            return

        # Get transcript
        print(f"Fetching transcript in languages: {args.languages}")
        transcript_data, language, source = extractor.get_transcript(video_id, args.languages)
        print(f"Found transcript in '{language}' ({source})")

        # Format transcript
        include_timestamps = not args.no_timestamps
        formatted_text = extractor.format_transcript(
            transcript_data,
            include_timestamps=include_timestamps,
            chunk_size=args.chunk_size
        )

        # Handle chunked output
        if isinstance(formatted_text, list):
            print(f"Text split into {len(formatted_text)} chunks")
            for i, chunk in enumerate(formatted_text, 1):
                filename = args.output or f"transcript_chunk_{i}_{video_id}.txt"
                if len(formatted_text) > 1:
                    base, ext = os.path.splitext(filename)
                    filename = f"{base}_chunk_{i}{ext}"

                saved_file = extractor.save_to_file(chunk, filename, video_id)
                print(f"Chunk {i} saved to: {saved_file}")
        else:
            # Save to file
            saved_file = extractor.save_to_file(formatted_text, args.output, video_id)
            print(f"Transcript saved to: {saved_file}")

            # Show preview
            preview = formatted_text[:500] + "..." if len(formatted_text) > 500 else formatted_text
            print(f"\nPreview:\n{preview}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

# Example usage as a module
def extract_youtube_transcript(url, languages=['en'], include_timestamps=False, chunk_size=None):
    """
    Simple function to extract YouTube transcript

    Args:
        url: YouTube URL or video ID
        languages: List of preferred languages
        include_timestamps: Whether to include timestamps
        chunk_size: Split into chunks of this size (characters)

    Returns:
        String or list of strings (if chunked)
    """
    extractor = YouTubeTranscriptExtractor()

    try:
        video_id = extractor.extract_video_id(url)
        transcript_data, language, source = extractor.get_transcript(video_id, languages)

        formatted_text = extractor.format_transcript(
            transcript_data,
            include_timestamps=include_timestamps,
            chunk_size=chunk_size
        )

        return {
            'text': formatted_text,
            'language': language,
            'source': source,
            'video_id': video_id
        }
    except Exception as e:
        raise Exception(f"Failed to extract transcript: {str(e)}")

if __name__ == "__main__":
    main()