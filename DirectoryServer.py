from flask_restful import Resource, Api
from flask import Flask

app = Flask(__name__)
api = Api(app)


class DirectoryServer(Resource):

    def get(self, requested_file):
        return {"Hello": "World"}

    def post(self, requested_file):
        # TODO implement what this does
        return "", # no content to return


# this adds a url handle for the Directory Server
api.add_resource(DirectoryServer, '/')

if __name__ == "__main__":
    # let it run on the default localhost:5000
    app.run(debug=True)
