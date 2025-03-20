"""
Módulo para localização e verificação de elementos na página.
"""

import logging
from time import sleep
from typing import Union, List, Optional, Tuple, Callable, Any, Dict

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    ElementNotInteractableException
)


class ElementHelper:
    """
    Classe auxiliar para encontrar e verificar elementos na página.
    """
    
    LOCATOR_MAP = {
        "id": By.ID,
        "name": By.NAME,
        "xpath": By.XPATH,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT,
        "tag": By.TAG_NAME,
        "class": By.CLASS_NAME,
        "css": By.CSS_SELECTOR
    }
    
    def __init__(
        self,
        driver: WebDriver,
        logger: logging.Logger,
        default_timeout: int = 10,
        max_retries: int = 3,
        retry_delay: int = 2
    ):
        """
        Inicializa o helper de elementos.
        
        Args:
            driver: Instância do WebDriver
            logger: Logger para registrar eventos
            default_timeout: Tempo padrão de espera (em segundos)
            max_retries: Número máximo de tentativas para operações
            retry_delay: Tempo de espera entre tentativas (em segundos)
        """
        self.driver = driver
        self.logger = logger
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def _resolve_locator(self, locator_type: str, locator_value: str) -> Tuple[str, str]:
        """
        Resolve o tipo de localizador para o formato do Selenium.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            
        Returns:
            Tupla com o tipo e valor do localizador pronto para uso pelo Selenium
        """
        locator_type = locator_type.lower()
        
        # Se o locator_type já for um valor By válido, retorna como está
        if locator_type in [By.ID, By.NAME, By.XPATH, By.CLASS_NAME, By.CSS_SELECTOR, 
                           By.LINK_TEXT, By.PARTIAL_LINK_TEXT, By.TAG_NAME]:
            return locator_type, locator_value
        
        # Converter para o formato do Selenium
        if locator_type in self.LOCATOR_MAP:
            return self.LOCATOR_MAP[locator_type], locator_value
        
        # Tentar inferir o tipo de localizador
        if locator_value.startswith("//"):
            return By.XPATH, locator_value
        elif locator_value.startswith(".") or locator_value.startswith("#") or " " in locator_value:
            return By.CSS_SELECTOR, locator_value
        else:
            # Default para ID se não for possível inferir
            return By.ID, locator_value
    
    def retry_on_exception(
        self, 
        func: Callable, 
        *args, 
        max_retries: Optional[int] = None, 
        retry_delay: Optional[int] = None, 
        expected_exceptions: Tuple = (
            StaleElementReferenceException, 
            ElementClickInterceptedException,
            ElementNotInteractableException
        ), 
        **kwargs
    ) -> Any:
        """
        Executa uma função com múltiplas tentativas em caso de exceção.
        
        Args:
            func: Função a ser executada
            max_retries: Número máximo de tentativas (usa self.max_retries se None)
            retry_delay: Tempo de espera entre tentativas (usa self.retry_delay se None)
            expected_exceptions: Tupla de exceções que devem ser capturadas
            *args, **kwargs: Argumentos para a função
            
        Returns:
            Resultado da função
            
        Raises:
            A última exceção ocorrida após todas as tentativas
        """
        max_retries = self.max_retries if max_retries is None else max_retries
        retry_delay = self.retry_delay if retry_delay is None else retry_delay
        
        last_exception = None
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except expected_exceptions as e:
                last_exception = e
                self.logger.debug(f"Tentativa {attempt+1}/{max_retries} falhou: {str(e)}")
                if attempt < max_retries - 1:
                    sleep(retry_delay)
                else:
                    self.logger.error(f"Todas as tentativas falharam: {str(e)}")
        
        if last_exception:
            raise last_exception
        
        # Caso improvável, mas para garantir que retornamos algo
        return None
    
    def find_element(
        self, 
        locator_type: str, 
        locator_value: str, 
        timeout: Optional[int] = None,
        parent_element: Optional[WebElement] = None,
        wait_condition: str = "clickable"
    ) -> Optional[WebElement]:
        """
        Encontra um elemento na página.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            parent_element: Elemento pai para busca contextual
            wait_condition: Condição de espera ('present', 'visible', 'clickable')
            
        Returns:
            WebElement se encontrado, None caso contrário
        """
        timeout = self.default_timeout if timeout is None else timeout
        by_type, by_value = self._resolve_locator(locator_type, locator_value)
        
        try:
            if parent_element:
                # Busca a partir do elemento pai
                element = parent_element.find_element(by_type, by_value)
            else:
                # Busca em toda a página com espera
                wait = WebDriverWait(self.driver, timeout)
                
                if wait_condition == "clickable":
                    element = wait.until(EC.element_to_be_clickable((by_type, by_value)))
                elif wait_condition == "visible":
                    element = wait.until(EC.visibility_of_element_located((by_type, by_value)))
                elif wait_condition == "present":
                    element = wait.until(EC.presence_of_element_located((by_type, by_value)))
                else:
                    raise ValueError(f"Condição de espera inválida: {wait_condition}")
            
            self.logger.debug(f"Elemento encontrado: {locator_type}={locator_value}")
            return element
            
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.debug(f"Elemento não encontrado: {locator_type}={locator_value}")
            return None
    
    def find_elements(
        self, 
        locator_type: str, 
        locator_value: str, 
        timeout: Optional[int] = None,
        parent_element: Optional[WebElement] = None
    ) -> List[WebElement]:
        """
        Encontra múltiplos elementos na página.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            parent_element: Elemento pai para busca contextual
            
        Returns:
            Lista de WebElements
        """
        timeout = self.default_timeout if timeout is None else timeout
        by_type, by_value = self._resolve_locator(locator_type, locator_value)
        
        try:
            if parent_element:
                # Busca a partir do elemento pai
                elements = parent_element.find_elements(by_type, by_value)
            else:
                # Busca em toda a página com espera
                wait = WebDriverWait(self.driver, timeout)
                elements = wait.until(EC.presence_of_all_elements_located((by_type, by_value)))
            
            self.logger.debug(f"Encontrados {len(elements)} elementos: {locator_type}={locator_value}")
            return elements
            
        except TimeoutException:
            self.logger.debug(f"Nenhum elemento encontrado: {locator_type}={locator_value}")
            return []
    
    def is_element_present(
        self, 
        locator_type: str, 
        locator_value: str, 
        timeout: Optional[int] = None
    ) -> bool:
        """
        Verifica se um elemento está presente na página.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se o elemento estiver presente, False caso contrário
        """
        timeout = self.default_timeout if timeout is None else timeout
        by_type, by_value = self._resolve_locator(locator_type, locator_value)
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((by_type, by_value)))
            return True
        except TimeoutException:
            return False
    
    def is_element_visible(
        self, 
        locator_type: str, 
        locator_value: str, 
        timeout: Optional[int] = None
    ) -> bool:
        """
        Verifica se um elemento está visível na página.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se o elemento estiver visível, False caso contrário
        """
        timeout = self.default_timeout if timeout is None else timeout
        by_type, by_value = self._resolve_locator(locator_type, locator_value)
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located((by_type, by_value)))
            return True
        except TimeoutException:
            return False
    
    def is_element_clickable(
        self, 
        locator_type: str, 
        locator_value: str, 
        timeout: Optional[int] = None
    ) -> bool:
        """
        Verifica se um elemento está clicável na página.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se o elemento estiver clicável, False caso contrário
        """
        timeout = self.default_timeout if timeout is None else timeout
        by_type, by_value = self._resolve_locator(locator_type, locator_value)
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.element_to_be_clickable((by_type, by_value)))
            return True
        except TimeoutException:
            return False
    
    def wait_for_element_to_disappear(
        self, 
        locator_type: str, 
        locator_value: str, 
        timeout: Optional[int] = None
    ) -> bool:
        """
        Espera até que um elemento desapareça da página.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se o elemento desapareceu, False caso contrário
        """
        timeout = self.default_timeout if timeout is None else timeout
        by_type, by_value = self._resolve_locator(locator_type, locator_value)
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.invisibility_of_element_located((by_type, by_value)))
            return True
        except TimeoutException:
            return False
    
    def wait_for_page_load(self, timeout: Optional[int] = None) -> bool:
        """
        Espera até que a página seja completamente carregada.
        
        Args:
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se a página foi carregada, False caso contrário
        """
        timeout = self.default_timeout if timeout is None else timeout
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            return True
        except TimeoutException:
            self.logger.warning("Tempo esgotado esperando a página carregar.")
            return False
    
    def wait_for_ajax(self, timeout: Optional[int] = None) -> bool:
        """
        Espera até que todas as requisições AJAX sejam concluídas.
        
        Args:
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se AJAX foi concluído, False caso contrário
        """
        timeout = self.default_timeout if timeout is None else timeout
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(lambda d: d.execute_script("return jQuery.active == 0"))
            return True
        except Exception:
            self.logger.warning("Tempo esgotado esperando AJAX ou jQuery não disponível.")
            return False
            
    def get_text(
        self, 
        locator_type: str, 
        locator_value: str, 
        timeout: Optional[int] = None
    ) -> Optional[str]:
        """
        Obtém o texto de um elemento.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            Texto do elemento ou None se não encontrado
        """
        element = self.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível obter texto: elemento não encontrado {locator_type}={locator_value}")
            return None
        
        try:
            text = element.text
            
            # Se text estiver vazio, tenta obter o valor (para inputs)
            if not text:
                text = element.get_attribute("value") or ""
                
            return text
        except Exception as e:
            self.logger.error(f"Erro ao obter texto de {locator_type}={locator_value}: {str(e)}")
            return None
    
    def get_attribute(
        self, 
        locator_type: str, 
        locator_value: str, 
        attribute: str, 
        timeout: Optional[int] = None
    ) -> Optional[str]:
        """
        Obtém o valor de um atributo de um elemento.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            attribute: Nome do atributo a ser obtido
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            Valor do atributo ou None se não encontrado
        """
        element = self.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível obter atributo: elemento não encontrado {locator_type}={locator_value}")
            return None
        
        try:
            value = element.get_attribute(attribute)
            return value
        except Exception as e:
            self.logger.error(f"Erro ao obter atributo {attribute} de {locator_type}={locator_value}: {str(e)}")
            return None
    
    def get_css_property(
        self, 
        locator_type: str, 
        locator_value: str, 
        property_name: str, 
        timeout: Optional[int] = None
    ) -> Optional[str]:
        """
        Obtém o valor de uma propriedade CSS de um elemento.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            property_name: Nome da propriedade CSS a ser obtida
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            Valor da propriedade CSS ou None se não encontrado
        """
        element = self.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível obter propriedade CSS: elemento não encontrado {locator_type}={locator_value}")
            return None
        
        try:
            value = element.value_of_css_property(property_name)
            return value
        except Exception as e:
            self.logger.error(f"Erro ao obter propriedade CSS {property_name} de {locator_type}={locator_value}: {str(e)}")
            return None
    
    def get_element_rect(
        self,
        locator_type: str,
        locator_value: str,
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, int]]:
        """
        Obtém as dimensões e posição de um elemento.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            Dicionário com x, y, height, width ou None se não encontrado
        """
        element = self.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível obter retângulo: elemento não encontrado {locator_type}={locator_value}")
            return None
        
        try:
            rect = element.rect
            return rect
        except Exception as e:
            self.logger.error(f"Erro ao obter retângulo de {locator_type}={locator_value}: {str(e)}")
            return None
    
    def get_element_size(
        self,
        locator_type: str,
        locator_value: str,
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, int]]:
        """
        Obtém o tamanho de um elemento.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            Dicionário com width e height ou None se não encontrado
        """
        element = self.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível obter tamanho: elemento não encontrado {locator_type}={locator_value}")
            return None
        
        try:
            size = element.size
            return size
        except Exception as e:
            self.logger.error(f"Erro ao obter tamanho de {locator_type}={locator_value}: {str(e)}")
            return None
    
    def get_element_location(
        self,
        locator_type: str,
        locator_value: str,
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, int]]:
        """
        Obtém a posição de um elemento.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            Dicionário com x e y ou None se não encontrado
        """
        element = self.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível obter localização: elemento não encontrado {locator_type}={locator_value}")
            return None
        
        try:
            location = element.location
            return location
        except Exception as e:
            self.logger.error(f"Erro ao obter localização de {locator_type}={locator_value}: {str(e)}")
            return None
    
    def is_element_selected(
        self,
        locator_type: str,
        locator_value: str,
        timeout: Optional[int] = None
    ) -> Optional[bool]:
        """
        Verifica se um elemento está selecionado (checkbox, radio, etc.).
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se o elemento estiver selecionado, False se não estiver, None se não encontrado
        """
        element = self.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível verificar seleção: elemento não encontrado {locator_type}={locator_value}")
            return None
        
        try:
            is_selected = element.is_selected()
            return is_selected
        except Exception as e:
            self.logger.error(f"Erro ao verificar seleção de {locator_type}={locator_value}: {str(e)}")
            return None
    
    def is_element_enabled(
        self,
        locator_type: str,
        locator_value: str,
        timeout: Optional[int] = None
    ) -> Optional[bool]:
        """
        Verifica se um elemento está habilitado.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se o elemento estiver habilitado, False se não estiver, None se não encontrado
        """
        element = self.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível verificar habilitação: elemento não encontrado {locator_type}={locator_value}")
            return None
        
        try:
            is_enabled = element.is_enabled()
            return is_enabled
        except Exception as e:
            self.logger.error(f"Erro ao verificar habilitação de {locator_type}={locator_value}: {str(e)}")
            return None
    
    def get_tag_name(
        self,
        locator_type: str,
        locator_value: str,
        timeout: Optional[int] = None
    ) -> Optional[str]:
        """
        Obtém o nome da tag de um elemento.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            Nome da tag ou None se não encontrado
        """
        element = self.find_element(locator_type, locator_value, timeout)
        
        if not element:
            self.logger.warning(f"Não foi possível obter nome da tag: elemento não encontrado {locator_type}={locator_value}")
            return None
        
        try:
            tag_name = element.tag_name
            return tag_name
        except Exception as e:
            self.logger.error(f"Erro ao obter nome da tag de {locator_type}={locator_value}: {str(e)}")
            return None
    
    def count_elements(
        self,
        locator_type: str,
        locator_value: str,
        timeout: Optional[int] = None
    ) -> int:
        """
        Conta o número de elementos que correspondem ao localizador.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            Número de elementos encontrados
        """
        elements = self.find_elements(locator_type, locator_value, timeout)
        return len(elements)
    
    def get_element_by_index(
        self,
        locator_type: str,
        locator_value: str,
        index: int = 0,
        timeout: Optional[int] = None
    ) -> Optional[WebElement]:
        """
        Obtém um elemento específico de uma lista pelo índice.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            index: Índice do elemento desejado (começa em 0)
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            WebElement no índice especificado ou None se não encontrado
        """
        elements = self.find_elements(locator_type, locator_value, timeout)
        
        if not elements:
            self.logger.warning(f"Não foi possível obter elemento por índice: nenhum elemento encontrado {locator_type}={locator_value}")
            return None
        
        try:
            if 0 <= index < len(elements):
                return elements[index]
            else:
                self.logger.warning(f"Índice {index} fora do intervalo, encontrados {len(elements)} elementos")
                return None
        except Exception as e:
            self.logger.error(f"Erro ao obter elemento por índice de {locator_type}={locator_value}: {str(e)}")
            return None
    
    def wait_for_text_to_be_present(
        self,
        locator_type: str,
        locator_value: str,
        text: str,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Espera até que um texto específico esteja presente em um elemento.
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            text: Texto a ser esperado
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se o texto apareceu, False caso contrário
        """
        timeout = self.default_timeout if timeout is None else timeout
        by_type, by_value = self._resolve_locator(locator_type, locator_value)
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.text_to_be_present_in_element((by_type, by_value), text))
            return True
        except TimeoutException:
            self.logger.warning(f"Tempo esgotado esperando texto '{text}' aparecer em {locator_type}={locator_value}")
            return False
    
    def wait_for_value_to_be_present(
        self,
        locator_type: str,
        locator_value: str,
        value: str,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Espera até que um valor específico esteja presente em um elemento (geralmente inputs).
        
        Args:
            locator_type: Tipo do localizador ('id', 'xpath', 'css', etc.)
            locator_value: Valor do localizador
            value: Valor a ser esperado
            timeout: Tempo máximo de espera (usa self.default_timeout se None)
            
        Returns:
            True se o valor apareceu, False caso contrário
        """
        timeout = self.default_timeout if timeout is None else timeout
        by_type, by_value = self._resolve_locator(locator_type, locator_value)
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.text_to_be_present_in_element_value((by_type, by_value), value))
            return True
        except TimeoutException:
            self.logger.warning(f"Tempo esgotado esperando valor '{value}' aparecer em {locator_type}={locator_value}")
            return False