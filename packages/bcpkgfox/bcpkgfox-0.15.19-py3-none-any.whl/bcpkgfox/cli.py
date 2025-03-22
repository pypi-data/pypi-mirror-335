import argparse
import time
import re
import os

def main():

    def hsl_to_rgb(h, s, l):
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

    def rgb_text(text, r, g, b): return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

    def animate_rgb_text(text, delay=0.01):
        import time
        from bcpkgfox import DK_ORANGE
        hue = 0
        print(f" {DK_ORANGE}>{RESET} Dependências do arquivo {ORANGE}'{target_file}'{RESET} identificadas com sucesso")
        time.sleep(2)
        print(f"{DK_ORANGE} PIP:{RESET}")
        while True:
            r, g, b = hsl_to_rgb(hue, s=1.0, l=0.5)
            print(f" ---> \033[1m{rgb_text(text, r, g, b)}\033[0m (CTRL + C)", end="\r")
            hue = (hue + 1) % 360
            time.sleep(delay)

    current_dir = os.getcwd()

    parser = argparse.ArgumentParser(description="A CLI tool to find imports.")
    parser.add_argument("file", type=str, help="The target .py file to process")

    args = parser.parse_args()
    target_file = os.path.join(current_dir, args.file)

    if not os.path.exists(target_file):
        print(f"Error: File '{target_file}' does not exist.")
        return

    try:
        with open(target_file, "r", encoding="utf-8", errors="replace") as file:
            file_content = file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    if not file_content:
        print(f"Erro: Não foi possível ler o arquivo '{target_file}' com nenhuma codificação testada.")
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

    imports = []
    for lib in libraries:
        pattern = rf"\b{re.escape(lib)}\b"
        if re.search(pattern, file_content):
            imports.append(lib)

    if re.search(r"\.extract_pdf\b", file_content):
        imports.append("PyMuPDF")

    if re.search(r"\.invoke_api_\b", file_content):
        imports.append("requests")

    if re.search(r"\.wait_for\b", file_content):
        imports.append("pygetwindow")

    if re.search(r"\.from selenium_stealth import stealth\b", file_content):
        imports.append("selenium-stealth")

    if re.search(r"\.import undetected_chromedriver\b", file_content):
        imports.append("undetected-chromedriver")

    if re.search(r"\.from webdriver_manager.chrome import ChromeDriverManager\b", file_content):
        imports.append("webdriver-manager")

    if re.search(r"\.move_to_image\b", file_content):
        imports.extend(["pyscreeze", "pyautogui", "Pillow", "opencv-python"])

    if re.search(r"\.move_mouse_smoothly\b", file_content):
        imports.extend(["pyscreeze", "pyautogui", "Pillow"])

    if re.search(r"\.initialize_driver\b", file_content):
        imports.extend(["webdriver-manager", "undetected-chromedriver", "pyautogui", "psutil"])

    if re.search(r"\.stealth max\b", file_content):
        imports.extend(["webdriver-manager", "undetected-chromedriver", "fake-useragent"])

    imports = list(set(imports))
    import pyperclip
    pyperclip.copy(f"pip install {' '.join(imports)}")

    from bcpkgfox import DK_ORANGE, ORANGE, RESET
    if imports:
        try:
            animate_rgb_text(f'pip install {" ".join(imports)}', delay=0.002)
        except KeyboardInterrupt:
            print(f" {DK_ORANGE}--->{RESET} {ORANGE}pip install {' '.join(imports)}{RESET}                   \n\n {DK_ORANGE}>{RESET} Copiado para sua área de transferencia. \n(obs: só identifica as libs que são pertencentes da bibliotca bcfox) \n")
    else:
        print("No libraries from the list were found in the script.")
if __name__ == "__main__":
    main()