"""
Exemplos de uso do módulo BeautifulSoup.
"""

import os
import logging
from bs4 import BeautifulSoup

from parser import HTMLParser
from extractors import DataExtractor
from utils import HTMLUtils


# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BeautifulSoupExamples')


def exemplo_parser():
    """Exemplo de uso do HTMLParser."""
    parser = HTMLParser(logger=logger)
    
    # Análise de string HTML
    html = """
    <html>
        <head>
            <title>Exemplo de Página</title>
            <meta name="description" content="Esta é uma página de exemplo">
        </head>
        <body>
            <h1>Bem-vindo ao exemplo</h1>
            <p>Este é um parágrafo de exemplo com um <a href="https://exemplo.com">link</a>.</p>
            <div class="content">
                <h2>Seção de Exemplo</h2>
                <p>Mais texto de exemplo.</p>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                    <li>Item 3</li>
                </ul>
            </div>
        </body>
    </html>
    """
    
    # Analisa o HTML
    soup = parser.parse_html(html)
    
    # Demonstra métodos básicos
    print("Título da página:", soup.title.text)
    
    # Limpa o HTML
    cleaned_soup = parser.clean_html(soup, remove_scripts=True, remove_styles=True)
    
    # Salva o HTML
    parser.save_to_file(cleaned_soup, "exemplo_limpo.html", pretty_print=True)
    
    # Extrai texto
    texto = parser.extract_text(soup)
    print("Texto extraído:", texto[:100] + "...")


def exemplo_extratores():
    """Exemplo de uso do DataExtractor."""
    parser = HTMLParser(logger=logger)
    extractor = DataExtractor(logger=logger)
    
    # Carrega HTML de exemplo
    html = """
    <html>
        <head>
            <title>Exemplo de Página</title>
        </head>
        <body>
            <article>
                <h1>Artigo de Exemplo</h1>
                <div class="author">Por João Silva</div>
                <div class="date">2023-09-15</div>
                
                <p>Este é o primeiro parágrafo do artigo.</p>
                <p>Este é o segundo parágrafo com um <a href="https://exemplo.com">link</a>.</p>
                
                <h2>Subtítulo do Artigo</h2>
                <p>Mais conteúdo do artigo.</p>
                
                <table>
                    <thead>
                        <tr>
                            <th>Nome</th>
                            <th>Idade</th>
                            <th>Cidade</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>João</td>
                            <td>30</td>
                            <td>São Paulo</td>
                        </tr>
                        <tr>
                            <td>Maria</td>
                            <td>25</td>
                            <td>Rio de Janeiro</td>
                        </tr>
                    </tbody>
                </table>
                
                <ul>
                    <li>Item da lista 1</li>
                    <li>Item da lista 2
                        <ul>
                            <li>Subitem 1</li>
                            <li>Subitem 2</li>
                        </ul>
                    </li>
                    <li>Item da lista 3</li>
                </ul>
            </article>
            
            <div class="contact">
                <p>Email: contato@exemplo.com</p>
                <p>Telefone: (11) 99999-9999</p>
            </div>
        </body>
    </html>
    """
    
    # Analisa o HTML
    soup = parser.parse_html(html)
    
    # Extrai conteúdo de artigo
    article = extractor.extract_article_content(soup)
    print("\nConteúdo do Artigo:")
    print(f"Título: {article['metadata'].get('title', 'N/A')}")
    print(f"Autor: {article['metadata'].get('author', 'N/A')}")
    print(f"Data: {article['metadata'].get('date', 'N/A')}")
    print(f"Parágrafos: {len([c for c in article['content'] if c.get('type') == 'paragraph'])}")
    
    # Extrai tabela
    headers, rows = extractor.extract_table(soup, table_selector="table")
    print("\nTabela Extraída:")
    print(f"Cabeçalhos: {headers}")
    for row in rows:
        print(f"Linha: {row}")
    
    # Extrai links
    links = extractor.extract_links(soup)
    print("\nLinks Extraídos:")
    for link in links:
        print(f"- {link['text']} ({link['url']})")
    
    # Extrai itens de lista
    lists = extractor.extract_list_items(soup)
    print("\nListas Extraídas:")
    for list_item in lists:
        print(f"Tipo de Lista: {list_item['type']}")
        for item in list_item['items']:
            print(f"- {item['text']}")
            if 'sublists' in item:
                for sublist in item['sublists']:
                    print(f"  Sublista do tipo {sublist['type']}:")
                    for subitem in sublist['items']:
                        print(f"    - {subitem['text']}")
    
    # Extrai e-mails e telefones da página
    text = parser.extract_text(soup)
    utils = HTMLUtils(logger=logger)
    
    emails = utils.extract_emails(text)
    phones = utils.extract_phone_numbers(text)
    
    print("\nContatos Extraídos:")
    print(f"E-mails: {emails}")
    print(f"Telefones: {phones}")


