# -*- coding: utf-8 -*-
import json
from aiohttp import web
from recoveryVSD import createTransaction

RECOVERY_PATH = r"C:\PYTHON\Servers\recovery.json"
jsonFile = open("settings.json", encoding="utf-8")
settingsMercury = (json.load(jsonFile))


async def returnVsd(request):
    dateReturn = await request.text()
    createTransaction(settingsMercury["url"], settingsMercury["headers"], begin_date=str(dateReturn))
    file = open(RECOVERY_PATH, encoding="utf-8")
    data = (json.load(file))
    file.close()
    headers = {'Access-control-allow-origin': '*'}
    return web.json_response(data["recovery"], headers=headers)


app = web.Application()
app.add_routes([web.post('/returnVsd', returnVsd)])

if __name__ == '__main__':
    web.run_app(app)
