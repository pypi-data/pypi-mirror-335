from P_EO.common.config import Default, LogConfig
from P_EO.core.driver import (
    WebDriverManager,
    chrome_driver,
    chrome_driver_new,
    debug_chrome_driver,
    debug_chrome_driver_new
)
from P_EO.core.elements import Element, Elements, IFrame
from P_EO.core.page import Page

VERSION = '1.5.0'

__all__ = [
    Element,
    Elements,
    IFrame,
    Page,
    Default,
    LogConfig,
    WebDriverManager,
    chrome_driver,
    chrome_driver_new,
    debug_chrome_driver,
    debug_chrome_driver_new,
]
