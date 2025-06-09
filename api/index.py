from flask_app import app
import os

# Set Vercel environment variable
os.environ['VERCEL'] = '1'

# Initialize database for serverless environment
from app import init_db
init_db()

# Vercel serverless entrypoint
def handler(environ, start_response):
    return app(environ, start_response)
