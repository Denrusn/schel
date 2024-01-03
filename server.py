from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def homepage():
    return jsonify({"response": "hello word"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
