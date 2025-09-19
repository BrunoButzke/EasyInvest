uns sefrom selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def open_page():
    """
    Abre o navegador Chrome, navega até a URL especificada e
    permanece aberto por 30 segundos antes de fechar.
    """
    url = "https://www.fundsexplorer.com.br/ranking"
    
    # Usaremos uma configuração mínima, sem modo headless, para ver o navegador abrir
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    
    service = Service(ChromeDriverManager().install())
    
    driver = None
    try:
        print(f"Tentando abrir a página: {url}")
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        
        print("Página aberta com sucesso.")
        print("O navegador permanecerá aberto por 30 segundos.")
        
        # Mantém o navegador aberto para inspeção visual
        time.sleep(30)
        
        print("Fechando o navegador.")

    except Exception as e:
        print(f"Ocorreu um erro ao tentar abrir a página: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == '__main__':
    open_page()
