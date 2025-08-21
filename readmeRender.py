import subprocess
from datetime import datetime

import random, string
import re
import shutil
from bs4 import BeautifulSoup
from PIL import Image
import io
from database import *
import requests
from playwright.sync_api import sync_playwright
# Я изменил битрейт с 1M на 10M:
# C:\Users\savel\PyCharmProjects\dsvl0.space\.venv\Lib\site-packages\playwright\driver\package\lib\server\chromium
# Lunix Servers Path: /usr/local/lib/python3.12/dist-packages/playwright/driver/package/lib/server/chromium
# videoRecorder.js
# const args = `... -b:v 1M` - -b:v 10M`

import time
import os

isLinux = os.name == "posix"
if not os.path.exists("userFiles"):
    os.mkdir("userFiles")

def webm_to_webp(input_file: str, output_file: str, fps: int = 24, quality: int = 80):
    """
    :param quality:
    :param input_file: путь к .webm
    :param output_file: путь к .webp
    :param fps: частота кадров (по умолчанию 15)
    :param scale: масштаб (ширина:высота, -1 = автоподбор)
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-vf", f"fps={fps},scale=-1:-1:flags=lanczos",
        "-loop", "0",
        "-q:v", str(quality),
        output_file
    ]

    subprocess.run(cmd, check=True)
    return output_file

def interpolate_webm(input_file, output_file, newFps = 30):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-vf", f"minterpolate=fps={newFps}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1",
        "-c:v", "libvpx-vp9",
        "-crf", "15",  # от 15 (очень хорошее качество) до 30 (хуже)
        "-b:v", "0",  # без ограничения битрейта
        "-threads", "12",
        "-c:a", "copy",
        output_file
    ]

    subprocess.run(cmd, check=True)
    return output_file

def cutVideo(input_file, output_file, start):
    # ffmpeg -ss 1.548 -i input.webm -c copy output.webm
    cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(start),
        "-i", input_file,
        "-c", "copy",
        output_file
    ]

    subprocess.run(cmd, check=True)
    return output_file


def YourselfCleaner(userName, output_file):
    cleanFiles = [
        output_file,
        f"userFiles/{userName}/{userName}.webp",
        f"userFiles/{userName}/{userName}_interpolated.webm",
        f"userFiles/{userName}/{userName}_cutted.webm",
    ]

    for file in cleanFiles:
        if os.path.exists(file):
            try: os.remove(file)
            except Exception as e:
                print(e)


def SetCookedStatus(userName):
    timeStamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    ReadmeDatabase.SetReadmeTime(userName, timeStamp)
    ReadmeDatabase.SetReadmeState(userName, "Cooked")
    ReadmeDatabase.SetCooked(userName, True)



def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


def GetCookedFile(userName, debug):
    shutil.rmtree(f"userFiles/{userName}/resourses", ignore_errors=True)
    if not os.path.exists(f"userFiles/{userName}/resourses"):
        os.mkdir(f"userFiles/{userName}/resourses")
    if debug: return ""

    HTML_CONTENT = requests.get(f"https://raw.githubusercontent.com/{userName}/{userName}/refs/heads/main/files/layout.html")
    file = f"userFiles/{userName}/{userName}.html"
    fileContent = HTML_CONTENT.text
    with open(file, "w") as f:
        f.write(fileContent)
    soup = BeautifulSoup(fileContent, "html.parser")
    elements = soup.find_all(src=True)

    generatedWords = []
    for el in elements:
        url = el["src"]
        try:
            if ("https://" not in url) and ("github.com" not in url):
                url = f"https://github.com/{userName}/{userName}/raw/refs/heads/main/files/{url}"
            response = requests.get(url, stream=True)
            filename = url.split("/")[-1]
            filename = re.sub(r'[\\/:*?"<>|]', '', filename)
            if "github-readme-stats.vercel.app" in url:
                newFilename = randomword(12)
                while newFilename in generatedWords:
                    newFilename = randomword(12)
                generatedWords.append(newFilename)
                filename = f"{newFilename}.svg"

            local_path = f"userFiles/{userName}/resourses/{filename}"

            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # заменить src в html
            el["src"] = os.path.abspath(f"userFiles/{userName}/resourses/{filename}")
        except Exception as e:
            raise e
            print(f"Не удалось скачать {url}: {e}")

    with open(f"userFiles/{userName}/{userName}.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
    return file


def record_apng(userName, WidthAndHeight, duration, IsPhoto, debug, quality):
    try:
        MaxSteps = 6 if IsPhoto else 7
        print("IN ARGS:",userName, WidthAndHeight, duration, IsPhoto, debug)
        # WidthAndHeight = {"width": 910, "height": 513}


        ReadmeDatabase.SetCooked(userName, False)
        ReadmeDatabase.SetReadmeState(userName, f"[Step 1/{MaxSteps}] Cleaning And Preparing...")
        if not os.path.exists(f"userFiles/{userName}"):
            os.mkdir(f"userFiles/{userName}")
        clean_temp()




        ReadmeDatabase.SetReadmeState(userName, f"[Step 2/{MaxSteps}] Downloading Sources From HTML...")
        file = GetCookedFile(userName, debug)
        if debug: file = f"{userName}.html"


        html_file = os.path.abspath(file)
        output_file = f"userFiles/{userName}/{userName}.webm"

        YourselfCleaner(userName, output_file)


        ReadmeDatabase.SetReadmeState(userName, f"[Step 3/{MaxSteps}] Headless Browser Loading...")
        loadingTime = 0
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=[
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-extensions',
                '--disable-translate',
                '--disable-plugins',
                '--disable-accelerated-2d-canvas',
            ])
            ReadmeDatabase.SetReadmeState(userName, f"[Step 4/{MaxSteps}] Opened layout, waiting for network idle...")
            globalStartTime = time.time()
            context = browser.new_context(
                viewport=WidthAndHeight,
                record_video_dir="video_temp",
                record_video_size=WidthAndHeight,
            )
            page = context.new_page()

            print("Content is loading...")
            ReadmeDatabase.SetReadmeState(userName, f"[Step 4/{MaxSteps}] Opened layout, waiting for network idle (1/2)...")
            try:page.goto(f"file://{html_file}", wait_until="domcontentloaded")
            except Exception as e:
                page.goto(f"file://{html_file}")
            ReadmeDatabase.SetReadmeState(userName, f"[Step 5/{MaxSteps}] Recording... ")
            page.evaluate("""
                document.querySelectorAll('video').forEach(v => { v.currentTime = 0; v.play(); });
            """)

            if IsPhoto:
                buffer = page.screenshot()
                ReadmeDatabase.SetReadmeState(userName, f"[Step 6/{MaxSteps}] Captured. Saving screenshot to webp...")
                img = Image.open(io.BytesIO(buffer)).convert("RGB")
                img.save(f"userFiles/{userName}/{userName}.webp", "webp")
                SetCookedStatus(userName)
                ReadmeDatabase.SetCurrentReadme(userName, f"userFiles/{userName}/{userName}.webp")
                return

            recordStartTime = time.time()
            loadingTime = recordStartTime - globalStartTime
            time.sleep(2 if IsPhoto else duration)
            page.close()
            if not IsPhoto: page.video.save_as(output_file)  # сохраняем в нужный файл
            browser.close()
            print("Готово!", output_file)
            print("Страница загрузужалась:", loadingTime, "сек")

        while not os.path.exists(f"userFiles/{userName}/{userName}.webm"):
            time.sleep(0.1)

        ReadmeDatabase.SetReadmeState(userName, f"[Step 6/{MaxSteps}] Captured. Cutting non-loaded area...")
        output_file = cutVideo(output_file, f"userFiles/{userName}/{userName}_cutted.webm", loadingTime)
        ReadmeDatabase.SetReadmeState(userName, f"[Step 7/{MaxSteps}] Converting into animated image...")
        output_file = webm_to_webp(output_file, f"userFiles/{userName}/{userName}.webp", fps=24, quality=quality)

        SetCookedStatus(userName)
        ReadmeDatabase.SetCurrentReadme(userName, output_file)


    except Exception as e:
        ReadmeDatabase.SetReadmeState(userName, f"[ERR] Error: {e}")
        ReadmeDatabase.SetCooked(userName, True)
        raise e



def clean_temp():
    for file in os.listdir("video_temp"):
        try: os.remove(f"video_temp/{file}")
        except: pass
clean_temp()