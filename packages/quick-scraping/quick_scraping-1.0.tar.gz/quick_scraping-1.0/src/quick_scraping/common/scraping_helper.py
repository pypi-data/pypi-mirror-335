"""
Funções e classes comuns compartilhadas entre os módulos Selenium e BeautifulSoup.
Facilitam a integração entre as duas bibliotecas para web scraping mais avançado.
"""

import logging
import time
from typing import Optional, Union, Dict, List, Any, Tuple
from pathlib import Path
import re
import json

from bs4 import BeautifulSoup


class ScrapingHelper:
    """
    Classe auxiliar que combina funcionalidades do Selenium e BeautifulSoup.
    """
    
    def __init__(
        self,
        selenium_helper=None,
        bs_parser=None,
        bs_extractor=None,
        bs_utils=None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Inicializa o helper de scraping.
        
        Args:
            selenium_helper: Instância do SeleniumHelper (opcional)
            bs_parser: Instância do HTMLParser (opcional)
            bs_extractor: Instância do DataExtractor (opcional)
            bs_utils: Instância do HTMLUtils (opcional)
            logger: Logger para registrar eventos
        """
        # Configura logger
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger("ScrapingHelper")
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                self.logger.setLevel(logging.INFO)
        
        # Armazena as instâncias
        self.selenium = selenium_helper
        self.parser = bs_parser
        self.extractor = bs_extractor
        self.utils = bs_utils
        
        # Importa e inicializa componentes se necessário
        if not self.selenium and self._check_selenium_available():
            try:
                from ..selenium_functions import SeleniumHelper
                self.selenium = SeleniumHelper(logger=self.logger)
                self.logger.debug("SeleniumHelper inicializado automaticamente")
            except ImportError:
                self.logger.warning("SeleniumHelper não disponível")
        
        if not self.parser:
            try:
                from beautifulsoup_functions.parser import HTMLParser
                self.parser = HTMLParser(logger=self.logger)
                self.logger.debug("HTMLParser inicializado automaticamente")
            except ImportError:
                self.logger.warning("HTMLParser não disponível")
        
        if not self.extractor and self.parser:
            try:
                from beautifulsoup_functions.extractors import DataExtractor
                self.extractor = DataExtractor(logger=self.logger)
                self.logger.debug("DataExtractor inicializado automaticamente")
            except ImportError:
                self.logger.warning("DataExtractor não disponível")
        
        if not self.utils:
            try:
                from beautifulsoup_functions.utils import HTMLUtils
                self.utils = HTMLUtils(logger=self.logger)
                self.logger.debug("HTMLUtils inicializado automaticamente")
            except ImportError:
                self.logger.warning("HTMLUtils não disponível")
    
    def _check_selenium_available(self) -> bool:
        """Verifica se Selenium está disponível."""
        try:
            import selenium
            return True
        except ImportError:
            return False
    
    def extract_from_current_page(self) -> Optional[BeautifulSoup]:
        """
        Extrai o conteúdo HTML da página atual do Selenium.
        
        Returns:
            Objeto BeautifulSoup da página atual ou None se não disponível
        """
        if not self.selenium or not self.parser:
            self.logger.error("Selenium ou BeautifulSoup não inicializados")
            return None
        
        try:
            # Obtém o HTML da página atual
            html = self.selenium.driver.page_source
            
            # Analisa o HTML com BeautifulSoup
            soup = self.parser.parse_html(html)
            
            self.logger.debug("Página extraída com sucesso")
            return soup
        except Exception as e:
            self.logger.error(f"Erro ao extrair página: {str(e)}")
            return None
    
    def navigate_and_extract(
        self, 
        url: str, 
        wait_for_selector: Optional[str] = None,
        wait_time: int = 3
    ) -> Optional[BeautifulSoup]:
        """
        Navega para uma URL com Selenium e extrai o conteúdo HTML.
        
        Args:
            url: URL para navegar
            wait_for_selector: Seletor CSS para aguardar (opcional)
            wait_time: Tempo de espera em segundos
            
        Returns:
            Objeto BeautifulSoup da página carregada ou None se falhar
        """
        if not self.selenium or not self.parser:
            self.logger.error("Selenium ou BeautifulSoup não inicializados")
            return None
        
        try:
            # Navega para a URL
            self.selenium.navigate.to(url)
            
            # Aguarda o carregamento completo da página
            self.selenium.element.wait_for_page_load()
            
            # Se um seletor foi especificado, aguarda até que ele esteja presente
            if wait_for_selector:
                selector_type, selector_value = self._convert_css_to_selenium(wait_for_selector)
                self.selenium.element.is_element_present(selector_type, selector_value)
            
            # Aguarda um tempo adicional se necessário
            if wait_time > 0:
                time.sleep(wait_time)
            
            # Extrai o HTML
            return self.extract_from_current_page()
        except Exception as e:
            self.logger.error(f"Erro ao navegar e extrair página: {str(e)}")
            return None
    
    def _convert_css_to_selenium(self, css_selector: str) -> Tuple[str, str]:
        """
        Converte seletor CSS para o formato do Selenium.
        
        Args:
            css_selector: Seletor CSS
            
        Returns:
            Tupla com (tipo_localizador, valor_localizador)
        """
        # Seletores simples que podem ser convertidos diretamente
        if css_selector.startswith('#'):
            # Seletor por ID
            return 'id', css_selector[1:]
        elif css_selector.startswith('.'):
            # Seletor por classe
            return 'class', css_selector[1:]
        elif css_selector.lower() in ['body', 'a', 'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                                     'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'form', 'input', 'button']:
            # Seletor por tag name
            return 'tag', css_selector
        else:
            # Usa CSS seletor completo
            return 'css', css_selector
    
    def extract_data_with_selenium(
        self, 
        url: str, 
        extraction_config: Dict[str, Any],
        wait_time: int = 3
    ) -> Dict[str, Any]:
        """
        Navega para uma URL e extrai dados com base em uma configuração.
        
        Args:
            url: URL para navegar
            extraction_config: Configuração de extração (dict)
            wait_time: Tempo de espera em segundos
            
        Returns:
            Dicionário com os dados extraídos
        """
        results = {}
        
        if not self.selenium or not self.parser or not self.extractor:
            self.logger.error("Componentes necessários não inicializados")
            return results
        
        try:
            # Navega para a URL
            soup = self.navigate_and_extract(
                url, 
                wait_for_selector=extraction_config.get('wait_for_selector'),
                wait_time=wait_time
            )
            
            if not soup:
                self.logger.error("Falha ao extrair página")
                return results
            
            # Processa cada tipo de extração especificado
            for key, config in extraction_config.items():
                if key == 'wait_for_selector':
                    continue  # Pula, é apenas para navegação
                
                extraction_type = config.get('type', '').lower()
                selector = config.get('selector', '')
                
                if not extraction_type or not selector:
                    continue
                
                # Extrai baseado no tipo
                if extraction_type == 'text':
                    # Extrai texto de um elemento
                    element = soup.select_one(selector)
                    if element:
                        results[key] = element.get_text().strip()
                
                elif extraction_type == 'attribute':
                    # Extrai valor de um atributo
                    element = soup.select_one(selector)
                    attribute = config.get('attribute', '')
                    if element and attribute:
                        results[key] = element.get(attribute, '')
                
                elif extraction_type == 'table':
                    # Extrai tabela
                    headers, rows = self.extractor.extract_table(
                        soup, 
                        table_selector=selector,
                        has_header=config.get('has_header', True)
                    )
                    results[key] = {
                        'headers': headers,
                        'rows': rows
                    }
                
                elif extraction_type == 'links':
                    # Extrai links
                    links = self.extractor.extract_links(
                        soup, 
                        selector=selector,
                        base_url=url,
                        make_absolute=config.get('make_absolute', True)
                    )
                    results[key] = links
                
                elif extraction_type == 'list':
                    # Extrai itens de lista
                    lists = self.extractor.extract_list_items(
                        soup,
                        list_selector=selector,
                        nested=config.get('nested', True)
                    )
                    results[key] = lists
                
                elif extraction_type == 'article':
                    # Extrai conteúdo de artigo
                    article = self.extractor.extract_article_content(
                        soup,
                        article_selector=selector
                    )
                    results[key] = article
                
                elif extraction_type == 'metadata':
                    # Extrai metadados
                    metadata = self.extractor.extract_metadata(soup)
                    results[key] = metadata
            
            return results
        except Exception as e:
            self.logger.error(f"Erro na extração de dados: {str(e)}")
            return results
    
    def paginated_scrape(
        self, 
        base_url: str, 
        extraction_config: Dict[str, Any],
        next_button_selector: str,
        max_pages: int = 5,
        wait_time: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Executa scraping em várias páginas usando paginação.
        
        Args:
            base_url: URL inicial
            extraction_config: Configuração de extração por página
            next_button_selector: Seletor CSS para o botão de próxima página
            max_pages: Número máximo de páginas a processar
            wait_time: Tempo de espera entre páginas
            
        Returns:
            Lista de resultados de cada página
        """
        all_results = []
        
        if not self.selenium:
            self.logger.error("Selenium não inicializado")
            return all_results
        
        try:
            # Navega para a URL inicial
            self.selenium.navigate.to(base_url)
            self.selenium.element.wait_for_page_load()
            
            page_num = 1
            
            while page_num <= max_pages:
                self.logger.info(f"Processando página {page_num}")
                
                # Extrai conteúdo da página atual
                soup = self.extract_from_current_page()
                if not soup:
                    break
                
                # Extrai dados da página atual
                page_data = {}
                
                # Processa cada tipo de extração especificado
                for key, config in extraction_config.items():
                    extraction_type = config.get('type', '').lower()
                    selector = config.get('selector', '')
                    
                    if not extraction_type or not selector:
                        continue
                    
                    # Realiza extração baseada no tipo
                    # (implementação similar ao método extract_data_with_selenium)
                    # ...
                
                # Adiciona resultados
                all_results.append(page_data)
                
                # Verifica se existe botão de próxima página
                selector_type, selector_value = self._convert_css_to_selenium(next_button_selector)
                if not self.selenium.element.is_element_present(selector_type, selector_value):
                    self.logger.info("Botão de próxima página não encontrado")
                    break
                
                # Clica no botão de próxima página
                self.selenium.interact.click(selector_type, selector_value)
                
                # Aguarda o carregamento da próxima página
                self.selenium.element.wait_for_page_load()
                time.sleep(wait_time)
                
                page_num += 1
            
            self.logger.info(f"Processadas {len(all_results)} páginas")
            return all_results
        except Exception as e:
            self.logger.error(f"Erro no scraping paginado: {str(e)}")
            return all_results
    
    def save_results(
        self, 
        data: Any, 
        output_file: Union[str, Path],
        format: str = 'json'
    ) -> bool:
        """
        Salva resultados em arquivo.
        
        Args:
            data: Dados a serem salvos
            output_file: Caminho do arquivo de saída
            format: Formato dos dados ('json', 'csv', 'txt')
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        if not self.utils:
            self.logger.error("HTMLUtils não inicializado")
            return False
        
        try:
            # Verifica a extensão do arquivo
            output_path = Path(output_file)
            file_ext = output_path.suffix.lower()
            
            # Determina formato com base na extensão se não especificado
            if format == 'auto':
                if file_ext == '.json':
                    format = 'json'
                elif file_ext == '.csv':
                    format = 'csv'
                else:
                    format = 'txt'
            
            # Cria diretório se não existir
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Salva no formato apropriado
            if format == 'json':
                # Salva como JSON
                self.utils.data_to_json(data, output_path)
            elif format == 'csv' and isinstance(data, list):
                # Salva como CSV (se for lista de dicionários)
                self.utils.data_to_csv(data, output_path)
            else:
                # Salva como texto
                with open(output_path, 'w', encoding='utf-8') as f:
                    if isinstance(data, (dict, list)):
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    else:
                        f.write(str(data))
            
            self.logger.info(f"Dados salvos em: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar resultados: {str(e)}")
            return False
    
    def close(self):
        """Fecha todos os recursos."""
        if self.selenium:
            try:
                self.selenium.close()
                self.logger.debug("Selenium fechado")
            except Exception as e:
                self.logger.error(f"Erro ao fechar Selenium: {str(e)}")