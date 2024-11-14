import requests
import string
import sys
import time
from queue import Queue
from threading import Thread

# Configurações
BASE_URL = "http://192.168.29.200/"  # Substitua pelo URL alvo
WORDLIST_CHARACTERS = string.ascii_letters + string.digits + "-_"
MAX_DEPTH = 10  # Profundidade máxima de caracteres para evitar loops infinitos
NUM_THREADS = 10  # Número de threads para acelerar a enumeração

# Variáveis globais
found_flag = False
flag = ""
lock = False  # Simples flag para controle de término

# Fila para gerenciar paths a serem testados
path_queue = Queue()

def worker():
    global found_flag, flag, lock
    while not path_queue.empty() and not found_flag:
        current_path = path_queue.get()
        print(f"[*] Testando /{current_path}")
        try:
            url = BASE_URL + current_path
            response = requests.get(url, timeout=5)
            # Verifica se a resposta contém a flag
            if response.status_code == 200:
                # check response size
                print(len(response.text))
            if response.status_code == 404:
                continue
            else:
                print(response.status_code)
                print(response.text)
       
        except requests.exceptions.RequestException as e:
            print(f"[-] Erro ao acessar /{current_path}: {e}")
        finally:
            path_queue.task_done()

def main():
    global found_flag, flag, lock
    print("Iniciando a enumeração de diretórios...\n")
    start_time = time.time()
    
    # Iniciar com paths de um único caractere
    for char in WORDLIST_CHARACTERS:
        path_queue.put(char)
    
    # Criar e iniciar threads
    threads = []
    for _ in range(NUM_THREADS):
        t = Thread(target=worker)
        t.daemon = True  # As threads encerram quando a thread principal encerra
        t.start()
        threads.append(t)
    
    try:
        while not path_queue.empty() and not found_flag:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Interrompido pelo usuário.")
    finally:
        # Aguardar todas as threads terminarem
        path_queue.join()
        end_time = time.time()
        duration = end_time - start_time
        if found_flag:
            print(f"\n[+] Flag encontrada em {duration:.2f} segundos!")
        else:
            print(f"\n[-] Flag não encontrada após {duration:.2f} segundos.")
        sys.exit(0)

if __name__ == "__main__":
    main()
