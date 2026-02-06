import os
import time
import shutil
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config import RELATORIOS # Importa as receitas que criamos no config.py

load_dotenv()

PASTA_DOWNLOAD = os.path.join(os.path.dirname(__file__), "relatorios_xlsx")

def configurar_driver():
    if not os.path.exists(PASTA_DOWNLOAD):
        os.makedirs(PASTA_DOWNLOAD)
    
    chrome_options = Options()
    # Para ver o robô trabalhando, deixe a linha abaixo comentada. 
    # Para rodar "escondido", remova o #.
    # chrome_options.add_argument("--headless") 
    
    prefs = {
        "download.default_directory": PASTA_DOWNLOAD,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def verificar_e_recuperar_perfil(driver, wait, url_alvo):
    """A Função Guardiã para o bug da tela de perfil."""
    time.sleep(2)
    if "home/user/profile" in driver.current_url:
        print("[Scraper] Alerta: Tela de perfil detectada. Recuperando...")
        try:
            # Tenta clicar no botão 'Aplicar' (ajuste o seletor se mudar no sistema)
            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-cy="APPLY"]')))
            btn.click()
            time.sleep(2)
            driver.get(url_alvo)
        except Exception as e:
            print(f"[Scraper] Erro ao tentar sair da tela de perfil: {e}")

def extrair_relatorio(tipo_relatorio):
    config = RELATORIOS.get(tipo_relatorio)
    if not config:
        print(f"[Scraper] Erro: Relatório {tipo_relatorio} não configurado.")
        return None

    driver = configurar_driver()
    wait = WebDriverWait(driver, 30)
    
    try:
        # 1. Login
        print(f"[Scraper] Acessando URL de Login...")
        driver.get(os.getenv("PSOFFICE_URL"))
        
        print(f"[Scraper] Preenchendo credenciais...")
        wait.until(EC.presence_of_element_located((By.ID, "user_login"))).send_keys(os.getenv("PSOFFICE_USER"))
        driver.find_element(By.ID, "user_pass").send_keys(os.getenv("PSOFFICE_PASSWORD"))
        driver.find_element(By.ID, "button_processLogin").click()
        
        print("[Scraper] Login enviado. Aguardando processamento da sessão...")
        # 2. Navegação Direta

        try:
            # Aqui esperamos o corpo da página inicial carregar ou a URL mudar
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3) # Tempo técnico para o navegador estabilizar os cookies
            print("[Scraper] Sessão validada com sucesso.")
        except:
            print("[Scraper] Aviso: Demora na resposta do servidor após login.")


        print(f"[Scraper] Login feito. Indo para a URL do relatório: {config['url']}")
        driver.get(config["url"])
        
        # Chama o guardião caso caia na tela de perfil
        verificar_e_recuperar_perfil(driver, wait, config["url"])

        # 3. Execução das Ações
        for i, acao in enumerate(config["acoes"]):
            print(f"[Scraper] Executando ação {i+1}: {acao['type']} no seletor {acao['selector']}")
            
            # Espera o elemento aparecer antes de interagir
            elemento = wait.until(EC.presence_of_element_located(acao["selector"]))
            
            if acao["type"] == "select":
                Select(elemento).select_by_value(acao["value"])
                print(f"          Formato {acao['value']} selecionado.")
            elif acao["type"] == "click":
                # Espera ser clicável antes de clicar
                wait.until(EC.element_to_be_clickable(acao["selector"])).click()
                print(f"          Botão clicado.")
            time.sleep(4) # Pequena pausa para o sistema processar

        print(f"[Scraper] Todas as ações feitas. Aguardando o download do arquivo...")
        
        # Loop para esperar o arquivo aparecer na pasta (mais seguro que sleep fixo)
        tentativas_download = 0
        while tentativas_download < 20:
            arquivos = [f for f in os.listdir(PASTA_DOWNLOAD) if not f.endswith('.crdownload') and not f.endswith('.tmp')]
            if arquivos:
                arquivo_recente = max([os.path.join(PASTA_DOWNLOAD, f) for f in arquivos], key=os.path.getctime)
                print(f"[Scraper] Download detectado: {os.path.basename(arquivo_recente)}")
                return arquivo_recente
            
            time.sleep(2)
            tentativas_download += 1
            if tentativas_download % 5 == 0:
                print(f"          Ainda aguardando arquivo na pasta {PASTA_DOWNLOAD}...")

        print("[Scraper] Erro: O tempo de espera pelo download esgotou.")
        return None

    except Exception as e:
        print(f"\n[Scraper] !!! ERRO DURANTE A EXTRAÇÃO !!!")
        print(f"Dica: Verifique se o ID '{acao['selector']}' está correto no config.py")
        print(f"Detalhes: {e}")
        driver.save_screenshot("erro_extracao.png")
        return None
    finally:
        driver.quit()