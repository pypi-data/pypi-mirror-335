"""
Módulo para navegação web com Selenium.
"""

import logging
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException


class NavigationHelper:
    """
    Classe auxiliar para navegação web.
    """
    
    def __init__(
        self,
        driver: WebDriver,
        logger: logging.Logger
    ):
        """
        Inicializa o helper de navegação.
        
        Args:
            driver: Instância do WebDriver
            logger: Logger para registrar eventos
        """
        self.driver = driver
        self.logger = logger
    
    def to(self, url: str) -> bool:
        """
        Navega para uma URL específica.
        
        Args:
            url: URL para navegar
            
        Returns:
            True se a navegação foi bem-sucedida, False caso contrário
        """
        try:
            self.driver.get(url)
            self.logger.info(f"Navegando para: {url}")
            return True
        except WebDriverException as e:
            self.logger.error(f"Erro ao navegar para {url}: {str(e)}")
            return False
    
    def refresh(self) -> bool:
        """
        Atualiza a página atual.
        
        Returns:
            True se a atualização foi bem-sucedida, False caso contrário
        """
        try:
            self.driver.refresh()
            self.logger.debug("Página atualizada")
            return True
        except WebDriverException as e:
            self.logger.error(f"Erro ao atualizar a página: {str(e)}")
            return False
    
    def back(self) -> bool:
        """
        Volta para a página anterior.
        
        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        try:
            self.driver.back()
            self.logger.debug("Voltando para a página anterior")
            return True
        except WebDriverException as e:
            self.logger.error(f"Erro ao voltar para a página anterior: {str(e)}")
            return False
    
    def forward(self) -> bool:
        """
        Avança para a próxima página.
        
        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        try:
            self.driver.forward()
            self.logger.debug("Avançando para a próxima página")
            return True
        except WebDriverException as e:
            self.logger.error(f"Erro ao avançar para a próxima página: {str(e)}")
            return False
    
    def get_current_url(self) -> str:
        """
        Obtém a URL atual.
        
        Returns:
            URL atual
        """
        return self.driver.current_url
    
    def get_title(self) -> str:
        """
        Obtém o título da página atual.
        
        Returns:
            Título da página atual
        """
        return self.driver.title
    
    def scroll_to(self, x: int = 0, y: int = 0) -> bool:
        """
        Rola a página para uma posição específica.
        
        Args:
            x: Posição horizontal
            y: Posição vertical
            
        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        try:
            self.driver.execute_script(f"window.scrollTo({{top: {y}, left: {x}, behavior: 'smooth'}});")
            self.logger.debug(f"Rolagem para a posição x={x}, y={y} bem-sucedida")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao rolar para a posição x={x}, y={y}: {str(e)}")
            return False
    
    def scroll_to_bottom(self) -> bool:
        """
        Rola a página para o final.
        
        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        try:
            self.driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
            self.logger.debug("Rolagem para o final da página bem-sucedida")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao rolar para o final da página: {str(e)}")
            return False
    
    def scroll_to_top(self) -> bool:
        """
        Rola a página para o topo.
        
        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        try:
            self.driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
            self.logger.debug("Rolagem para o topo da página bem-sucedida")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao rolar para o topo da página: {str(e)}")
            return False