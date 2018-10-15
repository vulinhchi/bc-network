from flask import Flask, jsonify, request
import logging
import time

app = Flask(__name__)
logging.basicConfig(level = logging.DEBUG)

if __name == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=4444)