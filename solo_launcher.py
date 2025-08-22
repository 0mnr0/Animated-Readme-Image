from flask import *
import flask_cors

app = Flask(__name__, static_folder='web/static', template_folder='web')
flask_cors.CORS(app)

import readmeServerCode
readmeServerCode.importApp(app)



app.run(port=7777, debug=True, use_reloader=False)