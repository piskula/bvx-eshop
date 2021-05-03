#!/usr/bin/python

import yaml
import json
import time
from _datetime import datetime
from model.order import Order
from model.order_item import OrderItem
from model.address import Address
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from pathlib import Path
import jinja2
import webbrowser
from posta.libs.start_browser import start_browser

with open("./config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

WP_HOMEPAGE = cfg['wordpress']['page']
WP_USERNAME = cfg['wordpress']['username']
WP_PASSWORD = cfg['wordpress']['password']

driver = start_browser(1400, 900)


def login(user_login, user_pass):
    time.sleep(0.2)
    driver.find_element_by_id('user_login').send_keys(user_login)
    time.sleep(0.2)
    driver.find_element_by_id('user_pass').send_keys(user_pass)
    driver.find_element_by_id('wp-submit').click()


def logout():
    user_bar = driver.find_element_by_id('wp-admin-bar-my-account')
    hover = ActionChains(driver).move_to_element(user_bar)
    hover.perform()

    logout_element = driver.find_element_by_id('wp-admin-bar-logout')
    logout_element.click()


def exit_window():
    time.sleep(1)
    driver.quit()


def click_next_page():
    next_page = driver.find_element_by_css_selector("a[class='next-page button']")
    next_page.click()


def extract_address(modal):
    addressElemement = modal.find_element_by_css_selector('div.wc-order-preview-addresses > div:nth-child(2) > a')
    addressLines = addressElemement.text.split("\n")
    if len(addressLines) == 3:
        return Address(addressLines[0], addressLines[1], addressLines[2])
    return Address(addressLines[0], addressLines[1] + ' ' + addressLines[2], addressLines[3])


def extractPriceFromChild(element):
    total_currency = element.find_element_by_class_name('woocommerce-Price-currencySymbol').text
    return float(element.find_element_by_class_name('woocommerce-Price-amount').text.replace(total_currency, ''))


def get_order_from_row(row_data):
    number_wrapper = row_data.find_element_by_class_name('column-order_number')
    number_preview = number_wrapper.find_element_by_class_name('order-preview')
    number = number_preview.get_attribute('data-order-id')

    number_view = number_wrapper.find_element_by_class_name('order-view')
    name = number_view.text

    date_wrapper = row_data.find_element_by_class_name('column-order_date')
    date = date_wrapper.find_element_by_tag_name('time').get_attribute('datetime')

    total_wrapper = row_data.find_element_by_class_name('column-order_total')
    total = extractPriceFromChild(total_wrapper)

    order_items = []

    ActionChains(driver) \
        .key_down(Keys.CONTROL) \
        .click(number_view) \
        .key_up(Keys.CONTROL) \
        .perform()
    driver.switch_to.window(driver.window_handles[1])

    data_container = driver.find_element_by_class_name('order_data_column_container')
    data_container.find_element_by_css_selector('div:nth-child(3) > h3')\
        .find_element_by_class_name('edit_address').click()
    name = data_container.find_element_by_id('_shipping_first_name').get_attribute('value')
    surname = data_container.find_element_by_id('_shipping_last_name').get_attribute('value')
    company = data_container.find_element_by_id('_shipping_company').get_attribute('value')
    addr_line_1 = data_container.find_element_by_id('_shipping_address_1').get_attribute('value')
    addr_line_2 = data_container.find_element_by_id('_shipping_address_2').get_attribute('value')
    city = data_container.find_element_by_id('_shipping_city').get_attribute('value')
    postcode = data_container.find_element_by_id('_shipping_postcode').get_attribute('value')
    country = data_container.find_element_by_id('select2-_shipping_country-container').text
    address = Address(
        name=name + ' ' + surname,
        company=company,
        line_1=addr_line_1,
        line_2=addr_line_2,
        city=city,
        postcode=postcode,
        country=country,
    )

    for item in driver.find_element_by_id('order_line_items') \
            .find_elements_by_css_selector('tr.item'):
        item_name = item.find_element_by_class_name('wc-order-item-name').text
        item_price = float(item.find_element_by_class_name('item_cost').get_attribute('data-sort-value'))
        item_amount = item.find_element_by_class_name('quantity').find_element_by_class_name('view').text
        order_items.append(
            OrderItem(
                title=item_name, amount=item_amount, price=item_price
            )
        )

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return Order(date, name, number, float(total), order_items, address)


def json_default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    else:
        return value.__dict__


def process_orders():
    page = 1
    orders = []
    while True:
        # check for empty page:
        try:
            driver.find_element_by_css_selector('table.wp-list-table') \
                .find_element_by_tag_name('tbody')\
                .find_element_by_class_name('no-items')
            print("Page is empty.")
            break
        except NoSuchElementException:
            pass

        print("Processing page " + str(page) + "...")
        for row in driver.find_element_by_css_selector('table.wp-list-table') \
                .find_element_by_tag_name('tbody') \
                .find_elements_by_css_selector('tr'):
            order = get_order_from_row(row)
            orders.append(order)

        # TODO solve problem with click on next page, sleep did not help
        # if page == 2:
        #     break
        # try:
        #     click_next_page()
        #     page = page + 1
        # except NoSuchElementException:
        #     print('no nextPage')
        break
    return orders


def save_orders_to_json(orders, relative_json_path):
    path = Path(__file__).parent / relative_json_path
    # TODO delete previous file if exists
    with open(path, 'x', encoding="utf-8") as f:
        jsonText = json.dumps(orders, default=json_default, ensure_ascii=False)
        f.write(jsonText)


def fill_orders_with_how_old(orders):
    for order in orders:
        diff = datetime.now() - order.date.replace(tzinfo=None)
        order.howOld = diff


def generate_html(orders_for_shipping, orders_awaiting_payment):
    fill_orders_with_how_old(orders_for_shipping)
    fill_orders_with_how_old(orders_awaiting_payment)

    subs = jinja2.Environment(
        loader=jinja2.FileSystemLoader('./')
    ).get_template('./template/template.html').render(
        orders_for_shipping=orders_for_shipping,
        orders_awaiting_payment=orders_awaiting_payment,
        timestamp=datetime.now().strftime("%d %b %Y %H:%M"),
    )

    EXPORT_HTML_PATH = Path(__file__).parent / "./data/order_export.html"
    with open(EXPORT_HTML_PATH, 'w', encoding="utf-8") as f: f.write(subs)
    webbrowser.open('file://' + str(EXPORT_HTML_PATH), new=2)


time.sleep(5)
try:
    # Start
    driver.get(WP_HOMEPAGE)
    login(WP_USERNAME, WP_PASSWORD)

    # go to orders section
    driver.find_element_by_class_name('processing-orders').click()
    time.sleep(1)

    # go to all orders
    # driver.find_element_by_class_name('wc-on-hold').click()
    # driver.find_element_by_class_name('all').click()

    orders_for_shipping = process_orders()
    save_orders_to_json(orders_for_shipping, './data/orders-for-shipping.json')

    # go to orders section
    driver.find_element_by_class_name('wp-menu-name').click()
    driver.find_element_by_class_name('on-hold-orders').click()

    orders_awaiting_payment = process_orders()
    save_orders_to_json(orders_awaiting_payment, './data/orders-awaiting-payment.json')

    logout()

    generate_html(orders_for_shipping=orders_for_shipping, orders_awaiting_payment=orders_awaiting_payment)

finally:
    exit_window()
