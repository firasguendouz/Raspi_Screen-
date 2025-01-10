import webbrowser
import sys

def launch_streaming(url=None):
    """
    Launch the default web browser in kiosk mode to stream content.

    Args:
        url (str): The URL of the content to stream.
    """
    try:
        # Default streaming URL if none is provided
        default_url = "http://example.com/stream"
        stream_url = url if url else default_url

        # Open the URL in the default web browser
        print(f"Launching streaming URL: {stream_url}")
        webbrowser.open(stream_url)

    except Exception as e:
        print(f"Error launching streaming URL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Accept URL as a command-line argument if provided
    if len(sys.argv) > 1:
        launch_streaming(sys.argv[1])
    else:
        launch_streaming()
