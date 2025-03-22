import subprocess
import threading
import argparse
import time
import sys
import re
import os

class cli:
    def __init__(self):
        self.current_dir = os.getcwd()

        self.visuals = self.visual(self)
        self.exec_gen = self.exec_gen_(self)
        self.find_imports = self.find_import(self)

    class visual:
        def __init__(self):
            self.RESET = "\033[0m"
            self.DK_ORANGE = "\033[38;5;130m"
            self.Neg = "\033[1m"
            self.hue = 0

        def hsl_to_rgb(self, h, s, l):
            h = h % 360
            c = (1 - abs(2 * l - 1)) * s
            x = c * (1 - abs((h / 60) % 2 - 1))
            m = l - c / 2

            if 0 <= h < 60: r, g, b = c, x, 0
            elif 60 <= h < 120: r, g, b = x, c, 0
            elif 120 <= h < 180: r, g, b = 0, c, x
            elif 180 <= h < 240: r, g, b = 0, x, c
            elif 240 <= h < 300: r, g, b = x, 0, c
            elif 300 <= h < 360: r, g, b = c, 0, x

            r = int((r + m) * 255) ; g = int((g + m) * 255) ; b = int((b + m) * 255)
            return r, g, b

        def rgb_text(self, text, r, g, b): return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

        def animate_rgb_text(self, text, delay=0.01):
            r, g, b = self.hsl_to_rgb(self.hue, s=1.0, l=0.5)
            self.hue = (self.hue + 1) % 360
            time.sleep(delay)
            return f"    \033[1m{self.rgb_text(text, r, g, b)}\033[0m"

    class exec_gen_:
        def __init__(self, self_cli):
            self.cli = self_cli
            self.current_dir = None
            self.self.target_file = None
            self.file_name = None
            self.visuals = self.cli.visuals

        def preparations(self):
            self.current_dir = os.getcwd()

            parser = argparse.ArgumentParser(description="Script to generate .exe and preventing bugs")
            parser.add_argument("file", type=str, help="Put the name of file after the command (with the extension '.py')")

            args = parser.parse_args()
            self.file_name = args.file
            self.self.target_file = os.path.join(self.current_dir, self.file_name)

            if not os.path.exists(self.self.target_file):
                print(f"Error: File '{self.self.target_file}' does not exist.")
                return

        def run_pyinstaller(self):
            global process_finished

            def print_footer():
                """Função que mantém a mensagem 'Aguarde download' na última linha."""
                while not process_finished:
                    sys.stdout.write(f"\r \033[F\r\033[K\033[E {self.visuals.animate_rgb_text(f"   {self.visuals.Neg}| Gerando executável do '{self.file_name}', aguarde finalização. |{self.visuals.RESET}")}\n\033[F")
                    sys.stdout.flush()

            process_finished = False
            command = ["pyinstaller", self.self.target_file]
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            footer_thread = threading.Thread(target=print_footer)
            footer_thread.start()

            # Lê a saída do PyInstaller em tempo real
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    sys.stdout.write(f"\033[F\r\033[K{output.strip()}\033[K\n\n")
                    sys.stdout.flush()

            process_finished = True
            footer_thread.join()

            print(f"\r \033[F\r\033[K\033[f\r\033[K\033[2E{self.visuals.Neg}{self.visuals.DK_ORANGE}>{self.visuals.RESET}{self.visuals.Neg} Executável gerado com sucesso!\n{self.visuals.RESET}\033[3E")

        def main():
            script = exec_gen()
            visuals = visual()
            script.preparations()
            script.run_pyinstaller()

    class find_import:
        def __init__(self, self_cli):
            self.cli = self_cli
            self.visuals = self.cli.visuals

            self.imports = None

        def hsl_to_rgb(self, h, s, l):
            h = h % 360
            c = (1 - abs(2 * l - 1)) * s
            x = c * (1 - abs((h / 60) % 2 - 1))
            m = l - c / 2

            if 0 <= h < 60: r, g, b = c, x, 0
            elif 60 <= h < 120: r, g, b = x, c, 0
            elif 120 <= h < 180: r, g, b = 0, c, x
            elif 180 <= h < 240: r, g, b = 0, x, c
            elif 240 <= h < 300: r, g, b = x, 0, c
            elif 300 <= h < 360: r, g, b = c, 0, x

            r = int((r + m) * 255) ; g = int((g + m) * 255) ; b = int((b + m) * 255)
            return r, g, b

        def rgb_text(self, text, r, g, b): return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

        def animate_rgb_text(self, text, delay=0.01):
            import time
            from bcpkgfox import DK_ORANGE
            hue = 0
            print(f" {DK_ORANGE}>{self.visuals.RESET} Dependências do arquivo {self.visuals.ORANGE}'{self.target_file}'{self.visuals.RESET} identificadas com sucesso")
            time.sleep(2)
            print(f"{DK_ORANGE} PIP:{self.visuals.RESET}")
            while True:
                r, g, b = self.hsl_to_rgb(hue, s=1.0, l=0.5)
                print(f" ---> \033[1m{self.rgb_text(text, r, g, b)}\033[0m (CTRL + C)", end="\r")
                hue = (hue + 1) % 360
                time.sleep(delay)

        def main(self):
            current_dir = os.getcwd()

            parser = argparse.ArgumentParser(description="A CLI tool to find imports.")
            parser.add_argument("file", type=str, help="The target .py file to process")

            args = parser.parse_args()
            self.self.target_file = os.path.join(current_dir, args.file)

            if not os.path.exists(self.target_file):
                print(f"Error: File '{self.target_file}' does not exist.")
                return

            try:
                with open(self.target_file, "r", encoding="utf-8", errors="replace") as file:
                    file_content = file.read()
            except Exception as e:
                print(f"Error reading file: {e}")
                return

            if not file_content:
                print(f"Erro: Não foi possível ler o arquivo '{self.target_file}' com nenhuma codificação testada.")
                return

            libraries = [
                'undetected-chromedriver',
                'webdriver-manager',
                'opencv-python',
                'pygetwindow',
                'setuptools',
                'pyscreeze',
                'pyautogui',
                'selenium',
                'requests',
                'PyMuPDF',
                'Pillow',
                'psutil'
            ]

            self.imports = []
            for lib in libraries:
                pattern = rf"\b{re.escape(lib)}\b"
                if re.search(pattern, file_content):
                    self.imports.append(lib)

            if re.search(r"\.extract_pdf\b", file_content):
                self.imports.append("PyMuPDF")

            if re.search(r"\.import requests\b", file_content):
                self.imports.append("requests")

            if re.search(r"\.import pyautogui\b", file_content):
                self.imports.append("pyautogui")

            if re.search(r"\.from PIL import Image\b", file_content):
                self.imports.append("Pillow")

            if re.search(r"\.from reportlab.lib import utils\b", file_content):
                self.imports.append("reportlab")

            if re.search(r"\.from PyPDF2 import PdfMerger\b", file_content):
                self.imports.append("PyPDF2")

            if re.search(r"\.import PyPDF2\b", file_content):
                self.imports.append("PyPDF2")

            if re.search(r"\.invoke_api_\b", file_content):
                self.imports.append("requests")

            if re.search(r"\.wait_for\b", file_content):
                self.imports.append("pygetwindow")

            if re.search(r"\.from selenium_stealth import stealth\b", file_content):
                self.imports.append("selenium-stealth")

            if re.search(r"\.import undetected_chromedriver\b", file_content):
                self.imports.append("undetected-chromedriver")

            if re.search(r"\.from webdriver_manager.chrome import ChromeDriverManager\b", file_content):
                self.imports.append("webdriver-manager")

            if re.search(r"\.move_to_image\b", file_content):
                self.imports.extend(["pyscreeze", "pyautogui", "Pillow", "opencv-python"])

            if re.search(r"\.move_mouse_smoothly\b", file_content):
                self.imports.extend(["pyscreeze", "pyautogui", "Pillow"])

            if re.search(r"\.initialize_driver\b", file_content):
                self.imports.extend(["webdriver-manager", "undetected-chromedriver", "pyautogui", "psutil"])

            if re.search(r"\.stealth max\b", file_content):
                self.imports.extend(["webdriver-manager", "undetected-chromedriver", "fake-useragent"])

            imports = list(set(imports))
            import pyperclip
            pyperclip.copy(f"pip install {' '.join(imports)}")

            from bcpkgfox import DK_ORANGE, ORANGE, RESET
            if imports:

                def print_footer():
                    """Função que mantém a mensagem 'Aguarde download' na última linha."""
                    while not process_finished:
                        sys.stdout.write(f"\r \033[F\r\033[K\033[E {self.visuals.animate_rgb_text(f"   {self.visuals.Neg}| Gerando executável do '{self.file_name}', aguarde finalização. |{self.visuals.RESET}")}\n\033[F")
                        sys.stdout.flush()

                process_finished = False
                command = ["pyinstaller", self.self.target_file]
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                footer_thread = threading.Thread(target=print_footer)
                footer_thread.start()

                # Lê a saída do PyInstaller em tempo real
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        sys.stdout.write(f"\033[F\r\033[K{output.strip()}\033[K\n\n")
                        sys.stdout.flush()

                process_finished = True
                footer_thread.join()

                print(f"\r \033[F\r\033[K\033[f\r\033[K\033[2E{self.visuals.Neg}{self.visuals.DK_ORANGE}>{self.visuals.RESET}{self.visuals.Neg} Executável gerado com sucesso!\n{self.visuals.RESET}\033[3E")

                try: self.animate_rgb_text(f'pip install {" ".join(imports)}', delay=0.002)
                except KeyboardInterrupt: print(f" {DK_ORANGE}--->{RESET} {ORANGE}pip install {' '.join(imports)}{RESET}                   \n\n {DK_ORANGE}>{RESET} Copiado para sua área de transferencia. \n(obs: só identifica as libs que são pertencentes da bibliotca bcfox) \n")
            else: print("No libraries from the list were found in the script.")
