# app/__init__.py

from flask import Flask

# Initialize the app
app = Flask(__name__, instance_relative_config=True)

from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://////media/sf_Sentinelle/Code/ai vision dashboard/test.db'
db = SQLAlchemy(app)


# Load the views
from app import views

# Load the config file
app.config.from_object('config')
