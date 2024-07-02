## 정상 동작하는 app.py 입니다.

from flask import Flask, request, jsonify, render_template_string
import requests

from FirstPersona import FirstPersona
from SecondPersona import SecondPersona
from makePersona import makePersona
import hcx_dash

app = Flask(__name__)


@app.route("/")
def index():
    return render_template_string(
        """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>POST Request with Fetch</title>
    </head>
    <body>
        <h1>Send POST Request</h1>
        <form id="postForm">
            <label for="question">Question:</label>
            <textarea id="question" name="question"></textarea><br><br>
            <input type="submit" value="Send POST Request">
        </form>

        <div id="response"></div>

        <script>
            document.getElementById('postForm').addEventListener('submit', function(event) {
                event.preventDefault();
                const question = document.getElementById('question').value;

                // 입력 유효성 검증
                if (!question.trim()) {
                    const responseDiv = document.getElementById('response');
                    responseDiv.innerHTML = '<h3>Error:</h3><p>Question cannot be empty.</p>';
                    return;
                }

                // '/dash'로 POST 요청
                fetch('/dash', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ question: question })
                })
                .then(response => response.json())
                .then(data => {
                    const responseDiv = document.getElementById('response');
                    if (data.status === 'success') {
                        if (data.message.includes("적합합니다")) {
                            // 성공 메시지를 표시하고, 3초 후에 '/run'으로 POST 요청
                            responseDiv.innerHTML = '<h3>Success:</h3><p>' + data.message + '</p>';
                            setTimeout(() => {
                                // 데이터와 함께 '/run'으로 POST 요청
                                fetch('/run', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({ question: question })
                                })
                                .then(response => response.json())
                                .then(data => {
                                    if (data.status === 'success') {
                                        // 배열 확인 및 처리
                                        const responseContent = Array.isArray(data.response) ? data.response.join('<br>') : data.response;
                                        responseDiv.innerHTML = '<h3>Response:</h3><pre>' + responseContent + '</pre>';
                                    } else {
                                        responseDiv.innerHTML = '<h3>Error:</h3><p>' + data.message + '</p>';
                                    }
                                })
                                .catch(error => {
                                    console.error('Error fetching /run:', error);
                                    responseDiv.innerHTML = '<h3>Error:</h3><p>Failed to fetch /run</p>';
                                });
                            }, 3000);  // 3초 후 '/run'으로 POST 요청
                        } else {
                            responseDiv.innerHTML = '<h3>Error:</h3><p>' + data.message + '</p>';
                        }
                    } else {
                        responseDiv.innerHTML = '<h3>Error:</h3><p>' + data.message + '</p>';
                    }
                })
                .catch(error => {
                    console.error('Error fetching /dash:', error);
                    const responseDiv = document.getElementById('response');
                    responseDiv.innerHTML = '<h3>Error:</h3><p>Failed to fetch /dash</p>';
                });
            });
        </script>
    </body>
    </html>
    """
    )


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
