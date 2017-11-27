import sys
from flask_restful import Resource, Api
from flask import Flask

app = Flask(__name__)
api = Api(app)


class FileServer(Resource):
    def get(self):
        # placeholder
    def post(self):
        # placeholder

if __name__ == "__main__":
    app.run(debug=True, port=int(sys.argv))