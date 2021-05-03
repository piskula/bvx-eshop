#!/usr/bin/python

import json
import yaml
from pathlib import Path
import jinja2
from datetime import date

with open("./config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

USER_ID = cfg['posta']['userId']
API_KEY = cfg['posta']['apiKey']

orders_for_shipping_path = Path(__file__).parent / "./data/orders-for-shipping.json"

with open(orders_for_shipping_path, "r", encoding="utf-8") as read_file:
    orders_for_shipping = json.load(read_file)

if not isinstance(orders_for_shipping, list):
    exit('not a list')

for order in orders_for_shipping:
    country = order['address']['country']
    if country == 'Slovensko':
        order['address']['country_code'] = 'SK'
    elif country == 'Česko':
        order['address']['country_code'] = 'CZ'
    else:
        order['address']['country_code'] = ''

subs = jinja2.Environment(
    loader=jinja2.FileSystemLoader('./')
).get_template('./template/slovenska_posta_template.xml').render(
    amount=len(orders_for_shipping),
    data=orders_for_shipping,
    timestamp=date.today().isoformat(),
    userId=USER_ID,
    apiKey=API_KEY,
)

EXPORT_HTML_PATH = Path(__file__).parent / "./data/slovenska_posta_export.xml"
with open(EXPORT_HTML_PATH, 'w', encoding="utf-8") as f: f.write(subs)
