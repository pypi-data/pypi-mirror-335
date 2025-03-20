"""
Módulo de configuração para o Selenium.
Contém funções para configurar diferentes navegadores.
"""

import os
from pathlib import Path
from typing import Union, List, Optional, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService

# Verifica se o webdriver_manager está disponível
try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False


def setup_browser(
    browser_type: str,
    download_dir: Path,
    headless: bool = False,
    user_agent: Optional[str] = None,
    proxy: Optional[str] = None,
    user_data_dir: Optional[str] = None,
    extensions: Optional[List[str]] = None,
    zoom_level: float = 1.0,
    disable_images: bool = False,
    incognito: bool = False
) -> webdriver.Remote:
    """
    Configura e retorna um driver de navegador.
    
    Args:
        browser_type: Tipo de navegador ('chrome', 'firefox', 'edge')
        download_dir: Diretório para download de arquivos
        headless: Se True, executa o navegador sem interface gráfica
        user_agent: String de User Agent personalizado
        proxy: Servidor proxy no formato "host:porta"
        user_data_dir: Diretório de perfil do usuário
        extensions: Lista de caminhos para extensões
        zoom_level: Nível de zoom da página
        disable_images: Se True, desativa o carregamento de imagens
        incognito: Se True, executa o navegador em modo anônimo
        
    Returns:
        Instância configurada do WebDriver
    """
    browser_type = browser_type.lower()
    
    if browser_type == "chrome":
        driver = setup_chrome_browser(
            download_dir=download_dir,
            headless=headless,
            user_agent=user_agent,
            proxy=proxy,
            user_data_dir=user_data_dir,
            extensions=extensions,
            zoom_level=zoom_level,
            disable_images=disable_images,
            incognito=incognito
        )
    elif browser_type == "firefox":
        driver = setup_firefox_browser(
            download_dir=download_dir,
            headless=headless,
            user_agent=user_agent,
            proxy=proxy,
            user_data_dir=user_data_dir,
            disable_images=disable_images,
            incognito=incognito
        )
    elif browser_type == "edge":
        driver = setup_edge_browser(
            download_dir=download_dir,
            headless=headless,
            user_agent=user_agent,
            proxy=proxy,
            disable_images=disable_images,
            incognito=incognito
        )
    else:
        raise ValueError(f"Tipo de navegador não suportado: {browser_type}")
    
    # Configurações comuns
    driver.maximize_window()
    
    return driver


def setup_chrome_browser(
    download_dir: Path,
    headless: bool,
    user_agent: Optional[str],
    proxy: Optional[str],
    user_data_dir: Optional[str],
    extensions: Optional[List[str]],
    zoom_level: float,
    disable_images: bool,
    incognito: bool
) -> webdriver.Chrome:
    """
    Configura e retorna uma instância do Chrome WebDriver.
    
    Args:
        Parâmetros de configuração do Chrome
        
    Returns:
        Instância configurada do Chrome WebDriver
    """
    options = ChromeOptions()
    
    # Configurações gerais
    options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--force-device-scale-factor={zoom_level}")
    
    # Modo headless
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
    
    # User Agent personalizado
    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")
    
    # Proxy
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
    
    # Perfil de usuário
    if user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")
    
    # Modo incognito
    if incognito:
        options.add_argument("--incognito")
    
    # Desativar imagens
    if disable_images:
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    
    # Adicionar extensões
    if extensions:
        for extension in extensions:
            if os.path.exists(extension):
                options.add_extension(extension)
    
    # Configuração de download
    download_prefs = {
        "download.default_directory": str(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1
    }
    options.add_experimental_option("prefs", download_prefs)
    
    # Cria o driver
    if WEBDRIVER_MANAGER_AVAILABLE:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    
    return driver


def setup_firefox_browser(
    download_dir: Path,
    headless: bool,
    user_agent: Optional[str],
    proxy: Optional[str],
    user_data_dir: Optional[str],
    disable_images: bool,
    incognito: bool
) -> webdriver.Firefox:
    """
    Configura e retorna uma instância do Firefox WebDriver.
    
    Args:
        Parâmetros de configuração do Firefox
        
    Returns:
        Instância configurada do Firefox WebDriver
    """
    options = FirefoxOptions()
    
    # Modo headless
    if headless:
        options.add_argument("--headless")
    
    # User Agent personalizado
    if user_agent:
        options.set_preference("general.useragent.override", user_agent)
    
    # Proxy
    if proxy:
        host, port = proxy.split(":")
        options.set_preference("network.proxy.type", 1)
        options.set_preference("network.proxy.http", host)
        options.set_preference("network.proxy.http_port", int(port))
        options.set_preference("network.proxy.ssl", host)
        options.set_preference("network.proxy.ssl_port", int(port))
    
    # Perfil de usuário
    if user_data_dir:
        options.set_preference("profile", user_data_dir)
    
    # Modo incognito
    if incognito:
        options.set_preference("browser.privatebrowsing.autostart", True)
    
    # Desativar imagens
    if disable_images:
        options.set_preference("permissions.default.image", 2)
    
    # Configuração de download
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", str(download_dir))
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", 
        "application/pdf,application/x-pdf,application/octet-stream,application/csv,text/csv,application/vnd.ms-excel,application/zip")
    
    # Cria o driver
    if WEBDRIVER_MANAGER_AVAILABLE:
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
    else:
        driver = webdriver.Firefox(options=options)
    
    return driver


def setup_edge_browser(
    download_dir: Path,
    headless: bool,
    user_agent: Optional[str],
    proxy: Optional[str],
    disable_images: bool,
    incognito: bool
) -> webdriver.Edge:
    """
    Configura e retorna uma instância do Edge WebDriver.
    
    Args:
        Parâmetros de configuração do Edge
        
    Returns:
        Instância configurada do Edge WebDriver
    """
    options = EdgeOptions()
    
    # Configurações gerais
    options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    
    # Modo headless
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
    
    # User Agent personalizado
    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")
    
    # Proxy
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
    
    # Modo incognito
    if incognito:
        options.add_argument("--inprivate")
    
    # Desativar imagens
    if disable_images:
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    
    # Configuração de download
    download_prefs = {
        "download.default_directory": str(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", download_prefs)
    
    # Cria o driver
    if WEBDRIVER_MANAGER_AVAILABLE:
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
    else:
        driver = webdriver.Edge(options=options)
    
    return driver