#!/usr/bin/python

import json
from pathlib import Path
import jinja2
from datetime import datetime

orders_for_shipping_path = Path(__file__).parent / "./orders-for-shipping.json"
orders_awaiting_payment_path = Path(__file__).parent / "./orders-awaiting-payment.json"

orders_for_shipping = None
with open(orders_for_shipping_path, "r") as read_file:
    orders_for_shipping = json.load(read_file)

orders_awaiting_payment = None
with open(orders_awaiting_payment_path, "r") as read_file:
    orders_awaiting_payment = json.load(read_file)

if not isinstance(orders_for_shipping, list):
    exit('not a list')
if not isinstance(orders_awaiting_payment, list):
    exit('not a list')

for order in orders_for_shipping:
    time = datetime.fromisoformat(order['date']).replace(tzinfo=None)
    diff = datetime.now() - time
    order['howOld'] = diff
for order in orders_awaiting_payment:
    time = datetime.fromisoformat(order['date']).replace(tzinfo=None)
    diff = datetime.now() - time
    order['howOld'] = diff

subs = jinja2.Environment(
    loader=jinja2.FileSystemLoader('./')
).get_template('./template/template.html').render(
    orders_for_shipping=orders_for_shipping,
    orders_awaiting_payment=orders_awaiting_payment,
    timestamp=datetime.now().strftime("%d %b %Y %H:%M"),
)

EXPORT_HTML_PATH = Path(__file__).parent / "./order_export_test.html"
with open(EXPORT_HTML_PATH, 'w') as f: f.write(subs)
