import subprocess
import threading
import time
import sys

def print_footer():
    """Função que mantém a mensagem 'Aguarde download' na última linha."""
    while not process_finished:
        sys.stdout.write("\rAguarde download...")  # Reescreve a mensagem
        sys.stdout.flush()
        time.sleep(0.1)  # Intervalo para evitar sobrecarga

def run_pyinstaller():
    global process_finished
    process_finished = False

    # Comando PyInstaller (substitua pelo seu comando real)
    command = ["pyinstaller", "seu_script.py"]

    # Inicia o processo do PyInstaller
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    # Inicia a thread para exibir o footer
    footer_thread = threading.Thread(target=print_footer)
    footer_thread.start()

    # Lê a saída do PyInstaller em tempo real
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            # Exibe o log do PyInstaller
            sys.stdout.write(f"{output.strip()}\n")
            sys.stdout.flush()

    # Finaliza
    process_finished = True
    footer_thread.join()  # Aguarda a thread do footer terminar
    print("\nProcesso concluído!")

if __name__ == "__main__":
    run_pyinstaller()