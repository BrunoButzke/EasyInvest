import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import time

# Carrega as variáveis de ambiente do arquivo .env (se ele existir)
# Isso é útil para o desenvolvimento local.
load_dotenv()

def scrape_with_precise_steps():
    """
    Executa a sequência exata de operações com pausas generosas em modo visível.
    """
    # Busca a URL da variável de ambiente, com um valor padrão para fallback
    url = os.environ.get("SCRAPE_URL")
    
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
        
        # Extração de cabeçalho mais robusta
        header_elements = driver.find_elements(By.XPATH, '//thead/tr/th')
        # Usamos get_attribute("textContent") que é mais confiável que .text
        headers = [header.get_attribute("textContent").strip() for header in header_elements]
        
        # --- DEBUGGING DE CABEÇALHOS ---
        print("\n--- CABEÇALHOS EXTRAÍDOS DO SITE ---")
        print(headers)
        print("-------------------------------------\n")
        # --- FIM DEBUGGING ---

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

def clean_and_convert(value_str, to_int=False):
    """Converte um valor em string para numérico, com opção para inteiro."""
    if value_str is None or value_str.strip() in ('', '--', 'N/A'):
        return None
    
    cleaned_str = value_str.replace('R$', '').replace('%', '').strip()
    cleaned_str = cleaned_str.replace('.', '')
    cleaned_str = cleaned_str.replace(',', '.')

    try:
        float_val = float(cleaned_str)
        if to_int:
            return int(float_val)
        return float_val
    except ValueError:
        return value_str

def save_to_supabase(headers, rows):
    """Salva os dados extraídos em uma tabela do Supabase."""
    
    # Busca as credenciais das variáveis de ambiente (mais seguro)
    # No GitHub, elas serão configuradas como "Secrets"
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    table_name = "ranking_fiis"

    if not url or not key:
        print("Credenciais do Supabase (SUPABASE_URL, SUPABASE_KEY) não encontradas.")
        print("O script não pode continuar sem as credenciais.")
        return

    try:
        supabase: Client = create_client(url, key)
    except Exception as e:
        print(f"Erro ao conectar ao Supabase: {e}")
        return

    # Mapeamento explícito dos cabeçalhos do site para as colunas do DB
    header_map = {
        'Fundos': 'fundos', 'Setor': 'setor', 'Preço Atual (R$)': 'preco_atual_rs',
        'Liquidez Diária (R$)': 'liquidez_diaria_rs', 'P/VP': 'p_vp', 'Último Dividendo': 'ultimo_dividendo',
        'Dividend Yield': 'dividend_yield', 'DY (3M) Acumulado': 'dy_3m_acumulado',
        'DY (6M) Acumulado': 'dy_6m_acumulado', 'DY (12M) Acumulado': 'dy_12m_acumulado',
        'DY (3M) média': 'dy_3m_media', 'DY (6M) média': 'dy_6m_media',
        'DY (12M) média': 'dy_12m_media', 'DY Ano': 'dy_ano', 'Variação Preço': 'variacao_preco',
        'Rentab. Período': 'rentab_periodo', 'Rentab. Acumulada': 'rentab_acumulada',
        'Patrimônio Líquido': 'patrimonio_liquido', 'VPA': 'vpa', 'P/VPA': 'p_vpa',
        'DY Patrimonial': 'dy_patrimonial', 'Variação Patrimonial': 'variacao_patrimonial',
        'Rentab. Patr. Período': 'rentab_patr_periodo', 'Rentab. Patr. Acumulada': 'rentab_patr_acumulada',
        'Quant. Ativos': 'quant_ativos', 'Volatilidade': 'volatilidade', 'Num. Cotistas': 'num_cotistas',
        'Tax. Gestão': 'tax_gestao', 'Tax. Performance': 'tax_performance', 'Tax. Administração': 'tax_administracao'
    }

    sanitized_headers = [header_map.get(h) for h in headers]
    
    # --- DEBUGGING ---
    print(f"\n--- INÍCIO DA DEPURAÇÃO DE DADOS ---")
    print(f"Total de cabeçalhos mapeados: {len(sanitized_headers)}")
    if rows:
        print(f"Total de células na primeira linha de dados: {len(rows[0])}")
        print(f"Conteúdo da primeira linha (bruto): {rows[0]}")
    print(f"--- FIM DA DEPURAÇÃO DE DADOS ---\n")
    # --- FIM DEBUGGING ---

    integer_columns = {'quant_ativos', 'num_cotistas'}
    
    numeric_columns = {
        'preco_atual_rs', 'liquidez_diaria_rs', 'p_vp', 'ultimo_dividendo',
        'patrimonio_liquido', 'vpa', 'p_vpa', 'dividend_yield', 'dy_3m_acumulado',
        'dy_6m_acumulado', 'dy_12m_acumulado', 'dy_3m_media', 'dy_6m_media',
        'dy_12m_media', 'dy_ano', 'dy_patrimonial', 'variacao_preco',
        'rentab_periodo', 'rentab_acumulada', 'variacao_patrimonial',
        'rentab_patr_periodo', 'rentab_patr_acumulada', 'volatilidade'
    }

    records_to_upsert = []
    for row in rows:
        record = {}
        # Ignora linhas que não tem o mesmo número de colunas que o cabeçalho
        if len(row) != len(sanitized_headers):
            continue
            
        for header, value in zip(sanitized_headers, row):
            if not header: # Pula se o cabeçalho não foi mapeado
                continue
            if header in integer_columns:
                record[header] = clean_and_convert(value, to_int=True)
            elif header in numeric_columns:
                record[header] = clean_and_convert(value)
            else:
                record[header] = value if value.strip() not in ('', '--', 'N/A') else None
        
        # Garante que a chave primária não seja nula
        if record.get('fundos'):
            records_to_upsert.append(record)

    if not records_to_upsert:
        print("Nenhum dado válido para ser salvo no banco.")
        return

    print("\n--- INÍCIO DA INTERAÇÃO COM O SUPABASE ---")
    print(f"Primeiro registro a ser enviado (exemplo): {records_to_upsert[0]}")

    try:
        print(f"Enviando {len(records_to_upsert)} registros para o Supabase (tabela: {table_name})...")
        response = supabase.table(table_name).upsert(records_to_upsert).execute()
        
        # O Supabase não retorna um erro em caso de falha, então verificamos a resposta
        if hasattr(response, 'data') and response.data:
            print("Dados salvos no Supabase com sucesso!")
            print(f"Resposta do Supabase (primeiro item): {response.data[0]}")
        else:
            print("O Supabase não retornou dados de sucesso. Verifique se a tabela e as permissões estão corretas.")
            if hasattr(response, 'error') and response.error:
                print(f"Detalhe do erro do Supabase: {response.error}")
            else:
                print(f"Resposta completa (sem dados): {response}")

    except Exception as e:
        print(f"Ocorreu uma exceção CRÍTICA ao salvar dados no Supabase: {e}")
    
    print("--- FIM DA INTERAÇÃO COM O SUPABASE ---\n")

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
        
        # Após gerar o HTML, salva no Supabase
        save_to_supabase(headers, rows)
        
    else:
        print("Processo finalizado sem extração de dados.")

if __name__ == '__main__':
    main()
