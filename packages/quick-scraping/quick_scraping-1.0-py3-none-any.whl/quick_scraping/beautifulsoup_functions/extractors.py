"""
Módulo com extratores específicos para BeautifulSoup.
Fornece funcionalidades para extrair dados estruturados de documentos HTML.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Union, Tuple
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag, ResultSet


class DataExtractor:
    """
    Classe para extração de dados estruturados de documentos HTML.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Inicializa o extrator de dados.
        
        Args:
            logger: Logger para registrar eventos
        """
        # Configura logger
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger("BeautifulSoupExtractor")
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                self.logger.setLevel(logging.INFO)
    
    def extract_table(
        self, 
        soup: Union[BeautifulSoup, Tag], 
        table_selector: str = "table",
        has_header: bool = True,
        first_row_is_header: bool = True,
        include_header: bool = True,
        strip_text: bool = True
    ) -> Tuple[List[str], List[List[str]]]:
        """
        Extrai dados de uma tabela HTML.
        
        Args:
            soup: Objeto BeautifulSoup ou Tag
            table_selector: Seletor CSS para a tabela
            has_header: Se True, tenta extrair cabeçalho da tabela
            first_row_is_header: Se True e has_header for True, considera a primeira linha como cabeçalho
            include_header: Se True, inclui o cabeçalho nos dados retornados
            strip_text: Se True, remove espaços em branco de todas as células
            
        Returns:
            Tupla contendo (cabeçalhos, linhas de dados)
        """
        try:
            # Encontra a tabela
            table = soup
            if isinstance(soup, BeautifulSoup):
                table = soup.select_one(table_selector)
                if not table:
                    self.logger.warning(f"Nenhuma tabela encontrada com o seletor: {table_selector}")
                    return [], []
            
            headers = []
            rows = []
            
            # Extrai cabeçalhos da tabela
            if has_header:
                # Tenta encontrar elementos th para o cabeçalho
                header_row = table.find("thead")
                if header_row:
                    headers = [th.get_text().strip() if strip_text else th.get_text() 
                              for th in header_row.find_all("th")]
                    if not headers:
                        headers = [td.get_text().strip() if strip_text else td.get_text() 
                                 for td in header_row.find_all("td")]
                
                # Se não encontrou cabeçalho ou não tem elementos, tenta usar a primeira linha
                if not headers and first_row_is_header:
                    first_row = table.find("tr")
                    if first_row:
                        headers = [th.get_text().strip() if strip_text else th.get_text() 
                                 for th in first_row.find_all("th")]
                        if not headers:
                            headers = [td.get_text().strip() if strip_text else td.get_text() 
                                     for td in first_row.find_all("td")]
            
            # Extrai todas as linhas
            body = table.find("tbody") or table
            table_rows = body.find_all("tr")
            
            # Se a primeira linha é cabeçalho e não estamos incluindo cabeçalho nos dados
            start_idx = 1 if first_row_is_header and has_header and not include_header and table_rows else 0
            
            for row in table_rows[start_idx:]:
                cols = row.find_all(["td", "th"])
                if cols:
                    row_data = [col.get_text().strip() if strip_text else col.get_text() for col in cols]
                    rows.append(row_data)
            
            self.logger.debug(f"Tabela extraída com {len(headers)} colunas e {len(rows)} linhas")
            return headers, rows
        
        except Exception as e:
            self.logger.error(f"Erro ao extrair tabela: {str(e)}")
            return [], []
    
    def extract_links(
        self, 
        soup: Union[BeautifulSoup, Tag], 
        base_url: Optional[str] = None,
        selector: str = "a",
        make_absolute: bool = True,
        filter_external: bool = False,
        filter_by_pattern: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Extrai links de um documento HTML.
        
        Args:
            soup: Objeto BeautifulSoup ou Tag
            base_url: URL base para resolver links relativos
            selector: Seletor CSS para os links
            make_absolute: Se True, converte URLs relativas em absolutas
            filter_external: Se True, filtra links externos (requer base_url)
            filter_by_pattern: Filtra links por expressão regular (opcional)
            
        Returns:
            Lista de dicionários com 'url', 'text' e 'title' para cada link
        """
        try:
            # Extrai todos os links
            links = soup.select(selector)
            result = []
            
            # Compilar o padrão regex se fornecido
            pattern = re.compile(filter_by_pattern) if filter_by_pattern else None
            
            # Função para verificar se um link é interno
            def is_internal(url):
                if not base_url:
                    return True
                base_domain = urlparse(base_url).netloc
                link_domain = urlparse(url).netloc
                return not link_domain or link_domain == base_domain
            
            for link in links:
                href = link.get("href", "")
                
                # Pula links sem URL ou com apenas âncoras
                if not href or href.startswith("#"):
                    continue
                
                # Converte URL relativa para absoluta
                if make_absolute and base_url and not href.startswith(("http://", "https://", "mailto:", "tel:")):
                    href = urljoin(base_url, href)
                
                # Filtra links externos se necessário
                if filter_external and not is_internal(href):
                    continue
                
                # Filtra por padrão regex
                if pattern and not pattern.search(href):
                    continue
                
                # Extrai texto e título
                text = link.get_text().strip()
                title = link.get("title", "").strip()
                
                result.append({
                    "url": href,
                    "text": text,
                    "title": title
                })
            
            self.logger.debug(f"Extraídos {len(result)} links")
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair links: {str(e)}")
            return []
    
    def extract_images(
        self, 
        soup: Union[BeautifulSoup, Tag], 
        base_url: Optional[str] = None,
        selector: str = "img",
        make_absolute: bool = True,
        include_data_src: bool = True
    ) -> List[Dict[str, str]]:
        """
        Extrai imagens de um documento HTML.
        
        Args:
            soup: Objeto BeautifulSoup ou Tag
            base_url: URL base para resolver links relativos
            selector: Seletor CSS para as imagens
            make_absolute: Se True, converte URLs relativas em absolutas
            include_data_src: Se True, também busca em atributos data-src e similares
            
        Returns:
            Lista de dicionários com 'url', 'alt' e 'title' para cada imagem
        """
        try:
            # Extrai todas as imagens
            images = soup.select(selector)
            result = []
            
            # Lista de possíveis atributos de origem da imagem
            src_attrs = ["src"]
            if include_data_src:
                src_attrs.extend(["data-src", "data-original", "data-lazy-src", "data-original-src"])
            
            for img in images:
                # Busca a URL da imagem nos possíveis atributos
                img_url = None
                for attr in src_attrs:
                    if img.get(attr):
                        img_url = img.get(attr)
                        break
                
                # Pula imagens sem URL
                if not img_url:
                    continue
                
                # Converte URL relativa para absoluta
                if make_absolute and base_url and not img_url.startswith(("http://", "https://", "data:")):
                    img_url = urljoin(base_url, img_url)
                
                # Extrai textos alternativos e título
                alt_text = img.get("alt", "").strip()
                title = img.get("title", "").strip()
                
                result.append({
                    "url": img_url,
                    "alt": alt_text,
                    "title": title
                })
            
            self.logger.debug(f"Extraídas {len(result)} imagens")
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair imagens: {str(e)}")
            return []
    
    def extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extrai metadados de um documento HTML.
        
        Args:
            soup: Objeto BeautifulSoup
            
        Returns:
            Dicionário com os metadados
        """
        try:
            metadata = {}
            
            # Extrai título da página
            title_tag = soup.find("title")
            if title_tag:
                metadata["title"] = title_tag.get_text().strip()
            
            # Extrai tags meta
            for meta in soup.find_all("meta"):
                # Meta com name e content
                if meta.get("name") and meta.get("content"):
                    metadata[meta["name"]] = meta["content"].strip()
                
                # Meta com property (Open Graph)
                elif meta.get("property") and meta.get("content"):
                    metadata[meta["property"]] = meta["content"].strip()
            
            # Extrai links canônicos
            canonical = soup.find("link", rel="canonical")
            if canonical and canonical.get("href"):
                metadata["canonical"] = canonical["href"]
            
            # Extrai outros elementos comuns de metadados
            for link in soup.find_all("link", rel=["alternate", "icon", "stylesheet"]):
                if link.get("href"):
                    rel = link.get("rel", [""])[0]
                    type_attr = link.get("type", "")
                    media = link.get("media", "")
                    
                    key = f"link_{rel}"
                    if type_attr:
                        key += f"_{type_attr}"
                    if media:
                        key += f"_{media}"
                    
                    metadata[key] = link["href"]
            
            self.logger.debug(f"Extraídos {len(metadata)} metadados")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair metadados: {str(e)}")
            return {}
    
    def extract_structured_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extrai dados estruturados (JSON-LD, microdata) de um documento HTML.
        
        Args:
            soup: Objeto BeautifulSoup
            
        Returns:
            Lista de dicionários com os dados estruturados
        """
        try:
            import json
            structured_data = []
            
            # Extrai JSON-LD
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string)
                    if data:
                        structured_data.append({
                            "type": "json-ld",
                            "data": data
                        })
                except json.JSONDecodeError:
                    self.logger.warning("Erro ao decodificar JSON-LD")
            
            # Extrai microdata (simplificado)
            items = soup.find_all(itemscope=True)
            for item in items:
                item_type = item.get("itemtype", "")
                if not item_type:
                    continue
                
                props = {}
                for prop in item.find_all(itemprop=True):
                    prop_name = prop.get("itemprop", "")
                    if not prop_name:
                        continue
                    
                    # Extrai o valor da propriedade
                    if prop.get("content"):
                        # Meta tags
                        props[prop_name] = prop["content"]
                    elif prop.name == "a" and prop.get("href"):
                        # Links
                        props[prop_name] = prop["href"]
                    elif prop.name == "img" and prop.get("src"):
                        # Imagens
                        props[prop_name] = prop["src"]
                    elif prop.name == "time" and prop.get("datetime"):
                        # Datas
                        props[prop_name] = prop["datetime"]
                    else:
                        # Texto
                        props[prop_name] = prop.get_text().strip()
                
                structured_data.append({
                    "type": "microdata",
                    "itemtype": item_type,
                    "properties": props
                })
            
            self.logger.debug(f"Extraídos {len(structured_data)} blocos de dados estruturados")
            return structured_data
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados estruturados: {str(e)}")
            return []
    
    def extract_text_blocks(
        self, 
        soup: Union[BeautifulSoup, Tag], 
        selectors: List[str] = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"],
        min_length: int = 0,
        combine_consecutive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Extrai blocos de texto de um documento HTML.
        
        Args:
            soup: Objeto BeautifulSoup ou Tag
            selectors: Lista de seletores CSS para elementos de texto
            min_length: Comprimento mínimo do texto para ser incluído
            combine_consecutive: Se True, combina elementos de texto consecutivos do mesmo tipo
            
        Returns:
            Lista de dicionários com 'type', 'text' e 'level' para cada bloco
        """
        try:
            results = []
            last_type = None
            combined_text = ""
            
            for selector in selectors:
                for element in soup.select(selector):
                    text = element.get_text().strip()
                    
                    # Pula textos vazios ou muito curtos
                    if not text or len(text) < min_length:
                        continue
                    
                    element_type = element.name
                    level = None
                    
                    # Determina o nível para elementos de cabeçalho
                    if element_type.startswith('h') and element_type[1:].isdigit():
                        level = int(element_type[1])
                    
                    # Se estamos combinando elementos consecutivos do mesmo tipo
                    if combine_consecutive and element_type == last_type:
                        combined_text += " " + text
                    else:
                        # Adiciona o bloco anterior (se existe)
                        if combined_text:
                            results.append({
                                "type": last_type,
                                "text": combined_text,
                                "level": level
                            })
                        
                        # Inicia um novo bloco
                        combined_text = text
                        last_type = element_type
            
            # Adiciona o último bloco se existe
            if combined_text and combine_consecutive:
                results.append({
                    "type": last_type,
                    "text": combined_text,
                    "level": level if last_type.startswith('h') and last_type[1:].isdigit() else None
                })
            
            self.logger.debug(f"Extraídos {len(results)} blocos de texto")
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair blocos de texto: {str(e)}")
            return []
    
    def extract_list_items(
        self, 
        soup: Union[BeautifulSoup, Tag], 
        list_selector: str = "ul, ol",
        nested: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Extrai itens de listas HTML (ul, ol).
        
        Args:
            soup: Objeto BeautifulSoup ou Tag
            list_selector: Seletor CSS para as listas
            nested: Se True, mantém a estrutura de sublistas
            
        Returns:
            Lista de dicionários com 'type', 'items' para cada lista
        """
        try:
            results = []
            
            # Funçào recursiva para extrair listas aninhadas
            def extract_items(list_element):
                items = []
                for li in list_element.find_all("li", recursive=False):
                    item_text = li.get_text().strip()
                    
                    # Verifica se o item tem sublistas
                    sublists = li.find_all(["ul", "ol"], recursive=False) if nested else []
                    
                    if sublists:
                        # Remove sublistas do texto do item atual
                        for sublist in sublists:
                            sublist_text = sublist.get_text()
                            item_text = item_text.replace(sublist_text, "").strip()
                        
                        # Adiciona o item com suas sublistas
                        sublist_data = []
                        for sublist in sublists:
                            sublist_data.append({
                                "type": sublist.name,
                                "items": extract_items(sublist)
                            })
                        
                        items.append({
                            "text": item_text,
                            "sublists": sublist_data
                        })
                    else:
                        # Adiciona item simples
                        items.append({"text": item_text})
                
                return items
            
            # Encontra e extrai todas as listas
            for list_elem in soup.select(list_selector):
                list_type = list_elem.name
                items = extract_items(list_elem)
                
                results.append({
                    "type": list_type,
                    "items": items
                })
            
            self.logger.debug(f"Extraídas {len(results)} listas")
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair itens de listas: {str(e)}")
            return []
    
    def extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extrai dados de formulários HTML.
        
        Args:
            soup: Objeto BeautifulSoup
            
        Returns:
            Lista de dicionários com dados dos formulários
        """
        try:
            results = []
            
            for form in soup.find_all("form"):
                form_data = {
                    "action": form.get("action", ""),
                    "method": form.get("method", "get").upper(),
                    "id": form.get("id", ""),
                    "name": form.get("name", ""),
                    "fields": []
                }
                
                # Extrai campos do formulário
                for field in form.find_all(["input", "select", "textarea", "button"]):
                    field_type = field.name
                    
                    # Configura campos padrão
                    field_data = {
                        "type": field_type,
                        "name": field.get("name", ""),
                        "id": field.get("id", ""),
                        "required": field.has_attr("required")
                    }
                    
                    # Adiciona campos específicos por tipo
                    if field_type == "input":
                        input_type = field.get("type", "text")
                        field_data["input_type"] = input_type
                        field_data["placeholder"] = field.get("placeholder", "")
                        field_data["value"] = field.get("value", "")
                        
                        # Verifica valores padrão para checkboxes e radios
                        if input_type in ["checkbox", "radio"]:
                            field_data["checked"] = field.has_attr("checked")
                    
                    elif field_type == "select":
                        options = []
                        for option in field.find_all("option"):
                            options.append({
                                "value": option.get("value", ""),
                                "text": option.get_text().strip(),
                                "selected": option.has_attr("selected")
                            })
                        field_data["options"] = options
                    
                    elif field_type == "textarea":
                        field_data["placeholder"] = field.get("placeholder", "")
                        field_data["value"] = field.get_text().strip()
                    
                    elif field_type == "button":
                        button_type = field.get("type", "submit")
                        field_data["button_type"] = button_type
                        field_data["text"] = field.get_text().strip()
                    
                    form_data["fields"].append(field_data)
                
                results.append(form_data)
            
            self.logger.debug(f"Extraídos {len(results)} formulários")
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair formulários: {str(e)}")
            return []
    
    def extract_article_content(
        self, 
        soup: BeautifulSoup,
        article_selector: str = "article, .article, .post, .content, #content, main"
    ) -> Dict[str, Any]:
        """
        Extrai conteúdo de um artigo estruturado.
        
        Args:
            soup: Objeto BeautifulSoup
            article_selector: Seletor CSS para o contêiner principal do artigo
            
        Returns:
            Dicionário com o conteúdo estruturado do artigo
        """
        try:
            # Tenta encontrar o contêiner principal do artigo
            article = soup.select_one(article_selector)
            if not article:
                article = soup  # Usa a página inteira se não encontrar contêiner específico
            
            # Extrai metadados
            metadata = {}
            
            # Título
            title_selectors = ["h1", "h1.title", "h1.entry-title", "h1.post-title", ".title", ".entry-title", ".post-title"]
            for selector in title_selectors:
                title_elem = article.select_one(selector)
                if title_elem:
                    metadata["title"] = title_elem.get_text().strip()
                    break
            
            # Autor
            author_selectors = [".author", ".byline", ".post-author", "meta[name='author']", "[rel='author']"]
            for selector in author_selectors:
                author_elem = soup.select_one(selector)  # Procura em toda a página
                if author_elem:
                    if author_elem.name == "meta":
                        metadata["author"] = author_elem.get("content", "").strip()
                    else:
                        metadata["author"] = author_elem.get_text().strip()
                    break
            
            # Data de publicação
            date_selectors = [
                "time", ".date", ".published", ".post-date", ".entry-date", 
                "meta[property='article:published_time']", "meta[name='publish-date']"
            ]
            for selector in date_selectors:
                date_elem = soup.select_one(selector)  # Procura em toda a página
                if date_elem:
                    if date_elem.name == "time" and date_elem.get("datetime"):
                        metadata["date"] = date_elem.get("datetime")
                    elif date_elem.name == "meta":
                        metadata["date"] = date_elem.get("content", "")
                    else:
                        metadata["date"] = date_elem.get_text().strip()
                    break
            
            # Extrai conteúdo principal (parágrafos)
            content = []
            for p in article.find_all(["p", "h2", "h3", "h4", "blockquote", "figure"]):
                # Pula elementos vazios
                if not p.get_text().strip():
                    continue
                
                # Determina o tipo de elemento
                if p.name == "figure":
                    # Processa figuras e imagens
                    img = p.find("img")
                    caption = p.find("figcaption")
                    
                    if img:
                        item = {
                            "type": "image",
                            "src": img.get("src", ""),
                            "alt": img.get("alt", "")
                        }
                        
                        if caption:
                            item["caption"] = caption.get_text().strip()
                        
                        content.append(item)
                
                elif p.name == "blockquote":
                    # Processa citações
                    content.append({
                        "type": "quote",
                        "text": p.get_text().strip()
                    })
                
                elif p.name.startswith("h"):
                    # Processa cabeçalhos
                    content.append({
                        "type": "heading",
                        "level": int(p.name[1]),
                        "text": p.get_text().strip()
                    })
                
                else:
                    # Processa parágrafos normais
                    content.append({
                        "type": "paragraph",
                        "text": p.get_text().strip()
                    })
            
            # Extrai imagens
            images = []
            for img in article.find_all("img"):
                if img.parent.name == "figure":
                    # Pula imagens já processadas dentro de figures
                    continue
                
                alt = img.get("alt", "").strip()
                src = img.get("src", "")
                
                if src:
                    images.append({
                        "src": src,
                        "alt": alt
                    })
            
            result = {
                "metadata": metadata,
                "content": content,
                "images": images
            }
            
            self.logger.debug("Conteúdo do artigo extraído com sucesso")
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair conteúdo do artigo: {str(e)}")
            return {"metadata": {}, "content": [], "images": []}
    
    def scrape_text_pattern(
        self, 
        soup: BeautifulSoup, 
        pattern: str,
        scope_selector: Optional[str] = None,
        flags: int = re.IGNORECASE
    ) -> List[str]:
        """
        Extrai texto que corresponde a um padrão regex.
        
        Args:
            soup: Objeto BeautifulSoup
            pattern: Padrão regex para buscar
            scope_selector: Seletor CSS para limitar o escopo da busca (opcional)
            flags: Flags para a regex
            
        Returns:
            Lista de correspondências encontradas
        """
        try:
            # Compila o padrão regex
            regex = re.compile(pattern, flags)
            
            # Limita o escopo se especificado
            if scope_selector:
                elements = soup.select(scope_selector)
                if not elements:
                    return []
                search_text = " ".join(element.get_text() for element in elements)
            else:
                search_text = soup.get_text()
            
            # Busca todas as correspondências
            matches = regex.findall(search_text)
            
            self.logger.debug(f"Encontradas {len(matches)} correspondências para o padrão '{pattern}'")
            return matches
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar padrão: {str(e)}")
            return []