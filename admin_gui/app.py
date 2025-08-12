import json

from flask import Flask, redirect, render_template, request

app = Flask(__name__)
CONFIG_PATH = "config.json"


def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return {}


def save_config(config):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
        print("✅ Config updated.")
    except Exception as e:
        print(f"❌ Failed to save config: {e}")


@app.route("/", methods=["GET", "POST"])
def index():
    config = load_config()
    if not config:
        return "❌ Config file missing or invalid."

    if request.method == "POST":
        config["min_duration_seconds"] = float(request.form["min_duration_seconds"])
        config["default_source"] = request.form["default_source"]
        config["default_platform"] = request.form["default_platform"]
        config["default_account"] = request.form["default_account"]
        config["product_filter_keywords"] = request.form[
            "product_filter_keywords"
        ].split(",")
        config["product_filter_min_price"] = int(
            request.form["product_filter_min_price"]
        )
        config["product_filter_max_price"] = int(
            request.form["product_filter_max_price"]
        )
        save_config(config)
        return redirect("/")
    return render_template("index.html", config=config)


@app.route("/run_batch", methods=["POST"])
def run_batch():
    print
