#!/usr/bin/env python3
"""
URL Streaming Manager for Raspberry Pi Screen

This script manages URL streaming to the display, including:
- URL validation and sanitization
- Error handling and fallback content
- Connection monitoring
"""

import os
import sys
import time
import argparse
from typing import Optional

from utils import (
    setup_logging,
    load_config,
    validate_url,
    create_http_session,
    ConfigurationError,
    NetworkError
)

# Initialize logging
logger = setup_logging('stream_url')

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Stream URL to display')
    parser.add_argument('url', help='URL to stream')
    parser.add_argument('--fallback', help='Fallback URL or local content')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Connection timeout in seconds')
    parser.add_argument('--retry', type=int, default=3,
                       help='Number of retry attempts')
    return parser.parse_args()

def validate_and_prepare_url(url: str) -> str:
    """
    Validate and prepare URL for streaming.
    
    Args:
        url: URL to validate
        
    Returns:
        Validated and prepared URL
        
    Raises:
        ConfigurationError: If URL is invalid
    """
    if not validate_url(url):
        raise ConfigurationError(f"Invalid URL: {url}")
    
    # Ensure URL uses HTTPS if available
    if url.startswith('http://'):
        https_url = url.replace('http://', 'https://', 1)
        try:
            session = create_http_session()
            response = session.head(https_url, timeout=5)
            if response.status_code == 200:
                url = https_url
                logger.info("Upgraded to HTTPS connection")
        except Exception:
            logger.warning("HTTPS upgrade failed, using HTTP")
    
    return url

def check_url_availability(url: str, timeout: int = 5) -> bool:
    """
    Check if URL is available.
    
    Args:
        url: URL to check
        timeout: Request timeout in seconds
        
    Returns:
        True if URL is available, False otherwise
    """
    try:
        session = create_http_session()
        response = session.head(url, timeout=timeout)
        return response.status_code == 200
    except Exception as e:
        logger.warning(f"URL availability check failed: {str(e)}")
        return False

def load_fallback_content() -> Optional[str]:
    """
    Load fallback content from configuration.
    
    Returns:
        Fallback content URL or path, None if not configured
    """
    try:
        config = load_config('display')
        return config.get('fallback_content')
    except Exception as e:
        logger.warning(f"Failed to load fallback content: {str(e)}")
        return None

def stream_url(url: str, fallback: Optional[str] = None,
              timeout: int = 30, retry_count: int = 3) -> None:
    """
    Stream URL to display with fallback and retry mechanism.
    
    Args:
        url: URL to stream
        fallback: Fallback content URL or path
        timeout: Connection timeout in seconds
        retry_count: Number of retry attempts
        
    Raises:
        NetworkError: If streaming fails after all retries
    """
    # Validate and prepare URL
    try:
        url = validate_and_prepare_url(url)
    except ConfigurationError as e:
        logger.error(str(e))
        if fallback:
            logger.info(f"Using fallback content: {fallback}")
            url = fallback
        else:
            raise
    
    # Attempt to stream URL with retries
    for attempt in range(retry_count):
        try:
            if not check_url_availability(url):
                raise NetworkError(f"URL not available: {url}")
            
            # Start streaming (implementation depends on display hardware)
            logger.info(f"Streaming URL: {url}")
            # TODO: Implement actual streaming logic here
            
            return
            
        except Exception as e:
            logger.warning(f"Streaming attempt {attempt + 1} failed: {str(e)}")
            if attempt < retry_count - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                if fallback and fallback != url:
                    logger.info(f"Using fallback content: {fallback}")
                    stream_url(fallback, None, timeout, 1)  # Single attempt for fallback
                else:
                    raise NetworkError(f"Failed to stream URL after {retry_count} attempts")

def main() -> None:
    """Main function."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Use provided fallback or load from config
        fallback = args.fallback or load_fallback_content()
        
        # Stream URL
        stream_url(args.url, fallback, args.timeout, args.retry)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
