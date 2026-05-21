"""
Render/Gunicorn entry point — app.py
--------------------------------------
Gunicorn runs: `gunicorn app:app --bind 0.0.0.0:$PORT`
This file satisfies that by:
  1. Neutralizing run_pipeline's internal Flask server (gunicorn handles that)
  2. Starting the background simulation queue thread
  3. Exposing the Flask `app` object for gunicorn to serve
"""
import threading
import run_pipeline

# Gunicorn serves Flask — prevent run_pipeline from also trying to bind a server
run_pipeline.run_flask = lambda: None

# Start the full pipeline queue loop in a background daemon thread
_pipeline_thread = threading.Thread(target=run_pipeline.main, daemon=True)
_pipeline_thread.start()

# This `app` is what gunicorn binds to
app = run_pipeline.app
