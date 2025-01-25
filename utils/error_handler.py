from typing import Callable, TypeVar, Any
from functools import wraps
import logging
from colorama import Fore, Style

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

T = TypeVar('T')

class SetupError(Exception):
    """Base exception class for setup-related errors."""
    pass

class NetworkError(SetupError):
    """Network-related errors."""
    pass

class APError(SetupError):
    """Access Point related errors."""
    pass

class ActivationError(SetupError):
    """Activation-related errors."""
    pass

def handle_errors(logger: logging.Logger = None) -> Callable:
    """
    Decorator for handling errors in a consistent way across the application.
    
    Args:
        logger: Optional logger instance. If not provided, creates a new one.
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except NetworkError as e:
                logger.error(f"Network error: {e}")
                print(Fore.RED + f"Network error: {e}" + Style.RESET_ALL)
                raise
            except APError as e:
                logger.error(f"Access Point error: {e}")
                print(Fore.RED + f"Access Point error: {e}" + Style.RESET_ALL)
                raise
            except ActivationError as e:
                logger.error(f"Activation error: {e}")
                print(Fore.RED + f"Activation error: {e}" + Style.RESET_ALL)
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                print(Fore.RED + f"An unexpected error occurred: {e}" + Style.RESET_ALL)
                raise SetupError(f"Unexpected error: {str(e)}")
        return wrapper
    return decorator 