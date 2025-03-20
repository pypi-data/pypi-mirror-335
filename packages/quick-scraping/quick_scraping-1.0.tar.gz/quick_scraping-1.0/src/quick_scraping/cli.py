"""
Interface de linha de comando para Quick Scrapping.
Permite usar as funcionalidades da biblioteca diretamente do terminal.
"""

import argparse
import sys
import logging
import time
from pathlib import Path

def main():
    """Função principal da interface de linha de comando."""
    parser = argparse.ArgumentParser(description="Quick Scrapping CLI")
    parser.add_argument("url", help="URL para extrair dados")
    parser.add_argument("-o", "--output", help="Caminho para salvar os resultados", default="output.json")
    parser.add_argument("-f", "--format", choices=["json", "csv", "txt"], default="json", help="Formato de saída")
    parser.add_argument("--headless", action="store_true", help="Executar navegador em modo headless")
    parser.add_argument("--wait", type=int, default=3, help="Tempo de espera após carregar a página (segundos)")
    parser.add_argument("--debug", action="store_true", help="Ativar modo de depuração")

    args = parser.parse_args()

    # Configurar logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("quick-scrapping")

    try:
        # Módulos importados aqui para melhorar o tempo de inicialização
        # quando apenas verificando ajuda ou argumentos
        from .selenium_functions import SeleniumHelper
        from .beautifulsoup_functions import HTMLParser, DataExtractor
        from .common.scraping_helper import ScrapingHelper

        # Inicializar o scraper
        logger.info(f"Iniciando scraping de {args.url}")
        
        with SeleniumHelper(browser_type="chrome", headless=args.headless) as selenium:
            # Configurar componentes
            parser = HTMLParser(logger=logger)
            extractor = DataExtractor(logger=logger)
            scraper = ScrapingHelper(selenium_helper=selenium, bs_parser=parser, bs_extractor=extractor, logger=logger)

            # Navegar para a URL
            logger.info("Navegando para a URL...")
            selenium.navigate.to(args.url)
            selenium.element.wait_for_page_load()

            # Aguardar tempo adicional se especificado
            if args.wait > 0:
                logger.info(f"Aguardando {args.wait} segundos...")
                time.sleep(args.wait)

            # Extrair dados
            logger.info("Extraindo conteúdo da página...")
            soup = scraper.extract_from_current_page()

            # Extrair informações básicas
            results = {
                "url": args.url,
                "metadata": extractor.extract_metadata(soup),
                "links": extractor.extract_links(soup, base_url=args.url, make_absolute=True),
                "images": extractor.extract_images(soup, base_url=args.url, make_absolute=True),
                "tables": [],
            }

            # Extrair tabelas
            tables = soup.find_all("table")
            for i, table in enumerate(tables):
                headers, rows = extractor.extract_table(table)
                results["tables"].append({
                    "index": i,
                    "headers": headers,
                    "rows": rows
                })

            # Salvar resultados
            output_path = Path(args.output)
            logger.info(f"Salvando resultados em {output_path}...")
            
            # Garantir que a pasta de saída existe
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Salvar com o formato correto
            scraper.save_results(results, output_path, format=args.format)
            logger.info(f"Dados salvos com sucesso em {output_path}")

    except ImportError as e:
        logger.error(f"Erro ao importar módulos necessários: {str(e)}")
        logger.error("Verifique se todos os requisitos estão instalados (pip install quick-scrapping[all])")
        return 1
    except Exception as e:
        logger.error(f"Erro durante o scraping: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())