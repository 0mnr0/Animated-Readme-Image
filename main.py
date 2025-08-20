import subprocess

import requests
from playwright.sync_api import sync_playwright
# Я изменил битрейт с 1M на 10M:
# C:\Users\savel\dsvl0.space\AnimatedProfileReadme\.venv\Lib\site-packages\playwright\driver\package\lib\server\chromium
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
        "ffmpeg",
        "-i", input_file,
        "-vf", f"fps={fps},scale=-1:-1:flags=lanczos",
        "-loop", "0",  # бесконечный цикл
        "-q:v", str(quality),  # бесконечный цикл
        output_file
    ]
    subprocess.run(cmd, check=True)

def interpolate_webm(input_file, output_file, newFps = 30):
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-vf", f"minterpolate=fps={newFps}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1",
        "-c:v", "libvpx-vp9",
        "-b:v", "10M",
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
        "-ss", str(start),
        "-i", input_file,
        "-c", "copy",
        output_file
    ]

    subprocess.run(cmd, check=True)
    return output_file


def record_apng(userName, WidthAndHeight, duration, interpolate: bool = False):
    HTML_CONTENT = requests.get(f"https://raw.githubusercontent.com/{userName}/{userName}/refs/heads/main/files/layout.html")
    file = f"userFiles/{userName}.html"
    with open(file, "w") as f:
        f.write(HTML_CONTENT.text)
    html_file = os.path.abspath(file)
    output_file = f"userFiles/{userName}.webm"

    if os.path.exists(output_file):
        os.remove(output_file)
    if os.path.exists(f"userFiles/{userName}.webp"):
        os.remove(f"userFiles/{userName}.webp")
    if os.path.exists(f"userFiles/{userName}_interpolated.webm"):
        os.remove(f"userFiles/{userName}_interpolated.webm")
    if os.path.exists(f"userFiles/{userName}_cutted.webm"):
        os.remove(f"userFiles/{userName}_cutted.webm")


    loadingTime = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=[
            '--disable-gpu',
            '--disable-software-rasterizer',
            '--disable-extensions',
            '--disable-background-networking',
            '--disable-sync',
            '--disable-translate',
            '--disable-plugins',
            '--disable-images',
            '--disable-accelerated-2d-canvas',
        ])
        globalStartTime = time.time()
        context = browser.new_context(
            viewport=WidthAndHeight,
            record_video_dir="video_temp",
            record_video_size=WidthAndHeight,
        )
        page = context.new_page()
        page.set_viewport_size(WidthAndHeight)

        print("Content is loading...")
        page.goto(f"file://{html_file}", wait_until="networkidle")
        print("Content is loaded! Recording...")
        page.evaluate("""
            document.querySelectorAll('video').forEach(v => { v.currentTime = 0; v.play(); });
        """)
        recordStartTime = time.time()
        loadingTime = recordStartTime - globalStartTime

        time.sleep(duration)  # ждём, пока проиграется
        page.close()
        page.video.save_as(output_file)  # сохраняем в нужный файл
        browser.close()
        print("Готово!", output_file)
        print("Страница загрузужалась:", loadingTime, "сек")

    while not os.path.exists(f"userFiles/{userName}.webm"):
        time.sleep(0.1)



    output_file = cutVideo(output_file, f"userFiles/{userName}_cutted.webm", loadingTime)
    if interpolate:
        output_file = interpolate_webm(os.path.abspath(output_file), f"userFiles/{userName}_interpolated.webm", newFps = 50)

    webm_to_webp(output_file, f"userFiles/{userName}.webp", fps=24, quality=10)


def clean_temp():
    for file in os.listdir("video_temp"):
        try: os.remove(f"video_temp/{file}")
        except: pass
clean_temp()


if __name__ == "__main__":
    record_apng("0mnr0",{"width": 912, "height": 513 },  duration=10)
