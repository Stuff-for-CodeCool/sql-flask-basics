from flask import Flask, jsonify
from database import run_query

app = Flask(__name__)


@app.get("/")
def index():
    return "ok"


if __name__ == "__main__":
    app.run(debug=True)
