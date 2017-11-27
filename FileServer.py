import sys
from flask_restful import Resource, Api
from flask import Flask

app = Flask(__name__)
api = Api(app)


class FileServer(Resource):
    def get(self):
        return {"Hello": "World"}
    def post(self):
        return 0

# this adds a url handle for the FileServer
api.add_resource(FileServer, '/')

if __name__ == "__main__":
    app.run(debug=True, port=int(sys.argv[1]))