"""
Exemplos de uso do SeleniumHelper.
"""

import time
from ..selenium_functions import SeleniumHelper


def exemplo_basico():
    """Exemplo básico de navegação e interação."""
    # Inicializa o helper com Chrome
    with SeleniumHelper(browser_type="chrome") as browser:
        # Navegação básica
        browser.navigate.to("https://www.google.com")
        
        # Digita na barra de pesquisa
        browser.interact.type_text("name", "q", "Selenium Python tutorial", press_enter=True)
        
        # Espera a página de resultados carregar
        browser.element.wait_for_page_load()
        
        # Captura uma screenshot
        browser.utils.take_screenshot("google_search")
        
        # Demonstra alguns métodos de elementos
        if browser.element.is_element_present("xpath", "//h3[contains(text(), 'Selenium')]"):
            print("Encontrou resultados relacionados ao Selenium!")
            
            # Clica no primeiro resultado
            browser.interact.click("xpath", "//h3[contains(text(), 'Selenium')]")
            
            # Espera a nova página carregar
            browser.element.wait_for_page_load()
            
            # Obtém o título da página
            title = browser.navigate.get_title()
            print(f"Navegou para: {title}")
            
            # Volta para a página de resultados
            browser.navigate.back()


def exemplo_formulario():
    """Exemplo de preenchimento de formulário."""
    with SeleniumHelper() as browser:
        # Navega para um site com formulário
        browser.navigate.to("https://www.selenium.dev/selenium/web/web-form.html")
        
        # Preenche campos de texto
        browser.interact.type_text("name", "my-text", "Teste Automatizado")
        browser.interact.type_text("name", "my-textarea", "Este é um exemplo de automação com SeleniumHelper")
        
        # Seleciona opção em dropdown
        browser.interact.select_dropdown_by_text("name", "my-select", "Two")
        
        # Clica em checkbox
        browser.interact.click("css", "input[name='my-check']")
        
        # Seleciona um botão radio
        browser.interact.click("css", "input[value='radio-1']")
        
        # Escolhe uma data
        browser.interact.type_text("name", "my-date", "2023-09-15")
        
        # Clica no botão de submissão
        browser.interact.click("css", "button[type='submit']")
        
        # Verifica se a submissão foi bem-sucedida
        if browser.element.is_element_present("id", "message"):
            message = browser.element.get_text("id", "message")
            print(f"Resultado: {message}")


def exemplo_janelas():
    """Exemplo de manipulação de múltiplas janelas."""
    with SeleniumHelper() as browser:
        # Navega para um site
        browser.navigate.to("https://www.selenium.dev/documentation/webdriver/interactions/windows/")
        
        # Clica em um link que abre uma nova janela
        browser.interact.click("link_text", "new window")
        
        # Muda para a nova janela
        browser.frame.switch_to_new_window()
        
        # Verifica o título da nova janela
        new_window_title = browser.navigate.get_title()
        print(f"Nova janela: {new_window_title}")
        
        # Fecha a janela atual e volta para a original
        browser.frame.close_current_window()
        
        # Verifica se voltou para a janela original
        original_title = browser.navigate.get_title()
        print(f"Janela original: {original_title}")


def exemplo_alertas():
    """Exemplo de manipulação de alertas."""
    with SeleniumHelper() as browser:
        # Navega para um site com alertas
        browser.navigate.to("https://www.selenium.dev/documentation/webdriver/interactions/alerts/")
        
        # Executa JavaScript para criar um alerta
        browser.utils.execute_javascript("alert('Este é um alerta de exemplo');")
        
        # Obtém o texto do alerta
        alert_text = browser.alert.get_text()
        print(f"Texto do alerta: {alert_text}")
        
        # Aceita o alerta
        browser.alert.accept()


def exemplo_frames():
    """Exemplo de manipulação de frames."""
    with SeleniumHelper() as browser:
        # Navega para um site com frames
        browser.navigate.to("https://www.selenium.dev/documentation/webdriver/interactions/frames/")
        
        # Muda para um iframe
        browser.frame.switch_to("tag", "iframe")
        
        # Interage com elementos dentro do iframe
        if browser.element.is_element_present("tag", "h1"):
            iframe_title = browser.element.get_text("tag", "h1")
            print(f"Conteúdo do iframe: {iframe_title}")
        
        # Volta para o conteúdo principal
        browser.frame.switch_to_default_content()


def exemplo_downloads():
    """Exemplo de download e manipulação de arquivos."""
    with SeleniumHelper(download_dir="./downloads") as browser:
        # Navega para um site com arquivos para download
        browser.navigate.to("https://www.selenium.dev/downloads/")
        
        # Clica em um link de download
        browser.interact.click("link_text", "Latest stable version")
        
        # Aguarda o download completar
        browser.utils.wait_for_downloads(timeout=30)
        
        # Lista os arquivos baixados
        downloads = browser.utils.get_downloaded_files(file_pattern="*.zip", only_recent=True)
        
        for download in downloads:
            print(f"Arquivo baixado: {download}")


def exemplo_avancado():
    """Exemplo com interações mais avançadas."""
    with SeleniumHelper() as browser:
        # Navega para um site
        browser.navigate.to("https://www.google.com")
        
        # Exemplos de diferentes tipos de interações
        
        # Drag and drop (simulado aqui)
        if browser.element.is_element_present("css", ".source") and browser.element.is_element_present("css", ".target"):
            browser.interact.drag_and_drop("css", ".source", "css", ".target")
        
        # Hover sobre um elemento
        if browser.element.is_element_present("css", ".menu"):
            browser.interact.hover("css", ".menu")
            
            # Clica em um item do submenu que aparece após o hover
            if browser.element.is_element_visible("css", ".submenu-item"):
                browser.interact.click("css", ".submenu-item")
        
        # Executa JavaScript personalizado
        browser.utils.execute_javascript("""
            console.log('Executando código JavaScript personalizado');
            document.body.style.backgroundColor = '#f0f0f0';
        """)
        
        # Manipulação de cookies
        browser.utils.add_cookie({"name": "exemplo", "value": "teste"})
        cookies = browser.utils.get_cookies()
        print(f"Total de cookies: {len(cookies)}")


if __name__ == "__main__":
    # Executa os exemplos
    try:
        print("Executando exemplo básico...")
        exemplo_basico()
        
        print("\nExecutando exemplo de formulário...")
        exemplo_formulario()
        
        print("\nExecutando exemplo de janelas...")
        exemplo_janelas()
        
        print("\nExecutando exemplo de alertas...")
        exemplo_alertas()
        
        print("\nExecutando exemplo de frames...")
        exemplo_frames()
        
        print("\nExecutando exemplo de downloads...")
        exemplo_downloads()
        
        print("\nExecutando exemplo avançado...")
        exemplo_avancado()
        
        print("\nTodos os exemplos foram executados com sucesso!")
    except Exception as e:
        print(f"Erro ao executar exemplos: {str(e)}")