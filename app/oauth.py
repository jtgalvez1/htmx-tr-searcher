from google.oauth2 import id_token
from google.auth.transport.requests import Request

from app import app

def verify_token(token):
  try:

    # Specify the CLIENT_ID of the app that accesses the backend:
    idinfo = id_token.verify_oauth2_token(token, Request(), app.config['GOOGLE_CLIENT_ID'], clock_skew_in_seconds=100000) # EXPERIMENTAL: clock_skew_in_seconds; for 'Token used too early' error

    # Or, if multiple clients access the backend server:
    # idinfo = id_token.verify_oauth2_token(token, requests.Request())
    # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
    #     raise ValueError('Could not verify audience.')

    # If auth request is from a G Suite domain:
    # GSUITE_DOMAIN_NAME = 'up.edu.ph'
    # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
    #     raise ValueError('Wrong hosted domain.')

    # ID token is valid. Get the user's Google Account ID from the decoded token.
    user = {
      'userid': idinfo['sub'],
      'email': idinfo['email'],
      'given_name': idinfo['given_name'],
      'family_name': idinfo['family_name'],
      'picture': idinfo['picture']
    }
    return user
  except ValueError as ve:
    # Invalid token
    print(ve)
    pass