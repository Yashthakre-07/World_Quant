"""
Vercel Serverless Entry Point
------------------------------
Vercel looks for a Flask/WSGI `app` object inside api/index.py.
We import the fully configured Flask app from run_pipeline.py WITHOUT
calling main(), so the background simulation thread is never started here.
The dashboard UI and all /api/* routes work normally as serverless functions.
"""
import sys
from pathlib import Path

# Make sure root project directory is on the path so imports resolve correctly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import ONLY the Flask app — never call main()
from run_pipeline import app  # noqa: F401

# Vercel expects the callable to be named 'app'
# That's it — Vercel handles the rest.
