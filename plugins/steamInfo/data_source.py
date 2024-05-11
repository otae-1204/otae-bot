import json
from PIL import Image
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from .config import imgpath, fontpath
from .models import PlayerSummariesResponse
import time

class BindData:
    def __init__(self, save_path: str) -> None:
        self.content: Dict[str, Dict] = {}
        self._save_path = save_path

        if Path(save_path).exists():
            self.content = json.loads(Path(save_path).read_text("utf-8"))
        else:
            # 新建文件夹
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            self.save()

    def save(self) -> None:
        with open(self._save_path, "w", encoding="utf-8") as f:
            json.dump(self.content, f, indent=4)

    def add(self, user_id: str, content: Dict[Dict, Dict]) -> None:
        print(content)
        # 存储格式：{user_id: {steam_id: "xxxx", bindGroups: [{group_id: "xxxx", nickname: "xxxx"}]}}

        self.content[user_id] = content
        # if parent_id not in self.content:
        #     self.content[parent_id] = [content]
        # else:
        #     self.content[parent_id].append(content)

    def update(self, parent_id: str, content: Dict[str, str]) -> None:
        self.content[parent_id] = content

    def get(self, parent_id: str, user_id: str) -> Optional[Dict[str, str]]:
        if user_id not in self.content:
            return None
        for i in self.content[user_id]["bindGroups"]:
            if i["group_id"] == parent_id:
                return self.content[user_id]
        # return {"user_id": user_id, "steam_id": self.conten   t[user_id]["steam_id"]}
        return None

        # if parent_id not in self.content:
        #     return None
        # for data in self.content[parent_id]:
        #     if data["user_id"] == user_id:
        #         return data
        # return None

    def get_all(self, parent_id: str) -> List[str]:
        returnList = []
        # print(type(self.content))
        for j in self.content:
            # print(type(self.content[j]["bindGroups"]))
            # print("=-="*20)
            # print(self.content[j]["bindGroups"])
            for k in list(self.content[j]["bindGroups"]):
                # print("=-="*20)
                # print(type(k["group_id"]))
                # print(k["group_id"])
                if str(k["group_id"]) == parent_id:
                    returnList.append(self.content[j]["steam_id"])
                    break
        return returnList
        # if parent_id not in self.content:
        #     return []
        # return [data["steam_id"] for data in self.content[parent_id]]

    def get_info(self, parent_id: str) -> List[str]:
        returnList = []
        for i in self.content:
            for j in self.content[i]["bindGroups"]:
                if str(j["group_id"]) == parent_id:
                    returnList.append(
                        {
                            "steam_id": self.content[i]["steam_id"],
                            "user_id": i,
                            "nickname": j["nickname"],
                        }
                    )
                    break
        return returnList
        # if parent_id not in self.content:
        #     return []
        # return [data for data in self.content[parent_id]]

    def get_nickname(self, parent_id: str, steam_id: str) -> Optional[str]:
        for i in self.content:
            if self.content[i]["steam_id"] == steam_id:
                for j in self.content[i]["bindGroups"]:
                    if str(j["group_id"]) == parent_id:
                        return j["nickname"]
        return None

    def delete(self, parent_id: str, user_id: str) -> bool:
        for i in self.content:
            if i == user_id:
                for j in self.content[i]["bindGroups"]:
                    if str(j["group_id"]) == parent_id:
                        self.content[i]["bindGroups"].remove(j)
                        return True
        return False

