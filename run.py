import os
os.environ['NO_AT_BRIDGE'] = '1'

# Import your main application
from test_qr_display import test_qr_display

if __name__ == "__main__":
    test_qr_display()