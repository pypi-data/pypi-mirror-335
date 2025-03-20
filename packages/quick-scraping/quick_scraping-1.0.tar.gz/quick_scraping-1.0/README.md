# Quick Scraping

Uma biblioteca Python completa para web scraping e automação, combinando o poder do Selenium e BeautifulSoup.

## Características

- **Módulo Selenium**: Automação completa de navegadores web
- **Módulo BeautifulSoup**: Análise e extração avançada de HTML
- **Integração**: Funções para trabalhar com ambas as bibliotecas de forma integrada
- **Ferramentas de Utilidade**: Processamento de texto, CSV, JSON e mais
- **Logging**: Sistema de registro completo para todas as operações

## Instalação

```bash
pip install quick-Scraping
```

Para instalar com dependências opcionais:

```bash
# Para desenvolvimento
pip install quick-Scraping[dev]

# Para documentação
pip install quick-Scraping[docs]
```

## Uso Básico

### Exemplo com Selenium

```python
from quick_Scraping.selenium_functions import SeleniumHelper

# Inicializa o Selenium Helper
with SeleniumHelper(browser_type="chrome", headless=True) as selenium:
    # Navega para uma URL
    selenium.navigate.to("https://www.exemplo.com")
    
    # Espera por um elemento e clica nele
    selenium.element.wait_for_element("id", "meu-botao", timeout=10)
    selenium.interact.click("id", "meu-botao")
    
    # Obtém o HTML da página
    html = selenium.driver.page_source
```

### Exemplo com BeautifulSoup

```python
from quick_Scraping.beautifulsoup_functions import HTMLParser, DataExtractor

# Inicializa o parser HTML e o extrator de dados
parser = HTMLParser()
extractor = DataExtractor()

# Carrega HTML de um arquivo ou URL
soup = parser.load_from_url("https://www.exemplo.com")

# Extrai dados estruturados
links = extractor.extract_links(soup)
table_headers, table_data = extractor.extract_table(soup, table_selector="table.dados")

# Extrai artigo completo
article = extractor.extract_article_content(soup)
```

### Exemplo de Integração

```python
from quick_Scraping.common import ScrapingHelper

# Inicializa o helper integrado
scraper = ScrapingHelper()

# Configura extração de dados
extraction_config = {
    "title": {"type": "text", "selector": "h1.title"},
    "products": {"type": "table", "selector": "table.products"},
    "links": {"type": "links", "selector": "a.product-link"}
}

# Navega e extrai dados
results = scraper.extract_data_with_selenium(
    url="https://www.exemplo.com/produtos",
    extraction_config=extraction_config,
    wait_time=3
)

# Salva os resultados
scraper.save_results(results, "produtos.json", format="json")
```

## Documentação

Para documentação completa, visite [https://quick-Scraping.readthedocs.io/](https://quick-Scraping.readthedocs.io/)

## Contribuindo

Contribuições são bem-vindas! Por favor, leia o guia de contribuição antes de enviar um pull request.

## Licença

Este projeto é licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.