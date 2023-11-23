import requests
from configs.path_config import IMAGE_PATH
import pymysql
from plugins.EFTHelper.object import Ammo
import os
from utils.user_agent import get_user_agent
from configs.config import SYSTEM_PROXY, password, user, address

path = IMAGE_PATH + 'EFTHelper/'

query_cn = """
{
    ammo(lang:zh){
        item{
            id #id
            name #名称
            iconLink #图标
            avg24hPrice #24平均价格
        }
  	    weight #重量
        caliber #口径
  	    stackMaxSize #最大堆叠数量
  	    tracer #是否曳光
		tracerColor #曳光颜色
      	damage #肉伤
  	    armorDamage #损甲百分比
     	fragmentationChance #碎弹率
  	    ricochetChance #跳弹率
      	penetrationPower #穿透值
  	    accuracyModifier #精度修正
      	recoilModifier #后座修正
  	    lightBleedModifier #小出血修正
      	heavyBleedModifier #大出血修正
        projectileCount #弹丸数量
        initialSpeed #初速
        staminaBurnPerDamage #消耗体力
  }
}
"""

# 口径查询开头
caliberStart = ["*", "✳", "＊"]

# ID查询开头
idStart = ["#", "＃"]

# 伤害查询开头
damageStart = ["%", "％"]

# 穿甲查询开头
penetrationStart = ["&", "＆"]

# 大于号兼容全角
greaterThan = [">", "＞"]

# 小于号兼容全角
lessThan = ["<", "＜"]

# 等于号兼容全角
equal = ["=", "＝"]

# 口径映射
caliber_mapping = {
    'Caliber556x45NATO': "5.56x45mm",
    'Caliber12g': "12/70",
    'Caliber762x54R': "7.62x54R",
    'Caliber762x39': "7.62x39mm",
    'Caliber40mmRU': "40x46mm",
    'Caliber9x19PARA': "9x19mm",
    'Caliber545x39': "5.45x39mm",
    'Caliber762x25TT': "7.62x25mm",
    'Caliber9x18PM': "9x18mmPM",
    'Caliber9x39': "9x39mm",
    'Caliber762x51': "7.62x51mm",
    'Caliber366TKM': ".366",
    'Caliber9x21': "9x21mm",
    'Caliber20g': "20/70",
    'Caliber46x30': "4.6x30mm",
    'Caliber127x55': "12.7x55mm",
    'Caliber57x28': "5.7x28mm",
    'Caliber1143x23ACP': ".45ACP",
    'Caliber23x75': "23x75mm",
    'Caliber40x46': "40x46mm",
    'Caliber762x35': ".300 AAC Blackout",
    'Caliber86x70': ".338 Lapua Magnum",
    'Caliber9x33R': ".357 Magnum",
    'Caliber26x75': "26x75mm"
}


# 通过任务编号查询任务名
def query_task_name(taskId):
    """
    说明:
        通过任务编号查询任务名
    参数:
        taskId : str
    返回:
        str
    """
    query_task = '{task(id:"' + taskId + '",lang:zh){name}}'
    headers = {"Content-Type": "application/json"}
    response = requests.post('https://api.tarkov.dev/graphql', json={
        'query': query_task}, headers=headers, timeout=30, proxies={"http" : SYSTEM_PROXY})
    if response.status_code == 200:
        result = response.json()
    else:
        print(f"请求失败,错误代码{response.status_code}")
        return -1
    print(result)
    return result["data"]["task"]["name"]


