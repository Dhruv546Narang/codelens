"""
app.py — Flask web server for CodeLens
"""

from flask import Flask, render_template, request, jsonify
from reviewer import review_code, fix_code
from database import init_db, save_review, get_history, get_review_by_id, delete_review, clear_history

app = Flask(__name__)
init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/review", methods=["POST"])
def review():
    data     = request.get_json()
    code     = data.get("code", "").strip()
    language = data.get("language", "python").strip()
    if not code:
        return jsonify({"error": "No code provided."}), 400
    if len(code) > 10000:
        return jsonify({"error": "Code too long. Max 10,000 characters."}), 400
    result = review_code(code, language)
    if "error" in result:
        return jsonify(result), 500
    result["history_id"] = save_review(language, code, result["review"], result.get("score"))
    return jsonify(result)


@app.route("/fix", methods=["POST"])
def fix():
    data     = request.get_json()
    code     = data.get("code", "").strip()
    language = data.get("language", "python").strip()
    if not code:
        return jsonify({"error": "No code provided."}), 400
    result = fix_code(code, language)
    if "error" in result:
        return jsonify(result), 500
    return jsonify(result)


@app.route("/history", methods=["GET"])
def history():
    return jsonify(get_history())


@app.route("/history/<int:review_id>", methods=["GET"])
def get_history_item(review_id):
    item = get_review_by_id(review_id)
    if not item:
        return jsonify({"error": "Not found"}), 404
    return jsonify(item)


@app.route("/history/<int:review_id>", methods=["DELETE"])
def delete_history_item(review_id):
    delete_review(review_id)
    return jsonify({"success": True})


@app.route("/history", methods=["DELETE"])
def clear_all_history():
    clear_history()
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True)
