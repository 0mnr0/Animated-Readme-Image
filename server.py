from flask import *
import flask_cors


app = Flask(__name__, static_folder='web/static', template_folder='web')
flask_cors.CORS(app)


@app.route('/')
def index():
    return "Hi!"


app.run(host='0.0.0.0', port=7777, debug=True)