def clean_name(name_str: str) -> str:
    """
    说明:
        清理和格式化名称字符串.
    参数:
        name_str : [str] 名称字符串
    返回:
        str
    """
    # print("=-=-="*20)
    # print(name_str)
    # print("=-=-="*20)
    name_mapping = {
        "40毫米VOG-25榴弹": "VOG-25榴弹",
        "“Express”": "6.5毫米鹿弹",
        "“Magnum”": "8.5毫米鹿弹",
        "“Poleva-3”": "Poleva-3",
        "“Poleva-6u”": "Poleva-6u",
        "Copper": "Copper Sabot Premier",
        ".50": ".50 BMG",
        "“SuperFormance”": "SuperFormance",
        "Dual": "Dual Sabot",
        "Poleva-6u": "Poleva-6u",
        "Poleva-3u": "Poleva-3u",
    }
    name_list = name_str.replace("独头弹", "").split(" ")
    ammo_Name = ""
    if name_list[0] in name_mapping:
        ammo_Name = name_mapping[name_list[0]]
    elif len(name_list) == 1:
        ammo_Name = name_list[0]
    elif name_list[0] == ".300":
        if name_list[1] == "AAC":
            ammo_Name = " ".join(name_list[3:])
        elif name_list[1] == "BPZ":
            ammo_Name = "BPZ"
        elif name_list[1] == "Blackout":
            ammo_Name = " ".join(name_list[2:])
    elif name_list[0] == ".338":
        if name_list[1] == "Lapua":
            ammo_Name = " ".join(name_list[3:])
        elif name_list[1] == "UPZ":
            ammo_Name = "UPZ"
    elif name_list[0] == ".357":
        ammo_Name = " ".join(name_list[2:])
    elif name_list[1] == "R" or name_list[1] == "毫米":
        ammo_Name = " ".join(name_list[2:])
    else:
        ammo_Name = " ".join(name_list[1:])
    # print("=-=-="*20)
    # print(ammo_Name)
    return ammo_Name


def process_ammo_data(db, ammo_data) -> int:
    """
    说明:       
        处理子弹数据
    参数:
        db : [DatabaseDao] 数据库操作对象       
        ammo_data : [dict] 子弹数据
    返回:
        int
    """
    try:
        for i in ammo_data["data"]["ammo"]:
            caliberStr = i["caliber"]
            caliber = caliber_mapping[caliberStr] if caliberStr in caliber_mapping else caliberStr
            name = clean_name(i["item"]["name"])
            print(name)
            new_ammo = Ammo(
                id=None,
                name=name,
                caliber=caliber,
                weight=i["weight"],
                stackMaxSize=i["stackMaxSize"],
                tracer=i["tracer"],
                tracerColor=i["tracerColor"],
                damage=i["damage"],
                armorDamage=i["armorDamage"],
                fragmentationChance=i["fragmentationChance"],
                penetrationPower=i["penetrationPower"],
                ricochetChance=i["ricochetChance"],
                accuracyModifier=i["accuracyModifier"],
                recoilModifier=i["recoilModifier"],
                lightBleedModifier=i["lightBleedModifier"],
                heavyBleedModifier=i["heavyBleedModifier"],
                img=caliber.replace("毫米", "mm").replace(
                    "/", "_").replace('"', "") + " " + name.rstrip().replace('"', "") + ".png",
                marketSale=1 if i["item"]["avg24hPrice"] > 0 else 0,
                apiID=i["item"]["id"],
                projectileCount=i["projectileCount"],
                initialSpeed=i["initialSpeed"],
                staminaBurnPerDamage=round(i["staminaBurnPerDamage"], 3)
            )

            ammo_id = db.selectAmmo(new_ammo)
            if ammo_id > 0:
                db.updateAmmo(ammo_id, new_ammo)
                # 删除旧图片
                image_path = os.path.join(path, "bullet", caliber.replace("毫米", "mm").replace(
                    "/", "_").replace('"', "") + " " + name.rstrip().replace('"', "") + ".png")
                if os.path.exists(image_path):
                    os.remove(image_path)
                # 下载新图片
                result = requests.get(
                    i["item"]["iconLink"], timeout=30, proxies={"http" : SYSTEM_PROXY})
                if result.status_code == 200:
                    img_path = caliber.replace("毫米", "mm").replace(
                        "/", "_").replace('"', "") + " " + name.rstrip().replace('"', "")
                    with open(path + f"bullet/{img_path}.png", 'wb') as f:
                        f.write(result.content)
                    print(f"更新{img_path}成功")
                else:
                    print(f"请求失败,错误代码{result.status_code}")
                    return -1
            else:
                db.insertAmmo(new_ammo)
                # 下载新图片
                result = requests.get(
                    i["item"]["iconLink"], timeout=30, proxies={"http" : SYSTEM_PROXY})
                if result.status_code == 200:
                    img_path = caliber.replace("毫米", "mm").replace(
                        "/", "_").replace('"', "") + " " + name.rstrip().replace('"', "")
                    with open(path + f"bullet/{img_path}.png", 'wb') as f:
                        f.write(result.content)
                    print(f"下载{img_path}成功")
                else:
                    print(f"请求失败,错误代码{result.status_code}")
                    return -1

        return 1
    except Exception as e:
        print("处理子弹数据时出现错误:\n")
        print(e)
        
        return -1


