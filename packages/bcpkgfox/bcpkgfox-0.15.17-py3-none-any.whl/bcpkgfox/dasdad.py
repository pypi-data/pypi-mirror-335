from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from typing import Optional

import undetected_chromedriver as uc

import random
import sys
import os

download_dir = "C:\\TMPIMGKIT\\LAST_IMG"

# Configurações para o Chrome
options = uc.ChromeOptions()
extension_path = "capmonster"
# extensao_caminho = os.path.abspath(extension_path)

# options = Options()
# options.add_argument(f'--load-extension={extensao_caminho}')
# driver = uc.Chrome(options=options)
print()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def backcode__dont_use__set_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    ]
    return random.choice(user_agents)

# Alterar o User-Agent
options.add_argument(f"user-agent={backcode__dont_use__set_user_agent()}")

# Default's
profile = {
    'download.prompt_for_download': False,
    'download.directory_upgrade': True,
    'download.default_directory': download_dir,
}
options.add_experimental_option('prefs', profile)

# extensao_caminho = resource_path(extension_path)
extensao_caminho = os.path.abspath(extension_path)
# print(extensao_caminho)

# Configurações para reduzir detecção
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--start-maximized')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-infobars')

if extension_path:
    options.add_argument(f'--load-extension={extensao_caminho}')

# options.add_argument('--disable-extensions') # Fix: Possibilita ter extensões ou não, nunca influenciou na detecção

# Inicializar o navegador com undetected_chromedriver
driver = uc.Chrome(options=options, use_subprocess=True)

driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
