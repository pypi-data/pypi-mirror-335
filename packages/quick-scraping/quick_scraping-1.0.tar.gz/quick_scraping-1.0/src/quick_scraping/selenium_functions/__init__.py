"""
Pacote para automação web com Selenium.
Fornece uma API simplificada para interações com páginas web.
"""

from .selenium_base import SeleniumHelper, create_chrome_driver
from .config import setup_browser, setup_chrome_browser, setup_firefox_browser, setup_edge_browser
from .elements import ElementHelper
from .interactions import InteractionHelper
from .navigation import NavigationHelper
from .frames import FrameHelper
from .alerts import AlertHelper
from .utils import UtilityHelper

__all__ = [
    'SeleniumHelper',
    'create_chrome_driver',
    'setup_browser',
    'setup_chrome_browser',
    'setup_firefox_browser',
    'setup_edge_browser',
    'ElementHelper',
    'InteractionHelper',
    'NavigationHelper',
    'FrameHelper',
    'AlertHelper',
    'UtilityHelper',
]

__version__ = '1.0.0'