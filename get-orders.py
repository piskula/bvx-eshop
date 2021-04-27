#!/usr/bin/python

import yaml
import json
import time
import datetime
from selenium import webdriver
from gui.order import Order
from gui.address import Address
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

with open("./config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

WP_HOMEPAGE = cfg['wordpress']['page']
WP_USERNAME = cfg['wordpress']['username']
WP_PASSWORD = cfg['wordpress']['password']

driver = webdriver.Chrome(cfg['browser'])
driver.implicitly_wait(30)
driver.set_window_size(1400, 900)


def login(user_login, user_pass):
    driver.find_element_by_id('user_login').send_keys(user_login)
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
    return Address(addressLines[0], addressLines[1] + ' ' + addressLines[2], addressLines[3])


def get_order_from_row(row_data):
    number_wrapper = row_data.find_element_by_class_name('column-order_number')
    number_preview = number_wrapper.find_element_by_class_name('order-preview')
    number = number_preview.get_attribute('data-order-id')

    number_view = number_wrapper.find_element_by_class_name('order-view')
    name = number_view.text

    date_wrapper = row_data.find_element_by_class_name('column-order_date')
    date = date_wrapper.find_element_by_tag_name('time').get_attribute('datetime')

    total_wrapper = row_data.find_element_by_class_name('column-order_total')
    total_currency = total_wrapper.find_element_by_class_name('woocommerce-Price-currencySymbol').text
    total = total_wrapper.find_element_by_class_name('woocommerce-Price-amount').text.replace(total_currency, '')

    order_items = []
    address = None

    number_preview.click()
    try:
        modal = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'wc-backbone-modal-content')))
        for item in modal.find_element_by_css_selector('table.wc-order-preview-table') \
                .find_element_by_tag_name('tbody') \
                .find_elements_by_css_selector('tr.wc-order-preview-table__item'):
            product = WebDriverWait(item, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'wc-order-preview-table__column--product')))
            order_item = driver.execute_script("return arguments[0].firstChild.textContent", product)

            address = extract_address(modal)

            order_items.append(order_item)
            # order_items.append(item.find_element_by_class_name('wc-order-preview-table__column--product').text)

        modal.find_element_by_css_selector('button.modal-close').click()
    except TimeoutException as ex:
        print('cannot open detail')
        exit_window()

    return Order(date, name, number, float(total), order_items, address)


def json_default(value):
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    else:
        return value.__dict__


def write_data_to_file(data, file):
    with open(file, 'x') as f:
        f.write(json.dumps(data, default=json_default, ensure_ascii=False))


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

    page = 1
    orders = []
    while True:
        print("Processing page " + str(page) + "...")
        for row in driver.find_element_by_css_selector('table.wp-list-table') \
                .find_element_by_tag_name('tbody') \
                .find_elements_by_css_selector('tr'):
            order = get_order_from_row(row)
            orders.append(order)
            # break #tmp
            # print(order)

        # TODO solve problem with click on next page, sleep did not help
        # if page == 2:
        #     break
        # try:
        #     click_next_page()
        # except NoSuchElementException:
        #     print('no nextPage')
        break

    write_data_to_file(orders, './data.json')
    logout()

finally:
    exit_window()
