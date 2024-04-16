from pydantic import BaseModel
from configs.path_config import IMAGE_PATH, FONT_PATH

imgpath = f"{IMAGE_PATH}/SteamInfo/"
fontpath = f"{FONT_PATH}/SteamInfo/"


class Config(BaseModel):
    steam_api_key: list = [
        "990D59CC71BE1CC6E9DDF078645C3522",
        "E3DBBE41003AAB4C4A29217BB4182063",
        "D55ABF876639B6D7F132D89F2D398CA8",
        "6948C9FFF96E239DF93B71EA44253E1C",
        "45163B1126357BBB1111BBBFA19569D3"
    ]
    proxy: str = "http://127.0.0.1:7890"
    steam_request_interval: int = 60  # seconds
