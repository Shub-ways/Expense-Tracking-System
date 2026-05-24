import os
import sys

# Add project root so `from backend.server import app` works
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Also add backend/ directory so server.py's bare `import db_helper` resolves
backend_dir = os.path.join(project_root, "backend")
sys.path.insert(0, backend_dir)