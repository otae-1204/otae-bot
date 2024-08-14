from pydantic import BaseModel
from configs.path_config import IMAGE_PATH, FONT_PATH

imgpath = f"{IMAGE_PATH}/SteamInfo/"
fontpath = f"{FONT_PATH}/SteamInfo/"


class Config(BaseModel):
    steam_api_key: list = [

    ]
    proxy: str = "http://127.0.0.1:7890"
    steam_request_interval: int = 60  # seconds
