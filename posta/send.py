#!/usr/bin/python

import yaml
import time
import pyautogui
from selenium import webdriver
from pathlib import Path

path = Path(__file__).parent / "../config.yml"
with path.open() as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

WP_HOMEPAGE = cfg['posta']['page']
WP_USERNAME = cfg['posta']['username']
WP_PASSWORD = cfg['posta']['password']
SEND_DATA_FULL_PATH = Path(__file__).parent / "./send-data.xml"

driver = webdriver.Chrome(cfg['browser'])
driver.implicitly_wait(30)
driver.set_window_size(1400, 900)


def login(user_login, user_pass):
    driver.find_element_by_id('username').send_keys(user_login)
    driver.find_element_by_css_selector("input[name='password'][type='password']").send_keys(user_pass)
    driver.find_element_by_css_selector("input[type='submit']").click()


def logout():
    driver.find_element_by_css_selector("div.account").click()
    driver.find_element_by_css_selector('div.popover > div:last-child').click()


def import_xml():
    driver.find_element_by_css_selector("div.import > div.button").click()
    driver.find_element_by_css_selector("div[class='button done file").click()
    pyautogui.write(SEND_DATA_FULL_PATH)
    pyautogui.press('enter')
    pyautogui.press('return')
    time.sleep(1)


def exit_window():
    time.sleep(1)
    driver.quit()


#######
# START
#######


try:
    driver.get(WP_HOMEPAGE)
    login(WP_USERNAME, WP_PASSWORD)
    import_xml()

    logout()
    time.sleep(2)

finally:
    exit_window()
