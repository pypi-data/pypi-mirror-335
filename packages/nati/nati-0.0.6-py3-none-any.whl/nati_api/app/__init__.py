"""
NATI API - Network Analytics and Telemetry Interface API
"""

from flask import Flask, redirect
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
app.config['BUNDLE_ERRORS'] = True

api = Api(app)


@app.route('/')
def hello():
    return "Hello World - Welcome to NATI API!"


key_parser = reqparse.RequestParser()
key_parser.add_argument("x-api-key",
                        type=str,
                        required=True,
                        help="API Key is required",
                        location='headers')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
