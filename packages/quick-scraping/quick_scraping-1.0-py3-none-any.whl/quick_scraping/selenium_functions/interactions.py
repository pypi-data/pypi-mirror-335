"""
Módulo para interações com elementos da página.
"""

import logging
from time import sleep
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    JavascriptException
)

from .elements import ElementHelper


class InteractionHelper:
    """
    Classe auxiliar para interações com elementos na página.
    """
    
    def __init__(
        self,
        driver: WebDriver,
        logger: logging.Logger,
        element_helper: ElementHelper,
        default_timeout: int = 10,
        max_retries: int = 3,
        retry_delay: int = 2
    ):
        """
        Inicializa o helper de interações.
        
        Args:
            driver: Instância do WebDriver
            logger: Logger para registrar eventos
            element_helper: Helper para localização de elementos
            default_timeout: Tempo padrão de espera (em segundos)
            max_retries: Número máximo de tentativas para operações
            retry_delay: Tempo de espera entre tentativas (em segundos)
        """
        self.driver = driver
        self.logger = logger
        self.element_helper = element_helper
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def click(
        self, 
        locator_type: str, 
        locator_value: str, 
        timeout: Optional[int] = None,
        safe_click: bool = True,
        scroll_into_view: bool = True
    ) -> bool:
        """
        Clica em um elemento na página.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            safe_click: Se True, tenta clicar com JavaScript caso o clique normal falhe
            scroll_into_view: Se True, rola a página para mostrar o elemento antes de clicar
            
        Returns:
            True se o clique foi bem-sucedido, False caso contrário
        """
        element = self.element_helper.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível clicar: elemento não encontrado {locator_type}={locator_value}")
            return False
        
        try:
            if scroll_into_view:
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                sleep(0.5)  # Pequeno delay para o scroll terminar
            
            try:
                # Primeira tentativa: clique normal
                element.click()
                self.logger.debug(f"Clique bem-sucedido em {locator_type}={locator_value}")
                return True
            except (ElementClickInterceptedException, ElementNotInteractableException) as e:
                if safe_click:
                    self.logger.debug(f"Clique normal falhou, tentando JavaScript: {str(e)}")
                    # Segunda tentativa: clique via JavaScript
                    try:
                        self.driver.execute_script("arguments[0].click();", element)
                        self.logger.debug(f"Clique via JavaScript bem-sucedido em {locator_type}={locator_value}")
                        return True
                    except JavascriptException as js_e:
                        self.logger.error(f"Falha no clique via JavaScript: {str(js_e)}")
                        raise
                else:
                    raise
        except Exception as e:
            self.logger.error(f"Erro ao clicar em {locator_type}={locator_value}: {str(e)}")
            return False
    
    def double_click(
        self, 
        locator_type: str, 
        locator_value: str, 
        timeout: Optional[int] = None
    ) -> bool:
        """
        Realiza duplo clique em um elemento.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se o duplo clique foi bem-sucedido, False caso contrário
        """
        element = self.element_helper.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível realizar duplo clique: elemento não encontrado {locator_type}={locator_value}")
            return False
        
        try:
            # Rolar para o elemento
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            sleep(0.5)  # Pequeno delay para o scroll terminar
            
            # Duplo clique via ActionChains
            action = ActionChains(self.driver)
            action.double_click(element).perform()
            
            self.logger.debug(f"Duplo clique bem-sucedido em {locator_type}={locator_value}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao realizar duplo clique em {locator_type}={locator_value}: {str(e)}")
            return False
    
    def right_click(
        self, 
        locator_type: str, 
        locator_value: str, 
        timeout: Optional[int] = None
    ) -> bool:
        """
        Realiza clique com botão direito em um elemento.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se o clique direito foi bem-sucedido, False caso contrário
        """
        element = self.element_helper.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível realizar clique direito: elemento não encontrado {locator_type}={locator_value}")
            return False
        
        try:
            # Rolar para o elemento
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            sleep(0.5)  # Pequeno delay para o scroll terminar
            
            # Clique direito via ActionChains
            action = ActionChains(self.driver)
            action.context_click(element).perform()
            
            self.logger.debug(f"Clique direito bem-sucedido em {locator_type}={locator_value}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao realizar clique direito em {locator_type}={locator_value}: {str(e)}")
            return False
    
    def hover(
        self, 
        locator_type: str, 
        locator_value: str, 
        timeout: Optional[int] = None
    ) -> bool:
        """
        Move o cursor para um elemento.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se o hover foi bem-sucedido, False caso contrário
        """
        element = self.element_helper.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível realizar hover: elemento não encontrado {locator_type}={locator_value}")
            return False
        
        try:
            # Rolar para o elemento
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            sleep(0.5)  # Pequeno delay para o scroll terminar
            
            # Hover via ActionChains
            action = ActionChains(self.driver)
            action.move_to_element(element).perform()
            
            self.logger.debug(f"Hover bem-sucedido em {locator_type}={locator_value}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao realizar hover em {locator_type}={locator_value}: {str(e)}")
            return False
    
    def type_text(
        self, 
        locator_type: str, 
        locator_value: str, 
        text: str, 
        timeout: Optional[int] = None,
        clear_first: bool = True,
        click_first: bool = False,
        press_enter: bool = False
    ) -> bool:
        """
        Digita texto em um elemento.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            text: Texto a ser digitado
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            clear_first: Se True, limpa o campo antes de digitar
            click_first: Se True, clica no elemento antes de digitar
            press_enter: Se True, pressiona Enter após digitar
            
        Returns:
            True se a digitação foi bem-sucedida, False caso contrário
        """
        element = self.element_helper.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível digitar: elemento não encontrado {locator_type}={locator_value}")
            return False
        
        try:
            # Rolar para o elemento
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            sleep(0.3)
            
            if click_first:
                element.click()
            
            if clear_first:
                element.clear()
            
            # Digita o texto
            element.send_keys(text)
            
            if press_enter:
                element.send_keys(Keys.RETURN)
            
            self.logger.debug(f"Texto '{text}' digitado com sucesso em {locator_type}={locator_value}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao digitar texto em {locator_type}={locator_value}: {str(e)}")
            return False
    
    def clear_text(
        self, 
        locator_type: str, 
        locator_value: str, 
        timeout: Optional[int] = None
    ) -> bool:
        """
        Limpa o texto de um elemento.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se a limpeza foi bem-sucedida, False caso contrário
        """
        element = self.element_helper.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível limpar texto: elemento não encontrado {locator_type}={locator_value}")
            return False
        
        try:
            element.clear()
            
            # Verificação extra para garantir que o campo realmente foi limpo
            if element.get_attribute("value") or element.text:
                # Se ainda tiver texto, tenta outros métodos
                element.send_keys(Keys.CONTROL + "a")
                element.send_keys(Keys.DELETE)
            
            self.logger.debug(f"Texto limpo com sucesso em {locator_type}={locator_value}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao limpar texto em {locator_type}={locator_value}: {str(e)}")
            return False
    
    def select_dropdown_by_text(
        self, 
        locator_type: str, 
        locator_value: str, 
        text: str, 
        timeout: Optional[int] = None
    ) -> bool:
        """
        Seleciona um item em um dropdown por texto visível.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            text: Texto visível do item a ser selecionado
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se a seleção foi bem-sucedida, False caso contrário
        """
        element = self.element_helper.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível selecionar: elemento não encontrado {locator_type}={locator_value}")
            return False
        
        try:
            select = Select(element)
            select.select_by_visible_text(text)
            
            self.logger.debug(f"Item '{text}' selecionado com sucesso em {locator_type}={locator_value}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao selecionar item em dropdown {locator_type}={locator_value}: {str(e)}")
            return False
    
    def select_dropdown_by_value(
        self, 
        locator_type: str, 
        locator_value: str, 
        value: str, 
        timeout: Optional[int] = None
    ) -> bool:
        """
        Seleciona um item em um dropdown por valor.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            value: Valor do item a ser selecionado
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se a seleção foi bem-sucedida, False caso contrário
        """
        element = self.element_helper.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível selecionar: elemento não encontrado {locator_type}={locator_value}")
            return False
        
        try:
            select = Select(element)
            select.select_by_value(value)
            
            self.logger.debug(f"Item com valor '{value}' selecionado com sucesso em {locator_type}={locator_value}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao selecionar item em dropdown {locator_type}={locator_value}: {str(e)}")
            return False
    
    def select_dropdown_by_index(
        self, 
        locator_type: str, 
        locator_value: str, 
        index: int, 
        timeout: Optional[int] = None
    ) -> bool:
        """
        Seleciona um item em um dropdown por índice.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            index: Índice do item a ser selecionado (começa em 0)
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se a seleção foi bem-sucedida, False caso contrário
        """
        element = self.element_helper.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível selecionar: elemento não encontrado {locator_type}={locator_value}")
            return False
        
        try:
            select = Select(element)
            select.select_by_index(index)
            
            self.logger.debug(f"Item no índice {index} selecionado com sucesso em {locator_type}={locator_value}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao selecionar item em dropdown {locator_type}={locator_value}: {str(e)}")
            return False
    
    def drag_and_drop(
        self, 
        source_locator_type: str, 
        source_locator_value: str, 
        target_locator_type: str, 
        target_locator_value: str, 
        timeout: Optional[int] = None
    ) -> bool:
        """
        Arrasta e solta um elemento em outro.
        
        Args:
            source_locator_type: Tipo do localizador de origem
            source_locator_value: Valor do localizador de origem
            target_locator_type: Tipo do localizador de destino
            target_locator_value: Valor do localizador de destino
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        source = self.element_helper.find_element(source_locator_type, source_locator_value, timeout)
        target = self.element_helper.find_element(target_locator_type, target_locator_value, timeout)
        
        if not source or not target:
            self.logger.warning("Não foi possível realizar drag and drop: elemento de origem ou destino não encontrado")
            return False
        
        try:
            action = ActionChains(self.driver)
            action.drag_and_drop(source, target).perform()
            
            self.logger.debug(f"Drag and drop bem-sucedido de {source_locator_type}={source_locator_value} para {target_locator_type}={target_locator_value}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao realizar drag and drop: {str(e)}")
            
            # Tenta método alternativo
            try:
                self.logger.debug("Tentando método alternativo para drag and drop")
                
                action = ActionChains(self.driver)
                action.click_and_hold(source) \
                      .move_to_element(target) \
                      .release() \
                      .perform()
                      
                return True
            except Exception as alt_e:
                self.logger.error(f"Método alternativo também falhou: {str(alt_e)}")
                return False