def updateAmmoData() -> int:
    # try:
        db = DatabaseDao()
        headers = {"Content-Type": "application/json"}
        response = requests.post('https://api.tarkov.dev/graphql', json={
            'query': query_cn}, headers=headers, timeout=30, proxies={"http" : SYSTEM_PROXY})
        if response.status_code == 200:
            cnData = response.json()
        else:
            print("查询无法运行，返回的代码为 {}. {}".format(
                response.status_code, query_cn))

        return process_ammo_data(db, cnData)
    # except Exception as e:
    #     print("更新子弹数据时出现错误:\n")
    #     print(e.args)
    #     return -1


# 数据库操作类


class DatabaseDao:
    conn = None
    cursor = None

    @staticmethod
    def get_Connect():
        """
        说明:
            打开链接
        """
        try:
            conn = pymysql.connect(
                host="localhost", user=user, password=password, database="tkf_bullet_data")
        except Exception as e:
            print(e)
        return conn

    def closeAll(self):
        """
        说明:
            关闭所有对象
        """
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            self.conn.close()

    def insertAmmo(self, ammo: Ammo):
        """
        说明:
            插入一条数据
        """
        try:
            self.conn = self.get_Connect()
            self.cursor = self.conn.cursor()
            sql = "insert into bulletdata(name,caliber,weight,stackMaxSize,tracer,tracerColor,damage,armorDamage," \
                  "fragmentationChance,ricochetChance,penetrationPower,accuracyModifier,recoilModifier," \
                  "lightBleedModifier,heavyBleedModifier,img,marketSale) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
                  "%s,%s,%s,%s,%s) "
            self.cursor.execute(sql, (ammo.name, ammo.caliber, ammo.weight, ammo.stackMaxSize, ammo.tracer,
                                      ammo.tracerColor, ammo.damage, ammo.armorDamage, ammo.fragmentationChance,
                                      ammo.ricochetChance, ammo.penetrationPower, ammo.accuracyModifier,
                                      ammo.recoilModifier, ammo.lightBleedModifier, ammo.heavyBleedModifier, ammo.img,
                                      ammo.marketSale))
            self.conn.commit()
        except Exception as e:
            print("插入数据时出现错误:\n")
            print(e)
        finally:
            self.closeAll()

    def selectAmmo(self, ammo: Ammo) -> int:
        """
        说明:
            查询子弹是否存在
        返回:
            id / -1
        """
        try:
            self.conn = self.get_Connect()
            self.cursor = self.conn.cursor()
            sql = "select id from bulletdata where name = %s and caliber = %s"
            self.cursor.execute(sql, (ammo.name, ammo.caliber))
            result = self.cursor.fetchone()
            if result is None:
                return -1
            else:
                return result[0]
        except Exception as e:
            print("查询数据时出现错误:\n")
            print(e)
        finally:
            self.closeAll()

    def updateAmmo(self, ammoId: int, ammo: Ammo):
        """
        说明:
            更新数据
        """
        try:
            self.conn = self.get_Connect()
            self.cursor = self.conn.cursor()
            sql = "update bulletdata set name = %s, caliber = %s, weight = %s, stackMaxSize = %s, tracer = %s, " \
                  "tracerColor = %s, damage = %s, armorDamage = %s, fragmentationChance = %s, ricochetChance = %s, " \
                  "penetrationPower = %s, accuracyModifier = %s, recoilModifier = %s, lightBleedModifier = %s, " \
                  "heavyBleedModifier = %s, img = %s, marketSale = %s, apiID = %s, projectileCount = %s, initialSpeed = %s, " \
                  "staminaBurnPerDamage = %s where id = %s"
            self.cursor.execute(sql, (ammo.name, ammo.caliber, ammo.weight, ammo.stackMaxSize, ammo.tracer,
                                      ammo.tracerColor, ammo.damage, ammo.armorDamage, ammo.fragmentationChance,
                                      ammo.ricochetChance, ammo.penetrationPower, ammo.accuracyModifier,
                                      ammo.recoilModifier, ammo.lightBleedModifier, ammo.heavyBleedModifier, ammo.img,
                                      ammo.marketSale, ammo.apiID, ammo.projectileCount, ammo.initialSpeed,
                                      round(ammo.staminaBurnPerDamage, 3), ammoId))
            self.conn.commit()
        # except Exception as e:
        #     print(e)
        finally:
            self.closeAll()

    def deleteAmmo(self):
        """
        说明:
            删除数据
        """
        try:
            self.conn = self.get_Connect()
            self.cursor = self.conn.cursor()
            sql = "TRUNCATE TABLE bulletdata"
            self.cursor.execute(sql)
        except Exception as e:
            print("删除数据时出现错误:\n")
            print(e)
        finally:
            self.closeAll()

    def selectAmmoByName(self, name: list) -> list:
        """
        说明:
            通过名称查询子弹数据
        返回:
            list
        """
        try:
            self.conn = self.get_Connect()
            self.cursor = self.conn.cursor()
            sql = "select * from bulletdata"
            for i in range(0, len(name)):
                name[i] = "%" + name[i] + "%"
                sql += f' where name like "{name[i]}"' if i == 0 else f' or name like "{name[i]}"'
            # print(sql)
            sql += "  ORDER BY caliber,penetrationPower"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            ammoList = []
            print(result)
            for j in result:
                ammo = Ammo(j[0], j[1], j[2], j[3], j[4], j[5], j[6], j[7], j[8], j[9], j[10], j[11], j[12], j[13],
                            j[14],
                            j[15], j[16], j[17])
                ammoList.append(ammo)
            print(ammoList)
            return ammoList
        except Exception as e:
            print("通过名称查询数据时出现错误:\n")
            print(e)
            return []
        finally:
            self.closeAll()

    def selectAmmoById(self, id: list) -> list:
        """
        说明:
            通过Id查询子弹数据
        返回:
            Ammo
        """
        try:
            self.conn = self.get_Connect()
            self.cursor = self.conn.cursor()
            sql = "select * from bulletdata"
            for i in range(0, len(id)):
                sql += f' where id = "{id[i]}"' if i == 0 else f' or id = "{id[i]}"'
            # print(sql)
            sql += "  ORDER BY caliber,penetrationPower"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            ammoList = []
            for j in result:
                ammo = Ammo(j[0], j[1], j[2], j[3], j[4], j[5], j[6], j[7], j[8], j[9], j[10], j[11], j[12], j[13],
                            j[14],
                            j[15], j[16], j[17])
                ammoList.append(ammo)
            return ammoList
        except Exception as e:
            print("通过ID查询数据时出现错误:\n")
            print(e)
            return []
        finally:
            self.closeAll()

    def selectAmmoByCaliber(self, caliber: list) -> list:
        """
        说明:
            通过口径查询子弹数据
        返回:
            list
        """
        try:
            self.conn = self.get_Connect()
            self.cursor = self.conn.cursor()
            sql = "select * from bulletdata"
            for i in range(0, len(caliber)):
                caliber[i] = "%" + caliber[i] + "%"
                sql += f' where caliber like "{caliber[i]}"' if i == 0 else f' or caliber like "{caliber[i]}"'
            # print(sql)
            sql += "  ORDER BY caliber,penetrationPower"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            ammoList = []
            for j in result:
                ammo = Ammo(j[0], j[1], j[2], j[3], j[4], j[5], j[6], j[7], j[8], j[9], j[10], j[11], j[12], j[13],
                            j[14],
                            j[15], j[16], j[17])
                ammoList.append(ammo)
            return ammoList
        except Exception as e:
            print("通过口径查询数据时出现错误:\n")
            print(e)
            return []
        finally:
            self.closeAll()

    def selectAmmoByDiverse(self, conditions):
        """
        说明:
            通过多条件查询子弹数据
        参数:
            conditions : list[list]
            例: [["*5.56", "55A"], ["*5.45", "BT"]]
        返回:
            list
        """
        try:
            print(conditions)
            self.conn = self.get_Connect()
            self.cursor = self.conn.cursor()
            sql = "select * from bulletdata"
            ammoList = []
            for i in range(0, len(conditions)):
                print("*" * 50)
                print(conditions[i])
                conditions[i] = conditions[i].replace("amp;", "")
                if conditions[i][:1] in caliberStart:
                    sqlEx = "%" + \
                            conditions[i][1:].replace(
                                "*", "x").replace("×", "x").replace("＊", "x") + "%"
                    print(sqlEx)
                    sql += f' where caliber like "{sqlEx}"' if i == 0 \
                        else f' and caliber like "{sqlEx}" '
                elif conditions[i][:1] in idStart:
                    sqlEx = "%" + conditions[i][1:] + "%"
                    sql += f' where id = "{sqlEx}"' if i == 0 \
                        else f' and id = "{sqlEx}" '
                elif conditions[i][:1] in damageStart:
                    if conditions[i][1:2] in greaterThan:
                        if conditions[i][2:3] in equal:
                            sqlEx = conditions[i][3:]
                            sql += f' where damage >= "{sqlEx}"' if i == 0 \
                                else f' and damage >= "{sqlEx}" '
                        else:
                            sqlEx = conditions[i][2:]
                            sql += f' where damage > "{sqlEx}"' if i == 0 \
                                else f' and damage > "{sqlEx}" '
                    elif conditions[i][1:2] in lessThan:
                        if conditions[i][2:3] in equal:
                            sqlEx = conditions[i][3:]
                            sql += f' where damage <= "{sqlEx}"' if i == 0 \
                                else f' and damage <= "{sqlEx}" '
                        else:
                            sqlEx = conditions[i][2:]
                            sql += f' where damage < "{sqlEx}"' if i == 0 \
                                else f' and damage < "{sqlEx}" '
                    elif conditions[i][1:2] in equal:
                        sqlEx = conditions[i][2:]
                        sql += f' where damage = "{sqlEx}"' if i == 0 \
                            else f' and damage = "{sqlEx}" '
                elif conditions[i][:1] in penetrationStart:
                    if conditions[i][1:2] in greaterThan:
                        if conditions[i][2:3] in equal:
                            sqlEx = conditions[i][3:]
                            sql += f' where penetrationPower >= "{sqlEx}"' if i == 0 \
                                else f' and penetrationPower >= "{sqlEx}" '
                        else:
                            sqlEx = conditions[i][2:]
                            sql += f' where penetrationPower > "{sqlEx}"' if i == 0 \
                                else f' and penetrationPower > "{sqlEx}" '
                    elif conditions[i][1:2] in lessThan:
                        if conditions[i][2:3] in equal:
                            sqlEx = conditions[i][3:]
                            sql += f' where penetrationPower <= "{sqlEx}"' if i == 0 \
                                else f' and penetrationPower <= "{sqlEx}" '
                        else:
                            sqlEx = conditions[i][2:]
                            sql += f' where penetrationPower < "{sqlEx}"' if i == 0 \
                                else f' and penetrationPower < "{sqlEx}" '
                    elif conditions[i][1:2] in equal:
                        sqlEx = conditions[i][2:]
                        sql += f' where penetrationPower = "{sqlEx}"' if i == 0 \
                            else f' and penetrationPower = "{sqlEx}" '
                else:
                    sqlEx = "%" + conditions[i] + "%"
                    sql += f' where name like "{sqlEx}"' if i == 0 \
                        else f' and name like "{sqlEx}"'
            sql += " ORDER BY caliber,penetrationPower"
            print(sql)
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            # print(result)
            for k in result:
                ammo = Ammo(k[0], k[1], k[2], k[3], k[4], k[5], k[6], k[7], k[8], k[9], k[10], k[11], k[12], k[13],
                            k[14],
                            k[15], k[16], k[17], k[18], k[19], k[20], k[21])
                ammoList.append(ammo)
                # print(ammoList)
            return ammoList
        except Exception as e:
            print("通过多条件查询数据时出现错误:\n")
            print(e)
            return []
        finally:
            self.closeAll()

    def selectAmmoByOneCondition(self, condition):
        """
        说明:
            通过单条件查询子弹数据
        参数:
            condition : str
            例: "*5.56"
        返回:
            list
        """
        try:

            self.conn = self.get_Connect()
            self.cursor = self.conn.cursor()
            sql = "select * from bulletdata"
            print(condition)
            condition = condition.replace("amp;", "")
            if condition[:1] in caliberStart:
                sqlEx = "%" + \
                        condition[1:].replace(
                            "*", "x").replace("×", "x").replace("＊", "x") + "%"
                sql += f' where caliber like "{sqlEx}"'
            elif condition[:1] in idStart:
                sqlEx = condition[1:]
                sql += f' where id = "{sqlEx}"'
            elif condition[:1] in damageStart:
                if condition[1:2] in greaterThan:
                    if condition[2:3] in equal:
                        sqlEx = condition[3:]
                        sql += f' where damage >= "{sqlEx}"'
                    else:
                        sqlEx = condition[2:]
                        sql += f' where damage > "{sqlEx}"'
                elif condition[1:2] in lessThan:
                    if condition[2:3] in equal:
                        sqlEx = condition[3:]
                        sql += f' where damage <= "{sqlEx}"'
                    else:
                        sqlEx = condition[2:]
                        sql += f' where damage < "{sqlEx}"'
                elif condition[1:2] in equal:
                    sqlEx = condition[2:]
                    sql += f' where damage = "{sqlEx}"'
            elif condition[:1] in ["&", ]:
                if condition[1:2] in greaterThan:
                    if condition[2:3] in equal:
                        sqlEx = condition[3:]
                        sql += f' where penetrationPower >= "{sqlEx}"'
                    else:
                        sqlEx = condition[2:]
                        sql += f' where penetrationPower > "{sqlEx}"'
                elif condition[1:2] in lessThan:
                    if condition[2:3] in equal:
                        sqlEx = condition[3:]
                        sql += f' where penetrationPower <= "{sqlEx}"'
                    else:
                        sqlEx = condition[2:]
                        sql += f' where penetrationPower < "{sqlEx}"'
                elif condition[1:2] in equal:
                    sqlEx = condition[2:]
                    sql += f' where penetrationPower = "{sqlEx}"'
            else:
                sqlEx = "%" + condition + "%"
                sql += f' where name like "{sqlEx}"'
            sql += " ORDER BY caliber,penetrationPower"
            print(sql)
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            ammoList = []
            for i in result:
                ammo = Ammo(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10], i[11], i[12], i[13],
                            i[14],
                            i[15], i[16], i[17], i[18], i[19], i[20], i[21])
                ammoList.append(ammo)
            return ammoList
        except Exception as e:
            print("通过单条件查询数据时出现错误:\n")
            print(e)
            return []
        finally:
            self.closeAll()

# updateAmmoData()
