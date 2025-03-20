import os
import yt_dlp
import logging
import sys
import re

# Set up logging
logging.basicConfig(level=logging.INFO)

def is_valid_url(url: str) -> bool:
    """Check if the provided URL is a valid YouTube URL."""
    youtube_regex = r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$'
    return re.match(youtube_regex, url) is not None

def download(url: str = None, output_folder: str = ''):
    """
    Downloads YouTube video provided in the url

    Args:
        url: YouTube video URL
        output_folder: Directory to save the downloaded video

    Returns:
        None
    """
    if not url or not is_valid_url(url):
        logging.error("Invalid URL provided.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logging.info(f"Output folder '{output_folder}' created.")

    options = {
        'format': 'best',
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',  # Save with video title as the filename
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            logging.info("\nDownloading video...")
            ydl.download([url])
            logging.info("Download completed successfully!")
    except yt_dlp.utils.DownloadError as e:
        logging.error(f"Download error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        logging.error("Usage: python youtube.py <url> <output_folder>")
    else:
        download(url=sys.argv[1], output_folder=sys.argv[2])