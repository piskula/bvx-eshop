import yaml
from selenium import webdriver
from pathlib import Path

path = Path(__file__).parent / "../../config.yml"
with path.open() as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

BROWSER = cfg['browser']


def start_browser(window_x=1400, window_y=900):
    if BROWSER == 'chrome':
        driver = webdriver.Chrome()
    elif BROWSER == 'firefox':
        driver = webdriver.Firefox()
    else:
        raise Exception('not specified browser in config.yml')

    driver.implicitly_wait(30)
    driver.set_window_size(window_x, window_y)
    return driver
