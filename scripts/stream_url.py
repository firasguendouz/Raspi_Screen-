import webbrowser
import sys

def open_stream_url(url=None):
    # Default streaming URL if none provided
    default_url = "https://www.youtube.com"
    stream_url = url if url else default_url
    
    try:
        # Open URL in default browser
        webbrowser.open(stream_url)
        print(f"Opening stream at: {stream_url}")
    except Exception as e:
        print(f"Error opening stream: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Accept URL as command line argument if provided
    if len(sys.argv) > 1:
        open_stream_url(sys.argv[1])
    else:
        open_stream_url()