from types import SimpleNamespace
import requests


def haveLayout(userName):
    return_code = requests.get(f"https://raw.githubusercontent.com/{userName}/{userName}/refs/heads/main/files/layout.html").status_code
    print("return_code:", return_code)
    return return_code == 200


def argsCollector(request):
    args = {
        "person": request.args.get('person'),
        "width": request.args.get('width'),
        "height": request.args.get('height'),
        "IsPhoto": request.args.get('type'),
        "fps": request.args.get('fps'),
        "noCache": request.args.get('nocache'),
        "length": request.args.get('length'),
        "debug": request.args.get('debug')
    }
    args = SimpleNamespace(**args)

    if args.width is not None:
        args.width = int(args.width)
    else:
        args.width = 910

    if args.height is not None:
        args.height = int(args.height)
    else:
        args.height = 513

    if args.fps is not None:
        args.fps = int(args.fps)

    if args.length is not None:
        args.length = int(args.length)

    args.IsPhoto = (args.IsPhoto == "image" or args.IsPhoto == "photo") # its "type" key, not "isVideo". AND ITS WORKING "AS IS"

    if args.noCache is not None:
        args.noCache = args.noCache == "true"
    else:
        args.noCache = False

    if args.debug is not None:
        args.debug = args.debug == "true"
    else:
        args.debug = False



    return args