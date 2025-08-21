import time

from flask import *
import flask_cors
import readmeRender
from database import *
from threading import Thread
import gitReader



app = Flask(__name__, static_folder='web/static', template_folder='web')
flask_cors.CORS(app)


@app.route('/')
def index():
    return "Hi!"


def gotoStatusStream(userName):
    return redirect(url_for('readmeStatus', person=userName))

def StartCreatingReadme(ReadmeOptions):
    def runInBg(ReadmeOptions):
        print("ReadmeOptions:", ReadmeOptions)
        readmeRender.record_apng(ReadmeOptions.person,
                                 {"width": ReadmeOptions.width, "height": ReadmeOptions.height},
                                 duration=ReadmeOptions.length,
                                 IsPhoto = ReadmeOptions.IsPhoto,
                                 debug=ReadmeOptions.debug)

    Thread(target=runInBg, args=(ReadmeOptions,)).start()

@app.route('/myReadme', methods=['GET'])
def myReadme():
    ReadmeOptions = gitReader.argsCollector(request)
    person = ReadmeOptions.person
    print("ReadmeOptions: ", ReadmeOptions)

    if ReadmeOptions.length is None and not ReadmeOptions.IsPhoto:
        if ReadmeDatabase.IsCooked(person):
            return send_file(ReadmeDatabase.GetCurrentReadme(person), mimetype="image/apng")
        return "Please Set Length of a video", 423


    if not ReadmeDatabase.IsUserExists(person):
        ReadmeDatabase.CreateNewUser(person)
        StartCreatingReadme(ReadmeOptions)
        return gotoStatusStream(person)

    if not ReadmeDatabase.IsCooked(person) and type(ReadmeDatabase.GetCurrentReadme(person)) != str:
        return gotoStatusStream(person)

    if not ReadmeDatabase.IsFreshReadme(person) or ReadmeOptions.noCache:
        StartCreatingReadme(ReadmeOptions)
        return gotoStatusStream(person)
    else:
        return send_file(ReadmeDatabase.GetCurrentReadme(person), mimetype="image/apng")


def event_stream(userName):
    if ReadmeDatabase.IsUserExists(userName):
        for i in range(0, 30):
            yield f"[{userName} Readme Status ({i}/30)]: {ReadmeDatabase.GetReadmeState(userName).get('state')}\n"
            time.sleep(1)
    yield f"Stream closed. If you want to know more, please refresh the page\n"

@app.route('/readmeStatus', methods=['GET'])
def readmeStatus():
    userName = request.args.get('person')
    return Response(event_stream(userName), mimetype="text/event-stream")


app.run(port=7777, debug=True, use_reloader=False)