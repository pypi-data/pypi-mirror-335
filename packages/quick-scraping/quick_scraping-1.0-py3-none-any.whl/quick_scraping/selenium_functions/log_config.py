"""
Módulo para configuração e gerenciamento de logs.
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logger(
    logger_name: str = "SeleniumAutomation",
    log_folder: str = "logs",
    log_filename: Optional[str] = None,
    maxBytes: int = 1024*1024,
    backupCount: int = 5
) -> logging.Logger:
    """
    Configura um logger que salva os logs em um arquivo.
    
    Args:
        logger_name: Nome do logger
        log_folder: Pasta onde os logs serão salvos
        log_filename: Nome do arquivo de log (se None, usa logger_name + timestamp)
        maxBytes: Tamanho máximo do arquivo de log antes da rotação
        backupCount: Número de arquivos de backup a manter
        
    Returns:
        Logger configurado
    """
    # Cria a pasta de logs se não existir
    log_folder_path = Path(log_folder)
    log_folder_path.mkdir(parents=True, exist_ok=True)
    
    # Define o nome do arquivo de log se não for fornecido
    if log_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_filename = f"{logger_name}_{timestamp}.log"
    
    # Caminho completo para o arquivo de log
    log_path = log_folder_path / log_filename
    
    # Configura o logger
    logger = logging.getLogger(logger_name)
    
    # Verifica se o logger já está configurado para evitar handlers duplicados
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Configura o formato do log
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Configura o handler para arquivo com rotação
        file_handler = RotatingFileHandler(
            log_path, 
            maxBytes=maxBytes,
            backupCount=backupCount
        )
        file_handler.setFormatter(formatter)
        
        # Adiciona o handler ao logger
        logger.addHandler(file_handler)
        
        # Handler para console (opcional)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger