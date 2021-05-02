#!/usr/bin/python

from libs.start_browser import start_browser
import yaml
import time
import pyautogui
from pathlib import Path

path = Path(__file__).parent / "../config.yml"
with path.open() as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

WP_HOMEPAGE = cfg['posta']['page']
WP_USERNAME = cfg['posta']['username']
WP_PASSWORD = cfg['posta']['password']
SEND_DATA_FULL_PATH = str(Path(__file__).parent / "./superfakturaepp.xml")

driver = start_browser(1400, 900)


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

    # element_present = EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='button done file']"))  # Example xpath
    #
    # WebDriverWait(driver, 2).until(element_present).click() # This opens the windows file selector
    #
    # time.sleep(2)
    # print('typing into box')
    # pyautogui.write(SEND_DATA_FULL_PATH)
    # pyautogui.press('enter')
    #


def choose_payment(icon):
    driver.find_element_by_css_selector("div[class='icon " + icon + "']").click()
    time.sleep(1)
    next_btn = driver.find_element_by_css_selector("div[class='button done']")
    # next_btn.click()
    driver.execute_script("arguments[0].click();", next_btn)
    print('clicked on payment type')


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
    choose_payment('lib_icon-eur')
    # choose_payment('lib_icon-card')

    time.sleep(3)

    logout()
    time.sleep(2)

finally:
    exit_window()
