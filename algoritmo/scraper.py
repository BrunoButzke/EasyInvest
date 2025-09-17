import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

def scrape_funds_explorer():
    """
    Abordagem final e robusta:
    1. Usa Selenium para carregar a página e esperar os dados aparecerem.
    2. Itera manualmente sobre a tabela, lendo cada célula (<td>) para garantir
       a captura dos dados corretos, evitando as abstrações do pandas.
    """
    url = "https://www.fundsexplorer.com.br/ranking"
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        
        # Espera pela presença do corpo da tabela (tbody) com pelo menos uma linha (tr)
        wait = WebDriverWait(driver, 30)
        table_body = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'tbody')))
        
        # Extrai o cabeçalho
        header_elements = driver.find_elements(By.XPATH, '//thead/tr/th')
        headers = [header.text.strip() for header in header_elements]
        
        # Extrai as linhas de dados manualmente
        rows = []
        # Encontra todas as linhas no corpo da tabela
        tr_elements = table_body.find_elements(By.TAG_NAME, 'tr')
        
        for tr in tr_elements:
            # Pega todas as células de cada linha
            td_elements = tr.find_elements(By.TAG_NAME, 'td')
            # Extrai o texto de cada célula
            row_data = [td.text.strip() for td in td_elements]
            # Adiciona apenas se a linha não estiver vazia
            if any(row_data):
                rows.append(row_data)
                
        return headers, rows

    except Exception as e:
        print(f"Ocorreu um erro durante o scraping: {e}")
        return None, None
    finally:
        if driver:
            driver.quit()

def generate_html(headers, rows):
    """
    Gera uma string HTML a partir dos dados da tabela.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ranking de Fundos Imobiliários</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f4f7f6;
                color: #333;
            }
            h1 {
                text-align: center;
                color: #2c3e50;
            }
            .table-container {
                overflow-x: auto;
                margin: 20px 0;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            table {
                width: 100%;
                border-collapse: collapse;
                background-color: #ffffff;
            }
            th, td {
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #ddd;
                white-space: nowrap;
            }
            thead th {
                background-color: #34495e;
                color: #ffffff;
                position: sticky;
                top: 0;
            }
            tbody tr:nth-of-type(even) {
                background-color: #f8f9fa;
            }
            tbody tr:hover {
                background-color: #e9ecef;
            }
        </style>
    </head>
    <body>
        <h1>Ranking de Fundos Imobiliários (FIIs)</h1>
        <div class="table-container">
            <table>
    """
    
    # Adiciona o cabeçalho da tabela
    if headers:
        html_content += "<thead><tr>"
        for header in headers:
            html_content += f"<th>{header}</th>"
        html_content += "</tr></thead>"
    
    # Adiciona o corpo da tabela
    if rows:
        html_content += "<tbody>"
        for row in rows:
            html_content += "<tr>"
            for cell in row:
                html_content += f"<td>{cell}</td>"
            html_content += "</tr>"
        html_content += "</tbody>"
        
    html_content += """
            </table>
        </div>
    </body>
    </html>
    """
    return html_content

def main():
    """
    Função principal que orquestra o scraping e a geração do HTML.
    """
    print("Iniciando o scraping da página do Funds Explorer com Selenium...")
    headers, rows = scrape_funds_explorer()
    
    if headers and rows:
        print(f"Scraping concluído com sucesso. {len(rows)} fundos encontrados.")
        print("Gerando arquivo HTML...")
        
        html_output = generate_html(headers, rows)
        
        output_filename = 'ranking.html'
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(html_output)
            
            # Obtém o caminho absoluto do arquivo para exibir ao usuário
            abs_path = os.path.abspath(output_filename)
            print(f"Arquivo '{output_filename}' gerado com sucesso!")
            print(f"Você pode abri-lo em seu navegador em: file://{abs_path}")
            
        except IOError as e:
            print(f"Erro ao salvar o arquivo HTML: {e}")
    else:
        print("Não foi possível extrair os dados. O arquivo HTML não será gerado.")

if __name__ == '__main__':
    main()
