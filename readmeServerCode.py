import time
import os

from flask import *
import readmeRender
from database import *
from threading import Thread
import gitReader

RECREATION_TIME = ReadmeRefreshInterval_Minutes  # Minutes

WHITELISTED_USERS = [
    "cyrsiansk",
    "AysCRvbc",
    "dinalt",
    "kihaas",
    "Kekovich-kw",
    "0mnr0"
]

RECREATION_TIME *= 60  # Convert into minutes


def BackgroundUpdater():
    if (
            RECREATION_TIME == False
            or RECREATION_TIME == 0
            or RECREATION_TIME is None
            or RECREATION_TIME == -1
    ): return

    isSomeOneCooked = False
    while True:
        time.sleep(20 * 60 if isSomeOneCooked else RECREATION_TIME)

        for user in ReadmeDatabase.GetAllUsers():
            userName = user.get("username")

            isSomeOneCooked = ReadmeDatabase.IsAnyOneCooking()
            if isSomeOneCooked:
                continue

            ReadmeDatabase.SetCooked(userName, False)
            ReadmeOptions = ReadmeDatabase.GetReadmeLineOptions(user.get("username"))
            if ReadmeOptions is None:
                continue

            readmeRender.record_apng(ReadmeOptions.person,
                                     {"width": ReadmeOptions.width, "height": ReadmeOptions.height},
                                     duration=ReadmeOptions.length,
                                     IsPhoto=ReadmeOptions.IsPhoto,
                                     debug=ReadmeOptions.debug,
                                     quality=ReadmeOptions.quality)
            time.sleep(3)


# bgCooker = Thread(target=BackgroundUpdater)
# bgCooker.start()


def importApp(app):
    def gotoStatusStream(userName):
        return redirect(url_for('readmeStatus', person=userName))

    def StartCreatingReadme(ReadmeOptions):
        def runInBg(ReadmeOptions):
            print("ReadmeOptions:", ReadmeOptions)
            readmeRender.record_apng(ReadmeOptions.person,
                                     {"width": ReadmeOptions.width, "height": ReadmeOptions.height},
                                     duration=ReadmeOptions.length,
                                     IsPhoto=ReadmeOptions.IsPhoto,
                                     debug=ReadmeOptions.debug,
                                     quality=ReadmeOptions.quality)

        Thread(target=runInBg, args=(ReadmeOptions,)).start()

    @app.route('/myReadme', methods=['GET'])
    def myReadme():
        ReadmeOptions = gitReader.argsCollector(request.args)
        person = ReadmeOptions.person

        # Пока всё сырое, даже в своём readme я зафиксировал фото, мне ещё нужно чуть чуть времени сделать всё стабильнее и потом пустить в ход.
        # Скорее всего успею к 1му сентября
        if person is None:
            return "Please Specify Person", 400

        if person != "0mnr0":
            returnStr = "Вы должны быть в белом списке чтобы получить свой readme."
            return returnStr, 403

        if not ReadmeOptions.lockfile:
            SavingReadmeOptions = SimpleNamespace(**vars(ReadmeOptions))
            SavingReadmeOptions.noCache = False
            ReadmeDatabase.UpdateReadmeLineOptions(person, SavingReadmeOptions)  # Save Options to Auto Update

        if not ReadmeDatabase.IsUserExists(person):
            ReadmeDatabase.CreateNewUser(person)
            StartCreatingReadme(ReadmeOptions)
            return gotoStatusStream(person)

        if type(ReadmeOptions.lockfile) == str:
            return send_file(ReadmeOptions.lockfile, mimetype="image/webp")

        if ReadmeOptions.length is None and not ReadmeOptions.IsPhoto:
            if ReadmeDatabase.IsCooked(person):
                return send_file(ReadmeDatabase.GetCurrentReadme(person), mimetype="image/apng")
            return "Please Set Length of a video", 423

        if not ReadmeDatabase.IsCooked(person) and type(
                ReadmeDatabase.GetCurrentReadme(person)) != str and not ReadmeOptions.noCache:
            return gotoStatusStream(person)

        previousFileNotExist = (ReadmeDatabase.GetCurrentReadme(person) is not None and not os.path.exists(
            ReadmeDatabase.GetCurrentReadme(person)))
        print("previousFileNotExist:", previousFileNotExist)

        try:
            if ReadmeDatabase.IsFreshReadme(person) and not previousFileNotExist and not ReadmeOptions.noCache:
                return send_file(ReadmeDatabase.GetCurrentReadme(person), mimetype="image/apng")
        except:
            pass

        StartCreatingReadme(ReadmeOptions)

        if ReadmeOptions.noCache or previousFileNotExist:
            return gotoStatusStream(person)
        response = make_response(send_file(ReadmeDatabase.GetCurrentReadme(person), mimetype="image/webp"))
        response.headers["Cache-Control"] = "public, max-age=3600"
        return response

    def event_stream(userName):
        if ReadmeDatabase.IsUserExists(userName):
            for i in range(30):
                yield f"[{userName} Readme Status ({i}/30)]: {ReadmeDatabase.GetReadmeState(userName).get('state')}\n"
                time.sleep(1)
        yield f"Stream closed. If you want to know more, please refresh the page\n"

    @app.route('/myReadmeSize', methods=['GET'])
    def myReadmeSize():
        userName = request.args.get('person')
        filePath = ReadmeDatabase.GetCurrentReadme(userName)
        if ReadmeDatabase.IsUserExists(userName) and filePath is not None:
            return f"\"{filePath}\" is:<br><b>{os.path.getsize(filePath) / 1024 / 1024:.2f} MB</b><br><br>( {os.path.getsize(filePath)} bytes )"
        return "User Or File Not Found"

    @app.route('/time', methods=['GET'])
    def myReadmeTime():
        return datetime.now().strftime("%m-%d_%H:%M")

    @app.route('/readmeStatus', methods=['GET'])
    def readmeStatus():
        userName = request.args.get('person')
        return Response(event_stream(userName), mimetype="text/event-stream",
                        headers={"Cache-Control": "no-cache", 'X-Accel-Buffering': 'no'})


def SetWorkingDir(path):
    os.chdir(path)
