from types import SimpleNamespace
import requests


def haveLayout(userName):
    return_code = requests.get(f"https://raw.githubusercontent.com/{userName}/{userName}/refs/heads/main/files/layout.html").status_code
    print("return_code:", return_code)
    return return_code == 200


def argsCollector(inputArgs):
    if hasattr(inputArgs, "args"):
        # Если случайно передали request, возьмём request.args
        inputArgs = inputArgs.args


    args = {
        "person": inputArgs.get('person'),
        "width": inputArgs.get('width'),
        "height": inputArgs.get('height'),
        "IsPhoto": inputArgs.get('type'),
        "fps": inputArgs.get('fps'),
        "noCache": inputArgs.get('nocache'),
        "length": inputArgs.get('length'),
        "debug": inputArgs.get('debug'),
        "debugvideoname": inputArgs.get('debugvideoname'),
        "quality": inputArgs.get('quality'),
        "lockfile": inputArgs.get('lockfile'),
    }
    args = SimpleNamespace(**args)

    args.width = int(args.width) if args.width is not None else 910
    args.height = int(args.height) if args.height is not None else 513
    if args.fps is not None:
        args.fps = int(args.fps)


    args.IsPhoto = args.IsPhoto in ["image", "photo"]

    if args.length is not None:
        args.length = float(args.length) if args.length != "auto" else "auto"
    elif not args.IsPhoto: 
        args.length = "auto"


    args.noCache = args.noCache == "true" if args.noCache is not None else False
    args.debug = args.debug == "true" if args.debug is not None else False


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