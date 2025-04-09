from flask import Flask
import time

app = Flask(__name__)

@app.get('/')
def home():
    time.sleep(5)
    return '<h1>Version 1</h1>'


if __name__ == '__main__':
    app.run(port=8000)