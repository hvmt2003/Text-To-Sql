print(">>> FLASK APP.PY IS RUNNING <<<")

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from chatbot_engine import ask_database

app = Flask(__name__)
CORS(app)

# Home → loads UI
@app.route("/")
def home():
    return render_template("index.html")

# API → takes natural language question, returns SQL + result
@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"success": False, "error": "Question cannot be empty"}), 400

    try:
        sql_query, result = ask_database(question)
        return jsonify({
            "success": True,
            "sql": sql_query,
            "result": result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Health check (Cloud Run / Docker)
@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
