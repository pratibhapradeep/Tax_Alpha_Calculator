from flask import Flask
from .routes import routes
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS globally

    # Enable debugging mode
    app.config['DEBUG'] = True
    app.config['ENV'] = 'development'

    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()

    # Basic route
    @app.route('/')
    def index():
        return "Welcome to the Tax Alpha Calculator API!"

    # Register other blueprints (API routes) here
    from .routes import routes
    app.register_blueprint(routes)

    return app
