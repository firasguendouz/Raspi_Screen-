#!/usr/bin/env python3
"""
UI Manager for Raspberry Pi Screen Management
Provides a responsive interface with real-time updates and QR code integration.
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

import webview
import websockets
from PIL import Image

from server.qr_code import QRCodeCache, generate_wifi_qr
from server.utils import setup_logging, validate_color

# Configure logging
logger = setup_logging(__name__)

@dataclass
class UIState:
    """Current UI state and configuration."""
    current_state: str = 'INIT'
    theme: str = 'light'
    qr_visible: bool = False
    error_state: Optional[str] = None
    last_update: float = time.time()

class UIManager:
    """Manages the UI components and state transitions."""
    
    # Screen states with messages and timeouts
    STATES = {
        'INIT': {
            'message': 'Initializing...',
            'color': '#007bff',
            'timeout': 5
        },
        'SCANNING': {
            'message': 'Scanning networks...',
            'color': '#ffc107',
            'timeout': 30
        },
        'CONNECTING': {
            'message': 'Connecting to network...',
            'color': '#17a2b8',
            'timeout': 60
        },
        'SUCCESS': {
            'message': 'Connected successfully!',
            'color': '#28a745',
            'timeout': 10
        },
        'ERROR': {
            'message': 'Connection failed',
            'color': '#dc3545',
            'timeout': 15
        }
    }

    # Visual themes
    THEMES = {
        'light': {
            'background': '#ffffff',
            'text': '#000000',
            'accent': '#007bff'
        },
        'dark': {
            'background': '#1a1a1a',
            'text': '#ffffff',
            'accent': '#00a0ff'
        }
    }

    # Error states and recovery actions
    ERROR_STATES = {
        'NETWORK_ERROR': {
            'message': 'Network unavailable',
            'action': 'retry_connection'
        },
        'TIMEOUT': {
            'message': 'Operation timed out',
            'action': 'show_help_qr'
        },
        'OFFLINE': {
            'message': 'Working offline',
            'action': 'activate_offline_mode'
        }
    }

    def __init__(self, window_title: str = "Raspberry Pi Screen Manager"):
        """Initialize the UI Manager."""
        self.window_title = window_title
        self.state = UIState()
        self.window = None
        self.qr_cache = QRCodeCache()
        self.websocket = None
        self.callbacks = {}
        self.retry_count = 0
        self.max_retries = 3

    async def initialize(self):
        """Initialize UI components and WebSocket connection."""
        try:
            # Create window with initial HTML
            self.window = webview.create_window(
                self.window_title,
                html=self._generate_initial_html(),
                js_api=self
            )
            
            # Connect WebSocket
            await self.connect_websocket()
            
            # Set initial state
            await self.update_state('INIT')
            
            logger.info("UI Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize UI: {e}")
            await self.handle_error('INIT_ERROR')

    async def connect_websocket(self):
        """Establish WebSocket connection for real-time updates."""
        try:
            self.websocket = await websockets.connect('ws://localhost:5000/ws')
            asyncio.create_task(self._handle_websocket_messages())
            logger.info("WebSocket connection established")
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            await self.handle_error('NETWORK_ERROR')

    async def update_state(self, new_state: str):
        """Update UI state with transitions and animations."""
        if new_state not in self.STATES:
            logger.error(f"Invalid state: {new_state}")
            return

        old_state = self.state.current_state
        self.state.current_state = new_state
        self.state.last_update = time.time()

        state_config = self.STATES[new_state]
        
        # Update UI
        await self._update_ui_elements(state_config)
        
        # Schedule automatic transition
        if state_config['timeout'] > 0:
            asyncio.create_task(
                self._schedule_transition(state_config['timeout'])
            )

        logger.info(f"State updated: {old_state} -> {new_state}")

    async def display_qr(self, data: Dict[str, Any], fallback: bool = True):
        """Display QR code with optional fallback."""
        try:
            # Generate primary QR code
            qr_path = await self._generate_qr(data)
            
            # Update UI with QR code
            await self._update_qr_display(qr_path)
            
            # Generate fallback QR if needed
            if fallback:
                fallback_data = self._generate_fallback_data()
                fallback_path = await self._generate_qr(fallback_data)
                await self._update_fallback_qr(fallback_path)
                
            self.state.qr_visible = True
            
        except Exception as e:
            logger.error(f"Failed to display QR code: {e}")
            await self.handle_error('QR_ERROR')

    async def handle_error(self, error_type: str):
        """Handle errors and display recovery options."""
        if error_type not in self.ERROR_STATES:
            logger.error(f"Unknown error type: {error_type}")
            error_type = 'NETWORK_ERROR'  # Default error

        error_config = self.ERROR_STATES[error_type]
        self.state.error_state = error_type

        # Update UI with error
        await self._update_error_display(error_config)

        # Execute recovery action
        action = error_config['action']
        if hasattr(self, action):
            await getattr(self, action)()

        # Increment retry count
        self.retry_count += 1

    async def retry_connection(self):
        """Retry failed connection with exponential backoff."""
        if self.retry_count >= self.max_retries:
            logger.warning("Max retries reached")
            await self.show_help_qr()
            return

        delay = 2 ** self.retry_count
        await asyncio.sleep(delay)
        await self.update_state('INIT')

    async def show_help_qr(self):
        """Display help QR code with troubleshooting info."""
        help_data = {
            'type': 'help',
            'url': 'https://example.com/help',
            'message': 'Scan for troubleshooting'
        }
        await self.display_qr(help_data, fallback=False)

    async def activate_offline_mode(self):
        """Switch to offline mode with limited functionality."""
        logger.info("Activating offline mode")
        await self._update_ui_elements({
            'message': 'Working offline',
            'color': '#6c757d'
        })

    def _generate_initial_html(self) -> str:
        """Generate initial HTML template."""
        theme = self.THEMES[self.state.theme]
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    background-color: {theme['background']};
                    color: {theme['text']};
                    font-family: 'Roboto', system-ui, sans-serif;
                    margin: 0;
                    padding: 20px;
                    display: flex;
                    flex-direction: column;
                    height: 100vh;
                }}
                #status-bar {{
                    height: 60px;
                    background-color: {theme['accent']};
                    padding: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }}
                #content {{
                    flex-grow: 1;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }}
                #feedback {{
                    height: 60px;
                    padding: 10px;
                    text-align: center;
                }}
                .qr-container {{
                    position: relative;
                    width: 300px;
                    height: 300px;
                }}
                .qr-fallback {{
                    position: absolute;
                    bottom: 10px;
                    right: 10px;
                    width: 100px;
                    height: 100px;
                }}
                @keyframes pulse {{
                    0% {{ transform: scale(1); }}
                    50% {{ transform: scale(1.05); }}
                    100% {{ transform: scale(1); }}
                }}
                .pulse {{
                    animation: pulse 2s infinite;
                }}
            </style>
        </head>
        <body>
            <div id="status-bar">
                <span id="status-message">Initializing...</span>
                <span id="status-time"></span>
            </div>
            <div id="content">
                <div class="qr-container">
                    <img id="qr-main" style="display: none;">
                    <img id="qr-fallback" class="qr-fallback" style="display: none;">
                </div>
            </div>
            <div id="feedback"></div>
            <script>
                // JavaScript for UI updates and animations
                function updateStatus(message, color) {{
                    const statusBar = document.getElementById('status-bar');
                    const statusMessage = document.getElementById('status-message');
                    statusBar.style.backgroundColor = color;
                    statusMessage.textContent = message;
                }}

                function updateQR(mainSrc, fallbackSrc) {{
                    const mainQR = document.getElementById('qr-main');
                    const fallbackQR = document.getElementById('qr-fallback');
                    
                    if (mainSrc) {{
                        mainQR.src = mainSrc;
                        mainQR.style.display = 'block';
                    }}
                    
                    if (fallbackSrc) {{
                        fallbackQR.src = fallbackSrc;
                        fallbackQR.style.display = 'block';
                    }}
                }}

                function showError(message) {{
                    const feedback = document.getElementById('feedback');
                    feedback.textContent = message;
                    feedback.style.color = '#dc3545';
                }}
            </script>
        </body>
        </html>
        """

    async def _update_ui_elements(self, config: Dict[str, str]):
        """Update UI elements with new configuration."""
        if not self.window:
            return

        js_code = f"""
        updateStatus(
            "{config['message']}",
            "{config['color']}"
        );
        """
        await self.window.evaluate_js(js_code)

    async def _update_qr_display(self, qr_path: str):
        """Update QR code display."""
        if not self.window:
            return

        js_code = f"""
        updateQR("{qr_path}", null);
        """
        await self.window.evaluate_js(js_code)

    async def _update_fallback_qr(self, qr_path: str):
        """Update fallback QR code display."""
        if not self.window:
            return

        js_code = f"""
        updateQR(null, "{qr_path}");
        """
        await self.window.evaluate_js(js_code)

    async def _update_error_display(self, error_config: Dict[str, str]):
        """Update error display."""
        if not self.window:
            return

        js_code = f"""
        showError("{error_config['message']}");
        """
        await self.window.evaluate_js(js_code)

    async def _generate_qr(self, data: Dict[str, Any]) -> str:
        """Generate QR code and return its path."""
        try:
            if data.get('type') == 'wifi':
                return generate_wifi_qr(
                    ssid=data['ssid'],
                    password=data['password'],
                    security=data.get('security', 'WPA'),
                    color=data.get('color', '#000000')
                )
            else:
                # Generate generic QR code
                return self.qr_cache.get_or_generate(
                    json.dumps(data),
                    color=data.get('color', '#000000')
                )
        except Exception as e:
            logger.error(f"Failed to generate QR code: {e}")
            raise

    def _generate_fallback_data(self) -> Dict[str, Any]:
        """Generate fallback QR code data."""
        return {
            'type': 'help',
            'url': 'https://example.com/help',
            'message': 'Need help? Scan this code'
        }

    async def _schedule_transition(self, timeout: int):
        """Schedule state transition after timeout."""
        await asyncio.sleep(timeout)
        
        # Check if we should still transition
        if time.time() - self.state.last_update >= timeout:
            next_state = self._get_next_state()
            if next_state:
                await self.update_state(next_state)

    def _get_next_state(self) -> Optional[str]:
        """Get next state based on current state."""
        state_flow = {
            'INIT': 'SCANNING',
            'SCANNING': 'CONNECTING',
            'CONNECTING': 'SUCCESS',
            'SUCCESS': None,
            'ERROR': 'INIT'
        }
        return state_flow.get(self.state.current_state)

    async def _handle_websocket_messages(self):
        """Handle incoming WebSocket messages."""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                message_type = data.get('type')
                
                if message_type in self.callbacks:
                    await self.callbacks[message_type](data)
                else:
                    logger.warning(f"Unknown message type: {message_type}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.error("WebSocket connection closed")
            await self.handle_error('NETWORK_ERROR')
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await self.handle_error('NETWORK_ERROR')

    def register_callback(self, message_type: str, callback: Callable):
        """Register callback for WebSocket message type."""
        self.callbacks[message_type] = callback

    def run(self):
        """Run the UI manager."""
        webview.start()
