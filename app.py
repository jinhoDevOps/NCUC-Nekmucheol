from flask import Flask, request, jsonify, render_template_string
import requests

from FirstPersona import FirstPersona
from SecondPersona import SecondPersona
from makePersona import makePersona

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template_string('''
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

                fetch('/run', {
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
                        responseDiv.innerHTML = '<h3>Response:</h3><pre>' + data.response.join('<br>') + '</pre>';
                    } else {
                        responseDiv.innerHTML = '<h3>Error:</h3><p>' + data.message + '</p>';
                    }
                })
                .catch((error) => {
                    const responseDiv = document.getElementById('response');
                    responseDiv.innerHTML = '<h3>Error:</h3><p>' + error + '</p>';
                });
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/run', methods=['POST'])
def run():
    data = request.json
    question = data.get('question')
    print(question)

    try:
        output = makePersona(question)
        return jsonify({'status': 'success', 'response': output}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)