"""
Módulo base para automação web com Selenium.
Contém a classe principal SeleniumHelper e funções utilitárias.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Union, List, Optional, Dict

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException

from .config import setup_browser
from .elements import ElementHelper
from .interactions import InteractionHelper
from .navigation import NavigationHelper
from .frames import FrameHelper
from .alerts import AlertHelper
from .utils import UtilityHelper


class SeleniumHelper:
    """
    Classe principal para automação web com Selenium.
    Integra os diferentes helpers para fornecer uma API completa.
    """

    def __init__(
        self,
        browser_type: str = "chrome",
        download_dir: Optional[Union[str, Path]] = None,
        headless: bool = False,
        user_agent: Optional[str] = None,
        proxy: Optional[str] = None,
        user_data_dir: Optional[str] = None,
        extensions: Optional[List[str]] = None,
        zoom_level: float = 1.0,
        disable_images: bool = False,
        incognito: bool = False,
        default_timeout: int = 10,
        max_retries: int = 3,
        retry_delay: int = 2,
        log_level: int = logging.INFO,
        log_folder: Union[str, Path] = "logs"
    ):
        """
        Inicializa o Selenium Helper.
        
        Args:
            browser_type: Tipo de navegador ('chrome', 'firefox', 'edge')
            download_dir: Diretório para download de arquivos
            headless: Se True, executa o navegador sem interface gráfica
            user_agent: String de User Agent personalizado
            proxy: Servidor proxy no formato "host:porta"
            user_data_dir: Diretório de perfil do usuário para persistência de sessão
            extensions: Lista de caminhos para extensões (apenas Chrome)
            zoom_level: Nível de zoom da página (1.0 = 100%)
            disable_images: Se True, desativa o carregamento de imagens
            incognito: Se True, executa o navegador em modo anônimo
            default_timeout: Tempo padrão de espera para elementos (em segundos)
            max_retries: Número máximo de tentativas para operações
            retry_delay: Tempo de espera entre tentativas (em segundos)
            log_level: Nível de log (logging.DEBUG, logging.INFO, etc.)
            log_folder: Diretório onde os logs serão armazenados
        """
        # Configuração de logging
        self.logger = self._setup_logger(log_level, log_folder)
        
        # Configurações comuns
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.zoom_level = zoom_level
        
        # Configura diretório de download
        if download_dir:
            self.download_dir = Path(download_dir)
            self.download_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.download_dir = Path("downloads")
            self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializa o driver
        self.driver = setup_browser(
            browser_type=browser_type,
            download_dir=self.download_dir,
            headless=headless,
            user_agent=user_agent,
            proxy=proxy,
            user_data_dir=user_data_dir,
            extensions=extensions,
            zoom_level=zoom_level,
            disable_images=disable_images,
            incognito=incognito
        )
        
        # Inicializa os helpers
        self._init_helpers()
    
    def _setup_logger(self, log_level: int, log_folder: Union[str, Path] = "logs") -> logging.Logger:
        """
        Configura e retorna um logger com handlers para console e arquivo rotativo.
        
        Args:
            log_level: Nível de log (logging.INFO, logging.DEBUG, etc.)
            log_folder: Diretório onde os logs serão armazenados
            
        Returns:
            logging.Logger: Logger configurado
        """
        # Converter para Path se for string
        log_folder = Path(log_folder)
        
        # Criar o logger
        logger = logging.getLogger("SeleniumHelper")
        
        # Se o logger já estiver configurado, remover handlers existentes para evitar duplicação
        if logger.handlers:
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
        
        # Garantir que o diretório de log existe
        log_folder.mkdir(parents=True, exist_ok=True)
        
        # Configurar o formato de log
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Adicionar handler para saída no console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Adicionar handler para arquivo com rotação
        timestamp = datetime.now().strftime("%Y%m%d")
        log_path = log_folder / f"SeleniumHelper_{timestamp}.log"
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_path, 
            maxBytes=1024*1024,  # 1MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Definir o nível de log
        logger.setLevel(log_level)
        
        # Log inicial para indicar início da sessão
        logger.info(f"Iniciando nova sessão do SeleniumHelper com nível de log: {logging.getLevelName(log_level)}")
        
        return logger
    
    def _init_helpers(self):
        """Inicializa os helpers para diferentes funcionalidades."""
        # Helper para elementos
        self.element = ElementHelper(
            driver=self.driver,
            logger=self.logger,
            default_timeout=self.default_timeout,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay
        )
        
        # Helper para interações
        self.interact = InteractionHelper(
            driver=self.driver,
            logger=self.logger,
            element_helper=self.element,
            default_timeout=self.default_timeout,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay
        )
        
        # Helper para navegação
        self.navigate = NavigationHelper(
            driver=self.driver,
            logger=self.logger
        )
        
        # Helper para frames
        self.frame = FrameHelper(
            driver=self.driver,
            logger=self.logger,
            element_helper=self.element,
            default_timeout=self.default_timeout
        )
        
        # Helper para alertas
        self.alert = AlertHelper(
            driver=self.driver,
            logger=self.logger,
            default_timeout=self.default_timeout
        )
        
        # Helper para utilitários
        self.utils = UtilityHelper(
            driver=self.driver,
            logger=self.logger,
            download_dir=self.download_dir,
            zoom_level=self.zoom_level
        )
    
    def close(self) -> None:
        """
        Encerra o navegador e libera os recursos.
        """
        try:
            self.driver.quit()
            self.logger.info("Navegador encerrado")
        except Exception as e:
            self.logger.error(f"Erro ao encerrar navegador: {str(e)}")
    
    def __enter__(self):
        """Suporte para uso como gerenciador de contexto."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Encerra o navegador ao sair do gerenciador de contexto."""
        self.close()


# Funções utilitárias para uso independente

def create_chrome_driver(
    download_dir: Optional[Union[str, Path]] = None,
    headless: bool = False,
    user_agent: Optional[str] = None,
    proxy: Optional[str] = None,
    user_data_dir: Optional[str] = None,
    disable_images: bool = False,
    incognito: bool = False,
    zoom_level: float = 1.0
) -> webdriver.Chrome:
    """
    Cria uma instância do Chrome WebDriver com configurações personalizadas.
    
    Args:
        download_dir: Diretório para download de arquivos
        headless: Se True, executa o navegador sem interface gráfica
        user_agent: String de User Agent personalizado
        proxy: Servidor proxy no formato "host:porta"
        user_data_dir: Diretório de perfil do usuário
        disable_images: Se True, desativa o carregamento de imagens
        incognito: Se True, executa o navegador em modo anônimo
        zoom_level: Nível de zoom (1.0 = 100%)
        
    Returns:
        Instância configurada do Chrome WebDriver
    """
    # Usa a função do módulo config para criar o driver
    from .config import setup_chrome_browser
    
    download_path = None
    if download_dir:
        download_path = Path(download_dir)
        download_path.mkdir(parents=True, exist_ok=True)
    
    return setup_chrome_browser(
        download_dir=download_path,
        headless=headless,
        user_agent=user_agent,
        proxy=proxy,
        user_data_dir=user_data_dir,
        extensions=None,
        zoom_level=zoom_level,
        disable_images=disable_images,
        incognito=incognito
    )