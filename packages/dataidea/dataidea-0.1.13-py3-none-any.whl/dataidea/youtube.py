import yt_dlp

def download(url:str=None, output_folder:str=''):
    """
    Downloads YouTube video provided in the url

    Args:
        url:
        output_folder:

    Returns:

    """
    options = {
        'format': 'best',
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',  # Save with video title as the filename
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            print("\nDownloading video...")
            ydl.download([url])
            print("Download completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    download(url='https://www.youtube.com/watch?v=jJcqew3dQ9g')