def exemplo_utils():
    """Exemplo de uso do HTMLUtils."""
    parser = HTMLParser(logger=logger)
    utils = HTMLUtils(logger=logger)
    
    # Carrega HTML de exemplo
    html = """
    <html>
        <head>
            <title>Exemplo de Página</title>
            <script>alert('Teste');</script>
            <style>body { color: red; }</style>
        </head>
        <body>
            <div class="content">
                <h1>Título Principal</h1>
                <p>Este é um parágrafo com <b>texto em negrito</b> e um 
                   <a href="https://exemplo.com">link de exemplo</a>.</p>
                <p>Este é outro parágrafo com   espaços   extras   e
                   quebras de linha.</p>
                <img src="imagem.jpg" alt="Descrição da imagem">
                <div class="ad">Este é um anúncio.</div>
            </div>
        </body>
    </html>
    """
    
    # Analisa o HTML
    soup = parser.parse_html(html)
    
    # Remove elementos indesejados
    cleaned_soup = utils.remove_unwanted_elements(soup, selectors=["script", "style", ".ad"])
    
    # Converte HTML para texto simples
    plain_text = utils.html_to_plain_text(
        cleaned_soup,
        preserve_links=True,
        preserve_images=True,
        preserve_linebreaks=True
    )
    print("\nHTML Convertido para Texto:")
    print(plain_text)
    
    # Extrai palavras-chave
    keywords = utils.extract_keywords(plain_text)
    print("\nPalavras-Chave Extraídas:")
    print(keywords)
    
    # Demonstra conversão para JSON
    data = {
        "title": "Exemplo de Página",
        "content": plain_text,
        "keywords": keywords
    }
    
    json_str = utils.data_to_json(data)
    print("\nDados em JSON:")
    print(json_str)
    
    # Demonstra conversão para CSV
    csv_data = [
        {"nome": "João", "idade": 30, "cidade": "São Paulo"},
        {"nome": "Maria", "idade": 25, "cidade": "Rio de Janeiro"}
    ]
    
    csv_str = utils.data_to_csv(csv_data)
    print("\nDados em CSV:")
    print(csv_str)


def exemplo_carregamento_url():
    """Exemplo de carregamento de HTML a partir de uma URL."""
    parser = HTMLParser(logger=logger)
    extractor = DataExtractor(logger=logger)
    
    try:
        # Carrega uma página de exemplo (substituir por uma URL válida)
        url = "https://www.example.com"
        soup = parser.load_from_url(url)
        
        # Extrai metadados
        metadata = extractor.extract_metadata(soup)
        print("\nMetadados da Página:")
        for key, value in metadata.items():
            print(f"{key}: {value}")
        
        # Extrai links
        links = extractor.extract_links(soup, base_url=url, make_absolute=True)
        print("\nLinks na Página:")
        for link in links[:5]:  # Limita a 5 links para não sobrecarregar o exemplo
            print(f"- {link['text']} ({link['url']})")
        
    except Exception as e:
        logger.error(f"Erro ao carregar URL: {str(e)}")
        print(f"Não foi possível acessar a URL. Erro: {str(e)}")


if __name__ == "__main__":
    print("======= Exemplos do Módulo BeautifulSoup =======")
    
    print("\n--- Exemplo do Parser ---")
    exemplo_parser()
    
    print("\n--- Exemplo dos Extratores ---")
    exemplo_extratores()
    
    print("\n--- Exemplo dos Utilitários ---")
    exemplo_utils()
    
    print("\n--- Exemplo de Carregamento de URL ---")
    exemplo_carregamento_url()
    
    print("\n======= Fim dos Exemplos =======")