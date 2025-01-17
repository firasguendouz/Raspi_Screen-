import webview
import os
import base64
from pathlib import Path
import pkg_resources

# Get version and backend info
try:
    version = pkg_resources.get_distribution('pywebview').version
    print(f"PyWebView version: {version}")
    print(f"Using backend: {webview.initialize()}")
except Exception as e:
    print(f"Backend detection error: {e}")

def image_to_data_url(image_path):
    with open(image_path, 'rb') as img_file:
        img_data = base64.b64encode(img_file.read()).decode()
        return f'data:image/png;base64,{img_data}'

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Image Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        #debug { background: #f0f0f0; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>Image Display Test</h1>
    <div id="debug"></div>
    <img id="testImage" style="max-width: 300px; border: 1px solid #ccc;"/>
    
    <script>
        function log(msg) {
            const debug = document.getElementById('debug');
            debug.innerHTML += `<div>${msg}</div>`;
            console.log(msg);
        }

        function loadImage(dataUrl) {
            log('Attempting to load image...');
            const img = document.getElementById('testImage');
            
            img.onerror = () => {
                log('Error: Failed to load image');
            };
            
            img.onload = () => {
                log('Success: Image loaded');
                log(`Image size: ${img.naturalWidth}x${img.naturalHeight}`);
            };
            
            img.src = dataUrl;
        }
    </script>
</body>
</html>
"""

def main():
    image_path = Path(__file__).parent / "test_qr.png"
    
    if not image_path.exists():
        print(f"Error: Image not found at {image_path}")
        return
    
    print(f"Image path: {image_path}")
    print(f"Image size: {image_path.stat().st_size} bytes")
    print(f"Image permissions: {oct(image_path.stat().st_mode)[-3:]}")
    
    # Convert image to data URL
    data_url = image_to_data_url(image_path)
    print("Generated data URL")
    
    # Create window with compatible parameters
    window = webview.create_window(
        'Image Test', 
        html=html,
        width=800,
        height=600
    )
    
    def load_test_image():
        window.evaluate_js(f"loadImage('{data_url}')")
    
    webview.start(load_test_image)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")