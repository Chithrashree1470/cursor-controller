from flask import Flask, render_template
import subprocess, sys, os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/run-gesture-script")
def run_gesture():
    subprocess.Popen([sys.executable, "virtual_mouse.py"])
    return "Gesture Virtual Mouse Started"

if __name__ == "__main__":
    app.run(debug=True)
