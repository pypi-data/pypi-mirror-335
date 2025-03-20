"""
Utilitários para processamento e transformação de dados HTML.
"""

import logging
import re
import unicodedata
import string
from typing import Dict, List, Union, Optional, Callable, Any, Tuple
import json
import csv
import io
from pathlib import Path

from bs4 import BeautifulSoup, Tag


class HTMLUtils:
    """
    Funções utilitárias para processamento de HTML.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Inicializa os utilitários HTML.
        
        Args:
            logger: Logger para registrar eventos
        """
        # Configura logger
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger("BeautifulSoupUtils")
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                self.logger.setLevel(logging.INFO)
    
    def normalize_text(
        self, 
        text: str, 
        remove_extra_whitespace: bool = True,
        remove_newlines: bool = True,
        normalize_unicode: bool = True
    ) -> str:
        """
        Normaliza texto extraído de HTML.
        
        Args:
            text: Texto a ser normalizado
            remove_extra_whitespace: Se True, remove espaços em branco extras
            remove_newlines: Se True, substitui quebras de linha por espaços
            normalize_unicode: Se True, normaliza caracteres Unicode
            
        Returns:
            Texto normalizado
        """
        try:
            # Normaliza caracteres Unicode
            if normalize_unicode:
                text = unicodedata.normalize('NFKC', text)
            
            # Substitui quebras de linha por espaços
            if remove_newlines:
                text = re.sub(r'[\r\n]+', ' ', text)
            
            # Remove espaços em branco extras
            if remove_extra_whitespace:
                text = re.sub(r'\s+', ' ', text).strip()
            
            return text
        except Exception as e:
            self.logger.error(f"Erro ao normalizar texto: {str(e)}")
            return text
    
    def remove_unwanted_elements(
        self, 
        soup: BeautifulSoup, 
        selectors: List[str] = [
            "script", "style", "iframe", "noscript", 
            ".ad", ".ads", ".advertisement", 
            ".cookie-notice", ".popup", ".modal"
        ]
    ) -> BeautifulSoup:
        """
        Remove elementos indesejados do HTML.
        
        Args:
            soup: Objeto BeautifulSoup
            selectors: Lista de seletores CSS para elementos a remover
            
        Returns:
            BeautifulSoup com elementos removidos
        """
        try:
            # Cria uma cópia do soup para não modificar o original
            soup_copy = BeautifulSoup(str(soup), soup.parser.name)
            
            # Remove elementos indesejados
            for selector in selectors:
                for element in soup_copy.select(selector):
                    element.decompose()
            
            self.logger.debug("Elementos indesejados removidos")
            return soup_copy
        except Exception as e:
            self.logger.error(f"Erro ao remover elementos indesejados: {str(e)}")
            return soup
    
    def extract_emails(self, text: str) -> List[str]:
        """
        Extrai endereços de e-mail de um texto.
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            Lista de endereços de e-mail encontrados
        """
        try:
            # Padrão regex para e-mails
            pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(pattern, text)
            
            self.logger.debug(f"Extraídos {len(emails)} endereços de e-mail")
            return emails
        except Exception as e:
            self.logger.error(f"Erro ao extrair e-mails: {str(e)}")
            return []
    
    def extract_phone_numbers(self, text: str, country_code: str = "") -> List[str]:
        """
        Extrai números de telefone de um texto.
        
        Args:
            text: Texto a ser analisado
            country_code: Código do país (usado para formatação)
            
        Returns:
            Lista de números de telefone encontrados
        """
        try:
            # Padrão regex básico para números de telefone
            # Este é um padrão simplificado e pode precisar ser ajustado para diferentes formatos
            pattern = r'(?:\+\d{1,3}[\s.-]?)?(?:\(\d{1,4}\)[\s.-]?)?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,9}'
            phones = re.findall(pattern, text)
            
            # Limpa e formata os resultados
            cleaned_phones = []
            for phone in phones:
                # Remove caracteres não numéricos
                digits = ''.join(c for c in phone if c.isdigit())
                
                # Verifica se o número tem um tamanho razoável (pelo menos 7 dígitos)
                if len(digits) >= 7:
                    # Formata o número se o código do país foi fornecido
                    if country_code and not phone.startswith('+'):
                        formatted = f"{country_code} {digits}"
                    else:
                        formatted = phone
                    
                    cleaned_phones.append(formatted)
            
            self.logger.debug(f"Extraídos {len(cleaned_phones)} números de telefone")
            return cleaned_phones
        except Exception as e:
            self.logger.error(f"Erro ao extrair números de telefone: {str(e)}")
            return []
    
    def clean_element_text(
        self, 
        element: Tag, 
        remove_extra_whitespace: bool = True,
        strip: bool = True,
        join_strings: bool = True,
        join_separator: str = " "
    ) -> str:
        """
        Limpa o texto de um elemento HTML.
        
        Args:
            element: Elemento HTML (Tag)
            remove_extra_whitespace: Se True, remove espaços em branco extras
            strip: Se True, remove espaços em branco no início e fim
            join_strings: Se True, junta todos os strings filhos
            join_separator: Separador usado para juntar strings
            
        Returns:
            Texto limpo
        """
        try:
            if not element:
                return ""
            
            if join_strings:
                # Obtém todos os nós de texto
                text_nodes = element.find_all(string=True)
                text = join_separator.join(str(node) for node in text_nodes)
            else:
                text = element.get_text()
            
            # Limpa o texto
            if remove_extra_whitespace:
                text = re.sub(r'\s+', ' ', text)
            
            if strip:
                text = text.strip()
            
            return text
        except Exception as e:
            self.logger.error(f"Erro ao limpar texto de elemento: {str(e)}")
            return ""
    
    def extract_keywords(
        self, 
        text: str, 
        min_length: int = 3, 
        max_length: int = 25,
        lowercase: bool = True,
        remove_punct: bool = True,
        stopwords: Optional[List[str]] = None
    ) -> List[str]:
        """
        Extrai palavras-chave de um texto.
        
        Args:
            text: Texto a ser analisado
            min_length: Comprimento mínimo das palavras
            max_length: Comprimento máximo das palavras
            lowercase: Se True, converte para minúsculas
            remove_punct: Se True, remove pontuação
            stopwords: Lista de palavras para ignorar
            
        Returns:
            Lista de palavras-chave únicas
        """
        try:
            # Normaliza o texto
            text = self.normalize_text(text)
            
            # Converte para minúsculas se necessário
            if lowercase:
                text = text.lower()
            
            # Remove pontuação se necessário
            if remove_punct:
                text = text.translate(str.maketrans('', '', string.punctuation))
            
            # Lista padrão de stopwords em português e inglês
            default_stopwords = {
                'a', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', 'aquilo', 'as', 'até',
                'com', 'como', 'da', 'das', 'de', 'dela', 'delas', 'dele', 'deles', 'depois',
                'do', 'dos', 'e', 'ela', 'elas', 'ele', 'eles', 'em', 'entre', 'era', 'eram',
                'éramos', 'essa', 'essas', 'esse', 'esses', 'esta', 'estas', 'este', 'estes',
                'eu', 'foi', 'fomos', 'for', 'foram', 'fosse', 'fossem', 'fui', 'há', 'isso',
                'isto', 'já', 'lhe', 'lhes', 'mais', 'mas', 'me', 'mesmo', 'meu', 'meus', 'minha',
                'minhas', 'muito', 'na', 'não', 'nas', 'nem', 'no', 'nos', 'nós', 'nossa', 'nossas',
                'nosso', 'nossos', 'num', 'numa', 'o', 'os', 'ou', 'para', 'pela', 'pelas', 'pelo',
                'pelos', 'por', 'qual', 'quando', 'que', 'quem', 'são', 'se', 'seja', 'sejam',
                'sem', 'será', 'seu', 'seus', 'só', 'somos', 'sou', 'sua', 'suas', 'também', 'te',
                'tem', 'temos', 'tenho', 'ter', 'teu', 'teus', 'tu', 'tua', 'tuas', 'um', 'uma',
                'você', 'vocês', 'vos',
                
                'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'have',
                'he', 'i', 'in', 'is', 'it', 'its', 'of', 'on', 'or', 'that', 'the', 'this',
                'to', 'was', 'were', 'will', 'with'
            }
            
            # Usa a lista fornecida ou a padrão
            stop_words = set(stopwords) if stopwords else default_stopwords
            
            # Divide o texto em palavras
            words = text.split()
            
            # Filtra as palavras
            keywords = [
                word for word in words
                if (
                    min_length <= len(word) <= max_length and
                    word not in stop_words and
                    not word.isdigit()  # Ignora números
                )
            ]
            
            # Remove duplicatas preservando a ordem
            unique_keywords = []
            seen = set()
            for word in keywords:
                if word not in seen:
                    seen.add(word)
                    unique_keywords.append(word)
            
            self.logger.debug(f"Extraídas {len(unique_keywords)} palavras-chave únicas")
            return unique_keywords
        except Exception as e:
            self.logger.error(f"Erro ao extrair palavras-chave: {str(e)}")
            return []
    
    def html_to_plain_text(
        self, 
        soup: Union[BeautifulSoup, Tag, str],
        preserve_links: bool = False,
        preserve_images: bool = False,
        preserve_linebreaks: bool = True,
        indent_headings: bool = True,
        double_space_paragraphs: bool = True
    ) -> str:
        """
        Converte HTML em texto simples formatado.
        
        Args:
            soup: HTML a ser convertido (BeautifulSoup, Tag ou string)
            preserve_links: Se True, adiciona URLs após links
            preserve_images: Se True, adiciona descrições de imagens
            preserve_linebreaks: Se True, preserva quebras de linha
            indent_headings: Se True, adiciona caracteres de destaque aos cabeçalhos
            double_space_paragraphs: Se True, adiciona linha em branco entre parágrafos
            
        Returns:
            Texto formatado
        """
        try:
            # Converte para BeautifulSoup se for string
            if isinstance(soup, str):
                soup = BeautifulSoup(soup, 'html.parser')
            
            # Cria uma cópia para manipulação
            soup_copy = BeautifulSoup(str(soup), soup.parser.name)
            
            # Remove scripts e estilos
            for tag in soup_copy(['script', 'style', 'iframe', 'noscript']):
                tag.decompose()
            
            # Processa links
            if preserve_links:
                for a in soup_copy.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('http') and a.string:
                        a.string = f"{a.get_text()} [{href}]"
            
            # Processa imagens
            if preserve_images:
                for img in soup_copy.find_all('img', alt=True):
                    alt_text = img['alt'].strip()
                    if alt_text:
                        img.replace_with(f"[Image: {alt_text}]")
            
            # Processa cabeçalhos
            if indent_headings:
                for i in range(1, 7):
                    for heading in soup_copy.find_all(f'h{i}'):
                        heading_text = heading.get_text().strip()
                        prefix = '#' * i + ' '
                        heading.replace_with(f"\n\n{prefix}{heading_text}\n\n")
            
            # Processa parágrafos
            if double_space_paragraphs:
                for p in soup_copy.find_all('p'):
                    p_text = p.get_text().strip()
                    p.replace_with(f"\n\n{p_text}\n\n")
            
            # Processa quebras de linha
            if preserve_linebreaks:
                for br in soup_copy.find_all('br'):
                    br.replace_with('\n')
            
            # Converte para texto
            text = soup_copy.get_text()
            
            # Limpa o texto final
            text = re.sub(r'\n{3,}', '\n\n', text)  # Substitui 3+ quebras de linha por 2
            text = text.strip()
            
            self.logger.debug("HTML convertido para texto simples")
            return text
        except Exception as e:
            self.logger.error(f"Erro ao converter HTML para texto: {str(e)}")
            if isinstance(soup, (BeautifulSoup, Tag)):
                return soup.get_text()
            elif isinstance(soup, str):
                return soup
            else:
                return ""
    
    def data_to_json(
        self, 
        data: Any, 
        file_path: Optional[Union[str, Path]] = None,
        indent: int = 2,
        ensure_ascii: bool = False
    ) -> Optional[str]:
        """
        Converte dados para JSON e opcionalmente salva em arquivo.
        
        Args:
            data: Dados a serem convertidos
            file_path: Caminho para salvar o JSON (opcional)
            indent: Nível de indentação
            ensure_ascii: Se True, garante que saída use apenas ASCII
            
        Returns:
            String JSON ou None se apenas salvando em arquivo
        """
        try:
            # Converte para JSON
            json_str = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
            
            # Salva em arquivo se o caminho for fornecido
            if file_path:
                path = Path(file_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                
                self.logger.debug(f"Dados JSON salvos em: {file_path}")
                return None
            
            return json_str
        except Exception as e:
            self.logger.error(f"Erro ao converter dados para JSON: {str(e)}")
            return None
    
    def data_to_csv(
        self, 
        data: List[Dict[str, Any]], 
        file_path: Optional[Union[str, Path]] = None,
        headers: Optional[List[str]] = None,
        delimiter: str = ',',
        quotechar: str = '"'
    ) -> Optional[str]:
        """
        Converte dados para CSV e opcionalmente salva em arquivo.
        
        Args:
            data: Lista de dicionários a ser convertida
            file_path: Caminho para salvar o CSV (opcional)
            headers: Lista de cabeçalhos (usa todas as chaves se None)
            delimiter: Caractere delimitador
            quotechar: Caractere para aspas
            
        Returns:
            String CSV ou None se apenas salvando em arquivo
        """
        try:
            # Determina os cabeçalhos se não fornecidos
            if not headers and data:
                headers = list(set().union(*(d.keys() for d in data)))
            
            if not headers:
                raise ValueError("Não foi possível determinar os cabeçalhos do CSV")
            
            # Cria o CSV na memória
            output = io.StringIO()
            writer = csv.DictWriter(
                output, 
                fieldnames=headers, 
                delimiter=delimiter, 
                quotechar=quotechar, 
                quoting=csv.QUOTE_MINIMAL
            )
            
            writer.writeheader()
            writer.writerows(data)
            
            csv_str = output.getvalue()
            
            # Salva em arquivo se o caminho for fornecido
            if file_path:
                path = Path(file_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(path, 'w', encoding='utf-8', newline='') as f:
                    f.write(csv_str)
                
                self.logger.debug(f"Dados CSV salvos em: {file_path}")
                return None
            
            return csv_str
        except Exception as e:
            self.logger.error(f"Erro ao converter dados para CSV: {str(e)}")
            return None