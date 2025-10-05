import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from supabase_lib.supabase_config import *

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)

app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")


# Configure the database
supabase

# Initialize the app with the extension
# db.init_app(app)

with app.app_context():
    # Import models and routes
    # import models
    import routes
    
    # # Drop and recreate all tables (for development)
    # db.drop_all()
    # db.create_all()
    
    # Create admin user after tables are created
    # routes.create_admin()
