from pathlib import Path

# 图片路径
IMAGE_PATH = Path("res/img/")
# 音频路径
VOICE_PATH = Path("res/voice/")
# 文本路径
TEXT_PATH = Path("res/txt/")
# 日志路径
# LOG_PATH = Path("log/")
# 字体路径
FONT_PATH = Path("res/ttf/")
# 临时图片路径
TEMP_PATH = Path("res/img/temp/")
# 网页截图工具路径
EXECUTABLE_PATH = Path("phantomjs-2.1.1-windows/bin/phantomjs.exe")
# Json路径
JSON_PATH = Path("res/json/")
    

def init_path():
    global IMAGE_PATH, VOICE_PATH, TEXT_PATH, LOG_PATH, FONT_PATH, TEMP_PATH, JSON_PATH
    IMAGE_PATH.mkdir(parents=True, exist_ok=True)
    VOICE_PATH.mkdir(parents=True, exist_ok=True)
    TEXT_PATH.mkdir(parents=True, exist_ok=True)
    # LOG_PATH.mkdir(parents=True, exist_ok=True)
    FONT_PATH.mkdir(parents=True, exist_ok=True)
    TEMP_PATH.mkdir(parents=True, exist_ok=True)
    JSON_PATH.mkdir(parents=True, exist_ok=True)

    IMAGE_PATH = str(IMAGE_PATH.absolute()) + '/'
    VOICE_PATH = str(VOICE_PATH.absolute()) + '/'
    TEXT_PATH = str(TEXT_PATH.absolute()) + '/'
    # LOG_PATH = str(LOG_PATH.absolute()) + '/'
    FONT_PATH = str(FONT_PATH.absolute()) + '/'
    TEMP_PATH = str(TEMP_PATH.absolute()) + '/'
    JSON_PATH = str(JSON_PATH.absolute()) + '/'


init_path()
