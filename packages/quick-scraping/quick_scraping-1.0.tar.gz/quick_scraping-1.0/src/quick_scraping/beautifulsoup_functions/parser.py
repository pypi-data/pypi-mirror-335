"""
Módulo para análise e parsing HTML com BeautifulSoup.
Fornece funcionalidades para carregar e analisar documentos HTML.
"""

import logging
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
import re
import requests
from bs4 import BeautifulSoup, Tag, ResultSet


class HTMLParser:
    """
    Classe para parsing e manipulação de HTML com BeautifulSoup.
    """
    
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        parser: str = "html.parser",
        default_encoding: str = "utf-8"
    ):
        """
        Inicializa o parser HTML.
        
        Args:
            logger: Logger para registrar eventos
            parser: Parser a ser usado pelo BeautifulSoup ("html.parser", "lxml", "html5lib")
            default_encoding: Codificação padrão para arquivos HTML
        """
        self.parser = parser
        self.default_encoding = default_encoding
        
        # Configura logger
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger("BeautifulSoupHelper")
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                self.logger.setLevel(logging.INFO)
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """
        Analisa conteúdo HTML.
        
        Args:
            html_content: String contendo HTML
            
        Returns:
            Objeto BeautifulSoup
        """
        try:
            soup = BeautifulSoup(html_content, self.parser)
            self.logger.debug("HTML analisado com sucesso")
            return soup
        except Exception as e:
            self.logger.error(f"Erro ao analisar HTML: {str(e)}")
            raise
    
    def load_html_file(self, file_path: Union[str, Path], encoding: Optional[str] = None) -> BeautifulSoup:
        """
        Carrega HTML de um arquivo.
        
        Args:
            file_path: Caminho para o arquivo HTML
            encoding: Codificação do arquivo (usa default_encoding se None)
            
        Returns:
            Objeto BeautifulSoup
        """
        encoding = encoding or self.default_encoding
        file_path = Path(file_path) if isinstance(file_path, str) else file_path
        
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                html_content = file.read()
            
            soup = self.parse_html(html_content)
            self.logger.debug(f"Arquivo HTML carregado: {file_path}")
            return soup
        except Exception as e:
            self.logger.error(f"Erro ao carregar arquivo HTML {file_path}: {str(e)}")
            raise
    
    def load_from_url(
        self, 
        url: str, 
        headers: Optional[Dict[str, str]] = None, 
        timeout: int = 30,
        verify_ssl: bool = True,
        encoding: Optional[str] = None
    ) -> BeautifulSoup:
        """
        Carrega HTML de uma URL.
        
        Args:
            url: URL da página
            headers: Cabeçalhos HTTP
            timeout: Tempo máximo de espera para a requisição (em segundos)
            verify_ssl: Se True, verifica certificados SSL
            encoding: Codificação da página (detecta automaticamente se None)
            
        Returns:
            Objeto BeautifulSoup
        """
        try:
            if headers is None:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            
            response = requests.get(url, headers=headers, timeout=timeout, verify=verify_ssl)
            response.raise_for_status()
            
            # Define a codificação
            if encoding:
                response.encoding = encoding
            
            soup = self.parse_html(response.text)
            self.logger.debug(f"HTML carregado da URL: {url}")
            return soup
        except Exception as e:
            self.logger.error(f"Erro ao carregar HTML da URL {url}: {str(e)}")
            raise
    
    def save_to_file(
        self, 
        soup: BeautifulSoup, 
        file_path: Union[str, Path],
        encoding: Optional[str] = None,
        formatter: str = "minimal",
        pretty_print: bool = True
    ) -> bool:
        """
        Salva o HTML em um arquivo.
        
        Args:
            soup: Objeto BeautifulSoup
            file_path: Caminho para o arquivo de destino
            encoding: Codificação do arquivo (usa default_encoding se None)
            formatter: Formatador HTML ('minimal', 'html', 'html5')
            pretty_print: Se True, formata o HTML com indentação
            
        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        encoding = encoding or self.default_encoding
        file_path = Path(file_path) if isinstance(file_path, str) else file_path
        
        try:
            # Cria diretórios se não existirem
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Formata o HTML
            if pretty_print:
                html_content = soup.prettify(formatter=formatter, encoding=encoding)
                if isinstance(html_content, bytes):
                    html_content = html_content.decode(encoding)
            else:
                html_content = str(soup)
            
            # Salva no arquivo
            with open(file_path, 'w', encoding=encoding) as file:
                file.write(html_content)
            
            self.logger.debug(f"HTML salvo em: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar HTML em {file_path}: {str(e)}")
            return False
    
    def clean_html(
        self, 
        soup: BeautifulSoup, 
        remove_scripts: bool = True, 
        remove_styles: bool = True,
        remove_comments: bool = True,
        remove_attributes: Optional[List[str]] = None
    ) -> BeautifulSoup:
        """
        Limpa o HTML removendo elementos e atributos indesejados.
        
        Args:
            soup: Objeto BeautifulSoup
            remove_scripts: Se True, remove todas as tags <script>
            remove_styles: Se True, remove todas as tags <style>
            remove_comments: Se True, remove todos os comentários HTML
            remove_attributes: Lista de atributos para remover de todas as tags
            
        Returns:
            Objeto BeautifulSoup limpo
        """
        # Cria uma cópia para não modificar o original
        soup_copy = BeautifulSoup(str(soup), self.parser)
        
        try:
            # Remove tags <script>
            if remove_scripts:
                for script in soup_copy.find_all('script'):
                    script.decompose()
            
            # Remove tags <style>
            if remove_styles:
                for style in soup_copy.find_all('style'):
                    style.decompose()
            
            # Remove comentários HTML
            if remove_comments:
                for comment in soup_copy.find_all(text=lambda text: isinstance(text, str) and text.startswith('<!--')):
                    comment.extract()
            
            # Remove atributos específicos
            if remove_attributes:
                for tag in soup_copy.find_all(True):
                    for attr in list(tag.attrs):
                        if attr in remove_attributes:
                            del tag[attr]
            
            self.logger.debug("HTML limpo com sucesso")
            return soup_copy
        except Exception as e:
            self.logger.error(f"Erro ao limpar HTML: {str(e)}")
            return soup_copy
    
    def extract_text(
        self, 
        soup: Union[BeautifulSoup, Tag], 
        separator: str = " ", 
        strip: bool = True,
        line_breaks: bool = False
    ) -> str:
        """
        Extrai todo o texto de um elemento HTML.
        
        Args:
            soup: Objeto BeautifulSoup ou Tag
            separator: Separador entre textos
            strip: Se True, remove espaços em branco extras
            line_breaks: Se True, preserva quebras de linha
            
        Returns:
            Texto extraído
        """
        try:
            if line_breaks:
                # Preserva quebras de linha
                text = ""
                for element in soup.find_all(string=True):
                    if element.parent.name not in ['script', 'style', 'meta', 'head']:
                        text += element.strip() + "\n" if strip else element + "\n"
                return text.strip() if strip else text
            else:
                # Extrai texto com o separador
                text = separator.join([t.strip() if strip else t 
                                    for t in soup.find_all(string=True) 
                                    if t.parent.name not in ['script', 'style', 'meta', 'head']])
                return text.strip() if strip else text
        except Exception as e:
            self.logger.error(f"Erro ao extrair texto: {str(e)}")
            return ""
    
    def find_all(
        self, 
        soup: BeautifulSoup, 
        tag: Optional[str] = None,
        attrs: Optional[Dict[str, str]] = None,
        selector: Optional[str] = None,
        recursive: bool = True,
        limit: Optional[int] = None
    ) -> List[Tag]:
        """
        Encontra todos os elementos que correspondem aos critérios.
        
        Args:
            soup: Objeto BeautifulSoup
            tag: Nome da tag HTML (opcional)
            attrs: Dicionário de atributos (opcional)
            selector: Seletor CSS (opcional)
            recursive: Se True, busca em todos os níveis do documento
            limit: Limite máximo de resultados
            
        Returns:
            Lista de elementos encontrados
        """
        try:
            if selector:
                # Se um seletor CSS for fornecido, usa select()
                results = soup.select(selector, limit=limit)
            else:
                # Caso contrário, usa find_all()
                results = soup.find_all(tag, attrs=attrs, recursive=recursive, limit=limit)
            
            self.logger.debug(f"Encontrados {len(results)} elementos")
            return results
        except Exception as e:
            self.logger.error(f"Erro ao buscar elementos: {str(e)}")
            return []
    
    def find(
        self, 
        soup: BeautifulSoup, 
        tag: Optional[str] = None,
        attrs: Optional[Dict[str, str]] = None,
        selector: Optional[str] = None,
        recursive: bool = True
    ) -> Optional[Tag]:
        """
        Encontra o primeiro elemento que corresponde aos critérios.
        
        Args:
            soup: Objeto BeautifulSoup
            tag: Nome da tag HTML (opcional)
            attrs: Dicionário de atributos (opcional)
            selector: Seletor CSS (opcional)
            recursive: Se True, busca em todos os níveis do documento
            
        Returns:
            Primeiro elemento encontrado ou None
        """
        try:
            if selector:
                # Se um seletor CSS for fornecido, usa select_one()
                result = soup.select_one(selector)
            else:
                # Caso contrário, usa find()
                result = soup.find(tag, attrs=attrs, recursive=recursive)
            
            self.logger.debug(f"Elemento encontrado: {result is not None}")
            return result
        except Exception as e:
            self.logger.error(f"Erro ao buscar elemento: {str(e)}")
            return None