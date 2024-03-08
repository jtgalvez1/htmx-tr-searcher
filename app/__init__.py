from flask import Flask, render_template
from flask_session import Session
import json

app = Flask(__name__)

app.config.from_pyfile('configs.py')
Session(app)

CLIENT_SECRETS_FILE = open('client_secret.json')
CLIENT_SECRETS = json.load(CLIENT_SECRETS_FILE)
CLIENT_SECRETS_FILE.close()

app.config['GOOGLE_API_CLIENT_SECRETS'] = CLIENT_SECRETS['web']
app.config['GOOGLE_CLIENT_ID'] = CLIENT_SECRETS['web'].get('client_id')

from app import routes