"""ACEest Fitness & Gym - application entry point.

Run locally:
    python ACEest_Fitness.py

Run in container (gunicorn): see Dockerfile.
"""
import os

from app import create_app

app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
