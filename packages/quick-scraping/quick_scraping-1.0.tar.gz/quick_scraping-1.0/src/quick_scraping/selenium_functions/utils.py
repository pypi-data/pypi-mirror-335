"""
Módulo com utilitários para Selenium.
"""

import logging
import time
from pathlib import Path
from typing import Union, List, Optional, Dict

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import JavascriptException


class UtilityHelper:
    """
    Classe auxiliar com funções utilitárias para Selenium.
    """
    
    def __init__(
        self,
        driver: WebDriver,
        logger: logging.Logger,
        download_dir: Path,
        zoom_level: float = 1.0
    ):
        """
        Inicializa o helper de utilitários.
        
        Args:
            driver: Instância do WebDriver
            logger: Logger para registrar eventos
            download_dir: Diretório para download de arquivos
            zoom_level: Nível de zoom atual
        """
        self.driver = driver
        self.logger = logger
        self.download_dir = download_dir
        self.zoom_level = zoom_level
    
    def execute_javascript(self, script: str, *args) -> any:
        """
        Executa código JavaScript na página.
        
        Args:
            script: Código JavaScript a ser executado
            *args: Argumentos a serem passados para o script
            
        Returns:
            Resultado da execução do script
        """
        try:
            result = self.driver.execute_script(script, *args)
            return result
        except JavascriptException as e:
            self.logger.error(f"Erro ao executar JavaScript: {str(e)}")
            raise
    
    def set_zoom(self, zoom_level: float) -> bool:
        """
        Ajusta o nível de zoom da página.
        
        Args:
            zoom_level: Nível de zoom (1.0 = 100%)
            
        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        try:
            # Armazena o novo nível de zoom
            self.zoom_level = zoom_level
            
            # Tenta diferentes métodos para ajustar o zoom
            
            # Método 1: CSS zoom
            self.driver.execute_script(f"document.body.style.zoom = '{zoom_level}'")
            
            # Método 2: transform scale (para navegadores que não suportam zoom)
            self.driver.execute_script(f"document.body.style.transform = 'scale({zoom_level})'")
            
            self.logger.debug(f"Zoom ajustado para {zoom_level*100}%")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao ajustar zoom: {str(e)}")
            return False
    
    def take_screenshot(self, filename: Optional[str] = None, directory: Optional[Union[str, Path]] = None) -> Optional[str]:
        """
        Captura uma screenshot da página atual.
        
        Args:
            filename: Nome do arquivo (sem extensão)
            directory: Diretório onde salvar a screenshot
            
        Returns:
            Caminho completo para a screenshot ou None em caso de erro
        """
        try:
            # Define o diretório de destino
            if directory:
                target_dir = Path(directory)
            else:
                target_dir = Path("screenshots")
            
            # Cria o diretório se não existir
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Define o nome do arquivo
            if not filename:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}"
            
            # Garante que o arquivo tem a extensão .png
            if not filename.lower().endswith(".png"):
                filename += ".png"
            
            # Caminho completo
            filepath = target_dir / filename
            
            # Captura a screenshot
            self.driver.save_screenshot(str(filepath))
            
            self.logger.debug(f"Screenshot salva em {filepath}")
            return str(filepath)
        except Exception as e:
            self.logger.error(f"Erro ao capturar screenshot: {str(e)}")
            return None
    
    def wait_for_downloads(self, timeout: int = 60, check_interval: int = 2) -> bool:
        """
        Aguarda até que todos os downloads sejam concluídos.
        
        Args:
            timeout: Tempo máximo de espera em segundos
            check_interval: Intervalo entre verificações em segundos
            
        Returns:
            True se todos os downloads foram concluídos, False caso contrário
        """
        try:
            max_checks = timeout // check_interval
            
            for i in range(max_checks):
                # Verifica arquivos temporários de download (.crdownload, .part, etc.)
                temp_files = list(self.download_dir.glob("*.crdownload")) + list(self.download_dir.glob("*.part"))
                
                if not temp_files:
                    self.logger.debug("Todos os downloads concluídos")
                    return True
                
                self.logger.debug(f"Aguardando downloads... {i+1}/{max_checks}")
                time.sleep(check_interval)
            
            self.logger.warning(f"Tempo esgotado aguardando downloads após {timeout} segundos")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao aguardar downloads: {str(e)}")
            return False
    
    def get_downloaded_files(self, file_pattern: str = "*", only_recent: bool = False) -> List[Path]:
        """
        Obtém uma lista dos arquivos baixados.
        
        Args:
            file_pattern: Padrão para filtrar os arquivos (ex: "*.pdf")
            only_recent: Se True, retorna apenas os arquivos baixados na sessão atual
            
        Returns:
            Lista de caminhos dos arquivos
        """
        try:
            # Obtém todos os arquivos que correspondem ao padrão
            files = list(self.download_dir.glob(file_pattern))
            
            if only_recent:
                # Se only_recent, filtra pelos arquivos modificados recentemente
                import time
                # Considera arquivos modificados desde o início da sessão
                session_start_time = time.time() - (time.time() - self.driver.service.start_time)
                files = [f for f in files if f.stat().st_mtime >= session_start_time]
            
            # Ordena os arquivos por data de modificação (mais recentes primeiro)
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            return files
        except Exception as e:
            self.logger.error(f"Erro ao obter arquivos baixados: {str(e)}")
            return []
    
    def wait(self, seconds: float) -> None:
        """
        Pausa a execução por um determinado período.
        
        Args:
            seconds: Tempo em segundos para aguardar
        """
        time.sleep(seconds)
    
    def get_cookies(self) -> List[Dict]:
        """
        Obtém todos os cookies da sessão atual.
        
        Returns:
            Lista de cookies
        """
        return self.driver.get_cookies()
    
    def add_cookie(self, cookie: Dict) -> bool:
        """
        Adiciona um cookie à sessão atual.
        
        Args:
            cookie: Dicionário com informações do cookie
            
        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        try:
            self.driver.add_cookie(cookie)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao adicionar cookie: {str(e)}")
            return False
    
    def delete_all_cookies(self) -> bool:
        """
        Remove todos os cookies da sessão atual.
        
        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        try:
            self.driver.delete_all_cookies()
            return True
        except Exception as e:
            self.logger.error(f"Erro ao remover cookies: {str(e)}")
            return False
    
    def get_page_source(self) -> str:
        """
        Obtém o código fonte da página atual.
        
        Returns:
            Código fonte HTML da página
        """
        return self.driver.page_source
    
    def get_browser_logs(self) -> List[Dict]:
        """
        Obtém os logs do navegador.
        
        Returns:
            Lista de entradas de log
        """
        try:
            return self.driver.get_log('browser')
        except Exception as e:
            self.logger.error(f"Erro ao obter logs do navegador: {str(e)}")
            return []