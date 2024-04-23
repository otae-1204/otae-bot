from api import *
import asyncio
import base64
from PIL import Image
import io


async def test():
    # result = await submitRoomNumber(124516,"25w清火q1","onebot","2461673400","2461673400")
    # print(result)
    
    # result = await ycm()
    # print(result)
    
    result = await getUserData("onebot","2461673400")
    print(result)
    
    # result = await searchCard([3,0],"947")

    # for i in result:
    #     if "type" in i and i["type"] == "string":
    #         print(i["string"])
    #     else:
    #         base = i["string"]
    #         print(f"[图像大小: {len(base) / 1024:.2f}KB]") if isinstance(base, bytes) else None
    #         Image.open(io.BytesIO(base64.b64decode(base))).show()



asyncio.run(test())