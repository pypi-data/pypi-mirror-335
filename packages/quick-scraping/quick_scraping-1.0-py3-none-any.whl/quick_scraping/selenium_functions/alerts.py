"""
Módulo para manipulação de alertas JavaScript.
"""

import logging
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class AlertHelper:
    """
    Classe auxiliar para interação com alertas JavaScript.
    """
    
    def __init__(
        self,
        driver: WebDriver,
        logger: logging.Logger,
        default_timeout: int = 10
    ):
        """
        Inicializa o helper de alertas.
        
        Args:
            driver: Instância do WebDriver
            logger: Logger para registrar eventos
            default_timeout: Tempo padrão de espera (em segundos)
        """
        self.driver = driver
        self.logger = logger
        self.default_timeout = default_timeout
    
    def accept(self, timeout: Optional[int] = None) -> bool:
        """
        Aceita um alerta JavaScript.
        
        Args:
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        timeout = self.default_timeout if timeout is None else timeout
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            alert = wait.until(EC.alert_is_present())
            
            alert_text = alert.text
            alert.accept()
            
            self.logger.debug(f"Alerta aceito: '{alert_text}'")
            return True
        except TimeoutException:
            self.logger.warning("Nenhum alerta foi exibido")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao aceitar alerta: {str(e)}")
            return False
    
    def dismiss(self, timeout: Optional[int] = None) -> bool:
        """
        Cancela um alerta JavaScript.
        
        Args:
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        timeout = self.default_timeout if timeout is None else timeout
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            alert = wait.until(EC.alert_is_present())
            
            alert_text = alert.text
            alert.dismiss()
            
            self.logger.debug(f"Alerta cancelado: '{alert_text}'")
            return True
        except TimeoutException:
            self.logger.warning("Nenhum alerta foi exibido")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao cancelar alerta: {str(e)}")
            return False
    
    def get_text(self, timeout: Optional[int] = None) -> Optional[str]:
        """
        Obtém o texto de um alerta JavaScript sem interagir com ele.
        
        Args:
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            Texto do alerta ou None se não houver alerta
        """
        timeout = self.default_timeout if timeout is None else timeout
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            alert = wait.until(EC.alert_is_present())
            
            alert_text = alert.text
            self.logger.debug(f"Texto do alerta obtido: '{alert_text}'")
            return alert_text
        except TimeoutException:
            self.logger.warning("Nenhum alerta foi exibido")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao obter texto do alerta: {str(e)}")
            return None
    
    def send_text(self, text: str, timeout: Optional[int] = None, accept: bool = True) -> bool:
        """
        Envia texto para um alerta JavaScript e opcionalmente o aceita.
        
        Args:
            text: Texto a ser enviado para o alerta
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            accept: Se True, aceita o alerta após enviar o texto
            
        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        timeout = self.default_timeout if timeout is None else timeout
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            alert = wait.until(EC.alert_is_present())
            
            alert.send_keys(text)
            
            if accept:
                alert.accept()
                self.logger.debug(f"Texto '{text}' enviado para o alerta e aceito")
            else:
                self.logger.debug(f"Texto '{text}' enviado para o alerta")
            
            return True
        except TimeoutException:
            self.logger.warning("Nenhum alerta foi exibido")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao enviar texto para o alerta: {str(e)}")
            return False
    
    def is_present(self, timeout: Optional[int] = None) -> bool:
        """
        Verifica se um alerta está presente na página.
        
        Args:
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se o alerta estiver presente, False caso contrário
        """
        timeout = self.default_timeout if timeout is None else timeout
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.alert_is_present())
            return True
        except TimeoutException:
            return False
        except Exception:
            return False