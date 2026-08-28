import os
import sys

# Add project root directory to path for Vercel Serverless Function runtime
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from communicare.main import app
