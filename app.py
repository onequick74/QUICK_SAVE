from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET", "HEAD"])
def home():
    return jsonify({"ok": True, "app": "QUICK_SAVE"})

if __name__ == "__main__":
    # Runs on 0.0.0.0:5000 like your logs show
    app.run(host="0.0.0.0", port=5000)