class SteamInfoData:
    def __init__(self, save_path: str) -> None:
        self.content: Dict[str, PlayerSummariesResponse] = {}
        self._save_path = save_path

        if Path(save_path).exists():
            self.content = json.loads(Path(save_path).read_text("utf-8"))
        else:
            # 新建文件夹
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            self.save()

    def save(self) -> None:
        with open(self._save_path, "w", encoding="utf-8") as f:
            json.dump(self.content, f, indent=4)

    def update(self, parent_id: str, content: PlayerSummariesResponse) -> None:
        self.content[parent_id] = content

    def get(self, parent_id: str) -> Optional[PlayerSummariesResponse]:
        return self.content.get(parent_id, None)

    def compare(
        self, parent_id: str, new_content: PlayerSummariesResponse
    ) -> List[str]:
        old_content = self.get(parent_id)

        if old_content is None:
            self.update(parent_id, new_content)
            self.save()
            return []

        result = []

        for player in new_content["players"]:
            for old_player in old_content["players"]:
                if player["steamid"] == old_player["steamid"]:
                    # 判断旧游戏状态和新游戏状态是否一致
                    if player.get("gameextrainfo") != old_player.get("gameextrainfo"):
                        # 判断现在是否在游戏中
                        if player.get("gameextrainfo") is not None:
                            print(f"用户{player['personaname']}开始游戏,更新开始时间为{time.time()}")
                            player["update_time"] = time.time()
                            result.append(
                                {
                                    "type": "start",
                                    "player": player,
                                    "old_player": old_player,
                                }
                            )
                        # 判断之前是否在游戏中
                        elif old_player.get("gameextrainfo") is not None:
                            if "update_time" not in old_player:
                                old_player["update_time"] = time.time()
                            player["update_time"] = time.time()
                            print(f"用户{player['personaname']}结束游戏")
                            print(f"开始时间为{old_player['update_time']},结束时间为{player['update_time']}")
                            play_time = int(player["update_time"] - old_player["update_time"])
                            if play_time > 3600:
                                play_msg = f"{play_time//3600}小时{play_time%3600//60}分钟" if play_time%3600 >= 60 else f"{play_time//3600}小时"
                            elif play_time > 60:
                                play_msg = f"{play_time//60}分钟{play_time%60}秒" if play_time%60 > 0 else f"{play_time//60}分钟"
                            else:
                                play_msg = f"{play_time}秒"
                            result.append(
                                {
                                    "type": "stop",
                                    "player": player,
                                    "old_player": old_player,
                                    "play_time": play_msg
                                }
                            )
                        # 判断游戏状态是否一致
                        elif (
                            player.get("gameextrainfo") is not None
                            and old_player.get("gameextrainfo") is not None
                        ):
                            if "update_time" not in old_player:
                                old_player["update_time"] = time.time()
                            player["update_time"] = time.time()
                            play_time = player["update_time"] - old_player["update_time"]
                            if play_time > 3600:
                                play_msg = f"{play_time//3600}小时{play_time%3600//60}分钟" if play_time%3600 >= 60 else f"{play_time//3600}小时"
                            elif play_time > 60:
                                play_msg = f"{play_time//60}分钟{play_time%60}秒" if play_time%60 > 0 else f"{play_time//60}分钟"
                            else:
                                play_msg = f"{play_time}秒"
                            result.append(
                                {
                                    "type": "change",
                                    "player": player,
                                    "old_player": old_player,
                                    "play_time": play_msg
                                }
                            )
                        else:
                            result.append(
                                {
                                    "type": "error",
                                    "player": player,
                                    "old_player": old_player,
                                }
                            )
                    else:
                        player["update_time"] = old_player["update_time"]
        # print("保存的数据")
        # for i in new_content["players"]:
        #     print(i.keys())
        self.update(parent_id, new_content)
        self.save()
        return result

class ParentData:
    def __init__(self, save_path: str) -> None:
        self.content: Dict[str, str] = {}  # parent_id: name
        self._save_path = Path(save_path)

        if not (Path(save_path) / "parent_data.json").exists():
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            self.save()
        else:
            self.content = json.loads(
                (Path(save_path) / "parent_data.json").read_text("utf-8")
            )

    def save(self) -> None:
        with open(self._save_path / "parent_data.json", "w", encoding="utf-8") as f:
            json.dump(self.content, f, indent=4)

    def update(self, parent_id: str, avatar: Image.Image, name: str) -> None:
        self.content[parent_id] = name
        self.save()
        # 保存图片
        avatar_path = self._save_path / f"{parent_id}.png"
        avatar.save(avatar_path)

    def get(self, parent_id: str) -> Tuple[Image.Image, str]:
        if parent_id not in self.content:
            return Image.open(f"{imgpath}unknown_avatar.jpg"), parent_id
        avatar_path = self._save_path / f"{parent_id}.png"
        return Image.open(avatar_path), self.content[parent_id]
    
    def getAll(self):
        return self.content.keys()