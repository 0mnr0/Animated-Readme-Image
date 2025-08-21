import time

from flask import *
import flask_cors
import readmeRender
from database import *
from threading import Thread
import gitReader



app = Flask(__name__, static_folder='web/static', template_folder='web')
flask_cors.CORS(app)


WHITELISTED_USERS = [
    "0mnr0"
]

WHITELIST_SOON = [
    "cyrsiansk",
    "AysCRvbc",
    "dinalt",
    "kihaas",
    "Kekovich-kw"
]




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
                                 debug=ReadmeOptions.debug,
                                 quality=ReadmeOptions.quality)

    Thread(target=runInBg, args=(ReadmeOptions,)).start()

@app.route('/myReadme', methods=['GET'])
def myReadme():
    ReadmeOptions = gitReader.argsCollector(request)
    person = ReadmeOptions.person

    # Пока всё сырое, даже в своём readme я зафиксировал фото, мне ещё нужно чуть чуть времени сделать всё стабильнее и потом пустить в ход.
    # Скорее всего успею к 1му сентября
    if person is None:
        return "Please Specify Person", 400

    if person != "0mnr0":
        returnStr = "Вы должны быть в белом списке чтобы получить свой readme."

        if person in WHITELIST_SOON:
            returnStr += " Скоро я разрешу доступ к api этим людям:<br><br>"
            for _user_ in WHITELIST_SOON:
                returnStr += f" > {_user_}<br>"

        return returnStr, 403

    if type(ReadmeOptions.lockfile) == str:
        return send_file(ReadmeOptions.lockfile, mimetype="image/webp")

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
    return Response(event_stream(userName), mimetype="text/event-stream", headers={"Cache-Control": "no-cache", 'X-Accel-Buffering': 'no'})

if __name__ == '__main__':
    app.run(port=7777, debug=True, use_reloader=False)