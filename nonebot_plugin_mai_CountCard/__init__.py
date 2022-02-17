from nonebot.params import State, CommandArg, RegexDict
from nonebot import on_command, on_regex, on_keyword, require
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GROUP, MessageSegment, Event, Message, GroupMessageEvent
import nonebot
import os
from pathlib import Path
import json
import datetime

scheduler = require("nonebot_plugin_apscheduler").scheduler

# _LOCATION_PATH = nonebot.get_driver().config.loaction_path
file = os.path.join(os.path.dirname(__file__), 'data.json')
location_data=[]
# file = Path('') / 'data.json'
location_data=json.load(open(file, 'r', encoding='utf8'))

search_card = on_command("查卡", aliases={"查排卡"}, priority=25)

change_card = on_regex(r'^(?P<location>[\u4e00-\u9fa5_a-zA-Z0-9]+)\s*(?P<character>(\+|-))\s*(?P<card_num>\d+)$',priority=44, block=True)

@search_card.handle()
async def _(bot: Bot, event: GroupMessageEvent,  args: Message = CommandArg()):
    location = args.extract_plain_text().strip()
    # if location in getItem(location_data,'alias',f'{location}')['alias']:
    try:
        card = getItem(location_data,'alias',f'{location}')['card_count']
        location = getItem(location_data,'alias',f'{location}')['name']
        time = datetime.datetime.now().strftime("%H:%M:%S")
        msg = f'{location}店目前有{card}人'+f'\n更新时间为：{time}'

        await search_card.finish(msg)
    except TypeError:
        msg = '查询不到该店，请检查命令参数是否正确'
        await search_card.finish(msg)

@change_card.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: dict = RegexDict()):
    location = args['location']
    character = args['character']
    card_num = args['card_num']
    try:
        if character == '+':
            getItem(location_data, 'alias', f'{location}')['card_count'] += int(card_num)
        elif character == '-':
            getItem(location_data, 'alias', f'{location}')['card_count'] -= int(card_num)
        card = getItem(location_data, 'alias', f'{location}')['card_count']
        location = getItem(location_data, 'alias', f'{location}')['name']
        time = datetime.datetime.now().strftime("%H:%M:%S")
        msg = f'{location}店目前有{card}人' + f'\n更新时间为：{time}'
        with open(file, 'w', encoding='utf8') as f:
            json.dump(location_data, f, ensure_ascii=False, indent=4)
        await change_card.finish(msg)
    except TypeError:
        msg = '查询不到该店，请检查查询命令是否错误'
        await change_card.finish(msg)



# 重置一天的数据
@scheduler.scheduled_job("cron", hour=0, minute=00)
async def _():
    for i in range(len(location_data)):
        location_data[i]['card_count'] = 0
    with open(file, 'w', encoding='utf8') as f:
        json.dump(location_data, f, ensure_ascii=False, indent=4)


def getItem(arr, n, v):
    for i in range(len(arr)):
        if v in arr[i][n]:
            return arr[i]