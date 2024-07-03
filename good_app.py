## 정상 동작하는 app.py 입니다.

from flask import Flask, request, jsonify, render_template
import requests

from FirstPersona import FirstPersona
from SecondPersona import SecondPersona
from makePersona import makePersona
import hcx_dash

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/dash", methods=["POST"])
def dash_route():
    input_text = request.json.get("question", "")
    if not input_text.strip():
        return jsonify({"status": "error", "message": "Question cannot be empty"}), 400

    is_true, content = hcx_dash.get_discussion_result(input_text)
    if is_true == "True" or is_true is True:
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "토론 주제가 적합합니다. 3초 후에 결과가 표시됩니다.",
                }
            ),
            200,
        )
    elif is_true == "False" or is_true is False:
        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"토론 주제로 적합하지 않습니다. {content}",
                }
            ),
            201,
        )
    else:
        return jsonify({"status": "error", "message": "Unexpected error occurred"}), 500

@app.route("/run", methods=["POST"])
def run():
    if not request.is_json:
        return (
            jsonify({"status": "error", "message": "Invalid data, expected JSON"}),
            400,
        )

    data = request.get_json()
    question = data.get("question")

    try:
        output = makePersona(question)
        if not isinstance(output, list):
            output = [output]
        return jsonify({"status": "success", "response": output}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
