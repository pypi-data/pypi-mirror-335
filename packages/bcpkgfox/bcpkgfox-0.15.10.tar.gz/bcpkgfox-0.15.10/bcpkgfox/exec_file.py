import subprocess
import threading
import argparse
import time
import sys
import os

def main():
    class exec_gen():
        def __init__(self):
            self.current_dir = None

        def preparations(self):
            self.current_dir = os.getcwd()

            parser = argparse.ArgumentParser(description="Script to generate .exe and preventing bugs")
            parser.add_argument("file", type=str, help="Put the name of file after the command (with the extension '.py')")

            args = parser.parse_args()
            target_file = os.path.join(self.current_dir, args.file)

            if not os.path.exists(target_file):
                print(f"Error: File '{target_file}' does not exist.")
                return

        def run_pyinstaller(self):
            global process_finished

            def print_footer():
                """Função que mantém a mensagem 'Aguarde download' na última linha."""
                while not process_finished:
                    sys.stdout.write("\rAguarde download...")
                    sys.stdout.flush()
                    time.sleep(0.1)

            process_finished = False

            command = ["pyinstaller", "target_file"]
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

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
            footer_thread.join()
            print("\nProcesso concluído!")

    script = exec_gen()
    script.preparations()
    script.run_pyinstaller()
