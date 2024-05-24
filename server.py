import json
from flask import Flask, request,jsonify

app = Flask(__name__)

@app.route('/books/health', methods=['GET'],endpoint='health')
def Health():
    return 'OK', 200

@app.route('/book', methods=['POST'],endpoint='CreatNewBook')
def CreatNewBook():
    data = request.get_json()
    
if __name__ == '__main__':
    app.run(debug=True)
