from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "POS App Running!"

from app import app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

