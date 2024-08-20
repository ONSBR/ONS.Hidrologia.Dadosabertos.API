from flask import Flask
from routes import api_blueprint

app = Flask(__name__)
app.register_blueprint(api_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
