import webview
import sys

def launch_streaming(url=None):
    """
    Launch a pywebview window in full-screen mode to stream content.

    Args:
        url (str): The URL of the content to stream.
    """
    try:
        # Default streaming URL if none is provided
        default_url = "http://example.com/stream"
        stream_url = url if url else default_url

        # Open the streaming URL in a pywebview window
        print(f"Launching streaming URL: {stream_url}")
        webview.create_window("Streaming", stream_url, fullscreen=True)
        webview.start()
    except Exception as e:
        print(f"Error launching streaming URL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Accept URL as a command-line argument if provided
    if len(sys.argv) > 1:
        launch_streaming(sys.argv[1])
    else:
        launch_streaming()
