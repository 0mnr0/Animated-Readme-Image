from types import SimpleNamespace
import requests


def haveLayout(userName):
    return_code = requests.get(f"https://raw.githubusercontent.com/{userName}/{userName}/refs/heads/main/files/layout.html").status_code
    print("return_code:", return_code)
    return return_code == 200


def argsCollector(args):
    args = {
        "person": args.get('person'),
        "width": args.get('width'),
        "height": args.get('height'),
        "IsPhoto": args.get('type'),
        "fps": args.get('fps'),
        "noCache": args.get('nocache'),
        "length": args.get('length'),
        "debug": args.get('debug'),
        "quality": args.get('quality'),
        "lockfile": args.get('lockfile'),
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
        args.length = float(args.length)

    args.IsPhoto = (args.IsPhoto == "image" or args.IsPhoto == "photo") # its "type" key, not "isVideo". AND ITS WORKING "AS IS"

    if args.noCache is not None:
        args.noCache = args.noCache == "true"
    else:
        args.noCache = False

    if args.debug is not None:
        args.debug = args.debug == "true"
    else:
        args.debug = False

    if args.quality is not None and str(args.quality).isdigit():
        args.quality = int(args.quality)
    else:
        args.quality = 90

    if args.lockfile is None:
        args.lockfile = False

    return args


def argsToUrl(request):
    args = request.args.to_dict()
    return "&".join([f"{key}={value}" for key, value in args.items()])