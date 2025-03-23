"""Utilities for modules"""

import logging
import time
import pickle
import os
from pathlib import Path
from enum import Enum

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class LogLevel(str, Enum):
    """Logging level options for the scraper"""
    MINIMAL = "minimal"  # Only start/end messages
    NORMAL = "normal"   # Important progress (default)
    DEBUG = "debug"     # All details

COOKIE_PATH = Path(__file__).parent.joinpath("secrets")
URL = (
    "https://www.funda.nl/en/zoeken/huur?"
    + "selected_area=[%22eindhoven%22]&price=%22500-2000%22"
)
    
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger("funda_scraper")
ch = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def set_logging_level(level: LogLevel = LogLevel.NORMAL):
    """Set the logging level based on verbosity preference
    
    Args:
        level: LogLevel enum value (minimal, normal, or debug)
    """
    if level == LogLevel.MINIMAL:
        logger.setLevel(logging.ERROR)
        ch.setLevel(logging.ERROR)
    elif level == LogLevel.DEBUG:
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
    else:  # NORMAL
        logger.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)

def set_info_level():
    """Temporarily set logging level to INFO for important messages"""
    set_logging_level(LogLevel.NORMAL)

# Set default logging level to ERROR (minimal)
set_logging_level(LogLevel.MINIMAL)


# Cookies fetch
def get_selenium_web_driver():
    """Create a Chrome driver instance with selenium webdriver."""
    chrome_options = Options()

    return webdriver.Chrome(options=chrome_options)


def get_cookies(cookie_path : Path = COOKIE_PATH, url : str = URL):
    """Prompt user to solve captcha puzzle on an interactive web. Get and save cookies for later requests."""
    logger.error("Starting cookie extraction...")
    driver = get_selenium_web_driver()
    driver.get(url)
    
    try:
        button = driver.find_element(By.ID, "didomi-notice-agree-button")
        button.click()
    except Exception as e:
        logger.error(e)
        logger.error("Please accept the cookie policy manually")

    while "Je bent bijna op de pagina die je zoekt" in driver.page_source:
        time.sleep(5)
    
    logger.error("Cookies extracted successfully")

    # Save cookies after solving CAPTCHA
    cookies = driver.get_cookies()
    if not os.path.isdir(cookie_path):
        os.makedirs(cookie_path)
    with open(cookie_path.joinpath("cookies.pkl").__str__(), "wb") as file:
        pickle.dump(cookies, file)

    driver.quit()

    return cookies


if __name__=="__main__":
    get_cookies()
