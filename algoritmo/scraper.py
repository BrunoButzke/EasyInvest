import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

def scrape_with_precise_steps():
    """
    Executa a sequência exata de operações com pausas generosas em modo visível.
    """
    url = "https://www.fundsexplorer.com.br/ranking"
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # Muda a estratégia de carregamento da página
    options.page_load_strategy = 'eager'
    
    service = Service(ChromeDriverManager().install())
    
    driver = None
    try:
        # --- 1. Abrir a URL ---
        print(f"Abrindo a página: {url}")
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'tbody')))
        
        # --- 2. Pausa para a página estabilizar ---
        print("Aguardando 5 segundos para a página estabilizar...")
        time.sleep(5)
        
        # --- 3. Clicar no botão de colunas ---
        button_id = "colunas-ranking__select-button"
        print(f"Procurando e clicando no ID: '{button_id}'")
        select_button = wait.until(EC.element_to_be_clickable((By.ID, button_id)))
        select_button.click()

        # --- 4. Pausa ---
        print("Aguardando 1 segundo...")
        time.sleep(1)
        
        # --- 5. Clicar em 'Selecionar Todos' via seu <label> ---
        # Clicar no <label> é mais robusto do que no <input> escondido
        todos_label_xpath = "//label[@for='colunas-ranking__todos']"
        print(f"Procurando e clicando no label: {todos_label_xpath}")
        todos_button = wait.until(EC.element_to_be_clickable((By.XPATH, todos_label_xpath)))
        todos_button.click()
        
        # --- 6. Pausa para a tabela recarregar ---
        print("Aguardando 5 segundos para a tabela recarregar com todas as colunas...")
        time.sleep(5)
        
        # --- 7. Extrair dados ---
        print("Extraindo dados da tabela...")
        table_body = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'tbody')))
        
        header_elements = driver.find_elements(By.XPATH, '//thead/tr/th')
        headers = [header.text.strip() for header in header_elements]
        
        rows = []
        tr_elements = table_body.find_elements(By.TAG_NAME, 'tr')
        
        for tr in tr_elements:
            td_elements = tr.find_elements(By.TAG_NAME, 'td')
            row_data = [td.text.strip() for td in td_elements]
            if any(row_data):
                rows.append(row_data)
        
        print(f"Extração concluída: {len(rows)} linhas e {len(headers)} colunas encontradas.")
        return headers, rows

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None, None
    finally:
        if driver:
            print("Fechando o navegador.")
            driver.quit()

def generate_html(headers, rows):
    html_content = """
    <!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Ranking de Fundos Imobiliários</title><style>body{font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;margin:0;padding:20px;background-color:#f4f7f6;color:#333}h1{text-align:center;color:#2c3e50}.table-container{overflow-x:auto;margin:20px 0;border-radius:8px;box-shadow:0 4px 8px rgba(0,0,0,0.1)}table{width:100%;border-collapse:collapse;background-color:#fff}th,td{padding:12px 15px;text-align:left;border-bottom:1px solid #ddd;white-space:nowrap}thead th{background-color:#34495e;color:#fff;position:sticky;top:0}tbody tr:nth-of-type(even){background-color:#f8f9fa}tbody tr:hover{background-color:#e9ecef}</style></head><body><h1>Ranking de Fundos Imobiliários (FIIs)</h1><div class="table-container"><table>
    """
    if headers:
        html_content += "<thead><tr>"
        for header in headers: html_content += f"<th>{header}</th>"
        html_content += "</tr></thead>"
    if rows:
        html_content += "<tbody>"
        for row in rows:
            html_content += "<tr>"
            for cell in row: html_content += f"<td>{cell}</td>"
            html_content += "</tr>"
        html_content += "</tbody>"
    html_content += "</table></div></body></html>"
    return html_content

def main():
    headers, rows = scrape_with_precise_steps()
    if headers and rows:
        print("Gerando arquivo HTML...")
        html_output = generate_html(headers, rows)
        output_filename = 'ranking.html'
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(html_output)
            abs_path = os.path.abspath(output_filename)
            print(f"Arquivo '{output_filename}' gerado com sucesso!")
            print(f"Você pode abri-lo em: file://{abs_path}")
        except IOError as e:
            print(f"Erro ao salvar o arquivo HTML: {e}")
    else:
        print("Processo finalizado sem extração de dados.")

if __name__ == '__main__':
    main()
