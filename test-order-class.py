#!/usr/bin/python

import yaml
import json
import datetime
from gui.order import Order


def json_default(value):
  if isinstance(value, datetime.datetime):
    return value.isoformat()
  else:
    return value.__dict__


line_1 = Order('2021-04-22T12:58:18+00:00', 'title?', '15936', float('38.80'), [])
line_2 = Order('2021-04-22T12:58:18+00:00', 'Maroš Čižmár', '15936', float('38.80'), [])

print(str(line_1))
print(str(line_2))

# with open("./config.yml", 'r') as ymlfile:
#   cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
#
# print(cfg['wordpress']['username'])
# print(cfg['wordpress']['password'])

orders = [line_1, line_2]
# with open('./data.json', 'x') as f:
#   json.dump(orders, f, sort_keys=True)
with open('./data.json', 'x') as f:
  f.write(json.dumps(orders, default=json_default, ensure_ascii=False))
