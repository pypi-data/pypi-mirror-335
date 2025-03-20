"""
Módulo para manipulação de frames e iframes.
"""

import logging
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException

from .elements import ElementHelper


class FrameHelper:
    """
    Classe auxiliar para manipulação de frames e iframes.
    """
    
    def __init__(
        self,
        driver: WebDriver,
        logger: logging.Logger,
        element_helper: ElementHelper,
        default_timeout: int = 10
    ):
        """
        Inicializa o helper de frames.
        
        Args:
            driver: Instância do WebDriver
            logger: Logger para registrar eventos
            element_helper: Helper para localização de elementos
            default_timeout: Tempo padrão de espera (em segundos)
        """
        self.driver = driver
        self.logger = logger
        self.element_helper = element_helper
        self.default_timeout = default_timeout
    
    def switch_to(
        self, 
        locator_type: Optional[str] = None, 
        locator_value: Optional[str] = None, 
        index: Optional[int] = None,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Muda o contexto para um frame ou iframe.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            index: Índice do frame (alternativa ao localizador)
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se a mudança foi bem-sucedida, False caso contrário
        """
        try:
            # Se um índice foi fornecido, muda para o frame por índice
            if index is not None:
                self.driver.switch_to.frame(index)
                self.logger.debug(f"Alterado para frame no índice {index}")
                return True
            
            # Se um localizador foi fornecido, encontra o elemento e muda para o frame
            elif locator_type and locator_value:
                element = self.element_helper.find_element(locator_type, locator_value, timeout)
                
                if not element:
                    self.logger.warning(f"Não foi possível mudar para frame: elemento não encontrado {locator_type}={locator_value}")
                    return False
                
                self.driver.switch_to.frame(element)
                self.logger.debug(f"Alterado para frame {locator_type}={locator_value}")
                return True
            
            else:
                self.logger.error("Deve fornecer um índice ou um localizador para mudar de frame")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao mudar para frame: {str(e)}")
            return False
    
    def switch_to_default_content(self) -> bool:
        """
        Retorna ao contexto principal da página.
        
        Returns:
            True se a mudança foi bem-sucedida, False caso contrário
        """
        try:
            self.driver.switch_to.default_content()
            self.logger.debug("Alterado para o contexto principal")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao retornar ao contexto principal: {str(e)}")
            return False
    
    def switch_to_parent_frame(self) -> bool:
        """
        Retorna ao frame pai.
        
        Returns:
            True se a mudança foi bem-sucedida, False caso contrário
        """
        try:
            self.driver.switch_to.parent_frame()
            self.logger.debug("Alterado para o frame pai")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao retornar ao frame pai: {str(e)}")
            return False
    
    def switch_to_window(self, window_handle: Optional[str] = None, index: Optional[int] = None) -> bool:
        """
        Muda para uma janela específica.
        
        Args:
            window_handle: Identificador da janela
            index: Índice da janela (alternativa ao identificador)
            
        Returns:
            True se a mudança foi bem-sucedida, False caso contrário
        """
        try:
            if window_handle:
                self.driver.switch_to.window(window_handle)
                self.logger.debug(f"Alterado para a janela com handle {window_handle}")
                return True
            
            elif index is not None:
                handles = self.driver.window_handles
                
                if 0 <= index < len(handles):
                    self.driver.switch_to.window(handles[index])
                    self.logger.debug(f"Alterado para a janela no índice {index}")
                    return True
                else:
                    self.logger.error(f"Índice de janela inválido: {index}, máximo: {len(handles)-1}")
                    return False
            
            else:
                self.logger.error("Deve fornecer um identificador ou um índice para mudar de janela")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao mudar para janela: {str(e)}")
            return False
    
    def switch_to_new_window(self, wait_time: int = 3) -> bool:
        """
        Muda para uma nova janela que foi aberta recentemente.
        
        Args:
            wait_time: Tempo para aguardar a abertura da janela
            
        Returns:
            True se a mudança foi bem-sucedida, False caso contrário
        """
        try:
            # Obtém os handles atuais
            original_handles = self.driver.window_handles
            original_handle = self.driver.current_window_handle
            
            # Aguarda pela abertura de uma nova janela
            new_handle = None
            max_attempts = wait_time * 2  # Polling a cada 0.5 segundos
            
            for _ in range(max_attempts):
                current_handles = self.driver.window_handles
                
                if len(current_handles) > len(original_handles):
                    # Encontra o handle da nova janela
                    for handle in current_handles:
                        if handle not in original_handles:
                            new_handle = handle
                            break
                    
                    if new_handle:
                        break
                
                import time
                time.sleep(0.5)
            
            if new_handle:
                self.driver.switch_to.window(new_handle)
                self.logger.debug(f"Alterado para a nova janela {new_handle}")
                return True
            else:
                self.logger.warning("Nenhuma nova janela foi detectada")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao mudar para nova janela: {str(e)}")
            return False
    
    def close_current_window(self) -> bool:
        """
        Fecha a janela atual e volta para a anterior.
        
        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        try:
            # Obtém todos os handles antes de fechar
            handles = self.driver.window_handles
            
            if len(handles) <= 1:
                self.logger.warning("Tentativa de fechar a única janela existente")
                return False
            
            # Armazena o handle atual para poder removê-lo da lista
            current_handle = self.driver.current_window_handle
            
            # Fecha a janela atual
            self.driver.close()
            
            # Encontra um handle válido para alternar
            handles = self.driver.window_handles  # Atualiza a lista após fechar
            
            # Muda para a primeira janela disponível
            if handles:
                self.driver.switch_to.window(handles[0])
                self.logger.debug("Janela atual fechada e alterado para outra janela")
                return True
            else:
                self.logger.error("Todas as janelas foram fechadas")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao fechar janela atual: {str(e)}")
            return False